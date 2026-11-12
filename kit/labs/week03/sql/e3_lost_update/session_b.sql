-- E3 · Lost update vs serialization failure · SESSION B

-- Step 1
BEGIN ISOLATION LEVEL READ COMMITTED;        -- second run: REPEATABLE READ
-- Step 3
SELECT bal FROM acc WHERE id = 1;            -- the app also sees 100
-- Step 6 (A has committed)
UPDATE acc SET bal = 150 WHERE id = 1;       -- READ COMMITTED: succeeds -> A's +50 is overwritten
                                             -- REPEATABLE READ: ERROR: could not serialize access
                                             --                  due to concurrent update  (SQLSTATE 40001)
-- Step 7
COMMIT;                                      -- after an error PostgreSQL turns this into ROLLBACK
-- Fixes that work even at READ COMMITTED (try them!):
--   UPDATE acc SET bal = bal + 50 WHERE id = 1;          -- the DBMS does the arithmetic
--   SELECT bal FROM acc WHERE id = 1 FOR UPDATE;         -- in step 3: B waits for A, then reads 150
