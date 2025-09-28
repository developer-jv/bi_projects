# 02_branching.py
from datetime import datetime
from airflow.decorators import dag, task
from airflow.operators.python import BranchPythonOperator, PythonOperator

@dag(start_date=datetime(2025, 1, 1), schedule=None, catchup=False, tags=["branch"])
def branching_demo():
    def choose_path(**_):
        from random import choice
        return choice(["path_a", "path_b"])

    branch = BranchPythonOperator(task_id="branch", python_callable=choose_path)

    @task
    def path_a():
        print("Elegiste A")

    @task
    def path_b():
        print("Elegiste B")

    branch >> [path_a(), path_b()]

dag = branching_demo()
