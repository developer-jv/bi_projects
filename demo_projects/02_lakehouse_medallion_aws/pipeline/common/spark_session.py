from __future__ import annotations

from pyspark.sql import SparkSession

from pipeline.common.config import load_settings


def build_spark_session(app_name: str) -> SparkSession:
    settings = load_settings()
    return (
        SparkSession.builder.remote(settings.spark_remote_url)
        .appName(app_name)
        .getOrCreate()
    )
