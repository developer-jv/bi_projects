from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, timezone


@dataclass(frozen=True)
class Settings:
    aws_region: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_account_id: str
    lakehouse_bucket: str
    lakehouse_warehouse: str
    athena_output: str
    glue_crawler_role_arn: str
    spark_remote_url: str
    project_env: str


@dataclass(frozen=True)
class RunContext:
    batch_id: str
    ingestion_date: str
    started_at: str
    logical_date: str


def load_settings() -> Settings:
    return Settings(
        aws_region=os.environ["AWS_DEFAULT_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        aws_account_id=os.environ.get("AWS_ACCOUNT_ID", ""),
        lakehouse_bucket=os.environ["LAKEHOUSE_BUCKET"],
        lakehouse_warehouse=os.environ["LAKEHOUSE_WAREHOUSE"],
        athena_output=os.environ["ATHENA_OUTPUT"],
        glue_crawler_role_arn=os.environ["GLUE_CRAWLER_ROLE_ARN"],
        spark_remote_url=os.environ["SPARK_REMOTE_URL"],
        project_env=os.environ.get("PROJECT_ENV", "dev"),
    )


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def resolve_process_date(process_date: str | None = None, logical_date: datetime | None = None) -> str:
    if process_date:
        return date.fromisoformat(process_date).isoformat()

    base_date = _to_utc(logical_date or datetime.now(timezone.utc))
    return base_date.date().isoformat()


def build_run_context(
    process_date: str | None = None,
    logical_date: datetime | None = None,
    started_at: datetime | None = None,
) -> RunContext:
    resolved_logical_date = _to_utc(logical_date or datetime.now(timezone.utc))
    resolved_started_at = _to_utc(started_at or datetime.now(timezone.utc))
    resolved_process_date = resolve_process_date(process_date=process_date, logical_date=resolved_logical_date)

    return RunContext(
        batch_id=f"batch_{resolved_process_date.replace('-', '')}",
        ingestion_date=resolved_process_date,
        started_at=resolved_started_at.isoformat(),
        logical_date=resolved_logical_date.isoformat(),
    )
