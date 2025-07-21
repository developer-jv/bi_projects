# Arquitectura de BI – Atributos de Calidad

> **Objetivo**  
> Este documento resume los componentes clave de una arquitectura de Business Intelligence (BI) y los atributos de calidad que aumentan el valor percibido por las empresas, desde la ingesta de datos hasta la visualización.

---

## 1 · Cadena de valor (Ingesta → Visualización)

| Tramo de la cadena | ¿Qué busca la empresa? | ¿Por qué paga por ello? | Indicadores típicos |
|--------------------|------------------------|-------------------------|---------------------|
| **Ingesta & streaming** | Conectores listos (ERP/CRM, APIs, IoT)<br>Capacidad near‑real‑time (< 1–5 min)<br>Gestión automática de errores | Reduce trabajo de ingeniería y acelera *time‑to‑insight*.<br>Menos riesgo de datos faltantes. | `%` fuentes cubiertas sin código · MTTR |
| **Almacenamiento / “lake‑house”** | Escalabilidad elástica (separa cómputo y storage)<br>Formatos abiertos (Parquet/Iceberg/Delta)<br>Cifrado, retención y compresión nativas | Evita *vendor lock‑in* y asegura que el sistema no “quede chico”.<br>Cumple normas (GDPR, SOC 2). | Coste/terabyte · Crecimiento sin re‑plataformar |
| **Procesamiento & transformación (ELT/ETL)** | Motor columnar/MPP o Spark para lotes pesados<br>Orquestación declarativa (dbt, Airflow) con versionado<br>Reglas de calidad (tests, perfiles, observabilidad) | Garantiza consistencia de métricas aun tras 1 año.<br>Facilita auditorías y depuración. | `%` jobs reproducibles · Errores de calidad/mes |
| **Modelo semántico / métricas** | Catálogo central de KPIs (“single source of truth”)<br>Lineage visual y gobernanza de cambios<br>Capas de acceso por rol | Evita discusiones de “mi número vs tu número”.<br>Empodera autoservicio sin perder control. | Tiempo para lanzar una nueva KPI |
| **Servicio & visualización** | Dashboards < 2 s de carga, drill‑through, móvil<br>Exploración ad‑hoc (SQL, lenguaje natural, AI copilot)<br>Alertas y *storytelling* | UX ágil = adopción.<br>Usuarios no técnicos pueden auto‑explorar → mayor ROI. | Usuarios activos/mes · Latencia p95 |
| **Gobierno, seguridad & observabilidad** | Políticas unificadas (RBAC/ABAC) en toda la pila<br>Auditoría, lineage, *cost tracking* y SLA dashboards<br>Monitoreo proactivo de anomalías | Cumple regulaciones y evita “shadow BI”.<br>Reduce incidentes y sorpresas en la factura. | Incidentes de acceso · Cost overruns detectados |
| **Extensibilidad & ecosistema** | APIs/FaaS para ML, *reverse ETL*, **embedded analytics**<br>Marketplace de conectores y comunidad activa | Permite integrar innovaciones sin rehacer todo. | Tiempo de integración de nueva app |

---

## 2 · Atributos transversales de calidad

1. **Velocidad “click‑to‑insight”** – latencia mínima desde ingesta hasta dashboard.  
2. **Escalabilidad elástica** – crecer 10× sin migrar ni sobre‑pagar picos.  
3. **Confiabilidad y precisión** – tests, lineage y monitorización para confiar en los números.  
4. **Seguridad & cumplimiento** – cifrado, RBAC, mascarado y auditorías continuas.  
5. **Autoservicio gobernado** – usuarios crean vistas dentro de políticas definidas.  
6. **Interoperabilidad & formatos abiertos** – evita *lock‑in* y facilita ML/AI.  
7. **Experiencia de usuario** – UI móvil, narrativas automáticas, exploración NL/AI.  
8. **Cost‑Efficiency / FinOps** – métricas claras de coste por consulta o equipo.  
9. **Mantenibilidad** – pipelines declarativas, versionadas y *zero‑downtime deploys*.  
10. **Soporte y comunidad** – roadmap público y ecosistema de plugins/partners.

---

## 3 · Guía para evaluar soluciones

1. **Define SLOs** (p.ej. dashboard < 2 s, refresh < 15 min).  
2. **Pesa atributos** según tu dominio: en banca, seguridad > velocidad; en e‑commerce durante *flash sales*, latencia > todo.  
3. **Solicita pruebas de valor**: mide TCO, latencia, cobertura de conectores y self‑service real.  
4. **Exige métricas de observabilidad** en el demo; si el vendedor no las muestra, asume que serán problema después.

---

## 4 · Analogía de la tubería

- **Cobre** (caro, durable, excelente conductor) ≈ capa de almacenamiento columnar en formato abierto: costosa al inicio pero robusta y flexible.  
- **Plástico** (barato, rápido de instalar, puede degradarse) ≈ conector *ad‑hoc* o DB propietaria que resuelve hoy pero limita mañana.  
- El **valor** depende del **contexto de uso**: si necesitas flexibilidad y cumplimiento estricto, pagarás por el “cobre”. Si priorizas velocidad de despliegue y bajo presupuesto, empezarás con “plástico”, planificando cuándo migrar.

---

## 5 · Conclusión

La decisión de compra de un producto de BI no se basa solo en cuántos gráficos ofrece, sino en **cuán bien convierte datos en confianza y velocidad para decidir**, hoy y dentro de cinco años.  
Usa esta lista como *checklist* de diseño de tu arquitectura o como rúbrica al comparar proveedores.

---

> Elaborado: **21 de julio de 2025**
