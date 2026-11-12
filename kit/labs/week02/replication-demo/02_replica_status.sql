-- Replication demo · run on the REPLICA:
--   docker exec -it ce502-replica psql -U postgres -d lab -f /kit/labs/week02/replication-demo/02_replica_status.sql
SELECT pg_is_in_recovery()                    AS is_standby,
       pg_last_wal_receive_lsn()              AS received_up_to,
       pg_last_wal_replay_lsn()               AS replayed_up_to,
       pg_last_xact_replay_timestamp()        AS last_replayed_commit,
       CASE WHEN pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn() THEN interval '0'
            ELSE now() - pg_last_xact_replay_timestamp() END AS approx_lag;
