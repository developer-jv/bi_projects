USE erp;


-- Inserciones nuevas
INSERT INTO customers (customer_code, full_name, email) VALUES
('CUST-0004','Diana Prince','diana@example.com');


INSERT INTO orders (customer_id, order_ts, status, amount, currency) VALUES
(4, NOW(3), 'CREATED', 199.99, 'USD');


-- Actualizaciones
UPDATE orders SET status='PAID' WHERE order_id = 1;
UPDATE customers SET email='alice+new@example.com' WHERE customer_id = 1;


-- Borrado lógico
UPDATE customers SET is_active=0 WHERE customer_id = 2;


-- Borrado físico de una orden (para ver tombstones según configuración)
DELETE FROM orders WHERE order_id = 3;