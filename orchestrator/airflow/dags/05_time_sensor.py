# 05_time_sensor.py
from datetime import datetime, time, timedelta
from airflow.decorators import dag, task
from airflow.sensors.time_sensor import TimeSensor

@dag(start_date=datetime(2025, 1, 1), schedule="@daily", catchup=False, tags=["sensor"])
def wait_until_morning():
    # Espera hasta las 07:00 UTC antes de ejecutar la lógica
    wait = TimeSensor(task_id="wait_7am", target_time=time(7, 0))

    @task
    def morning_task():
        print("¡Buenos días!")

    wait >> morning_task()

dag = wait_until_morning()
