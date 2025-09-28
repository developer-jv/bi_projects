# 04_task_group.py
from datetime import datetime
from airflow.decorators import dag, task
from airflow.utils.task_group import TaskGroup

@dag(start_date=datetime(2025, 1, 1), schedule=None, catchup=False, tags=["group"])
def etl_grouped():
    @task
    def start(): ...

    with TaskGroup(group_id="extract") as extract:
        @task
        def extract_mysql(): ...
        @task
        def extract_api(): ...

    with TaskGroup(group_id="transform") as transform:
        @task
        def clean(): ...
        @task
        def enrich(): ...

    @task
    def load_dw(): ...

    start() >> extract >> transform >> load_dw()

dag = etl_grouped()
