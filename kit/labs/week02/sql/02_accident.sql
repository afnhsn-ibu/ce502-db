-- CE 502 · Practice 2 · Part A · Step 2: the accident
-- A script meant for a test database runs against production and deletes half the orders.
-- Run: docker exec -it ce502-postgres psql -U postgres -d shop -f /kit/labs/week02/sql/02_accident.sql

SELECT count(*) AS orders_before FROM orders;
DELETE FROM orders WHERE id % 2 = 0;
SELECT count(*) AS orders_after FROM orders;
\echo 'Half of the orders are gone, and the DELETE was committed (autocommit). Now restore.'
