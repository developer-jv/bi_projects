from datetime import datetime
from airflow.decorators import dag, task   # TaskFlow API (Airflow 3)

@dag(
    start_date=datetime(2025, 1, 1),
    schedule=None,          # se dispara a mano
    catchup=False,
    tags=["tutorial"]
)
def hello_world():
    @task
    def say_hello():
        print("¡Hola mundo desde Airflow!")

    say_hello()             # define la dependencia

dag = hello_world()
