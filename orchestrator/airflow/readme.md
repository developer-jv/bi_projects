# Detén lo que quede vivo y borra contenedores, redes y volúmenes del stack

Instalacion local de apache airflow para edicion de codigo.

pip install "apache-airflow==3.0.3" \
 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.0.3/constraints-3.9.txt"

# CREACION DE SECRET KEY

SECRET_KEY=$(openssl rand -hex 32)

# CREACION DE FERNET KEY

FERNET_KEY=$(openssl rand -base64 32)

# CREACION DE JWT KEY

JWT_KEY=$(openssl rand -base64 32)

# LEVANTAR EL AMBIENTE

sudo docker compose -f docker-compose.airflow.yml down -v --remove-orphans

sudo docker compose -f docker-compose.airflow.yml run --rm airflow-init

sudo docker compose -f docker-compose.airflow.yml up -d --force-recreate

sudo docker compose -f docker-compose.airflow.yml ps

# VERIFICAR LOG DEL WORKER PARA OBTENER CONTRASEÑA DE ADMIN

sudo docker compose -f docker-compose.airflow.yml logs --tail=100 airflow-api-server | grep -i password

# DEBUGGING

sudo docker compose -f docker-compose.airflow.yml exec airflow-worker printenv AIRFLOW**WEBSERVER**SECRET_KEY

sudo docker compose -f docker-compose.airflow.yml exec airflow-worker printenv AIRFLOW**CORE**FERNET_KEY

for svc in airflow-api-server airflow-scheduler airflow-dag-processor airflow-worker
do
sudo docker compose -f docker-compose.airflow.yml \
 exec $svc printenv AIRFLOW**API**SECRET_KEY
done

for svc in airflow-api-server airflow-scheduler airflow-worker
do
  sudo docker compose -f docker-compose.airflow.yml \
    exec $svc printenv AIRFLOW__API_AUTH__JWT_SECRET
done

# VERIFICAR LOG DEL WORKER

sudo docker compose -f docker-compose.airflow.yml logs --tail=100 airflow-worker
