-- CE 502 · Practice 1 · Extension (optional): the same order WITHOUT a transaction, and with a SAVEPOINT
-- Run inside psql AFTER 05_rollback.sql:   \i /kit/labs/week01/sql/06_autocommit_savepoint.sql

\set ON_ERROR_STOP off
-- reset the shop
UPDATE stock SET qty = 20 WHERE item = 500;
UPDATE customer SET balance = 100 WHERE id = 1;
DELETE FROM orders;

\echo '===== 1. Autocommit: every statement is its own transaction ====='
UPDATE stock    SET qty = qty - 1          WHERE item = 500;   -- committed immediately
UPDATE customer SET balance = balance - 25 WHERE id = 1;       -- committed immediately
INSERT INTO orders VALUES (1, NULL);                            -- fails on its own
SELECT s.qty AS stock_qty, c.balance AS customer_balance, (SELECT count(*) FROM orders) AS orders
FROM stock s, customer c WHERE s.item = 500 AND c.id = 1;
\echo '-> Inconsistent: the customer paid and stock went down, but there is no order.'

-- reset again
UPDATE stock SET qty = 20 WHERE item = 500;
UPDATE customer SET balance = 100 WHERE id = 1;

\echo '===== 2. SAVEPOINT: undo only part of a transaction ====='
BEGIN;
UPDATE stock    SET qty = qty - 1          WHERE item = 500;
UPDATE customer SET balance = balance - 25 WHERE id = 1;
SAVEPOINT before_order;
INSERT INTO orders VALUES (1, NULL);                            -- fails
ROLLBACK TO SAVEPOINT before_order;                             -- the transaction is usable again
INSERT INTO orders VALUES (1, 1, 500, 25.00);                   -- corrected order
COMMIT;
SELECT s.qty AS stock_qty, c.balance AS customer_balance, (SELECT count(*) FROM orders) AS orders
FROM stock s, customer c WHERE s.item = 500 AND c.id = 1;
\echo '-> Consistent: one cable, one charge, one order. All three were committed together.'
\set ON_ERROR_STOP on
