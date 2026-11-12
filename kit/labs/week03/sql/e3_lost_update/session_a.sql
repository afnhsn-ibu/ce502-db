-- E3 · Lost update vs serialization failure · SESSION A
-- The "application" reads the balance, adds 50 in its own code, and writes the result back.
-- Run twice: first READ COMMITTED (the lost update), then REPEATABLE READ (an error instead).
-- Reset with 00_setup.sql between the two runs.

-- Step 1
BEGIN ISOLATION LEVEL READ COMMITTED;        -- second run: REPEATABLE READ
-- Step 2
SELECT bal FROM acc WHERE id = 1;            -- the app sees 100
-- Step 4
UPDATE acc SET bal = 150 WHERE id = 1;       -- the app writes 100 + 50
-- Step 5
COMMIT;
-- Step 8 (after B has finished)
SELECT bal FROM acc WHERE id = 1;            -- READ COMMITTED: 150, not 200 -> one +50 was LOST
