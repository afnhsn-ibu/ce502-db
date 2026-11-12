-- Replication demo · run on the REPLICA after promoting it: it is now a primary and accepts writes.
--   docker exec -it ce502-replica psql -U postgres -d lab -f /kit/labs/week02/replication-demo/08_after_failover.sql
SELECT pg_is_in_recovery() AS still_standby;                   -- false: promoted
INSERT INTO repl_demo (note) VALUES ('written on the NEW primary after failover');
SELECT * FROM repl_demo ORDER BY id;
