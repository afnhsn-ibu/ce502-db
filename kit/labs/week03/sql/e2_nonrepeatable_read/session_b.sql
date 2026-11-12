-- E2 · Non-repeatable read · SESSION B
-- Step 3  (autocommit: committed immediately)
UPDATE acc SET bal = 500 WHERE id = 1;
