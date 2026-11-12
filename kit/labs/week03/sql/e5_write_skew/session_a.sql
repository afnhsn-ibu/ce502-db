-- E5 (optional extension) · Write skew · SESSION A
-- Rule: at least one of the two accounts must keep a balance > 0 ("one doctor must stay on call").
-- Each transaction checks the rule, then empties a DIFFERENT row. No row is written by both.
-- Run three times: READ COMMITTED, REPEATABLE READ, SERIALIZABLE. Reset with 00_setup.sql each time.

-- Step 1
BEGIN ISOLATION LEVEL REPEATABLE READ;       -- run 1: READ COMMITTED · run 2: REPEATABLE READ · run 3: SERIALIZABLE
-- Step 2
SELECT sum(bal) FROM acc;                    -- 200: "the other account still has money, I may empty mine"
-- Step 4
UPDATE acc SET bal = 0 WHERE id = 1;
-- Step 6
COMMIT;
-- Step 8
SELECT * FROM acc ORDER BY id;               -- READ COMMITTED / REPEATABLE READ: both 0 -> the rule is broken
                                             -- SERIALIZABLE: only row 1 is 0; B was refused (40001)
