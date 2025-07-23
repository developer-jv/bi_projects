# 08_sla_dag.py
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.utils.email import send_email

def sla_miss_callback(dag, task_list, blocking_task_list, slas, **_):
    send_email("alerts@example.com",
               f"SLA missed for DAG {dag.dag_id}",
               f"Tasks: {task_list}")

@dag(
    start_date=datetime(2025, 1, 1),
    schedule="@hourly",
    default_args={"sla": timedelta(minutes=5)},
    sla_miss_callback=sla_miss_callback,
    catchup=False,
    tags=["sla"],
)
def sla_example():
    @task
    def slow():
        import time; time.sleep(400)  # 6 min 40 s

    slow()

dag = sla_example()
