# Lakehouse Medallion con Airflow, Spark Connect, AWS S3, Glue, Iceberg y Athena

Proyecto de portafolio para demostrar habilidades de **AWS Data Engineering** mediante la implementación de una arquitectura **Lakehouse Medallion** usando **Apache Airflow local** como orquestador, un **cluster Apache Spark local** como motor de procesamiento distribuido, **Spark Connect** como mecanismo de conexión entre Airflow/Python y Spark, **Amazon S3** como almacenamiento del Data Lake, **Apache Iceberg** como formato de tabla abierto, **AWS Glue Data Catalog** como catálogo de metadatos, **AWS Glue Crawlers** para descubrimiento y actualización de tablas, y **Amazon Athena** para consultas analíticas.

El objetivo es construir un proyecto realista, sencillo de explicar en entrevista, de costo controlado y alineado con responsabilidades típicas de un rol de **AWS Data Engineer**.

---

## 1. Resumen Ejecutivo

Este proyecto implementa un pipeline de datos batch de punta a punta:

1. Ingesta de archivos crudos hacia una zona **Bronze** en Amazon S3.
2. Orquestación del flujo mediante **Apache Airflow local**.
3. Ejecución de transformaciones con un **cluster Spark local independiente de Airflow**, accedido mediante **Spark Connect**.
4. Limpieza, tipificación y validación de datos en una zona **Silver**.
5. Modelado analítico en una zona **Gold**.
6. Escritura de tablas en formato **Apache Iceberg** sobre S3.
7. Registro de metadatos en **AWS Glue Data Catalog**.
8. Ejecución de **AWS Glue Crawlers** para reconocimiento y actualización del catálogo.
9. Consulta de datos con **Amazon Athena**.
10. Logging, métricas y trazabilidad por ejecución.
11. Controles básicos de seguridad, calidad de datos y optimización de costos.

La solución asume que ya existen:

- Un entorno local de **Apache Airflow**.
- Un **cluster Apache Spark local independiente de Airflow**, con **Spark Connect Server** habilitado.
- Una cuenta AWS con permisos para S3, Glue, Athena, IAM y CloudWatch.

Airflow no ejecuta procesamiento pesado. Airflow solo orquesta y ejecuta clientes Python que se conectan a Spark mediante Spark Connect. El procesamiento distribuido lo realiza el cluster Spark local.

---

## 2. Problema de Negocio

Una empresa de comercio electrónico necesita consolidar datos operacionales provenientes de archivos CSV y JSON para analizar ventas, clientes, productos y órdenes.

Actualmente los datos llegan en formatos heterogéneos, con problemas de calidad, duplicados, campos nulos y diferencias de esquema entre cargas. El equipo de analítica requiere una capa confiable, gobernada y consultable por SQL para responder preguntas como:

- ¿Cuáles son los productos con mayor venta por mes?
- ¿Cuáles son los clientes con mayor valor acumulado?
- ¿Qué órdenes presentan problemas de calidad?
- ¿Cómo evoluciona el revenue por categoría?
- ¿Qué datos sensibles deben enmascararse antes de ser consumidos por analistas?

---

## 3. Objetivos del Proyecto

### Objetivo General

Construir un Lakehouse Medallion en AWS, orquestado con Airflow y procesado con Spark, que transforme datos crudos en tablas Iceberg analíticas consultables con Athena.

### Objetivos Específicos

- Implementar una arquitectura Bronze, Silver y Gold sobre Amazon S3.
- Orquestar el pipeline con Apache Airflow local.
- Ejecutar ETL/ELT con un cluster Spark local mediante Spark Connect.
- Procesar archivos CSV y JSON.
- Escribir tablas Apache Iceberg en S3.
- Integrar Spark con AWS Glue Data Catalog.
- Ejecutar Glue Crawlers desde Airflow.
- Consultar tablas con Amazon Athena.
- Aplicar reglas de calidad de datos.
- Enmascarar campos sensibles.
- Registrar métricas técnicas por ejecución.
- Implementar particionamiento y buenas prácticas de costo.
- Documentar despliegue y operación.
- Preparar una demo técnica clara para entrevista.

---

## 4. Alcance del Proyecto

### Incluido

- Pipeline batch.
- Airflow local como orquestador.
- Cluster Spark local como motor ETL.
- Spark Connect como interfaz de conexión entre Airflow/Python y Spark.
- Amazon S3 como Data Lake.
- Arquitectura Medallion: Bronze, Silver y Gold.
- Datos de ejemplo de e-commerce.
- Transformaciones Bronze → Silver.
- Transformaciones Silver → Gold.
- Tablas Apache Iceberg.
- AWS Glue Data Catalog.
- AWS Glue Crawlers.
- Consultas con Amazon Athena.
- Reglas de calidad de datos.
- Enmascaramiento de PII.
- Logging estructurado.
- Pruebas unitarias básicas.
- Infraestructura como código con Terraform o AWS CDK.
- Documentación para demo técnica.

---

## 5. Arquitectura de Alto Nivel

