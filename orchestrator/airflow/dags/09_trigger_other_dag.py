# 09_trigger_other_dag.py
from datetime import datetime
from airflow.decorators import dag
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

@dag(start_date=datetime(2025, 1, 1), schedule=None, catchup=False, tags=["trigger"])
def trigger_demo():
    TriggerDagRunOperator(
        task_id="launch_hello_world",
        trigger_dag_id="hello_world",
        wait_for_completion=True,
    )

dag = trigger_demo()
