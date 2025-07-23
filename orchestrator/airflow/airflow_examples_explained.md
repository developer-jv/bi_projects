# Ejercicios de Apache Airflow – Guía Rápida

A continuación encontrarás una descripción concisa de los **10 DAGs de ejemplo** en la carpeta `dags/`. Cada uno ilustra un concepto fundamental de Apache Airflow 3.0 para que puedas experimentar rápidamente.

## Índice

1. [01_print_date.py](#01_print_datepy)
2. [02_branching.py](#02_branchingpy)
3. [03_dynamic_tasks.py](#03_dynamic_taskspy)
4. [04_task_group.py](#04_task_grouppy)
5. [05_time_sensor.py](#05_time_sensorpy)
6. [06_http_call.py](#06_http_callpy)
7. [07_external_task_sensor.py](#07_external_task_sensorpy)
8. [08_sla_dag.py](#08_sla_dagpy)
9. [09_trigger_other_dag.py](#09_trigger_other_dagpy)
10. [10_daily_etl.py](#10_daily_etlpy)

---

## 01_print_date.py

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Mostrar un _operador básico_ (`BashOperator`) que ejecuta un comando sencillo. |
| **Función** | Ejecuta `date` y escribe la salida en el log. |
| **Schedule** | `None` → debes lanzarlo manualmente. |
| **Cuándo usarlo** | Verificar que tu entorno Airflow ejecuta contenedores y registra logs correctamente. |

---

## 02_branching.py

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Demostrar **ramificación** con `BranchPythonOperator`. |
| **Función** | Elegir aleatoriamente entre las tareas `path_a` y `path_b`. |
| **Aprendizaje clave** | Sólo la rama devuelta se sigue ejecutando; la otra queda en estado _skipped_. |

---

## 03_dynamic_tasks.py

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Usar **Dynamic Task Mapping** (`task.expand`). |
| **Función** | Crea una tarea "eat" por cada elemento en la lista `fruits`. |
| **Resultado** | Verás cuatro _task instances_ paralelas, una por fruta. |

---

## 04_task_group.py

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Agrupar tareas con **`TaskGroup`** para un ETL. |
| **Estructura** | `start` → grupo **extract** → grupo **transform** → `load_dw`. |
| **Ventaja** | La UI muestra los grupos colapsables, simplificando DAGs grandes. |

---

## 05_time_sensor.py

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Sincronizar ejecución diaria usando `TimeSensor`. |
| **Función** | Espera hasta las 07:00 UTC antes de lanzar `morning_task`. |
| **Uso típico** | Ajustar ventanas de llegada de datos o SLA de disponibilidad. |

---

## 06_http_call.py

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Integrar sensores y operadores HTTP. |
| **Requiere** | Conexión "jsonplaceholder" en **Admin → Connections** apuntando a `https://jsonplaceholder.typicode.com/`. |
| **Flujo** | `HttpSensor` espera 200 → `SimpleHttpOperator` hace GET y escribe la respuesta. |

---

## 07_external_task_sensor.py

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Coordinar DAGs dependientes con `ExternalTaskSensor`. |
| **Función** | Espera a que la tarea `load_dw` del DAG `etl_grouped` de **ayer** termine. |
| **Escenario real** | Disparar dashboards solo tras finalizar un pipeline anterior. |

---

## 08_sla_dag.py

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Configurar **SLA** y _callbacks_ de alerta. |
| **Definición** | `default_args["sla"] = 5 min` para todas las tareas. |
| **Callback** | Envía un e‑mail cuando se incumple el SLA (simulado con `time.sleep`). |
| **Requisito** | Debes configurar SMTP en `airflow.cfg` o en la conexión "smtp_default". |

---

## 09_trigger_other_dag.py

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Lanzar otro DAG desde una tarea con `TriggerDagRunOperator`. |
| **Función** | Dispara `hello_world` y regresa inmediatamente (`wait_for_completion=False`). |
| **Variaciones** | Usa `conf` para pasar parámetros al DAG destino. |

---

## 10_daily_etl.py

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Plantilla de **ETL diario** con buenas prácticas. |
| **Cron** | `0 2 * * *` → 02:00 UTC cada día. |
| **Paralelismo** | `max_active_runs=1` evita solapamiento si un día se retrasa. |
| **Tolerancia a fallos** | `retries=3`, `retry_delay=300 s` en la tarea `extract`. |

---

## Próximos pasos

1. **Trigger manual**: En la UI haz clic en ▶ sobre cualquier DAG sin schedule.
2. **Observa**: Explora los logs, _Task Groups_ y gráficos de dependencias.
3. **Modifica**: Cambia parámetros (por ej., intervalos de sondeo, número de frutas) y guarda; Airflow recargará automáticamente.
4. **Promueve**: Cuando un DAG te guste, súbelo a tu repositorio Git y prueba la estrategia QA/Prod que discutimos.

¡Con estos ejemplos dominarás la base de Airflow y estarás listo para flujos más complejos! 🚀