```text
                         ┌──────────────────────┐
                         │  Datos de ejemplo     │
                         │  CSV / JSON / API     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Amazon S3 - Bronze    │
                         │ Datos crudos          │
                         └──────────┬───────────┘
                                    │
                                    │ Airflow dispara jobs
                                    ▼
              ┌────────────────────────────────────────┐
              │ Apache Airflow local                    │
              │ DAG de orquestación                     │
              │ - valida entrada                        │
              │ - ejecuta clientes Spark Connect        │
              │ - ejecuta crawlers                      │
              │ - corre queries de validación Athena    │
              └───────────────────┬────────────────────┘
                                  │
                                  ▼
              ┌────────────────────────────────────────┐
              │ Cluster Apache Spark local              │
              │ Spark Connect Server + PySpark ETL/ELT  │
              │ Lectura Bronze / Escritura Iceberg      │
              └───────────────────┬────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
        ┌──────────────────────┐     ┌──────────────────────┐
        │ Amazon S3 - Silver    │     │ Amazon S3 - Gold      │
        │ Tablas Iceberg limpias│     │ Modelos analíticos    │
        └──────────┬───────────┘     └──────────┬───────────┘
                   │                            │
                   └──────────────┬─────────────┘
                                  ▼
              ┌────────────────────────────────────────┐
              │ AWS Glue Data Catalog                   │
              │ Bases, tablas, esquemas y metadatos     │
              └───────────────────┬────────────────────┘
                                  │
                                  ▼
              ┌────────────────────────────────────────┐
              │ AWS Glue Crawlers                      │
              │ Actualización de metadatos             │
              └───────────────────┬────────────────────┘
                                  │
                                  ▼
                         ┌──────────────────────┐
                         │ Amazon Athena         │
                         │ Consultas SQL         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ BI / Demo / Reportes  │
                         │ QuickSight opcional   │
                         └──────────────────────┘
```

---

## 6. Principios de Diseño

### Separación de responsabilidades

- **Airflow:** orquesta, agenda, controla dependencias y maneja reintentos.
- **Spark:** procesa datos de forma distribuida.
- **S3:** almacena datos por capas.
- **Iceberg:** administra tablas transaccionales sobre archivos.
- **Glue Data Catalog:** centraliza metadatos.
- **Glue Crawlers:** detectan o actualizan esquemas/tablas.
- **Athena:** permite análisis SQL serverless.

### Airflow no debe procesar datos pesados

Los workers de Airflow no deben ejecutar transformaciones grandes en memoria local. Airflow debe lanzar tareas livianas que se conecten al cluster Spark mediante **Spark Connect**. En este enfoque, los scripts Python crean una sesión remota hacia Spark usando `SparkSession.builder.remote(...)`, mientras que la ejecución real ocurre en el cluster Spark local.

Opciones de ejecución desde Airflow:

- `PythonOperator` ejecutando scripts PySpark que usan Spark Connect.
- `BashOperator` invocando scripts Python con parámetros de ejecución.
- `DockerOperator`, si el cliente Spark Connect corre en un contenedor separado.
- `SparkSubmitOperator` solo como alternativa si se decide ejecutar jobs clásicos con `spark-submit`.

Para este proyecto se recomienda usar **PythonOperator o BashOperator + Spark Connect**, porque el cluster Spark ya está local y separado de Airflow.

---

## 7. Servicios y Herramientas

### AWS

| Servicio              | Uso en el proyecto                                                     |
| --------------------- | ---------------------------------------------------------------------- |
| Amazon S3             | Almacenamiento de Bronze, Silver, Gold, scripts y resultados de Athena |
| AWS Glue Data Catalog | Catálogo central de metadatos para Iceberg                             |
| AWS Glue Crawlers     | Reconocimiento y actualización de tablas                               |
| Amazon Athena         | Consultas SQL sobre tablas Iceberg                                     |
| AWS IAM               | Roles y permisos de mínimo privilegio                                  |
| AWS KMS               | Cifrado de datos en reposo, opcional                                   |
| Amazon CloudWatch     | Logs y monitoreo complementario                                        |
| AWS CloudTrail        | Auditoría de llamadas API, opcional                                    |
| Amazon QuickSight     | Dashboard BI, opcional                                                 |
| Amazon EventBridge    | Programación alternativa o disparos complementarios, opcional          |

### Componentes existentes o autogestionados

| Herramienta                  | Uso                                                                                              |
| ---------------------------- | ------------------------------------------------------------------------------------------------ |
| Apache Airflow local         | Orquestación del pipeline                                                                        |
| Apache Spark cluster local   | Motor ETL/ELT distribuido                                                                        |
| Spark Connect                | Interfaz cliente-servidor para ejecutar lógica Spark desde Python sin acoplar Airflow al cluster |
| PySpark                      | Transformaciones                                                                                 |
| Apache Iceberg               | Formato Open Table                                                                               |
| Python                       | Scripts auxiliares, validaciones y pruebas                                                       |
| Git                          | Control de versiones                                                                             |
| Terraform o AWS CDK          | Infraestructura como código                                                                      |
| pytest                       | Pruebas unitarias                                                                                |
| Pandera o Great Expectations | Validación de calidad opcional                                                                   |

---

## 8. Diseño Medallion

### 8.1 Bronze Zone

La capa Bronze conserva los datos crudos tal como llegan desde la fuente.

Características:

- Sin limpieza agresiva.
- Preserva trazabilidad del archivo original.
- Incluye metadata técnica.
- Permite reprocesamiento.
- Acceso restringido porque puede contener PII sin enmascarar.

Rutas sugeridas:

```text
s3://<bucket-lakehouse>/bronze/orders/ingestion_date=2026-05-20/orders_2026_05_20.csv
s3://<bucket-lakehouse>/bronze/customers/ingestion_date=2026-05-20/customers_2026_05_20.json
s3://<bucket-lakehouse>/bronze/products/ingestion_date=2026-05-20/products_2026_05_20.csv
s3://<bucket-lakehouse>/bronze/order_items/ingestion_date=2026-05-20/order_items_2026_05_20.csv
```

Metadata técnica recomendada:

| Columna             | Descripción                      |
| ------------------- | -------------------------------- |
| ingestion_timestamp | Fecha y hora de ingesta          |
| ingestion_date      | Fecha de ingesta                 |
| source_file         | Nombre/ruta del archivo origen   |
| batch_id            | Identificador único de ejecución |
| source_system       | Sistema origen                   |

### 8.2 Silver Zone

La capa Silver contiene datos limpios, tipificados y normalizados.

Transformaciones:

