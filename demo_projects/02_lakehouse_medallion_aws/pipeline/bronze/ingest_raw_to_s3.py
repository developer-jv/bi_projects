from __future__ import annotations

from pipeline.common.aws import build_boto3_session
from pipeline.common.config import build_run_context, load_settings
from pipeline.common.sample_data import build_sample_payloads


def ingest_all_sources() -> dict:
    settings = load_settings()
    run_context = build_run_context()
    session = build_boto3_session()
    s3 = session.client("s3")
    payloads = build_sample_payloads()

    written = []
    for dataset, body in payloads.items():
        extension = "json" if dataset == "customers" else "csv"
        key = (
            f"bronze/{dataset}/ingestion_date={run_context.ingestion_date}/"
            f"{dataset}_{run_context.ingestion_date}.{extension}"
        )
        s3.put_object(Bucket=settings.lakehouse_bucket, Key=key, Body=body)
        written.append({"dataset": dataset, "s3_key": key})

    return {
        "batch_id": run_context.batch_id,
        "ingestion_date": run_context.ingestion_date,
        "files": written,
    }
