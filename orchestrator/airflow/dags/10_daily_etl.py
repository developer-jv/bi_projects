# 10_daily_etl.py
from datetime import datetime
from airflow.decorators import dag, task

@dag(
    start_date=datetime(2025, 1, 1),
    schedule="0 2 * * *",   # todos los días a las 02:00 UTC
    max_active_runs=1,
    catchup=False,
    tags=["production"],
)
def daily_etl():
    @task(retries=3, retry_delay=300)
    def extract():
        print("Extrayendo datos…")

    @task
    def transform():
        print("Transformando…")

    @task
    def load():
        print("Cargando al DWH…")

    extract() >> transform() >> load()

dag = daily_etl()
