from __future__ import annotations

from pipeline.common.aws import build_boto3_session
from pipeline.common.config import load_settings


VALIDATION_QUERIES = [
    "SELECT count(*) AS rows_customers FROM silver.customers",
    "SELECT count(*) AS rows_fact_sales FROM gold.fact_sales",
]


def run_athena_validations() -> list[dict]:
    settings = load_settings()
    session = build_boto3_session()
    athena = session.client("athena", region_name=settings.aws_region)
    results = []
    for query in VALIDATION_QUERIES:
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": "gold"},
            ResultConfiguration={"OutputLocation": settings.athena_output},
            WorkGroup="lakehouse-analytics",
        )
        results.append({"query": query, "execution_id": response["QueryExecutionId"]})
    return results
