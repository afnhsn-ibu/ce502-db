-- CE 502 · Practice 1 · Part B · Step 4b: checkpoints and full-page writes (FPW)
-- After a checkpoint, the FIRST change to a page writes a copy of the whole 8 kB page into the log
-- (protection against "torn pages"). Later changes to the same page log only the change itself.
-- Run inside psql:   \i /kit/labs/week01/sql/04_checkpoint_fpw.sql

SHOW full_page_writes;
VACUUM lab1;   -- tidy the pages first, so the next records show only our updates
CHECKPOINT;

SELECT pg_current_wal_lsn() AS a \gset
UPDATE lab1 SET v = 'y' WHERE id = 2;      -- first change to this page since the checkpoint
SELECT pg_current_wal_lsn() AS b \gset
UPDATE lab1 SET v = 'z' WHERE id = 3;      -- same page (rows 2 and 3 share page 0), changed again
SELECT pg_current_wal_lsn() AS c \gset

SELECT pg_wal_lsn_diff(:'b', :'a') AS bytes_first_update_after_checkpoint,
       pg_wal_lsn_diff(:'c', :'b') AS bytes_second_update_same_page,
       (SELECT ctid FROM lab1 WHERE id = 2) AS row2_location,
       (SELECT ctid FROM lab1 WHERE id = 3) AS row3_location;

\echo ''
\echo 'To see the two records, run in your second terminal:'
\echo '  docker exec -u postgres ce502-postgres bash /kit/labs/week01/scripts/04_waldump_range.sh' :a :c
\echo 'Look for "FPW" in the first UPDATE record and its absence in the second.'