- Conversión de tipos.
- Eliminación de duplicados.
- Validación de llaves primarias.
- Normalización de fechas.
- Estandarización de nombres de columnas.
- Enmascaramiento de PII.
- Rechazo o aislamiento de registros inválidos.
- Escritura en tablas Iceberg.

Tablas esperadas:

```text
silver.customers
silver.products
silver.orders
silver.order_items
silver.data_quality_errors
```

### 8.3 Gold Zone

La capa Gold contiene modelos analíticos listos para negocio.

Modelos propuestos:

```text
gold.fact_sales
gold.dim_customer
gold.dim_product
gold.sales_by_month
gold.customer_lifetime_value
gold.top_products_by_revenue
```

---

## 9. Modelo de Datos

### 9.1 Fuente: customers

| Columna     | Tipo origen |  Tipo destino | Descripción                     |
| ----------- | ----------: | ------------: | ------------------------------- |
| customer_id |      string |        string | Identificador único del cliente |
| first_name  |      string |        string | Nombre                          |
| last_name   |      string |        string | Apellido                        |
| email       |      string | string masked | Correo electrónico enmascarado  |
| phone       |      string | string masked | Teléfono enmascarado            |
| country     |      string |        string | País                            |
| created_at  |      string |     timestamp | Fecha de creación               |

### 9.2 Fuente: products

| Columna      |    Tipo origen |  Tipo destino | Descripción                |
| ------------ | -------------: | ------------: | -------------------------- |
| product_id   |         string |        string | Identificador del producto |
| product_name |         string |        string | Nombre del producto        |
| category     |         string |        string | Categoría                  |
| price        | string/decimal | decimal(10,2) | Precio unitario            |
| active       |    string/bool |       boolean | Estado del producto        |

### 9.3 Fuente: orders

| Columna        | Tipo origen | Tipo destino | Descripción            |
| -------------- | ----------: | -----------: | ---------------------- |
| order_id       |      string |       string | Identificador de orden |
| customer_id    |      string |       string | Cliente asociado       |
| order_status   |      string |       string | Estado de orden        |
| order_date     |      string |    timestamp | Fecha de orden         |
| payment_method |      string |       string | Método de pago         |

### 9.4 Fuente: order_items

| Columna       |    Tipo origen |  Tipo destino | Descripción              |
| ------------- | -------------: | ------------: | ------------------------ |
| order_item_id |         string |        string | Identificador de detalle |
| order_id      |         string |        string | Orden asociada           |
| product_id    |         string |        string | Producto asociado        |
| quantity      |     string/int |       integer | Cantidad                 |
| unit_price    | string/decimal | decimal(10,2) | Precio unitario          |

---

## 10. Reglas de Calidad de Datos

| Regla                                          | Severidad | Acción                                        |
| ---------------------------------------------- | --------- | --------------------------------------------- |
| ID principal no debe ser nulo                  | Alta      | Rechazar registro                             |
| Fechas deben ser parseables                    | Alta      | Enviar a tabla de errores                     |
| Precio debe ser mayor o igual a cero           | Alta      | Rechazar registro                             |
| Quantity debe ser mayor que cero               | Alta      | Rechazar registro                             |
| Email debe tener formato válido                | Media     | Enmascarar y marcar warning                   |
| order_status debe pertenecer a catálogo válido | Media     | Normalizar o rechazar                         |
| No deben existir duplicados por llave primaria | Alta      | Mantener último registro por fecha de ingesta |

Estados válidos de orden:

```text
CREATED
PAID
SHIPPED
DELIVERED
CANCELLED
REFUNDED
```

Tabla de errores:

```text
silver.data_quality_errors
```

Columnas sugeridas:

| Columna       | Descripción                |
| ------------- | -------------------------- |
| source_table  | Tabla fuente               |
| source_file   | Archivo origen             |
| record_id     | Identificador del registro |
| error_code    | Código de error            |
| error_message | Descripción del error      |
| raw_payload   | Registro original en JSON  |
| created_at    | Fecha de detección         |
| batch_id      | ID de ejecución            |

---

## 11. Apache Iceberg

Se utiliza Apache Iceberg para administrar tablas analíticas sobre S3.

Beneficios demostrados:

- Evolución de esquema.
- Particionamiento oculto.
- Snapshots.
- Time travel.
- Operaciones ACID.
- Mejor manejo de cargas incrementales.
- Compatibilidad con Spark y Athena.
- Separación entre datos físicos y metadatos de tabla.

Tablas Iceberg propuestas:

```text
silver.customers
silver.products
silver.orders
silver.order_items
gold.fact_sales
gold.dim_customer
gold.dim_product
gold.sales_by_month
```

Ejemplo conceptual de creación con Spark SQL:

```sql
CREATE TABLE IF NOT EXISTS glue_catalog.silver.orders (
    order_id STRING,
    customer_id STRING,
    order_status STRING,
    order_date TIMESTAMP,
    payment_method STRING,
    ingestion_date DATE,
    batch_id STRING
)
USING iceberg
PARTITIONED BY (days(order_date));
```

Ejemplo de time travel en Athena:

```sql
SELECT *
FROM silver.orders
FOR TIMESTAMP AS OF TIMESTAMP '2026-05-20 10:00:00 UTC'
WHERE order_status = 'PAID';
```

---

## 12. Configuración Spark Connect para Iceberg y Glue Catalog

El cluster Spark local debe tener habilitado **Spark Connect Server** y debe incluir las dependencias necesarias para Iceberg, AWS S3 y AWS Glue Catalog.

Spark Connect separa el cliente Python del motor de ejecución. Por eso, las dependencias críticas de Iceberg, S3 y Glue deben estar disponibles principalmente en el **servidor Spark Connect / cluster Spark**, no solo en el entorno Python de Airflow.

