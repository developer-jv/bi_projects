# Arquitectura de Datos Resiliente y Cloud‑Agnostic

> **Estado:** Diseño inicial  ▪︎ **Ámbito:** Ingesta CDC → Streaming → Lakehouse → Transformaciones → DWH → OLAP → BI  ▪︎ **Nube objetivo actual:** GCP (GCS + BigQuery) con estrategia de portabilidad

---

## 1) Objetivo

Diseñar y probar una arquitectura de datos **resiliente**, **escalable** y **portátil entre nubes**, que entregue datos confiables a usuarios finales (Power BI) y sea operable por ingeniería de datos con mínimos tiempos de inactividad, gobernanza clara y costos predecibles.

## 2) Alcance

* **Fuentes**: MySQL/MariaDB transaccionales.
* **CDC**: Debezium (via Kafka Connect).
* **Streaming**: Apache Kafka (modo KRaft o con ZooKeeper).
* **Formateo/Procesamiento**: PySpark (batch y streaming estructurado).
* **Lakehouse**: Google Cloud Storage (GCS) con formatos abiertos (Parquet + Iceberg/Delta/Hudi, a definir en PoC).
* **DWH**: BigQuery (modelo en estrella/constelación de hechos).
* **OLAP**: Modelo semántico/cubo (Power BI Dataset/Tabular) sobre BigQuery.
* **BI**: Power BI.
* **Operabilidad**: Observabilidad, calidad de datos, seguridad, CI/CD e IaC.


---

## 3) Principios de diseño (Cloud‑Agnostic)

1. **Formatos abiertos**: Parquet + (Iceberg/Delta/Hudi) para transaccionalidad y evolución de esquema.
2. **Acoplamiento débil**: Todo componente gestionado por interfaces estándar: Kafka APIs, JDBC/ODBC, SQL ANSI, Storage API S3‑compatible cuando sea posible.
3. **Infra como código**: Terraform para reproducibilidad; módulos por componente.
4. **Portabilidad**: Capa de abstracción en transformaciones (PySpark + dbt) y semántica (Power BI/Tabular) para minimizar *vendor lock‑in*.
5. **Idempotencia y re‑procesamiento**: Diseño *event‑driven* con *checkpointing* y *exactly‑once* cuando aplique.

---

## 4) Requisitos No Funcionales (RNF)

### 4.1 Calidad / Confiabilidad

* **Disponibilidad**: ≥ 99.9% para el plano de lectura (DWH/BI); ≥ 99.5% para ingesta.
* **RPO/RTO**: RPO ≤ 5 min; RTO ≤ 30 min en zonas regionales.
* **Latencia E2E** (CDC→BI): P95 ≤ 10 min (configurable por dominio).
* **Exactitud**: *Drift* de recuentos ≤ 0.1% entre fuente y *silver*; reconciliación diaria.
* **Evolución de esquema**: *Forward/backward compatible* vía Schema Registry.

### 4.2 Rendimiento / Escalabilidad

* **Throughput** inicial: 5–20k eventos/seg (escalable horizontalmente con particiones Kafka).
* **Particionamiento**: por dominio/tenant/fecha; *bucketing* por PK si aplica.
* **Autoescalado**: *Executors* PySpark y *task slots* de Connect/Spark.

### 4.3 Seguridad / Cumplimiento

* **Cifrado** en tránsito (TLS) y en reposo (KMS/CMEK cuando aplique).
* **IAM** con principio de menor privilegio; cuentas de servicio separadas por plano (ingesta, procesamiento, consulta).
* **Seguridad de red**: privados por defecto; saltos/egresos controlados.
* **Data masking**: PII pseudonimizada en *bronze*; *column‑level security* y *row‑level security* en *gold/BI*.

### 4.4 Observabilidad / Operación

* **Trazabilidad**: linaje de extremo a extremo (OpenLineage/Marquez o equivalente).
* **Métricas**: lag de consumidores, QPS, *dead‑letter queues*, calidad (completitud, unicidad, validez).
* **Alertas**: SLOs por pipeline; on‑call runbook y *playbooks* de remediación.

### 4.5 Mantenibilidad / Portabilidad

* **IaC** en Terraform + módulos reusables.
* **CI/CD**: *lint* (ruff/flake8), pruebas, *build*, *deploy* progresivo.
* **Compatibilidad multi‑nube**: describir equivalentes (S3/ADLS, Redshift/Synapse, Trino/Presto) y plan de *switch*.

---

## 5) Arquitectura lógica

1. **CDC**: Debezium captura binlogs (MySQL/MariaDB) → Kafka Topics por tabla.
2. **Esquemas**: Avro/Protobuf con Schema Registry (compatibilidad *backward*).
3. **Persistencia cruda** (*Bronze*)

   * Opción A: Kafka Connect → Sink a GCS (objetos particionados) + *topic compaction* cuando aplique.
   * Opción B: Spark Structured Streaming lee Kafka → escribe Parquet/Iceberg/Delta en GCS.
