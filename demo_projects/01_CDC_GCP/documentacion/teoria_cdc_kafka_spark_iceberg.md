# Teoría completa: Arquitectura CDC con Debezium → Kafka (Avro + Schema Registry) → Spark Structured Streaming → Apache Iceberg (ACID)

> Objetivo: que un lector que inicia desde cero comprenda **qué es**, **por qué** y **cómo** funciona esta arquitectura extremo a extremo, y cuente con referencias para profundizar.

---

## 1) Contexto y motivación

### 1.1 ¿Por qué CDC? (Change Data Capture)
- **CDC** captura los cambios (insert/update/delete) que ocurren en bases **OLTP** (e.g., MySQL) leyendo sus **logs de transacción** (binlog), en lugar de re‑extraer tablas completas.
- Beneficios:
  - **Baja latencia** para analítica casi en tiempo real.
  - **Menor carga** sobre la base origen (no hay full scans frecuentes).
  - Mantener **historial** y trazabilidad de cambios.
- Comparado con ETL batch tradicional: CDC reduce “ventanas ciegas” y evita sobrescrituras costosas.

### 1.2 Patrón arquitectónico (visión macro)
1. **MySQL (binlog en ROW)** registra cada cambio.
2. **Debezium (Kafka Connect)** lee el binlog y emite eventos **Avro** a **Kafka**.
3. **Schema Registry** versiona los esquemas Avro para evolución controlada.
4. **Spark Structured Streaming** consume los eventos, los deserializa y los transforma en **upserts/deletes**.
5. **Apache Iceberg** recibe las escrituras **ACID**, gestiona snapshots y sirve consultas analíticas y *time travel*.

---

## 2) Componentes y conceptos clave

### 2.1 MySQL y el binlog
- **binlog_format=ROW**: cada cambio a nivel de fila queda registrado (necesario para CDC fiable).
- **GTID** (opcional): facilita continuidad de réplica/migraciones.
- Requisitos típicos: permisos para leer binlog, retención suficiente, `binlog_row_image=FULL`.

### 2.2 Debezium sobre Kafka Connect
- **Conector MySQL** de Debezium:
  - Lee el binlog, interpreta operaciones DML y publica eventos.
  - Mantiene su posición (offset) para reanudar tras reinicios.
  - Tiene **modos de snapshot**:
    - `initial`: toma snapshot completo y luego sigue con cambios.
    - `when_needed`: sólo si nunca ha tomado snapshot.
    - **Incremental snapshot** (vía señales) para re‑ingestar tablas sin parar el conector.
    - `schema_only_recovery`: reconstruye **historia de DDL** si el *history topic* se perdió (no re‑ingesta datos).
- **History topic** (DDL): Debezium guarda aquí la evolución de esquemas de la fuente, usualmente con `cleanup.policy=compact`.
- **Envelope** Debezium: estructura con `before`, `after`, `op` (c=Create, u=Update, d=Delete, r=Read/snapshot), `source` (metadatos), `ts_ms`.

### 2.3 Kafka (brokers, topics y offsets)
- **Brokers**: nodos del clúster que almacenan **topics**.
- **Topic**: log particionado y **ordenado por partición**.
- **Particiones**: unidad de paralelismo y escalado; cada partición mantiene su **offset** secuencial.
- **Replicación**: tolerancia a fallas (ISR, `min.insync.replicas`).
- **Productores**: publican mensajes; pueden ser **idempotentes** y transaccionales.
- **Consumidores** y **grupos**: comparten trabajo; el **offset** comprometido define el progreso.
- **Políticas de limpieza**:
  - `delete` (retención por tiempo/tamaño).
  - `compact` (conserva último valor por clave). El *history topic* de Debezium suele ser compactado.

### 2.4 Schema Registry + Avro
- **Avro**: formato binario eficiente con esquema explícito.
- **Subjects**: por convención `<topic>-value` y `<topic>-key`.
- **Compatibilidad**: BACKWARD / FORWARD / FULL / NONE. Recomendable **BACKWARD** (o FULL) para consumidores existentes.
- **Evolución**: agregar campos **opcionales** con default; evitar cambios incompatibles como renombrar campos sin alias.

### 2.5 Spark Structured Streaming
- **Modelo**: micro‑batch (por defecto) o continuo.
- **Fuente Kafka**: lectura por partición/offset; control mediante **checkpoint** (metadatos de progreso y estado).
- **Deserialización Avro**: con `from_avro` usando **Schema Registry**; permite manejar evoluciones.
- **Semánticas**: al menos una vez (at-least-once). Para “exactly-once” **efectivo**, el *sink* debe ser idempotente o transaccional.
- **Watermarks y estado**: para deduplicación y *joins* con ventanas.

