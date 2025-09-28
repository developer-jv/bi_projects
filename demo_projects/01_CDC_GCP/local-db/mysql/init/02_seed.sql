USE erp;


INSERT INTO customers (customer_code, full_name, email) VALUES
('CUST-0001','Alice Johnson','alice@example.com'),
('CUST-0002','Bob Smith','bob@example.com'),
('CUST-0003','Carlos López','carlos@example.com');


INSERT INTO orders (customer_id, order_ts, status, amount, currency) VALUES
(1, NOW(3), 'CREATED', 120.50, 'USD'),
(1, NOW(3), 'PAID', 89.90, 'USD'),
(2, NOW(3), 'CREATED', 45.00, 'USD'),
(3, NOW(3), 'SHIPPED', 320.00, 'USD');