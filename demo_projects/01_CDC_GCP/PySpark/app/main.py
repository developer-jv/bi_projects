import os
import json
import urllib.request
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import BinaryType, DecimalType, LongType
from pyspark.sql.avro.functions import from_avro

# --------- ENV ---------
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "broker:9092")
SCHEMA_REGISTRY = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8081")
TOPIC = os.getenv("KAFKA_TOPIC", "erp_avro.erp.orders")
WAREHOUSE = os.getenv("ICEBERG_WAREHOUSE", "file:/opt/tables_apache_iceberg/warehouse")
CATALOG = os.getenv("ICEBERG_CATALOG", "lh")
DB = os.getenv("ICEBERG_DB", "erp")
TABLE = os.getenv("ICEBERG_TABLE", "orders_iceberg")
CHECKPOINT = os.getenv("CHECKPOINT_DIR", "file:/opt/checkpoints/orders_iceberg")

# --------- Spark + Iceberg ---------
spark = (
    SparkSession.builder.appName("kafka-to-iceberg-cdc")
    .config(f"spark.sql.catalog.{CATALOG}", "org.apache.iceberg.spark.SparkCatalog")
    .config(f"spark.sql.catalog.{CATALOG}.type", "hadoop")
    .config(f"spark.sql.catalog.{CATALOG}.warehouse", WAREHOUSE)
    .config("spark.sql.adaptive.enabled", "true")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# --------- Schema Registry (sin 'requests') ---------
def get_latest_value_schema(topic: str) -> str:
    subject = f"{topic}-value"
    url = f"{SCHEMA_REGISTRY}/subjects/{subject}/versions/latest"
    with urllib.request.urlopen(url, timeout=10) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload["schema"]

AVRO_SCHEMA_VALUE = get_latest_value_schema(TOPIC)

# --------- Confluent Avro wire -> Avro puro ---------
@F.udf(returnType=BinaryType())
def strip_confluent_wire(b: bytes):
    # Wire format: [magic:1][schemaId:4][payload...]
    if b and len(b) > 5:
        return b[5:]
    return None

# --------- Stream desde Kafka ---------
kafka_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
    .option("subscribe", TOPIC)
    .option("startingOffsets", "latest")  # usa 'earliest' si quieres re-procesar desde el inicio
    .load()
)

decoded = (
    kafka_df
    .select(strip_confluent_wire(F.col("value")).alias("value_raw"))
    .select(from_avro(F.col("value_raw"), AVRO_SCHEMA_VALUE).alias("r"))
)

# --------- Crear namespace/tabla si no existen ---------
spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {CATALOG}.{DB}")
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{DB}.{TABLE} (
  order_id BIGINT,
  customer_id BIGINT,
  amount DECIMAL(12,2),
  status STRING,
  ts TIMESTAMP
) USING iceberg
PARTITIONED BY (days(ts))
""")

# --------- foreachBatch robusto (1 sola vista global por batch) ---------
def upsert_batch(df, batch_id: int):
    # df = micro-lote de 'decoded' (tiene la columna 'r')
    df_cdc = df.select(
        F.col("r.op").alias("op"),
        F.col("r.ts_ms").cast(LongType()).alias("ts_ms"),
        F.col("r.before").alias("before"),
        F.col("r.after").alias("after")
    )

    # Unificamos clave: para 'd' viene en before; para 'c/u' viene en after
    stage = (
        df_cdc.select(
            F.col("op"),
            # clave
            F.coalesce(F.col("after.order_id"), F.col("before.order_id")).cast("long").alias("order_id"),
            # columnas de negocio (solo de 'after'; en delete quedarán nulas y no se usan)
            F.col("after.customer_id").cast("long").alias("customer_id"),
            F.col("after.amount").cast(DecimalType(12,2)).alias("amount"),
            F.col("after.status").cast("string").alias("status"),
            # timestamp a partir de ts_ms (epoch millis)
            F.to_timestamp(F.from_unixtime((F.col("ts_ms")/1000))).alias("ts")
        )
        .where(F.col("order_id").isNotNull())
    )

    # Si no hay filas en el micro-lote, no intentes MERGE
    cnt = stage.count()
    if cnt == 0:
        return

    vname = f"stage_cdc_{batch_id}"          # nombre único por batch
    stage.createOrReplaceGlobalTempView(vname)

    spark.sql(f"""
      MERGE INTO {CATALOG}.{DB}.{TABLE} t
      USING global_temp.{vname} s
      ON t.order_id = s.order_id
      WHEN MATCHED AND s.op = 'd' THEN DELETE
      WHEN MATCHED THEN UPDATE SET
        t.customer_id = s.customer_id,
        t.amount      = s.amount,
        t.status      = s.status,
        t.ts          = s.ts
      WHEN NOT MATCHED AND s.op <> 'd' THEN INSERT (order_id, customer_id, amount, status, ts)
      VALUES (s.order_id, s.customer_id, s.amount, s.status, s.ts)
    """)

    # Limpieza opcional (la vista global se sobreescribe en el siguiente batch igualmente)
    try:
        spark.catalog.dropGlobalTempView(vname)
    except Exception:
        pass

query = (
    decoded.writeStream
    .trigger(processingTime="5 seconds")
    .option("checkpointLocation", CHECKPOINT)
    .foreachBatch(upsert_batch)
    .outputMode("update")  # se ignora con foreachBatch, pero es requerido por la API
    .start()
)

query.awaitTermination()
