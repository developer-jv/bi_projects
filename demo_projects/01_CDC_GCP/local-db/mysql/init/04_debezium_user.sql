-- Usuario dedicado para Debezium (ajusta la contraseña si lo deseas)
CREATE USER IF NOT EXISTS 'debezium'@'%' IDENTIFIED BY 'dbz_pw_123';


-- Permisos mínimos para CDC con snapshots
GRANT SELECT, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%';
-- Opcionales según estrategia de snapshot (pueden ser útiles):
-- GRANT RELOAD ON *.* TO 'debezium'@'%';
-- GRANT SHOW VIEW ON *.* TO 'debezium'@'%';


GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT, LOCK TABLES ON *.* TO 'debezium'@'%';

FLUSH PRIVILEGES;
