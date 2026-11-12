-- E2 · Non-repeatable read · SESSION A. Run it twice: first with READ COMMITTED, then with REPEATABLE READ.
-- Step 1
BEGIN ISOLATION LEVEL READ COMMITTED;        -- second run: REPEATABLE READ
-- Step 2
SELECT bal FROM acc WHERE id = 1;            -- 100
-- Step 4
SELECT bal FROM acc WHERE id = 1;            -- READ COMMITTED: 500 (changed!)   REPEATABLE READ: 100
-- Step 5
COMMIT;
