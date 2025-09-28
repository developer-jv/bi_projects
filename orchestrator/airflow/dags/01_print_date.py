# 01_print_date.py
from datetime import datetime
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator

@dag(start_date=datetime(2025, 1, 1), schedule=None, catchup=False, tags=["basics"])
def print_date():
    BashOperator(task_id="show_date", bash_command="date")

dag = print_date()
