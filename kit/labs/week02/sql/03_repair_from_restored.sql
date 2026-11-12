-- CE 502 · Practice 2 · Part A · Step 5 (optional): repair shop using only the rows it lost.
-- Instead of replacing the whole database, copy back the deleted rows from shop_restored.
-- Uses dblink, an extension that ships with PostgreSQL, to read from the other database.
-- Run: docker exec -it ce502-postgres psql -U postgres -d shop -f /kit/labs/week02/sql/03_repair_from_restored.sql

CREATE EXTENSION IF NOT EXISTS dblink;

BEGIN;
INSERT INTO orders (id, customer_id, amount, created_at)
SELECT r.id, r.customer_id, r.amount, r.created_at
FROM dblink('dbname=shop_restored user=postgres',
            'SELECT id, customer_id, amount, created_at FROM orders')
     AS r(id int, customer_id int, amount numeric(10,2), created_at timestamptz)
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.id = r.id);
SELECT count(*) AS orders_after_repair, sum(amount) AS total_amount FROM orders;
COMMIT;
\echo 'Any order created AFTER the backup and then deleted could not be recovered this way:'
\echo 'a nightly logical backup has an RPO of up to 24 hours. Part B removes this gap.'
