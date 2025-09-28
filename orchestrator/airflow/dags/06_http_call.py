# 06_http_call.py  – GitHub API demo (Airflow 3.x)
from datetime import datetime
from airflow.decorators import dag
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.http.sensors.http import HttpSensor


@dag(
    start_date=datetime(2025, 1, 1),
    schedule=None,        # ejecútalo a mano desde la UI
    catchup=False,
    tags=["http", "github"],
)
def github_repo_info():
    """Ejemplo: espera a que la API de GitHub responda y luego obtiene
    los datos JSON del repo apache/airflow."""

    # 1️⃣  Sensor: comprueba que el endpoint devuelve 200
    api_up = HttpSensor(
        task_id="github_up",
        http_conn_id="github_api",      # definida en Admin → Connections
        endpoint="repos/apache/airflow",
        poke_interval=10,
        timeout=60,
    )

    # 2️⃣  Operador: hace la petición GET y registra el JSON
    fetch_repo = HttpOperator(
        task_id="get_repo_info",
        http_conn_id="github_api",
        endpoint="repos/apache/airflow",
        method="GET",
        response_filter=lambda r: r.json(),   # convierte la respuesta en dict
        log_response=True,                    # imprime el JSON en los logs
    )

    api_up >> fetch_repo


dag = github_repo_info()
