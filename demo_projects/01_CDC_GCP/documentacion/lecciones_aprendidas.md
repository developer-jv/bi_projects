# Runbook de Reestabilización – CDC con Debezium, Kafka, Spark Streaming y Apache Iceberg

> Proyecto: **Proyectos BI**  
> Arquitectura de referencia: **MySQL → Debezium (Kafka Connect) → Kafka (Avro + Schema Registry) → Spark Structured Streaming → Apache Iceberg (ACID)**

Este documento sintetiza las **lecciones aprendidas** en nuestros chats y define **playbooks operativos** para recuperar la estabilidad cuando algo se rompe. Úsalo como guía rápida en incidentes y como checklist de salud de la plataforma.

---

## 0) Mapa mental de la arquitectura

- **Fuente**: MySQL con binlog en **ROW** (GTID recomendado)  
- **Ingesta**: Debezium en Kafka Connect (topics `erp_avro.*`, Avro + Schema Registry)  
- **Procesamiento**: Spark Structured Streaming leyendo de Kafka (deserializa con `from_avro` usando el Schema Registry)  
- **Destino**: Tablas **Apache Iceberg** (ACID, snapshots, rollback, compactación)

---

## 1) Checklist RÁPIDO de estabilización

1. **Congela** lo que sigue consumiendo/escribiendo:
   - Pausa **Spark Streaming** (o detén el job) para evitar efectos dominó.
   - **Pausa** el conector Debezium (Kafka Connect REST) si la fuente está en estado incierto.
2. **Observa** y **anota**: errores exactos, timestamps, versiones, cambios recientes (deploys, DDL, reinicios de brokers, rotación de credenciales, purga de binlogs, etc.).
3. **Delimita el daño**: ¿se perdió binlog? ¿se perdió el *history topic*? ¿hubo cambio de esquema incompatible? ¿se borró un topic?
4. **Elige playbook** (secciones 3.x abajo) según el síntoma.
5. **Recupera** paso a paso y **reanuda** flujos en orden: fuente → ingesta → procesamiento → destino.
6. **Valida integridad**: conteos, checks de duplicados, estado de snapshots en Iceberg.

---

## 2) Qué debería resistir esta arquitectura (y qué NO)

**Tolera** (si está bien configurada):
- Reinicios de Kafka Connect, broker Kafka, jobs Spark → gracias a offsets y checkpoints.
- Cambios de esquema **compatibles** (BACKWARD/ FULL) en Avro via Schema Registry.
- Caídas temporales de red; reintentos de productores/consumidores.
- Fallas parciales de escritura en Iceberg → **ACID** y snapshots evitan data corrupta.

**NO tolera sin intervención**:
- **Purgas de binlog** antes del offset almacenado → requiere **re-snapshot**.
- Pérdida/corrupción del **history topic** de Debezium → requiere **schema_only_recovery**.
- Cambios de esquema **incompatibles** en producción (rompen consumidores).
- Borrado de topics, borrado de checkpoint de Spark o de metadatos de Iceberg sin plan.

---

## 3) Playbooks por síntoma

### 3.1 Conector Debezium en `FAILED` / errores de ejecución

**Síntomas**: `FAILED` en status; stacktraces sobre conexión, permisos, DDL, SR.

**Pasos**:
1. **Ver estado**: `GET /connectors/{name}/status`
2. **Revisar logs** de Connect (errores de autenticación, DDL no soportado, SR, etc.).
3. **Reintentar**: `POST /connectors/{name}/restart?includeTasks=true`
4. Si es **esquema**: revisar compatibilidad en Schema Registry; ver 3.4.
5. Si es **conexión**: validar `database.hostname`, credenciales, permisos binlog y `server_id`.

> Nota: Evita ciclos de restart sin entender la causa; pueden agravar el problema.

---

### 3.2 **Se purgó el binlog** o **se movió la BD** y el conector no puede continuar

**Síntomas**: errores tipo *“The binlog file … was not found”* (MySQL 1236), offset fuera de rango.

**Causa**: La posición guardada por Debezium ya no existe (purga), o cambió el origen (migración de servidor) sin continuidad del binlog/GTID.

**Solución** (**Re-snapshot controlado**):
1. **Detén/pausa** el conector.
2. Prepara **re-snapshot**:
   - Opción A: `snapshot.mode=initial` (relee tablas completas).
   - Opción B: **Incremental snapshot** (señales) para tablas específicas si el volúmen es grande.
