from datetime import datetime

from airflow.decorators import dag, task

from pipeline.bronze.ingest_raw_to_s3 import ingest_all_sources
from pipeline.silver.bronze_to_silver import build_silver_layer
from pipeline.gold.silver_to_gold import build_gold_layer
from pipeline.catalog.glue_catalog import run_glue_crawlers
from pipeline.quality.athena_validation import run_athena_validations


@dag(
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["lakehouse", "spark", "iceberg", "aws"],
)
def lakehouse_medallion_pipeline():
    @task
    def bronze() -> dict:
        return ingest_all_sources()

    @task
    def silver(run_context: dict) -> dict:
        return build_silver_layer(run_context)

    @task
    def gold(run_context: dict) -> dict:
        return build_gold_layer(run_context)

    @task
    def crawlers() -> list[str]:
        return run_glue_crawlers()

    @task
    def athena_checks() -> list[dict]:
        return run_athena_validations()

    bronze_ctx = bronze()
    silver_ctx = silver(bronze_ctx)
    gold_ctx = gold(silver_ctx)
    crawler_runs = crawlers()
    quality = athena_checks()

    bronze_ctx >> silver_ctx >> gold_ctx >> crawler_runs >> quality


dag = lakehouse_medallion_pipeline()