### Ejemplo conceptual de conexión Spark Connect

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .remote("sc://localhost:15002")
    .appName("de-portfolio-bronze-to-silver-orders")
    .getOrCreate()
)

orders_df = spark.read.option("header", True).csv(
    "s3a://de-portfolio-lakehouse-dev/bronze/orders/"
)
```

### Configuración del Spark Connect Server

El cluster Spark debe iniciar el servidor Spark Connect con las extensiones de Iceberg y el catálogo Glue configurado.

Ejemplo conceptual de configuración:

```bash
./sbin/start-connect-server.sh \
  --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:<iceberg-version>,software.amazon.awssdk:bundle:<aws-sdk-version>,software.amazon.awssdk:url-connection-client:<aws-sdk-version> \
  --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
  --conf spark.sql.catalog.glue_catalog=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.glue_catalog.catalog-impl=org.apache.iceberg.aws.glue.GlueCatalog \
  --conf spark.sql.catalog.glue_catalog.io-impl=org.apache.iceberg.aws.s3.S3FileIO \
  --conf spark.sql.catalog.glue_catalog.warehouse=s3://<bucket-lakehouse>/warehouse \
  --conf spark.sql.catalog.glue_catalog.client.region=us-east-1 \
  src/transformations/bronze_to_silver_orders.py
```

> Nota: las versiones exactas de Iceberg, Spark y AWS SDK deben alinearse con la versión instalada en el cluster Spark.

---

## 13. Catálogo de Datos

El proyecto utiliza AWS Glue Data Catalog como catálogo central.

Bases de datos sugeridas:

```text
de_portfolio_bronze
de_portfolio_silver
de_portfolio_gold
```

Tablas esperadas:

```text
de_portfolio_silver.customers
de_portfolio_silver.products
de_portfolio_silver.orders
de_portfolio_silver.order_items
de_portfolio_gold.fact_sales
de_portfolio_gold.sales_by_month
```

### Glue Crawlers

Crawlers propuestos:

```text
crawler_bronze_raw
crawler_silver_iceberg
crawler_gold_iceberg
```

Uso recomendado:

- `crawler_bronze_raw`: reconoce archivos crudos CSV/JSON.
- `crawler_silver_iceberg`: valida/actualiza metadatos de Silver.
- `crawler_gold_iceberg`: valida/actualiza metadatos de Gold.

En una implementación con Iceberg, Spark puede registrar directamente las tablas en Glue Catalog. Los crawlers se incluyen para demostrar descubrimiento, validación y actualización de metadatos, especialmente sobre Bronze y capas derivadas.

---

## 14. Orquestación con Apache Airflow

Airflow será el componente central de orquestación.

Responsabilidades de Airflow:

- Validar existencia de archivos en S3.
- Generar `batch_id`.
- Enviar jobs al cluster Spark.
- Controlar dependencias entre Bronze, Silver y Gold.
- Ejecutar Glue Crawlers.
- Ejecutar queries de validación en Athena.
- Registrar estado del pipeline.
- Manejar reintentos.
- Notificar fallos, opcional.

### DAG propuesto

```text
start
  │
  ▼
validate_input_files
  │
  ▼
generate_batch_id
  │
  ▼
bronze_ingestion
  │
  ▼
run_silver_customers ─┐
run_silver_products ──┼──► run_silver_quality_checks
run_silver_orders ────┤
run_silver_items ─────┘
  │
  ▼
run_gold_sales
  │
  ▼
run_glue_crawler_silver
  │
  ▼
run_glue_crawler_gold
  │
  ▼
run_athena_validation_queries
  │
  ▼
end
```

### Ejemplo conceptual de DAG

```python
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.amazon.aws.operators.glue_crawler import GlueCrawlerOperator
from airflow.providers.amazon.aws.operators.athena import AthenaOperator
from airflow.utils.dates import days_ago

PROJECT_NAME = "de_portfolio_lakehouse"
AWS_CONN_ID = "aws_default"
SPARK_CONN_ID = "spark_default"

with DAG(
    dag_id="de_portfolio_lakehouse_medallion",
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False,
    tags=["aws", "spark", "iceberg", "lakehouse", "portfolio"],
) as dag:

    start = EmptyOperator(task_id="start")

    bronze_ingestion = SparkSubmitOperator(
        task_id="bronze_ingestion",
        conn_id=SPARK_CONN_ID,
        application="/opt/airflow/dags/repo/src/ingestion/ingest_raw.py",
        application_args=[
            "--batch-id", "{{ ts_nodash }}",
            "--environment", "dev",
        ],
    )

    silver_orders = SparkSubmitOperator(
        task_id="silver_orders",
        conn_id=SPARK_CONN_ID,
        application="/opt/airflow/dags/repo/src/transformations/bronze_to_silver_orders.py",
        application_args=[
            "--batch-id", "{{ ts_nodash }}",
        ],
    )

    gold_sales = SparkSubmitOperator(
        task_id="gold_sales",
        conn_id=SPARK_CONN_ID,
        application="/opt/airflow/dags/repo/src/transformations/silver_to_gold_sales.py",
        application_args=[
            "--batch-id", "{{ ts_nodash }}",
        ],
    )

    crawl_silver = GlueCrawlerOperator(
        task_id="crawl_silver",
        config={"Name": "crawler_silver_iceberg"},
        aws_conn_id=AWS_CONN_ID,
    )

    athena_validation = AthenaOperator(
        task_id="athena_validation",
        query="SELECT COUNT(*) FROM de_portfolio_gold.sales_by_month",
        database="de_portfolio_gold",
        output_location="s3://<bucket-athena-results>/validation/",
        aws_conn_id=AWS_CONN_ID,
    )

    end = EmptyOperator(task_id="end")

    start >> bronze_ingestion >> silver_orders >> gold_sales >> crawl_silver >> athena_validation >> end
