# 🚀 Laboratorio de Arquitecturas de Datos Contenerizadas

[![Status](https://img.shields.io/badge/status-lab-orange)](#) [![License](https://img.shields.io/badge/license-MIT-green)](#)

> **Bienvenido**. Este repositorio es un **laboratorio vivo** donde versiono componentes clave de _Business Intelligence_ para reutilizarlos con rapidez en futuros proyectos. Aquí encontrarás la base para levantar entornos de desarrollo local, así como las semillas para QA y Producción en la nube.

---

## 📑 Tabla de Contenidos

1. [Objetivos](#objetivos)
2. [Estructura del Repositorio](#estructura-del-repositorio)
3. [Gestión de Entornos](#gestión-de-entornos)
4. [Requisitos Previos](#requisitos-previos)
5. [Wiki](#wiki)
6. [Contribuir](#contribuir)
7. [Licencia](#licencia)

---

## 🎯 Objetivos

- **Versionar** varias herramientas de inteligencia de datos (ingesta, orquestación, procesamiento, almacenamiento, catálogo y observabilidad).
- Garantizar que los entornos **Dev / QA / Prod** puedan iniciarse en minutos mediante comandos consistentes.
- Servir como referencia rápida durante entrevistas o evaluaciones técnicas.

## 📂 Estructura del Repositorio

```text
.
├── data_sources/      # Fuentes de datos
├── loaders/           # Ingesta EL(T)
├── orchestrator/      # Orquestadores
├── processing/        # Motor de procesamiento distribuido
├── data_warehouse/    # Bases de datos relacionales
├── data_catalog/      # Catálogo de datos
├── terraform/         # Infraestructura como código (próximamente)
└── storage/           # Almacenamiento de objetos
```

## 🧩 Gestión de Entornos

| Entorno  | Propósito                     | Implementación                            | Estado          |
| -------- | ----------------------------- | ----------------------------------------- | --------------- |
| **Dev**  | Desarrollo local reproducible | Contenedores locales                      | ✅ Implementado |
| **QA**   | Pre‑producción & pruebas      | Despliegue en la nube con contenedores    | 🔄 En progreso  |
| **Prod** | Despliegue final escalable    | Plantillas de Infraestructura como Código | 📝 Planificado  |

## 💻 Requisitos Previos

- Motor de contenedores compatible con Compose v2 (24 o superior recomendado)
- Git ≥ 2.40
- 8 GB de RAM (16 GB recomendado)
- Linux/macOS (desarrollado sobre **Ubuntu Server 24.04 LTS**)

## 📖 Wiki

La documentación detallada — guías paso a paso, ejemplos y buenas prácticas — vive en la **[Wiki del proyecto](../../wiki)**. ¡Te invito a consultarla y, si lo deseas, a complementar su contenido!

## 🤝 Contribuir

1. Haz **fork** del repositorio.
2. Crea una rama (`git checkout -b mejora/mi‑aporte`).
3. Realiza _commit_ de tus cambios.
4. Haz _push_ a la rama y abre un **Pull Request**.
   ¡Las mejoras y correcciones son bienvenidas!

## 📜 Licencia

Distribuido bajo licencia **MIT**.

---

> Hecho con ❤️ por **Javier Valdez** · [LinkedIn](https://www.linkedin.com/in/javier-valdez-one/)