4. **Refinado** (*Silver*)

   * Normalización, *de‑dup*, *late data handling*, ventanas y *watermarks*.
   * Estrategias SCD (1/2) para dimensionales; *hard/soft deletes*.
5. **Curado / *Gold***

   * Modelos en estrella (hechos y dimensiones) listos para consumo.
   * Cargas al DWH (BigQuery) desde *silver/gold* del lakehouse.
6. **Semántica / OLAP**

   * Dataset/tabular en Power BI (medidas DAX, RLS) sobre BigQuery.

---

## 6) Modelo de datos (resumen)

* **Estándares**: nombres *snake\_case*, *surrogate keys* (*hash/identity*), *audit columns* (ingestion\_ts, source\_lsn, op).
* **Particiones**: por *event\_date* y/o entidad; *clustering* por PK o dimensión frecuente.
* **Calidad**: reglas en Great Expectations/Deequ; *contracts* por dominio.

---

## 7) Layout de almacenamiento en GCS (propuesto)

```
gs://<bucket>/
  raw/                       # bronze, datos CDC por tópico/fecha
    <topic>/ingest_date=<yyyy-mm-dd>/part-*.parquet
  refined/                   # silver, normalizado y de-duplicado
    <domain>/<entity>/dt=<yyyy-mm-dd>/
  curated/                   # gold, listo para DWH/BI
    marts/<mart>/<table>/dt=<yyyy-mm-dd>/
  checkpoints/               # checkpoints de Spark
  _schemas/                  # backups de Schemas
```

> **Formato de tabla transaccional**: evaluar **Iceberg** (o Delta/Hudi) para *ACID*, *time travel*, *schema evolution* en el lakehouse.

---

## 8) BigQuery (DWH)

* **Zonas**: *staging* (aterrizaje), *core* (estrella), *marts* (por dominio/BI).
* **Carga**: *external tables* desde GCS (cuando convenga) o *LOAD* programado desde *curated*.
* **Costos**: usar *partition pruning* y *clustering*; vistas materializadas para *dashboards* críticos.

---

## 9) OLAP / Power BI

* **Modelo semántico (Tabular)**: dimensiones conformadas, jerarquías, *role‑playing dates*.
* **Medidas**: DAX con definiciones de negocio versionadas.
* **Seguridad**: RLS por región/cliente/rol.
* **Conectividad**: DirectQuery/BI Engine cuando aplique; *composite models* si se requiere caché.

---

## 10) Seguridad y cumplimiento (detalle)

* **Secrets**: Vault/KMS + *secret rotation*; sin credenciales embebidas en código.
* **PII**: *tokenization* y *column‑level encryption* donde aplique.
* **Auditoría**: *access logs* centralizados; *data access monitoring* para tablas sensibles.

---

## 11) Observabilidad

* **Logs**: Connect, Debezium, Kafka, Spark, cargas DWH.
* **Métricas clave**: *consumer lag*, errores por conector, *checkpoint age*, latencia E2E, costo por consulta.
* **Linaje**: OpenLineage + etiquetas de *job run id*.
* **Alertas**: SLOs (p.ej., latencia P95 > umbral, *lag* > umbral, fallos consecutivos > N).

---

## 12) Calidad de datos

* **Great Expectations/Deequ**: *suites* por tabla *silver/gold* (completitud, unicidad, validez, *freshness*).
* **DQ Gates**: bloquear promoción a *gold* si falla un *checkpoint* de calidad.
* **Recon fuente↔destino**: conteos, sumas, *hash totals* (diario).

---

## 13) Entornos y despliegue

* **Entornos**: *dev* → *stg* → *prod* (infra y datos segregados).
* **CI/CD**: GitHub Actions/Cloud Build: pruebas, *lint*, empaquetado, despliegue de conectores y *jobs* Spark.
* **Plantillas**: imágenes contenedor para Spark/Connect con versiones *pinned*.

---

## 14) Infraestructura como Código (Terraform)

* **Módulos**: red, Kafka, Connect, buckets GCS, permisos IAM, BigQuery datasets.
* **Variables**: proyecto, región, prefijos, *labels* de coste.
* **Políticas**: *org policies* y *budget alerts*.

---

## 15) Estrategia de portabilidad multi‑nube

| Capa           | GCP (actual)                 | Alternativas equivalentes                      |
| -------------- | ---------------------------- | ---------------------------------------------- |
| Almacenamiento | GCS                          | S3 / ADLS / MinIO (S3 API)                     |
| DWH            | BigQuery                     | Redshift / Snowflake / Synapse / BigLake+Trino |
| Procesamiento  | PySpark                      | Dataproc/EMR/Synapse Spark/K8s Spark           |
| Esquemas       | Schema Registry              | Confluent/Apicurio esquemas compatibles        |
| Lakehouse      | Iceberg/Delta/Hudi sobre GCS | Iceberg/Delta/Hudi sobre S3/ADLS               |
| BI             | Power BI                     | Tableau/Looker (si cambia la herramienta)      |