```

---

## 15. Estrategia de Ejecución con Spark Connect

### Opción recomendada

Usar Airflow para ejecutar scripts Python livianos que se conectan al cluster Spark local mediante Spark Connect.

Airflow debe conocer:

- Endpoint de Spark Connect, por ejemplo `sc://localhost:15002`.
- Ruta de scripts Python/PySpark.
- Configuración de Iceberg.
- Credenciales AWS.
- Bucket S3 de warehouse.

Flujo recomendado:

```text
Airflow Task
   │
   ▼
Python script cliente
   │
   ▼
SparkSession.builder.remote("sc://localhost:15002")
   │
   ▼
Spark Connect Server
   │
   ▼
Cluster Spark local
   │
   ▼
S3 + Glue Catalog + Iceberg
```

### Alternativas de integración

| Alternativa         | Cuándo usarla                                                   |
| ------------------- | --------------------------------------------------------------- |
| PythonOperator      | Recomendado para ejecutar scripts Python que usan Spark Connect |
| BashOperator        | Recomendado si se prefiere invocar scripts por CLI              |
| DockerOperator      | Útil si el cliente Spark Connect corre en contenedor separado   |
| SparkSubmitOperator | Alternativa si se decide ejecutar jobs Spark clásicos           |

### Convención de argumentos

Todos los jobs deben aceptar:

```bash
--batch-id
--environment
--source-path
--target-database
--target-table
--warehouse-path
```

Ejemplo:

```bash
python src/transformations/bronze_to_silver_orders.py \
  --batch-id 20260520T090000 \
  --environment dev \
  --spark-connect-url sc://localhost:15002 \
  --source-path s3://de-portfolio-lakehouse-dev/bronze/orders/ \
  --target-database de_portfolio_silver \
  --target-table orders \
  --warehouse-path s3://de-portfolio-lakehouse-dev/warehouse/
```

---

## 16. Seguridad y Credenciales

### Airflow Connections

Crear conexiones en Airflow:

```text
aws_default
spark_default
```

Variables sugeridas en Airflow:

```text
project_name
environment
aws_region
s3_lakehouse_bucket
s3_athena_results_bucket
glue_database_bronze
glue_database_silver
glue_database_gold
iceberg_warehouse_path
```

### IAM

Roles o usuarios mínimos:

```text
role_airflow_orchestrator
role_spark_etl
role_glue_crawler
role_athena_query
```

Permisos requeridos por componente:

| Componente   | Permisos mínimos                                                    |
| ------------ | ------------------------------------------------------------------- |
| Airflow      | Iniciar crawlers, ejecutar Athena, leer variables/secrets si aplica |
| Spark        | Leer Bronze, escribir Silver/Gold, crear/actualizar tablas Glue     |
| Glue Crawler | Leer rutas S3 y actualizar Data Catalog                             |
| Athena       | Leer Glue Catalog, leer Silver/Gold y escribir resultados           |

Principios:

- Mínimo privilegio.
- Buckets privados.
- Separación por prefijos.
- Bronze con acceso restringido.
- Gold expuesto para analítica.
- Cifrado en reposo.

### Cifrado

- S3 SSE-S3 para una primera versión.
- KMS para versión avanzada.
- Athena query results cifrados.

### PII

Campos sensibles:

```text
email
phone
first_name
last_name
```

Estrategia:

- Bronze conserva PII con acceso restringido.
- Silver enmascara email y teléfono.
- Gold evita exponer PII innecesaria.

Ejemplo:

```text
john.doe@example.com → j***@example.com
+50255551234 → +502*****234
```

---

## 17. Optimización de Costos

Medidas aplicadas:

- Usar datasets pequeños para demo.
- Usar el cluster Spark existente en vez de Glue Jobs para procesamiento.
- Ejecutar Airflow local sin servicios administrados adicionales.
- Usar Athena solo para consultas acotadas.
- Escribir datos en formato Iceberg/Parquet para reducir bytes escaneados.
- Particionar por fecha.
- Configurar S3 Lifecycle para temporales y resultados de Athena.
- Evitar QuickSight en la primera versión si no es necesario.
- Eliminar recursos AWS al finalizar.

Estimación de costo para demo:

| Componente        |                          Uso esperado | Costo esperado |
| ----------------- | ------------------------------------: | -------------: |
| S3                |                         Menos de 1 GB |       Muy bajo |
| Athena            | Pocas consultas sobre Iceberg/Parquet |       Muy bajo |
| Glue Crawlers     |           Ejecuciones manuales/cortas |           Bajo |
| Glue Data Catalog |                Bajo volumen de tablas |           Bajo |
| CloudWatch        |                          Logs mínimos |           Bajo |

---

## 18. Infraestructura AWS

Recursos mínimos:

```text
S3 bucket lakehouse
S3 bucket athena results
Glue database bronze
Glue database silver
Glue database gold
Glue crawlers
IAM roles/policies
Athena workgroup
CloudWatch log groups opcionales
```

Estructura S3 sugerida:

```text
s3://de-portfolio-lakehouse-dev/
├── bronze/
│   ├── customers/
│   ├── products/
│   ├── orders/
│   └── order_items/
├── warehouse/
│   ├── silver/
│   └── gold/
├── tmp/
└── logs/

s3://de-portfolio-athena-results-dev/
└── validation/
```

---

## 19. Estructura del Repositorio

