from datetime import datetime
from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook

@dag(start_date=datetime(2025,1,1), schedule=None, catchup=False, tags=["spark","connect"])
def spark_connect_smoke():
    @task
    def run():
        # Lee la conexión Spark Connect de Airflow
        conn = BaseHook.get_connection("spark_default")
        host = conn.host              # p.ej. 192.168.1.14
        port = conn.port or 15002
        remote = f"sc://{host}:{port}"

        from pyspark.sql import SparkSession
        spark = (SparkSession.builder
                 .remote(remote)       # Spark Connect
                 .appName("connect_smoke")
                 .getOrCreate())
        n = spark.range(0, 100000).count()
        print("CONNECT_OK", n, "spark", spark.version)
        spark.stop()

    run()

dag = spark_connect_smoke()
