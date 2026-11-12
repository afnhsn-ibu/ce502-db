-- E5 (optional extension) · Write skew · SESSION B

-- Step 1
BEGIN ISOLATION LEVEL REPEATABLE READ;       -- same level as session A
-- Step 3
SELECT sum(bal) FROM acc;                    -- 200
-- Step 5
UPDATE acc SET bal = 0 WHERE id = 2;
-- Step 7
COMMIT;   -- SERIALIZABLE: ERROR: could not serialize access due to read/write dependencies
          --               among transactions (SQLSTATE 40001)
