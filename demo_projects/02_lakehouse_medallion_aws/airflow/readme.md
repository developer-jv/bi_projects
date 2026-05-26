# Airflow del Proyecto

Esta carpeta es una copia versionable del stack de Airflow del proyecto.
No se levanta automaticamente como parte de esta fase.

## Uso futuro
1. Copia `.env.example` a `.env`
2. Copia `.env.airflow.example` a `.env.airflow`
3. Copia `../.env.example` a `../.env` y completa tus credenciales AWS
4. Ejecuta `docker compose -f docker-compose.airflow.yml up -d --build`