### 2.6 Apache Iceberg (tablas ACID para lago de datos)
- **Metadatos de tabla**: archivo de *table metadata* que referencia **manifest lists** y **manifest files**.
- **Particionamiento oculto**: evita acoplar consultas al layout físico; define **transformaciones** (e.g., `bucket(id, 16)`, `days(ts)`).
- **Snapshots** y *time travel*: cada commit crea un snapshot; se puede consultar un snapshot pasado o **hacer rollback**.
- **Operaciones ACID**: aislamiento **snapshot** con control de concurrencia optimista.
- **Deletes**:
  - **Equality deletes** (borra filas que coinciden con una expresión, típicamente por PK).
  - **Position deletes** (referencian archivos/posiciones exactas).
- **Mantenimiento**: expirar snapshots, remover archivos huérfanos, reescritura/compactación de *data files* y *manifests*.

---

## 3) Flujo extremo a extremo (E2E)

1. **Cambio en MySQL** (INSERT/UPDATE/DELETE) → queda en **binlog**.
2. **Debezium** lee binlog, enriquece con metadatos (`source`, `ts_ms`), publica evento **Avro** a **Kafka**.
3. **Schema Registry** fija versión de esquema para ese mensaje.
4. **Spark** consume de Kafka (por partición), usa `from_avro` (SR) para obtener columnas tipadas.
5. Lógica de **upsert/delete**:
   - Mapear `op` de Debezium → operaciones en Iceberg (INSERT/MERGE/DELETE).
   - Resolver **orden** y **deduplicación** (p.ej., por `(pk, ts_ms)` y *op*), especialmente en reintentos.
6. **Escritura en Iceberg** con garantías **ACID**: se crea snapshot; consultores ven estado **consistente**.

**Idempotencia**: si Spark re‑procesa un lote (fallo), la combinación **PK + op + ts** + escritura a Iceberg vía **MERGE** evita duplicados.

---

## 4) Diseño de esquemas y compatibilidad

- **Claves primarias** claras y estables (evitar cambios de PK).
- **Tipos**:
  - `DECIMAL` para dinero → en Avro `bytes` con *logicalType* `decimal`.
  - Tiempos: conservar **zona/UTC** y precisión (micros/nanos según engine).
- **Nullability**: preferir **nuevos campos opcionales** con defaults.
- **Estrategia de compatibilidad** en SR: **BACKWARD** o **FULL** para no romper lectores.
- **Evolución controlada**: *deprecate* en lugar de borrar; usa *aliases* si cambias nombres.

---

## 5) Patrones de operación y confiabilidad

### 5.1 Offsets, reintentos y re‑procesamiento
- **Kafka**: commit de offset tras procesar; si falla, se re‑intenta ese rango.
- **Spark**: el **checkpoint** mantiene offsets y estado; no lo borres sin plan.
- **Backfills**: ejecútalos con **nuevo checkpoint** y `startingOffsets=earliest`, hacia *staging* para reconciliar.

### 5.2 Escalabilidad y rendimiento
- **Kafka**: más **particiones** = más paralelismo de consumo; alinear con `tasks.max` y particiones aguas abajo.
- **Spark**: ajustar *micro‑batch interval*, *maxOffsetsPerTrigger*, *shuffle partitions*, *coalesce/repartition*.
- **Iceberg**: escribir **archivos del tamaño objetivo** (p.ej., 128–512 MB) y programar **compactación**.

### 5.3 Observabilidad
- **MySQL**: edad/tamaño de binlog; espacio en disco.
- **Debezium/Connect**: status del conector, *source lag*, errores por minuto.
- **Kafka**: *consumer lag*, *under-replicated partitions*.
- **Schema Registry**: latencia de *schema lookup* y errores.
- **Spark**: *batch duration*, *input rows*, fallas por microbatch.
- **Iceberg**: número de snapshots, archivos pequeños, latencia de consultas.

### 5.4 Seguridad
- **MySQL**: usuario con mínimos privilegios; rotación de credenciales.
- **Kafka**: TLS/SASL, ACLs por topic; credenciales protegidas.
- **Schema Registry**: autenticación/autorización; evitar *subject deletes* en caliente.
- **Spark/Iceberg**: control de acceso a warehouse y metastore.

---

## 6) Cómo escribir en Iceberg desde Spark (patrones típicos)

### 6.1 Upserts con MERGE
```sql
MERGE INTO db.dest AS d
USING temp_view AS s
ON d.pk = s.pk
WHEN MATCHED AND s.op = 'd' THEN DELETE
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED AND s.op IN ('c','u','r') THEN INSERT *;
```
- **Igualdad por PK**; opcionalmente usar `ts_ms` para ordenar últimos cambios.

### 6.2 Deletes
- **Equality delete** por `pk` (eficiente si el PK está particionado/bucketeado).
- **Position delete** cuando el *writer* conoce archivos/posiciones exactas (más bajo nivel).

---

## 7) Anti‑patrones y riesgos

- Usar CDC para **transformaciones complejas** en línea → mejor **staging** + procesos batch derivados.
- Tratar a **Kafka como base de datos** de almacenamiento duradero → Kafka es un *log*. Mantén retenciones razonables; datos “fuente de verdad” en el **warehouse** (Iceberg).
- **Renombrar campos/PK** en caliente sin estrategia → rompe consumidores y claves de *merge*.
- Borrar **checkpoint** de Spark sin un plan de re‑procesamiento.

---

## 8) Checklist de diseño (rápido)

- [ ] MySQL con `ROW` y retención de binlog suficiente.
- [ ] Debezium con history topic **compactado** y `snapshot.mode` definido.
- [ ] Particiones de Kafka suficientes para el SLA y el throughput.
- [ ] Schema Registry en **BACKWARD/FULL** y políticas de evolución documentadas.
- [ ] Spark con **checkpoint** dedicado por flujo, `from_avro` y control de offsets.
- [ ] Iceberg con **PK**/particionamiento adecuados, y tareas de **mantenimiento** programadas.
- [ ] Métricas y alertas por componente.
- [ ] Seguridad extremo a extremo (TLS/ACLs/credenciales).

---

## 9) Glosario esencial

- **CDC**: Change Data Capture; técnica para capturar cambios de una BD.
- **Binlog**: log de transacciones de MySQL.
- **Envelope**: estructura del evento Debezium con `before/after/op`.
- **Topic/Partición/Offset**: primitivas de Kafka para organizar y leer el log.
- **Schema Registry**: servicio que almacena y versiona esquemas.
- **Checkpoint**: estado persistido de un job streaming (offsets, estado).
- **Snapshot (Iceberg)**: versión consistente de la tabla en un tiempo.
- **Equality/Position delete**: estrategias de borrado en Iceberg.

---

## 10) Referencias para profundizar (lecturas y docs)

> Recomendación: empieza por las **documentaciones oficiales** y complementa con libros/artículos.

- **Debezium** (conceptos y conectores):  
  https://debezium.io/documentation/
- **Apache Kafka** (conceptos, diseño, operaciones):  
  https://kafka.apache.org/documentation/
- **Confluent Schema Registry** y Avro:  
  https://docs.confluent.io/platform/current/schema-registry/index.html  
  https://avro.apache.org/docs/
- **Apache Spark Structured Streaming**:  
  https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
- **Apache Iceberg** (tablas de lago, ACID, snapshots):  
  https://iceberg.apache.org/docs/latest/
- **Libros**:  
  *Designing Data‑Intensive Applications* — Martin Kleppmann  
  *I Heart Logs* — Jay Kreps
- **Artículos técnicos (sugeridos)**:  
  - *The Log: What every software engineer should know about real‑time data’s unifying abstraction* — Jay Kreps  
  - Blogs de ingeniería de Netflix, Uber y Apple sobre datos en tiempo real.

---

## 11) Apéndice: fragmentos ilustrativos

### 11.1 Ejemplo de configuración Debezium (esqueleto)
```json
{
  "name": "mysql-cdc-erp-avro",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "tasks.max": "1",

    "topic.prefix": "erp_avro",
    "database.hostname": "mysql-cdc",
    "database.port": "3306",
    "database.user": "<user>",
    "database.password": "<pass>",

    "include.schema.changes": "true",
    "tombstones.on.delete": "true",
    "snapshot.mode": "when_needed",

    "database.history.kafka.bootstrap.servers": "<brokers>",
    "database.history.kafka.topic": "schema-changes.erp_avro"
  }
}
```

### 11.2 Lectura en Spark desde Kafka + Avro
```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.avro.functions import from_avro

spark = (SparkSession.builder
         .appName("cdc-stream")
         .getOrCreate())

kafka_df = (spark.readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "broker:9092")
  .option("subscribe", "erp_avro.erp.orders")
  .option("startingOffsets", "latest")
  .load())

# Deserializar Avro con Schema Registry
sr_cfg = {"schema.registry.url": "http://schema-registry:8081"}
value_df = kafka_df.select(
    from_avro(F.col("value"), "<avro_schema_json>", sr_cfg).alias("rec"))

# Mapear envelope → upserts/deletes
records = value_df.select(
    F.col("rec.after").alias("after"),
    F.col("rec.before").alias("before"),
    F.col("rec.op").alias("op"),
    F.col("rec.source.ts_ms").alias("ts_ms")
)
```

### 11.3 Operaciones de mantenimiento en Iceberg (SQL genérico)
```sql
CALL system.expire_snapshots('db.tabla', TIMESTAMP '2025-01-01 00:00:00');
CALL system.remove_orphan_files('db.tabla');
CALL system.rewrite_data_files('db.tabla');
CALL system.rewrite_manifests('db.tabla');
```

---

### Nota final
Dominar esta arquitectura requiere entender **logs como fuente de verdad**, **contratos de esquema**, **procesamiento streaming** y **tablas ACID** en el lago. Con los conceptos de arriba y las referencias, tendrás una base sólida para operar y evolucionar un pipeline CDC robusto.

