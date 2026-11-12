-- Replication demo · run on the REPLICA: the row is here, but the replica refuses writes.
--   docker exec -it ce502-replica psql -U postgres -d lab -f /kit/labs/week02/replication-demo/04_read_on_replica.sql
\set ON_ERROR_STOP off
SELECT * FROM repl_demo ORDER BY id;
INSERT INTO repl_demo (note) VALUES ('written on the replica?');   -- ERROR: read-only transaction
