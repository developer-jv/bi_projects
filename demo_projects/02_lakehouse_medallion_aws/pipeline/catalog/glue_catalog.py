from __future__ import annotations

from pipeline.common.aws import build_boto3_session
from pipeline.common.config import load_settings


CRAWLERS = ["lakehouse-bronze", "lakehouse-silver", "lakehouse-gold"]


def run_glue_crawlers() -> list[str]:
    session = build_boto3_session()
    glue = session.client("glue", region_name=load_settings().aws_region)
    started = []
    for crawler_name in CRAWLERS:
        try:
            glue.start_crawler(Name=crawler_name)
            started.append(crawler_name)
        except glue.exceptions.CrawlerRunningException:
            started.append(crawler_name)
    return started
