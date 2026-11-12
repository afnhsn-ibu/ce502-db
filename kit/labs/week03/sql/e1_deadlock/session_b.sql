-- E1 · Deadlock · SESSION B (right terminal)

-- Step 1
BEGIN;
-- Step 3: B locks row 2
UPDATE acc SET bal = bal - 10 WHERE id = 2;
-- Step 5: B asks for row 1, which A holds -> wait cycle (deadlock).
-- When PostgreSQL aborts A, B's UPDATE goes through and prints UPDATE 1.
UPDATE acc SET bal = bal + 10 WHERE id = 1;
-- Step 6 (after A's error)
COMMIT;     -- if B survived. If B was the victim instead: ROLLBACK;
SELECT * FROM acc ORDER BY id;   -- B's transfer is visible: row 1 = 110, row 2 = 90
