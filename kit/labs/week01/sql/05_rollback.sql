-- CE 502 · Practice 1 · Part C · Steps 5-6: a transaction that fails half-way
-- One order = 1) take one cable from stock, 2) charge the customer 25.00, 3) record the order.
-- Step 3 fails (customer_id is missing), so the whole unit of work must disappear.
-- Run inside psql:   \i /kit/labs/week01/sql/05_rollback.sql

\set ON_ERROR_STOP off
\echo '--- Before ---'
SELECT s.qty AS stock_qty, c.balance AS customer_balance, (SELECT count(*) FROM orders) AS orders
FROM stock s, customer c WHERE s.item = 500 AND c.id = 1;

BEGIN;
UPDATE stock    SET qty = qty - 1            WHERE item = 500;
UPDATE customer SET balance = balance - 25   WHERE id = 1;
\echo '--- Inside the transaction, after two successful updates ---'
SELECT s.qty AS stock_qty, c.balance AS customer_balance
FROM stock s, customer c WHERE s.item = 500 AND c.id = 1;

INSERT INTO orders VALUES (1, NULL);          -- ERROR: not-null violation on customer_id
SELECT 1;                                     -- ERROR: current transaction is aborted
ROLLBACK;

\echo '--- After ROLLBACK ---'
SELECT s.qty AS stock_qty, c.balance AS customer_balance, (SELECT count(*) FROM orders) AS orders
FROM stock s, customer c WHERE s.item = 500 AND c.id = 1;
\echo 'Stock and balance are unchanged: none of the three steps was kept.'
\set ON_ERROR_STOP on
