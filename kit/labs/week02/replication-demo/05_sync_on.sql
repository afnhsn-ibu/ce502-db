-- Replication demo · run on the PRIMARY: make replication SYNCHRONOUS.
-- A COMMIT now waits until replica1 has the commit record on disk.
--   docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week02/replication-demo/05_sync_on.sql
ALTER SYSTEM SET synchronous_standby_names = 'replica1';
SELECT pg_reload_conf();
SELECT pg_sleep(1);
SELECT application_name, sync_state FROM pg_stat_replication;   -- sync_state is now "sync"
