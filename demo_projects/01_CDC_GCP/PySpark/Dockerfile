FROM bitnami/spark:3.5.1

USER root

# Instala Python3 y pip
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Normaliza finales de línea (Windows -> Linux) por si copiaste con CRLF
RUN mkdir -p /opt/app
COPY app/ /opt/app/
RUN sed -i 's/\r$//' /opt/app/*.py

# Dependencias Python
RUN pip3 install --no-cache-dir -r /opt/app/requirements.txt

# Señala a Spark qué intérprete usar
ENV PYSPARK_PYTHON=/usr/bin/python3 \
    PYSPARK_DRIVER_PYTHON=/usr/bin/python3

USER 1001
