#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para Spark Connect + Oracle con creación de tablas dentro del test.

Hace:
1) Conecta a Spark Connect (sc://localhost:15002)
2) Job pequeño -> escribe salida en ./_out_local
3) (Nuevo) Asegura que exista DEMO.EMP creando la tabla con datos de ejemplo si no existe
4) Lee DEMO.EMP y guarda una muestra en ./_out_local/jdbc_sample
5) Inserta "hola mundo" en DEMO.HOLA_MUNDO (crea la tabla si no existe)

Requisitos en el servidor spark-connect:
  --packages "com.oracle.database.jdbc:ojdbc11:23.4.0.24.05"
"""

from pyspark.sql import SparkSession, functions as F, types as T
import os

# ---------- Config "quemada" ----------
CONNECT_URL = "sc://localhost:15002"

ORA_HOST = "192.168.1.14"
ORA_PORT = 1521
ORA_SERVICE = "XEPDB1"
ORA_USER = "demo"
ORA_PASSWORD = "demo1234"

EMP_TABLE = "DEMO.EMP"
HOLA_TABLE = "DEMO.HOLA_MUNDO"

OUT_DIR = "./_out_local"
# -------------------------------------

JDBC_URL = f"jdbc:oracle:thin:@//{ORA_HOST}:{ORA_PORT}/{ORA_SERVICE}"
DRIVER = "oracle.jdbc.OracleDriver"


def ensure_outdir():
    os.makedirs(OUT_DIR, exist_ok=True)


def tiny_job(spark):
    df = spark.range(0, 100000).withColumn("parity", (F.col("id") % 2))
    agg = df.groupBy("parity").count().orderBy("parity")
    print("[INFO] Tiny job result:")
    agg.show()
    out_path = os.path.join(OUT_DIR, "connect_smoke_test")
    print(f"[INFO] Writing tiny job output to: {out_path}")
    (agg.coalesce(1)
        .write.mode("overwrite")
        .format("json")
        .save(out_path))


def jdbc_read_table(spark, table):
    print(f"[INFO] Leyendo {table} ...")
    df = (spark.read.format("jdbc")
          .option("url", JDBC_URL)
          .option("driver", DRIVER)
          .option("user", ORA_USER)
          .option("password", ORA_PASSWORD)
          .option("dbtable", table)
          .load())
    df.show(5, truncate=False)
    out_path = os.path.join(OUT_DIR, "jdbc_sample")
    print(f"[INFO] Escribiendo muestra JDBC en: {out_path}")
    (df.limit(100).coalesce(1)
       .write.mode("overwrite").parquet(out_path))


def ensure_emp_table(spark):
    """
    Garantiza que EMP_TABLE exista.
    Intentamos leer; si falla con ORA-00942, la creamos escribiendo un DF de ejemplo (overwrite).
    """
    try:
        jdbc_read_table(spark, EMP_TABLE)
        print(f"[INFO] {EMP_TABLE} ya existe.")
        return
    except Exception as e:
        msg = str(e)
        if "ORA-00942" not in msg and "table or view does not exist" not in msg.lower():
            print(f"[WARN] Fallo al leer {EMP_TABLE}, pero no parece ORA-00942. Detalle: {e}")
            # Igual intentamos crearla para efectos demo
        else:
            print(f"[INFO] {EMP_TABLE} no existe. La crearemos con datos de ejemplo...")

    sample = [
        (7369, "SMITH", "CLERK",   "1980-12-17",  800.00),
        (7499, "ALLEN", "SALESMAN","1981-02-20", 1600.00),
        (7521, "WARD",  "SALESMAN","1981-02-22", 1250.00),
    ]
    schema = T.StructType([
        T.StructField("EMPNO",   T.IntegerType(), False),
        T.StructField("ENAME",   T.StringType(),  True),
        T.StructField("JOB",     T.StringType(),  True),
        T.StructField("HIREDATE",T.StringType(),  True),  # luego lo convertimos a DATE en Oracle si quieres
        T.StructField("SAL",     T.DoubleType(),  True),
    ])
    df_emp = spark.createDataFrame(sample, schema=schema)
    # Escribimos con overwrite para que Oracle cree la tabla con ese esquema base
    print(f"[INFO] Creando {EMP_TABLE} con datos de ejemplo...")
    (df_emp.write.format("jdbc")
        .option("url", JDBC_URL)
        .option("driver", DRIVER)
        .option("user", ORA_USER)
        .option("password", ORA_PASSWORD)
        .option("dbtable", EMP_TABLE)
        .mode("overwrite")
        .save())
    print(f"[INFO] {EMP_TABLE} creada.")
    # Re-lee para mostrar
    jdbc_read_table(spark, EMP_TABLE)


def insert_hola_mundo(spark):
    print(f"[INFO] Insertando 'hola mundo' en {HOLA_TABLE} ...")
    df = spark.createDataFrame([(1, "hola mundo")], ["id", "mensaje"]) \
               .withColumn("ts", F.current_timestamp())

    writer = (df.write.format("jdbc")
              .option("url", JDBC_URL)
              .option("driver", DRIVER)
              .option("user", ORA_USER)
              .option("password", ORA_PASSWORD)
              .option("dbtable", HOLA_TABLE))

    try:
        writer.mode("append").save()
        print("[INFO] Inserción append OK.")
    except Exception as e:
        print(f"[WARN] Append falló, intentando crear tabla con overwrite. Motivo: {e}")
        writer.mode("overwrite").save()
        print("[INFO] Tabla creada e inserción OK con overwrite.")


def main():
    ensure_outdir()
    print(f"[INFO] Conectando a Spark Connect en: {CONNECT_URL}")
    spark = SparkSession.builder.remote(CONNECT_URL).appName("oracle-demo-create").getOrCreate()

    tiny_job(spark)
    ensure_emp_table(spark)     # crea DEMO.EMP si no existe y la lee
    insert_hola_mundo(spark)    # inserta/crea DEMO.HOLA_MUNDO

    spark.stop()
    print("[DONE] Demo finalizada. Revisa:", OUT_DIR)


if __name__ == "__main__":
    main()
