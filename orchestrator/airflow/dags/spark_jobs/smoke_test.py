from pyspark.sql import SparkSession
if __name__ == "__main__":
    spark = SparkSession.builder.appName("bia_smoke_test").getOrCreate()
    print(f"SMOKE_TEST_OK spark_version={spark.version} count={spark.range(0, 100000).count()}")
    spark.stop()
