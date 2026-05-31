from datetime import datetime

from airflow.sdk import dag, get_current_context, task

from pipeline.bronze.ingest_raw_to_s3 import ingest_all_sources
from pipeline.catalog.glue_catalog import run_glue_crawlers
from pipeline.gold.silver_to_gold import build_gold_layer
from pipeline.quality.athena_validation import run_athena_validations
from pipeline.silver.bronze_to_silver import build_silver_layer


@dag(
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["lakehouse", "spark", "iceberg", "aws"],
)
def lakehouse_medallion_pipeline():
    @task
    def bronze() -> dict:
        context = get_current_context()
        dag_run = context.get("dag_run")
        process_date = None
        if dag_run and getattr(dag_run, "conf", None):
            process_date = dag_run.conf.get("process_date")
        return ingest_all_sources(
            process_date=process_date,
            logical_date=context["logical_date"],
        )

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
