-- Replication demo · run on the PRIMARY: a mistake. Then check the replica with 04_read_on_replica.sql.
--   docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week02/replication-demo/07_mistake_on_primary.sql
DELETE FROM repl_demo;
SELECT count(*) AS rows_left_on_primary FROM repl_demo;
\echo 'Within a second the replica has replayed the same DELETE. Replication copies mistakes too:'
\echo 'it protects against a failed SERVER, not against a wrong COMMAND. Only a backup can undo this.'
