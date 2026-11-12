-- Replication demo · run on the PRIMARY: write something the replica should receive.
--   docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week02/replication-demo/03_write_on_primary.sql
CREATE TABLE IF NOT EXISTS repl_demo (
    id    serial PRIMARY KEY,
    note  text NOT NULL,
    at    timestamptz NOT NULL DEFAULT now()
);
INSERT INTO repl_demo (note) VALUES ('written on the primary at ' || clock_timestamp()::time(0));
SELECT * FROM repl_demo ORDER BY id;
