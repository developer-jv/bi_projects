from __future__ import annotations

from pyspark.sql import functions as F

from pipeline.common.spark_session import build_spark_session


def build_gold_layer(run_context: dict) -> dict:
    spark = build_spark_session("lakehouse_gold")

    orders = spark.table("lakehouse.silver.orders")
    order_items = spark.table("lakehouse.silver.order_items")
    products = spark.table("lakehouse.silver.products")
    customers = spark.table("lakehouse.silver.customers")

    fact_sales = (
        order_items.join(orders, "order_id", "inner")
        .join(products, "product_id", "left")
        .withColumn("revenue", F.col("quantity").cast("double") * F.col("unit_price").cast("double"))
    )

    sales_by_month = (
        fact_sales.withColumn("sales_month", F.date_format("order_timestamp", "yyyy-MM"))
        .groupBy("sales_month", "category")
        .agg(F.sum("revenue").alias("revenue"))
    )

    customer_lifetime_value = (
        fact_sales.join(customers.select("customer_id"), "customer_id", "left")
        .groupBy("customer_id")
        .agg(F.sum("revenue").alias("lifetime_value"))
    )

    fact_sales.writeTo("lakehouse.gold.fact_sales").using("iceberg").createOrReplace()
    products.writeTo("lakehouse.gold.dim_product").using("iceberg").createOrReplace()
    customers.writeTo("lakehouse.gold.dim_customer").using("iceberg").createOrReplace()
    sales_by_month.writeTo("lakehouse.gold.sales_by_month").using("iceberg").createOrReplace()
    customer_lifetime_value.writeTo("lakehouse.gold.customer_lifetime_value").using("iceberg").createOrReplace()

    spark.stop()
    return {"batch_id": run_context["batch_id"], "gold_tables": 5}
