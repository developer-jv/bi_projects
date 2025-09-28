FROM mysql:8.0


# Configuración MySQL preparada para Debezium
COPY my.cnf /etc/mysql/conf.d/my.cnf


# Scripts de inicialización (se ejecutan solo si el datadir está vacío)
COPY init/ /docker-entrypoint-initdb.d/


# Scripts de demo (no se ejecutan automáticamente)
RUN mkdir -p /opt/demo
COPY demo/03_demo_changes.sql /opt/demo/03_demo_changes.sql


# Permisos y limpieza
RUN chmod -R 755 /etc/mysql/conf.d /docker-entrypoint-initdb.d /opt/demo