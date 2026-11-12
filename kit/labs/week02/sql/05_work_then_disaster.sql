-- CE 502 · Practice 2 · Part B · Step 2: new work after the backup, a target time, then a disaster.
-- Run: docker exec -it ce502-postgres psql -U postgres -d shop -f /kit/labs/week02/sql/05_work_then_disaster.sql

-- New orders arrive AFTER the base backup. A nightly dump would lose them; PITR will not.
INSERT INTO orders (customer_id, amount) VALUES (1, 111.11), (2, 222.22), (3, 333.33);
SELECT count(*) AS orders_now, max(id) AS newest_order FROM orders;

SELECT pg_sleep(2);
SELECT to_char(now(), 'YYYY-MM-DD HH24:MI:SS TZ') AS target_time \gset
\echo ''
\echo '>>> RECOVERY TARGET TIME (copy this exactly):' :target_time
\echo ''
SELECT pg_sleep(2);

DROP TABLE orders;                       -- the disaster
\echo 'orders has been dropped.'
SELECT pg_switch_wal();                  -- close the current WAL file so it is archived now
SELECT pg_sleep(2);
\echo 'Next: bash /kit/labs/week02/scripts/06_pitr_restore.sh "<target time>"'