> **Nota:** Mantener **formatos y contratos** agnósticos para facilitar *lift‑and‑shift*.

---

## 16) Plan de pruebas (Diseño & PoC)

1. **Unitarias**: funciones PySpark, *udfs*, mapeos DAX críticos.
2. **Integración**: Debezium→Kafka→Sink→GCS; Kafka→Spark→Parquet; Spark→BigQuery.
3. **E2E**: *happy path* desde inserciones/updates/deletes en MySQL hasta Power BI.
4. **Rendimiento**: *load test* con 1×, 3×, 5× del volumen esperado; latencia P95.
5. **Resiliencia/Chaos**: caída de un *broker*, *network partition*, *checkpoint* corrupto, *backfill* masivo.
6. **Seguridad**: pruebas de RLS/CLS, acceso denegado, rotación de *secrets*.
7. **Costos**: verificación de límites de escaneo/almacenamiento.

**Criterios de aceptación** (ejemplos):

* E2E ≤ 10 min P95 en 100k filas/hora.
* RPO ≤ 5 min con corte de red de 15 min.
* 0% *data loss* verificado por reconciliación.

---

## 17) Convenciones y *playbooks*

* **Nombres de tópicos**: `<dominio>.<entidad>.<operacion>.<version>`
* **Nombres de tablas**: `<zona>_<dominio>_<entidad>_<version>`
* **Retención Kafka**: *raw* ≥ 7 días, DLQ ≥ 14 días.
* **DLQ**: política de reproceso con límites y etiquetado de causa.
* **Runbooks**: *lag alto*, *connector failed*, *schema incompatibility*, *skew* en Spark.

---

## 18) Esqueleto de repositorio (propuesto)

```
/infra/terraform/
  modules/
/apps/
  spark/
    jobs/
    libs/
  dbt/
/kafka/
  connect/
  debezium/
  schemas/
/data-quality/
  expectations/
/docs/
  architecture/
  runbooks/
```

---

## 19) Ejemplos de configuración (mínimos)

### 19.1 Debezium (conector MySQL → Kafka)

```json
{
  "name": "mysql-cdc-orders",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.hostname": "<host>",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "********",
    "database.server.id": "184054",
    "database.server.name": "src_mysql",
    "database.include.list": "erp",
    "table.include.list": "erp.orders,erp.customers",
    "include.schema.changes": "false",
    "topic.prefix": "erp",
    "snapshot.mode": "initial",
    "tombstones.on.delete": "false",
    "decimal.handling.mode": "double"
  }
}
```

### 19.2 Spark Structured Streaming (Kafka → Parquet en GCS)

```python
(
  spark.readStream
       .format("kafka")
       .option("kafka.bootstrap.servers", os.environ["KAFKA_BOOTSTRAP"])
       .option("subscribe", "erp.orders")
       .load()
       .selectExpr("CAST(value AS STRING)")
       .transform(parse_and_normalize)  # aplica esquemas/validaciones
       .writeStream
       .format("parquet")
       .option("path", "gs://<bucket>/raw/erp.orders/")
       .option("checkpointLocation", "gs://<bucket>/checkpoints/erp.orders/")
       .trigger(processingTime="1 minute")
       .outputMode("append")
       .start()
)
```

### 19.3 Carga a BigQuery (ejemplo PySpark)

```python
(df
  .write
  .format("bigquery")
  .option("table", "dwh.marts_orders")
  .option("temporaryGcsBucket", "<temp-bucket>")
  .mode("append")
  .save())
```

---

## 20) Roadmap (alto nivel)

1. **Semana 1–2**: PoC CDC→Kafka→GCS (*bronze*). Elegir formato de tabla (Iceberg/Delta/Hudi).
2. **Semana 3–4**: *Silver* con SCD y calidad; cargas BigQuery; primer mart.
3. **Semana 5**: Modelo semántico Power BI + *dashboards* críticos.
4. **Semana 6**: Observabilidad E2E, SLOs, *runbooks* y *chaos tests*.
5. **Semana 7+**: Endurecimiento seguridad, optimizaciones de costo, multi‑nube opcional.

---

## 21) Riesgos y mitigaciones

* **Vendor lock‑in DWH** → Abstraer transformaciones y semántica; pruebas de portabilidad.
* **Evolución de esquema** → *Contracts* versionados + validación en *ingest*.
* **Costos impredecibles** → *budget alerts* + vistas materializadas y particionamiento.
* ***Hot partitions*** → *salting*, *bucketing* y *key design*.

---

## 22) Licencia / Autoría

* **Licencia**: por definir.
* **Autores**: Equipo de Datos – Proyectos BI.

---

## 23) Próximos pasos

* Validar formato de tabla transaccional (Iceberg vs Delta vs Hudi) en GCS.
* Definir *contracts* por dominio y primeras *suites* de calidad.
* Preparar *docker‑compose* local para Kafka/Connect/Debezium + Spark.
* Crear *skeleton* Terraform e *issue* inicial por módulo.
* Documentar *playbooks* de operación.