```text
aws-data-engineering-lakehouse/
│
├── README.md
├── requirements.txt
├── pyproject.toml
├── Makefile
│
├── dags/
│   └── de_portfolio_lakehouse_medallion.py
│
├── data/
│   └── samples/
│       ├── customers/
│       ├── products/
│       ├── orders/
│       └── order_items/
│
├── src/
│   ├── common/
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── spark.py
│   │   ├── args.py
│   │   └── utils.py
│   │
│   ├── ingestion/
│   │   └── ingest_raw.py
│   │
│   ├── transformations/
│   │   ├── bronze_to_silver_customers.py
│   │   ├── bronze_to_silver_products.py
│   │   ├── bronze_to_silver_orders.py
│   │   ├── bronze_to_silver_order_items.py
│   │   └── silver_to_gold_sales.py
│   │
│   ├── quality/
│   │   ├── checks.py
│   │   └── rules.yaml
│   │
│   └── queries/
│       ├── athena_create_databases.sql
│       ├── athena_validation_queries.sql
│       └── business_queries.sql
│
├── infra/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── s3.tf
│   │   ├── glue.tf
│   │   ├── iam.tf
│   │   └── athena.tf
│   │
│   └── scripts/
│       ├── upload_sample_data.sh
│       ├── create_glue_crawlers.sh
│       ├── run_crawlers.sh
│       └── run_athena_queries.sh
│
├── tests/
│   ├── unit/
│   │   ├── test_quality_rules.py
│   │   └── test_transformations.py
│   └── integration/
│       └── test_pipeline_contracts.py
│
├── docs/
│   ├── architecture.md
│   ├── airflow_orchestration.md
│   ├── spark_configuration.md
│   ├── data_model.md
│   ├── cost_optimization.md
│   ├── security.md
│   └── demo_script.md
│
└── .github/
    └── workflows/
        └── ci.yml
```

---

## 20. Requerimientos Técnicos

### Entorno existente

- Apache Airflow local funcionando.
- Cluster Apache Spark disponible.
- Conectividad desde Airflow hacia Spark Connect Server.
- Conectividad desde el cluster Spark local hacia S3 y Glue Data Catalog.
- AWS CLI configurado.

### Librerías Python

```text
apache-airflow
apache-airflow-providers-amazon
apache-airflow-providers-apache-spark
pyspark
boto3
pyyaml
pytest
pandas
pyarrow
python-dotenv
faker
pandera
```

---

## 21. Variables de Entorno y Configuración

Archivo `.env` o variables de Airflow:

```bash
AWS_REGION=us-east-1
PROJECT_NAME=de-portfolio-lakehouse
ENVIRONMENT=dev

S3_BUCKET_LAKEHOUSE=de-portfolio-lakehouse-dev
S3_BUCKET_ATHENA=de-portfolio-athena-results-dev

GLUE_CATALOG_NAME=glue_catalog
GLUE_DATABASE_BRONZE=de_portfolio_bronze
GLUE_DATABASE_SILVER=de_portfolio_silver
GLUE_DATABASE_GOLD=de_portfolio_gold

WAREHOUSE_PATH=s3://de-portfolio-lakehouse-dev/warehouse
ATHENA_OUTPUT_LOCATION=s3://de-portfolio-athena-results-dev/validation/

SPARK_CONNECT_URL=sc://localhost:15002
SPARK_CLUSTER_MODE=local-cluster
```

---

## 22. Instalación y Preparación

### 22.1 Clonar repositorio

```bash
git clone https://github.com/<usuario>/aws-data-engineering-lakehouse.git
cd aws-data-engineering-lakehouse
```

### 22.2 Crear entorno Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 22.3 Configurar AWS CLI

```bash
aws configure
```

### 22.4 Crear infraestructura AWS

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

### 22.5 Cargar datos de ejemplo a S3

```bash
aws s3 sync data/samples/customers s3://de-portfolio-lakehouse-dev/bronze/customers/
aws s3 sync data/samples/products s3://de-portfolio-lakehouse-dev/bronze/products/
aws s3 sync data/samples/orders s3://de-portfolio-lakehouse-dev/bronze/orders/
aws s3 sync data/samples/order_items s3://de-portfolio-lakehouse-dev/bronze/order_items/
```

### 22.6 Configurar conexiones en Airflow

Crear conexión AWS:

```text
Conn Id: aws_default
Conn Type: Amazon Web Services
Region: us-east-1
```

Crear variable de Airflow para Spark Connect:

```text
Variable: spark_connect_url
Value: sc://localhost:15002
```

Opcionalmente, crear una conexión genérica:

```text
Conn Id: spark_connect_default
Conn Type: Generic
Host: localhost
Port: 15002
Schema: sc
```

### 22.7 Registrar DAG

Copiar el DAG a la carpeta de DAGs de Airflow:

```bash
cp dags/de_portfolio_lakehouse_medallion.py $AIRFLOW_HOME/dags/
```

### 22.8 Ejecutar pipeline

Desde UI de Airflow:

```text
DAG: de_portfolio_lakehouse_medallion
Trigger DAG
```

O por CLI:

```bash
airflow dags trigger de_portfolio_lakehouse_medallion
```

---

## 23. Transformaciones Principales

### 23.1 Customers

- Leer JSON o CSV desde Bronze.
- Validar `customer_id`.
- Normalizar país.
- Parsear `created_at`.
- Enmascarar email y teléfono.
- Eliminar duplicados por `customer_id`.
- Escribir tabla Iceberg `silver.customers`.

### 23.2 Products

- Leer productos desde Bronze.
- Convertir `price` a decimal.
- Validar precio no negativo.
- Normalizar categoría.
- Escribir tabla Iceberg `silver.products`.

### 23.3 Orders

- Leer órdenes desde Bronze.
- Validar `order_id` y `customer_id`.
- Parsear `order_date`.
- Normalizar `order_status`.
- Particionar por fecha de orden.
- Escribir tabla Iceberg `silver.orders`.

### 23.4 Order Items

- Leer detalles de orden desde Bronze.
- Validar `quantity > 0`.
- Validar `unit_price >= 0`.
- Calcular `line_total = quantity * unit_price`.
- Escribir tabla Iceberg `silver.order_items`.

### 23.5 Gold Sales

