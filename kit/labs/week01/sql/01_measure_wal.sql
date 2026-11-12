-- CE 502 · Practice 1 · Part A · Steps 1-3 (checking script)
-- Do the steps BY HAND first, as shown in the README. Then run this script to check your result.
-- It stores the LSNs in psql variables (\gset), so there is nothing to copy by hand.
-- Run inside psql:   \i /kit/labs/week01/sql/01_measure_wal.sql

TRUNCATE lab1;
CHECKPOINT;   -- start from a clean point so every run gives comparable numbers

SELECT pg_current_wal_lsn() AS lsn_before \gset
\echo 'WAL position before the insert:' :lsn_before

INSERT INTO lab1 SELECT g, md5(g::text) FROM generate_series(1, 100000) AS g;

SELECT pg_current_wal_lsn() AS lsn_after \gset
\echo 'WAL position after the insert: ' :lsn_after

SELECT pg_size_pretty(pg_wal_lsn_diff(:'lsn_after', :'lsn_before')) AS wal_generated,
       pg_size_pretty(pg_relation_size('lab1'))                      AS table_size,
       pg_size_pretty(pg_indexes_size('lab1'))                       AS index_size,
       round(pg_wal_lsn_diff(:'lsn_after', :'lsn_before')
             / (pg_relation_size('lab1') + pg_indexes_size('lab1'))::numeric, 2)
                                                                     AS wal_to_data_ratio;
-- Report: explain why the WAL volume is larger than the table on its own.
