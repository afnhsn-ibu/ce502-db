-- Replication demo · run on the PRIMARY:
--   docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week02/replication-demo/01_primary_status.sql
-- One row per connected standby. sent_lsn -> write_lsn -> flush_lsn -> replay_lsn is the log's journey.
SELECT application_name, client_addr, state, sync_state,
       sent_lsn, write_lsn, flush_lsn, replay_lsn,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS replay_gap,
       replay_lag
FROM pg_stat_replication;
SHOW synchronous_standby_names;
