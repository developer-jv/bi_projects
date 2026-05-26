#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
AIRFLOW_ENV_FILE="$ROOT/airflow/.env.airflow"

if [ -z "${AWS_ACCESS_KEY_ID:-}" ] || [ -z "${AWS_SECRET_ACCESS_KEY:-}" ]; then
  echo "Exporta AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY antes de ejecutar este script." >&2
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  cp "$ROOT/.env.example" "$ENV_FILE"
fi

if [ ! -f "$AIRFLOW_ENV_FILE" ]; then
  cp "$ROOT/airflow/.env.airflow.example" "$AIRFLOW_ENV_FILE"
fi

echo "Archivos de entorno listos:" 
printf "- %s\n- %s\n" "$ENV_FILE" "$AIRFLOW_ENV_FILE"
