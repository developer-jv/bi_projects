from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone


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


def build_run_context() -> RunContext:
    now = datetime.now(timezone.utc)
    return RunContext(
        batch_id=now.strftime("batch_%Y%m%dT%H%M%SZ"),
        ingestion_date=now.strftime("%Y-%m-%d"),
        started_at=now.isoformat(),
    )
