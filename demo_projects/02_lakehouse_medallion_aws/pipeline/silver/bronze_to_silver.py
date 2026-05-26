from __future__ import annotations

from pyspark.sql import functions as F

from pipeline.common.config import load_settings
from pipeline.common.spark_session import build_spark_session


def _mask(value: F.Column) -> F.Column:
    return F.concat(F.substring(value, 1, 2), F.lit("***"))


def build_silver_layer(run_context: dict) -> dict:
    settings = load_settings()
    spark = build_spark_session("lakehouse_silver")
    base = f"s3a://{settings.lakehouse_bucket}/bronze"

    customers = (
        spark.read.option("multiline", True).json(f"{base}/customers/ingestion_date={run_context[ingestion_date]}/*.json")
        .withColumn("email_masked", _mask(F.col("email")))
        .withColumn("phone_masked", _mask(F.col("phone")))
        .dropDuplicates(["customer_id"])
    )
    products = spark.read.option("header", True).csv(f"{base}/products/ingestion_date={run_context[ingestion_date]}/*.csv")
    orders = spark.read.option("header", True).csv(f"{base}/orders/ingestion_date={run_context[ingestion_date]}/*.csv")
    order_items = spark.read.option("header", True).csv(f"{base}/order_items/ingestion_date={run_context[ingestion_date]}/*.csv")

    customers.writeTo("lakehouse.silver.customers").using("iceberg").createOrReplace()
    products.writeTo("lakehouse.silver.products").using("iceberg").createOrReplace()
    orders.writeTo("lakehouse.silver.orders").using("iceberg").createOrReplace()
    order_items.writeTo("lakehouse.silver.order_items").using("iceberg").createOrReplace()

    spark.stop()
    return {"batch_id": run_context["batch_id"], "silver_tables": 4}
