# 07_external_task_sensor.py
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.sensors.external_task import ExternalTaskSensor

@dag(start_date=datetime(2025, 1, 1), schedule="@daily", catchup=False, tags=["external"])
def wait_for_other_dag():
    # Espera a que 'etl_grouped.load_dw' de ayer termine
    sensor = ExternalTaskSensor(
        task_id="wait_etl",
        external_dag_id="etl_grouped",
        external_task_id="load_dw",
        execution_delta=timedelta(days=1),
        poke_interval=30,
        timeout=3600,
    )

    @task
    def downstream():
        print("Continuamos tras el ETL")

    sensor >> downstream()

dag = wait_for_other_dag()
