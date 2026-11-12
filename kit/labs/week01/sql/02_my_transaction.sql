-- CE 502 · Practice 1 · Part B · Step 4a: one small transaction you will find in the log
-- Run inside psql:   \i /kit/labs/week01/sql/02_my_transaction.sql

BEGIN;
SELECT txid_current()                        AS my_txid,
       pg_walfile_name(pg_current_wal_lsn()) AS wal_file
\gset
UPDATE lab1 SET v = 'x' WHERE id = 1;
COMMIT;

\echo ''
\echo 'Your transaction ID (my_txid):' :my_txid
\echo 'Its records are in WAL file:  ' :wal_file
\echo ''
\echo 'Now open a SECOND terminal and run:'
\echo '  docker exec -u postgres ce502-postgres bash /kit/labs/week01/scripts/03_waldump.sh' :wal_file :my_txid
