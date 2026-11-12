-- E4 · Phantom read · SESSION A
-- Step 1
BEGIN ISOLATION LEVEL READ COMMITTED;        -- second run: REPEATABLE READ
-- Step 2
SELECT count(*) FROM acc WHERE bal >= 100;   -- 2 rows
-- Step 4
SELECT count(*) FROM acc WHERE bal >= 100;   -- READ COMMITTED: 3 (a phantom row appeared)   REPEATABLE READ: 2
-- Step 5
COMMIT;