- Unir orders, order_items, products y customers.
- Crear tabla de hechos `gold.fact_sales`.
- Crear agregados por mes y categoría.
- Crear ranking de productos.

---

## 24. Consultas de Negocio

### Revenue mensual

```sql
SELECT
    sales_month,
    SUM(total_revenue) AS revenue
FROM de_portfolio_gold.sales_by_month
GROUP BY sales_month
ORDER BY sales_month;
```

### Top productos

```sql
SELECT
    product_id,
    product_name,
    category,
    total_quantity,
    total_revenue
FROM de_portfolio_gold.top_products_by_revenue
ORDER BY total_revenue DESC
LIMIT 10;
```

### Clientes con mayor valor acumulado

```sql
SELECT
    customer_id,
    country,
    total_orders,
    lifetime_value
FROM de_portfolio_gold.customer_lifetime_value
ORDER BY lifetime_value DESC
LIMIT 10;
```

### Validación de errores de calidad

```sql
SELECT
    source_table,
    error_code,
    COUNT(*) AS total_errors
FROM de_portfolio_silver.data_quality_errors
GROUP BY source_table, error_code
ORDER BY total_errors DESC;
```

### Time travel con Iceberg

```sql
SELECT COUNT(*)
FROM de_portfolio_silver.orders
FOR TIMESTAMP AS OF TIMESTAMP '2026-05-20 00:00:00 UTC';
```

---

## 25. Pruebas

### Unitarias

Validan funciones puras:

- Enmascaramiento de email.
- Enmascaramiento de teléfono.
- Validación de status.
- Cálculo de `line_total`.
- Parseo de fechas.

### Integración / contratos

Validan:

- Las columnas esperadas existen.
- No hay duplicados por llave primaria.
- Las métricas de ventas son consistentes.
- Los registros inválidos van a tabla de errores.
- Las tablas Gold contienen datos.

Comando:

```bash
pytest tests/
```

---

## 26. Observabilidad

### Logs por job Spark

Cada job debe registrar:

- `dag_id`.
- `task_id`.
- `batch_id`.
- Fecha/hora de inicio.
- Fecha/hora de fin.
- Archivos procesados.
- Número de registros leídos.
- Número de registros válidos.
- Número de registros inválidos.
- Ruta destino.
- Duración total.
- Estado final.

Ejemplo:

```json
{
  "dag_id": "de_portfolio_lakehouse_medallion",
  "task_id": "bronze_to_silver_orders",
  "batch_id": "20260520T090000",
  "records_read": 10000,
  "records_valid": 9850,
  "records_invalid": 150,
  "duration_seconds": 42,
  "status": "SUCCESS"
}
```

### Métricas mínimas

| Métrica                  | Descripción                   |
| ------------------------ | ----------------------------- |
| records_read             | Registros leídos              |
| records_written          | Registros escritos            |
| records_rejected         | Registros rechazados          |
| job_duration_seconds     | Duración del job              |
| duplicate_records        | Duplicados detectados         |
| null_primary_keys        | Llaves nulas detectadas       |
| athena_validation_status | Resultado de validaciones SQL |

---

## 27. Estrategia de Particionamiento

| Tabla               | Partición sugerida        | Motivo                         |
| ------------------- | ------------------------- | ------------------------------ |
| silver.orders       | days(order_date)          | Consultas frecuentes por fecha |
| silver.order_items  | bucket(order_id) opcional | Distribución por orden         |
| gold.fact_sales     | months(order_date)        | Análisis mensual               |
| gold.sales_by_month | sales_month               | Agregados de negocio           |

Consideraciones:

- Evitar demasiadas particiones pequeñas.
- Usar particiones alineadas con patrones de consulta.
- Mantener archivos Parquet de tamaño razonable.
- Considerar compactación como mejora futura.

---

## 28. Manejo de Esquema

El proyecto debe demostrar evolución de esquema con Iceberg.

Caso de demo:

1. Ejecutar pipeline inicial con columnas base.
2. Agregar columna nueva `customer_segment` en customers.
3. Ejecutar nueva carga.
4. Mostrar que la tabla evoluciona sin recrearse completamente.
5. Consultar nueva columna desde Athena.

Ejemplo:

```sql
ALTER TABLE de_portfolio_silver.customers
ADD COLUMN customer_segment string;
```

---

## 29. Demo para Entrevista

### Guion sugerido de 7 a 10 minutos

1. **Contexto del problema**  
   “Construí un Lakehouse de e-commerce sobre AWS, orquestado con Airflow y procesado con Spark, para demostrar ingesta, transformación, calidad, catálogo y analítica.”

2. **Arquitectura**  
   Mostrar Airflow, Spark, S3 Bronze/Silver/Gold, Glue Catalog, Crawlers y Athena.

3. **DAG de Airflow**  
   Mostrar dependencias, reintentos, `batch_id` y ejecución de tareas.

4. **Código PySpark**  
   Mostrar una transformación con validaciones y escritura Iceberg.

5. **Catálogo**  
   Mostrar bases y tablas en Glue Data Catalog.

6. **Athena**  
   Ejecutar queries de revenue mensual y top productos.

7. **Calidad de datos**  
   Mostrar tabla `data_quality_errors`.

8. **Seguridad y costos**  
   Explicar IAM, cifrado, PII masking, particiones y uso del cluster existente.

9. **Iceberg**  
   Mostrar time travel o evolución de esquema.

10. **Mejoras futuras**  
    Streaming con Kinesis, CDC, Lake Formation, QuickSight y alertas.

---

## 30. Relación con Requerimientos del Rol

