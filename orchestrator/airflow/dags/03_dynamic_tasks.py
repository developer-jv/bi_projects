# 03_dynamic_tasks.py
from datetime import datetime
from airflow.decorators import dag, task

fruits = ["🍎", "🍌", "🍓", "🍍"]

@dag(start_date=datetime(2025, 1, 1), schedule=None, catchup=False, tags=["dynamic"])
def dynamic_mapping():
    @task
    def eat(fruit):
        print(f"Comiendo {fruit}")

    # Crea una tarea por elemento en la lista
    eat.expand(fruit=fruits)

dag = dynamic_mapping()