3. (Opcional) **Resetea offsets** del conector si vas a reconstruir desde cero. **No borres** los topics de datos a menos que tengas plan de reconciliación aguas abajo.
4. **Inicia** el conector con el modo elegido y monitorea.
5. **Reanuda Spark** y valida no duplicados (Iceberg + merge/idempotencia, ver 3.6).

> **Importante**: `schema_only_recovery` **no** resuelve pérdida de binlog; sirve para reconstruir el *history* de DDL (3.3). Para binlog perdido, el remedio es **nuevo snapshot**.

---

### 3.3 **Se perdió/corrompió el History Topic** de Debezium (DDL)

**Síntomas**: errores al reproducir DDL históricos; el conector no puede reconstruir el estado de esquema.

**Solución** (**Schema-only recovery**):
1. **Detén** el conector.
2. Arráncalo con `snapshot.mode=schema_only_recovery`.
   - Esto **reconstruye** el *history topic* leyendo el esquema actual de la base.
3. Cuando el *history* esté sano, **detén** y vuelve a `snapshot.mode=when_needed` (o tu modo habitual).
4. **Arranca** nuevamente y verifica flujo.

> Esto **no** reingesta datos; sólo restablece la historia de DDL que el conector necesita.

---

### 3.4 Cambios de esquema rompen consumidores (Avro/Schema Registry)

**Síntomas**: `Schema being evolved is incompatible`, errores de deserialización en Spark.

**Buenas prácticas**:
- Mantén **compatibilidad BACKWARD** (o FULL) en SR para *subjects* `*-value`.
- Introduce columnas nuevas como **opcionales** con default.
- Evita **renames** destructivos; usa alias o procesos de migración.

**Recuperación**:
1. Ajusta compatibilidad si fue endurecida inadvertidamente.
2. Publica una **nueva versión** de esquema compatible.
3. Actualiza Spark para leer la nueva versión (Avro + `from_avro` con SR).
4. Si hubo eventos escritos con esquema incompatible, evalúa **topic de transición** y backfill.

---

### 3.5 Topic de Kafka dañado/eliminado o mal configurado

**Síntomas**: producers/consumers fallan, particiones inconsistentes, *history topic* sin compactación.

**Solución**:
- Para **history topic** (DDL): debe tener `cleanup.policy=compact` y retención suficiente.
- Para **topics de datos** Debezium: típicamente `cleanup.policy=delete`.
- Si hay que **recrear**: crea con `replication.factor`, `min.insync.replicas` y retención apropiadas; documenta impacto aguas abajo.

---

### 3.6 Spark Streaming duplicando/atascado; dudas con offsets y checkpoint

**Síntomas**: duplicados en Iceberg, job se rehace constantemente, errores al deserializar Avro.

**Buenas prácticas**:
- Usa **checkpoint** estable y **no lo borres** sin plan; garantiza idempotencia en el *sink* (Iceberg con *merge* por clave + tipo de operación Debezium: `c/u/d`).
- Controla `startingOffsets` cuidadosamente (usar `latest` en productivo; `earliest` para backfills controlados con **nuevo** checkpoint aislado).
- Deserializa con `from_avro(value, schema, registryConfig)` para respetar evoluciones.

**Recuperación**:
1. **Detén** el job.
2. Si necesitas reprocesar, arranca un **job de backfill** con checkpoint **nuevo** y `startingOffsets=earliest` (acotado por tiempo/particiones si aplica).
3. Deduplica por **(pk, source_ts/op)** si el *envelope* de Debezium está disponible.
4. Verifica en Iceberg (conteos, keys únicas).

---

### 3.7 Tablas Iceberg con inconsistencias o archivos pequeños

**Síntomas**: consultas lentas, demasiados archivos, necesidad de rollback.

**Operaciones útiles** (dependen del engine):
```sql
-- Ver snapshots
SELECT * FROM db.table.snapshots;

-- Rollback a un snapshot conocido
CALL system.rollback_to_snapshot('db.table', <snapshot_id>);

-- Expirar snapshots antiguos
CALL system.expire_snapshots('db.table', TIMESTAMP '2025-09-01 00:00:00');

-- Remover archivos huérfanos (cuando aplica)
CALL system.remove_orphan_files('db.table');

-- Compactación (re-escritura de data/manifests)
CALL system.rewrite_data_files('db.table');
CALL system.rewrite_manifests('db.table');
```

---

## 4) Preguntas que surgieron (y respuestas claras)

**P: Si se pierde el binlog, ¿sirve `schema_only_recovery`?**  
**R:** No. Para binlog perdido se requiere **nuevo snapshot** (inicial o incremental). `schema_only_recovery` sólo repara la **historia de DDL**.

