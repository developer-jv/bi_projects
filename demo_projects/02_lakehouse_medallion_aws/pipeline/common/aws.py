from __future__ import annotations

import boto3

from pipeline.common.config import load_settings


def build_boto3_session() -> boto3.Session:
    settings = load_settings()
    return boto3.Session(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )
