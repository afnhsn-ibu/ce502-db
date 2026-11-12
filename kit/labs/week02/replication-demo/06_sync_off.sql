-- Replication demo · run on the PRIMARY: back to ASYNCHRONOUS replication (the default).
--   docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week02/replication-demo/06_sync_off.sql
ALTER SYSTEM RESET synchronous_standby_names;
SELECT pg_reload_conf();
SELECT pg_sleep(1);
SELECT application_name, sync_state FROM pg_stat_replication;   -- sync_state is "async" again