**P: ¿Al mover la BD a otro servidor el conector se recupera solo?**  
**R:** Sólo si hay **continuidad** del binlog/GTID y la config/credenciales apuntan correctamente. Si no, haz **re-snapshot**.

**P: ¿Cómo mantengo consistencia final en Iceberg?**  
**R:** Usa escritura **idempotente** (merge por PK + op), apóyate en **ACID** de Iceberg y en **checkpoints** consistentes.

---

## 5) Configuración recomendada (extractos)

**Debezium MySQL (ideas clave, ajusta a tu entorno):**
```json
{
  "connector.class": "io.debezium.connector.mysql.MySqlConnector",
  "tasks.max": "1",

  "topic.prefix": "erp_avro",
  "database.hostname": "mysql-cdc",
  "database.port": "3306",
  "database.user": "<user>",
  "database.password": "<pass>",

  "include.schema.changes": "true",
  "tombstones.on.delete": "true",
  "heartbeat.interval.ms": "10000",

  "snapshot.mode": "when_needed",          // usar initial o incremental signals según playbook
  "decimal.handling.mode": "precise",
  "time.precision.mode": "connect",

  // History topic (compactado) – nombres/propios según tu plataforma
  "database.history.kafka.bootstrap.servers": "<brokers>",
  "database.history.kafka.topic": "schema-changes.erp_avro"
}
```

**Schema Registry**:
- Compatibilidad **BACKWARD** por defecto.
- Evita borrados de subjects en caliente.

**Kafka**:
- Topics de datos con retención acorde; history topic con **compactación**.
- `min.insync.replicas` ≥ 2 en clústeres de 3 brokers.

**Spark**:
- Usa `from_avro` con URL del SR.
- Checkpoint por flujo/tabla; *trigger* y particionado ajustados al SLA.

**Iceberg**:
- Plan de **mantenimiento**: `expire_snapshots`, `remove_orphan_files`, `rewrite_*` periódico.

---

## 6) Observabilidad y alertas mínimas

- **MySQL**: lag de réplica (si aplica), tamaño y edad del **binlog**, `binlog_row_image=FULL`, espacio en disco.
- **Debezium/Connect**: estado del conector y tareas, errores por minuto, *queue size*, métricas de *source lag*.
- **Kafka**: *consumer lag*, *under-replicated partitions*, tasa de errores de produce/consume.
- **Schema Registry**: latencia y errores de *schema lookup*.
- **Spark**: *batch duration*, *processing time*, *input rows*, fallas por microbatch.
- **Iceberg**: recuento de snapshots, tamaño medio de archivos, consultas lentas.

---

## 7) Procedimientos de prueba (DR / simulacros)

- Simular **cambio de esquema compatible** y validar que Spark/Iceberg siguen sanos.
- Simular **fallo de conector** y recuperación por restart.
- Backfill **controlado**: job de lectura con `startingOffsets=earliest` hacia una tabla de staging en Iceberg y reconciliación.
- **Rollback** de Iceberg a un snapshot anterior y verificación de integridad.

---

## 8) Apéndice – Comandos útiles

**Kafka Connect REST**
```bash
# Estado
curl -s http://<connect-host>:8083/connectors/<name>/status | jq

# Pausar / Reanudar / Reiniciar
curl -X PUT  http://<connect-host>:8083/connectors/<name>/pause
curl -X PUT  http://<connect-host>:8083/connectors/<name>/resume
curl -X POST http://<connect-host>:8083/connectors/<name>/restart?includeTasks=true

# Actualizar config
curl -X PUT -H 'Content-Type: application/json' \
  --data @connector.json http://<connect-host>:8083/connectors/<name>/config
```

**Kafka – consumer groups**
```bash
kafka-consumer-groups --bootstrap-server <brokers> \
  --describe --group connect-<name>
```

**Schema Registry**
```bash
# Ver compatibilidad global
curl -s http://<sr-host>:8081/config | jq
# Ajustar compatibilidad global (ej. BACKWARD)
curl -X PUT -H 'Content-Type: application/json' \
  --data '{"compatibility":"BACKWARD"}' \
  http://<sr-host>:8081/config
```

**Spark SQL / Iceberg**
```sql
-- Inspección de snapshots
SELECT * FROM db.table.snapshots ORDER BY committed_at DESC LIMIT 10;
```

---

### Nota final
Este runbook prioriza **acciones seguras y reversibles**. Cuando dudes entre borrar y reconstruir o **re-snapshot + rollback**, prefiere lo segundo. Iceberg te da herramientas sólidas de integridad; aprovéchalas junto con un control cuidadoso de offsets y compatibilidad de esquemas.