| Requerimiento del rol   | Evidencia en el proyecto                                             |
| ----------------------- | -------------------------------------------------------------------- |
| Ingesta batch           | Carga de CSV/JSON hacia S3 Bronze                                    |
| Transformación ETL/ELT  | Scripts PySpark ejecutados vía Spark Connect: Bronze → Silver → Gold |
| Computación distribuida | Cluster Spark local independiente con Spark Connect                  |
| Formatos diversos       | CSV, JSON, Parquet/Iceberg                                           |
| Orquestación            | Apache Airflow local                                                 |
| Optimización SQL/costo  | Athena, particiones, Iceberg/Parquet                                 |
| APIs/CDC                | Extensión opcional con API o CDC simulado                            |
| S3                      | Data Lake principal                                                  |
| Glue Data Catalog       | Catálogo central                                                     |
| Glue Crawlers           | Reconocimiento y actualización de metadatos                          |
| Open Table Format       | Apache Iceberg                                                       |
| Calidad de datos        | Reglas y tabla de errores                                            |
| Monitoreo               | Logs de Airflow, Spark y CloudWatch opcional                         |
| Seguridad               | IAM, cifrado, PII masking                                            |
| Gobernanza              | Separación por capas, catálogo y control de acceso                   |
| BI                      | Queries listas para QuickSight                                       |
| IaC                     | Terraform o CDK                                                      |
| Git                     | Repositorio versionado                                               |

---

## 31. Roadmap

### Versión 1 - MVP

- Crear buckets S3.
- Cargar datos de ejemplo.
- DAG básico en Airflow.
- Jobs Spark Bronze → Silver → Gold.
- Tablas Iceberg.
- Consultas Athena.
- README completo.

### Versión 2 - Calidad y Observabilidad

- Tabla `data_quality_errors`.
- Métricas por job.
- Pruebas unitarias.
- Validaciones Athena desde Airflow.
- Logs estructurados.

### Versión 3 - Infraestructura como Código

- Terraform/CDK.
- IAM mínimo.
- Glue Crawlers.
- Athena Workgroup.
- S3 Lifecycle.

### Versión 4 - Gobernanza y BI

- KMS.
- Lake Formation.
- QuickSight.
- Data quality avanzada.

### Versión 5 - Streaming / CDC

- Kinesis.
- CDC simulado desde PostgreSQL.
- Procesamiento incremental.

---

## 32. Criterios de Aceptación

El proyecto se considera completo cuando:

- El DAG de Airflow ejecuta el pipeline end-to-end.
- Spark procesa datos desde S3 Bronze.
- Se generan tablas Iceberg en Silver y Gold.
- Glue Data Catalog contiene las tablas esperadas.
- Glue Crawlers se pueden ejecutar desde Airflow.
- Athena puede consultar al menos una tabla Gold.
- Existe tabla de errores de calidad.
- Existen pruebas unitarias básicas.
- El README explica arquitectura, ejecución y demo.
- Se incluye un guion de entrevista.

---

## 33. Limpieza de Recursos AWS

Para evitar costos innecesarios:

```bash
cd infra/terraform
terraform destroy
```

También revisar manualmente:

- Buckets S3 vacíos.
- Glue Crawlers eliminados.
- Glue Databases eliminadas.
- Athena query results eliminados.
- CloudWatch Log Groups eliminados si no se necesitan.
- Workgroups de Athena si se crearon aparte.

---

## 34. Posibles Preguntas de Entrevista y Respuestas

### ¿Por qué Airflow local, Spark local y Spark Connect?

Porque Airflow es excelente para orquestar dependencias, reintentos y calendarización, pero no debe ejecutar procesamiento pesado. Spark es el motor adecuado para procesamiento distribuido. Spark Connect permite separar el cliente Python del servidor Spark, de modo que Airflow solo dispara lógica liviana y el cluster Spark local ejecuta el trabajo pesado.

### ¿Por qué Iceberg y no solo Parquet?

Porque Iceberg agrega una capa transaccional y de metadatos sobre archivos Parquet. Permite evolución de esquema, snapshots, time travel, particionamiento flexible y operaciones más seguras en tablas analíticas.

### ¿Por qué arquitectura medallion?

Porque separa responsabilidades: Bronze conserva datos crudos, Silver entrega datos limpios y Gold ofrece modelos listos para consumo analítico. Esto mejora trazabilidad, calidad y reutilización.

### ¿Por qué usar Glue Data Catalog?

Porque centraliza metadatos y permite que servicios como Athena y motores Spark consulten las mismas definiciones de tablas.

### ¿Cómo optimizaste costos?

Usé el cluster Spark existente, ejecución bajo demanda, formatos columnares, particionamiento, consultas Athena acotadas y limpieza de temporales.

### ¿Cómo manejas datos inválidos?

Los registros inválidos no rompen el pipeline completo. Se aíslan en una tabla de errores con código, mensaje, fuente y batch_id para análisis posterior.

### ¿Cómo aplicas seguridad?

Con IAM de mínimo privilegio, buckets privados, separación por zonas, cifrado en reposo y enmascaramiento de campos sensibles antes de exponer datos en Silver y Gold.

### ¿Qué mejorarías si fuera productivo?

Agregaría Lake Formation, CI/CD, monitoreo avanzado, alertas, compactación Iceberg, CDC real, streaming con Kinesis y dashboard en QuickSight.

---

## 35. Resultado Esperado

Al finalizar, este repositorio debe permitir demostrar:

- Capacidad para diseñar un Data Lakehouse.
- Buen entendimiento de AWS Analytics.
- Manejo de S3, Glue, Athena e Iceberg.
- Orquestación con Airflow.
- Procesamiento distribuido con Spark local.
- Integración moderna mediante Spark Connect.
- Buenas prácticas de calidad, seguridad y costos.
- Capacidad de explicar decisiones técnicas.
- Uso de Git, Python, SQL, PySpark e IaC.

Este proyecto está diseñado para ser suficientemente simple para construirlo en pocos días, pero suficientemente completo para conversar en profundidad durante una entrevista técnica de AWS Data Engineer.
