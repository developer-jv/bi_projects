# 🚀 Arquitectura de Datos Contenerizada

&#x20;

Este repositorio demuestra **de extremo a extremo** cómo diseñar, orquestar y desplegar un _pipeline_ de datos moderno utilizando únicamente **Docker Compose**. Sirve como laboratorio personal y carta de presentación técnica para entrevistas.

## 📑 Tabla de Contenidos

1. [Objetivos](#objetivos)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Estructura del Repositorio](#estructura-del-repositorio)
4. [Requisitos Previos](#requisitos-previos)
5. [Puesta en Marcha Rápida](#puesta-en-marcha-rápida)
6. [Guía de Uso](#guía-de-uso)
7. [Monitorización](#monitorización)
8. [Roadmap](#roadmap)
9. [Contribuir](#contribuir)
10. [Licencia](#licencia)

---

## 🎯 Objetivos

- **Conectar** múltiples fuentes de datos relacionales y APIs.
- **Orquestar** procesos ETL/ELT con distintas herramientas de orquestacion
- **Procesar** grandes volúmenes mediante PySpark.
- **Almacenar** datos transformados en un _data warehouse_.
- **Catalogar** y **documentar** datos con DataHub.
- **Monitorear** servicios vía Prometheus.

## 🛠️ Stack Tecnológico

<div align="center">
  <img src="Arquitectura Pipeline de datos.drawio.svg" alt="Arquitectura de Datos" width="100%"/>
</div>

## 📂 Estructura del Repositorio

```text
.
├── data_sources/
├── loaders/
├── orchestrator/
│   ├── airflow/
│   └── prefect-platform/
├── processing/
├── data_warehouse/
├── data_catalog/
└── storage/
```

## 💻 Requisitos Previos

- Docker 24+ y **Docker Compose v2**
- Git
- 8 GB de RAM (16 GB recomendado)
- Linux (desarrollado y probado sobre **Ubuntu Server 24.04 LTS**)

## ⚡ Puesta en Marcha Rápida

> **Tip:** Ejecuta cada bloque dentro del directorio raíz del proyecto.

1. **Clona el repositorio**

```bash
git clone https://github.com/developer-jv/bi_projects.git
cd bi_projects
```

2. **Levanta los servicios** (≈5‑8 min)

En cada herramienta utilizada encontraras un archivo .md con insttrucciones de como levantar la herramienta.

## 🛣️ Roadmap

-

## 🤝 Contribuir

1. Haz un **fork** del repositorio.
2. Crea tu rama (`git checkout -b feature/nueva-feature`).
3. Realiza _commit_ de tus cambios (`git commit -m 'Añadir nueva feature'`).
4. Haz _push_ a la rama (`git push origin feature/nueva-feature`).
5. Abre un **Pull Request**.

¡Toda sugerencia es bienvenida!

## 📜 Licencia

Distribuido bajo licencia **MIT**. Consulta el archivo `LICENSE` para más detalles.

---

> Elaborado con ❤️ por **Javier Valdez** > [LinkedIn](https://www.linkedin.com/in/javier-valxdez-one/)
