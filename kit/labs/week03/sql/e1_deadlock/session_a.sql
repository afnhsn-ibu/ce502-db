-- E1 · Deadlock · SESSION A (left terminal) · Read Committed (the default)
-- Run ONE step at a time, in step order, switching terminals as the step numbers say.
-- Do not run this file with \i: copy each step into psql.

-- Step 1
BEGIN;
-- Step 2: A locks row 1
UPDATE acc SET bal = bal - 10 WHERE id = 1;
-- Step 4: A asks for row 2, which B holds. A now WAITS (psql seems to hang).
UPDATE acc SET bal = bal + 10 WHERE id = 2;
-- After step 5 (about 1 second later, deadlock_timeout) PostgreSQL finds the cycle A -> B -> A.
-- Usually A is the victim, because A has waited longest and its deadlock check runs first:
--   ERROR:  deadlock detected
--   DETAIL: Process ... waits for ShareLock on transaction ...; blocked by process ...
-- Step 6
ROLLBACK;   -- if A was the victim (its transaction is aborted). If A survived instead: COMMIT;
SELECT * FROM acc ORDER BY id;
