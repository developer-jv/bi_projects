# Lakehouse Medallion AWS

Proyecto base para construir un lakehouse medallion sobre AWS con:
- Terraform para infraestructura
- Airflow para orquestacion
- Spark Connect para procesamiento
- Apache Iceberg sobre S3
- Glue Data Catalog y Athena

## Estructura
- `airflow/`: copia versionable del stack de Airflow del proyecto
- `spark/`: stack local de Spark Connect para desarrollo
- `terraform/`: infraestructura AWS
- `pipeline/`: jobs Python por capas bronze, silver y gold
- `.env.example`: variables base del proyecto usando access key
