# Practice 1 · Inside the WAL: Watch the Log at Work

**CE 502 · Week 1** · Individual · about 90 minutes · 10 points
**Lessons:** 1-3 Transaction Logging, 1-4 Transaction Control
**Submit:** one PDF report, at most 4 pages, before the Week 2 lesson. Use `report-template.md`.

In Lesson 1-3 you learned that every change is written to the transaction log *before* it reaches the data files, and that COMMIT means "the log records are safely on disk". In this practice you will see this happen in a real DBMS. PostgreSQL calls its transaction log the **write-ahead log (WAL)**.

| Part | Steps | What you do | Lesson objective |
|---|---|---|---|
| A | 1–3 | Measure how much log a bulk insert of 100,000 rows produces, and compare it with the table | 1-3 O1, O2 |
| B | 4 | Find your own transaction and its COMMIT record in the binary log; see a full-page image after a checkpoint | 1-3 O3, O4 |
| C | 5–6 | Run an order that fails half-way inside `BEGIN … ROLLBACK` and prove that nothing remains | 1-4 O2, O3 |
| Extension | – | Autocommit vs SAVEPOINT; the cost of a COMMIT measured in Python (optional, no extra points) | 1-4 O3, O4 |

---

## Before you start

1. Finish `setup/SETUP.md` (Docker installed, container built and **healthy**).
2. From the kit's root folder, check the container:

   ```bash
   docker compose up -d
   docker exec -u postgres ce502-postgres bash /kit/setup/check_setup.sh
   ```

   Every line should say `[ OK ]`.
3. You need **two terminals**:
   - **Terminal 1, psql:** `docker exec -it ce502-postgres psql -U postgres -d lab`
   - **Terminal 2, container shell commands:** you run single `docker exec …` commands here.

All commands in this file can be copied. Do not retype them from the slides.

> **How the kit is reached from inside the container.** The kit folder is mounted read-only at `/kit`. In psql, `\i /kit/labs/week01/sql/00_setup.sql` runs a script. In terminal 2, `docker exec -u postgres ce502-postgres bash /kit/labs/week01/scripts/<script>.sh` runs a shell script as the `postgres` user.

### Setup (2 minutes)

In terminal 1 (psql):

```sql
\i /kit/labs/week01/sql/00_setup.sql
```

This creates four tables:

- `lab1(id, v)`: empty, for Parts A and B.
- `stock(item, name, qty)`: one row, item 500 with quantity 20.
- `customer(id, name, balance)`: one row, customer 1 with balance 100.00.
- `orders(id, customer_id NOT NULL, item, amount)`: empty.

You can run the setup again at any time to start over.

---

## Part A · Steps 1–3 · Measure how much log an insert produces (25 min)

**Step 1. Note the current position in the log.** Every byte of WAL has an address called the **log sequence number (LSN)**, written as two hexadecimal numbers such as `0/192CAD8`. In psql:

```sql
SELECT pg_current_wal_lsn();
```

Copy the value that **your** query printed. You will need it in step 3.

**Step 2. Insert 100,000 rows.**

```sql
INSERT INTO lab1 SELECT g, md5(g::text) FROM generate_series(1, 100000) g;
```

**Step 3. Compare the WAL produced with the size of the table.** Replace `0/192CAD8` with **your** LSN from step 1:

```sql
SELECT pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), '0/192CAD8')) AS wal_generated;
SELECT pg_size_pretty(pg_relation_size('lab1')) AS table_size,
       pg_size_pretty(pg_indexes_size('lab1'))  AS index_size;
```

> **Common mistake:** pasting the example LSN from the slide or this README. Use the value that **your** step 1 printed. Otherwise the difference measures the wrong part of the log and is meaningless.

**Check your result with the script.** It repeats steps 1–3 automatically. It stores the LSNs in psql variables with `\gset`, so nothing is copied by hand:

```sql
\i /kit/labs/week01/sql/01_measure_wal.sql
```

Expected output (your numbers will be close, not identical):

```
WAL position before the insert: 0/192CAD8
INSERT 0 100000
WAL position after the insert:  0/28AD420
 wal_generated | table_size | index_size | wal_to_data_ratio
---------------+------------+------------+-------------------
 16 MB         | 6672 kB    | 2208 kB    |              1.79
```

**What to think about for the report.** The log is larger than the table and its index together. Look at these possible reasons:

- Each inserted row is logged with a **record header**: the transaction ID, the LSN of the previous record and a CRC checksum.
- The **index** changes are logged as well.
- After the checkpoint, the first change to every page is logged as a **full-page image**, which you will see in Part B.

Which of these explain the extra volume? Why is it worth paying this price? Think of the write-ahead rule and of what recovery needs.

---

## Part B · Step 4 · Read the log (25 min)

### 4a. Find your own transaction and its COMMIT record

In terminal 1 (psql):

```sql
\i /kit/labs/week01/sql/02_my_transaction.sql
```

The script runs this transaction:

```sql
BEGIN;
SELECT txid_current() AS my_txid,
       pg_walfile_name(pg_current_wal_lsn()) AS wal_file;
UPDATE lab1 SET v = 'x' WHERE id = 1;
COMMIT;
```

It prints your transaction ID, the WAL file that holds its records, and the exact command to run next, for example:

```
Your transaction ID (my_txid): 741
Its records are in WAL file:   000000010000000000000002
Now open a SECOND terminal and run:
  docker exec -u postgres ce502-postgres bash /kit/labs/week01/scripts/03_waldump.sh 000000010000000000000002 741
```

Copy that command into terminal 2. The script calls **pg_waldump**, PostgreSQL's tool for turning the binary log into readable lines. `-x 741` keeps only the records of transaction 741:

```bash
pg_waldump -x 741 $PGDATA/pg_wal/000000010000000000000002
```

> **Key point:** use **your** transaction ID and **your** WAL file name. Filter with `pg_waldump -x <txid>`, not `grep 'tx: 742'`. pg_waldump pads the number with spaces (`tx:        741`), so a grep for `tx: 742` finds nothing.

Expected output (lines shortened):

```
rmgr: Heap        len (rec/tot):  54/  54, tx: 741, lsn: 0/028AD420, prev 0/028AD3F8, desc: LOCK xmax: 741, off: 1 ... blk 0
rmgr: Heap        len (rec/tot):  80/  80, tx: 741, lsn: 0/028AD458, prev 0/028AD420, desc: UPDATE old_off: 1 ... new_off: 41 ... blk 833, ... blk 0
rmgr: Btree       len (rec/tot):  64/  64, tx: 741, lsn: 0/028AD4A8, prev 0/028AD458, desc: INSERT_LEAF off: 3 ... blk 1
rmgr: Transaction len (rec/tot):  34/  34, tx: 741, lsn: 0/028AD4E8, prev 0/028AD4A8, desc: COMMIT 2026-10-25 23:49:04.143814 CET
```

**How to read one record.** Compare these fields with the log record fields from Lesson 1-3:

| Field | Meaning | Lesson 1-3 field |
|---|---|---|
| `rmgr` | Resource manager: the part of the DBMS that wrote the record (Heap = table rows, Btree = index, Transaction = commit/abort) | Type of record |
| `len (rec/tot)` | Size of the record; `tot` includes any page image | – |
| `tx` | Transaction ID | Transaction ID |
| `lsn` | Address of this record in the log | Log sequence number |
| `prev` | Address of the previous record **in the log as a whole**, not necessarily of the same transaction | Link to the previous record |
| `desc` | What changed: operation, offsets, and `blkref` = which file (`rel`) and page (`blk`) | Operation, object, before/after information |

**What to think about for the report.**

- The UPDATE wrote **four** records. What does each one describe?
- Why is there a Btree record, although you did not change the key? Hint: the new row version went to a different page (`blk 833`), so the index must point to it.
- Which record makes the transaction durable?

### 4b. See a full-page image after a checkpoint

In terminal 1 (psql):

```sql
\i /kit/labs/week01/sql/04_checkpoint_fpw.sql
```

The script runs `VACUUM` and `CHECKPOINT`, then updates row 2 and then row 3. Both rows are on page 0. It measures the log written by each update:

```
 bytes_first_update_after_checkpoint | bytes_second_update_same_page
-------------------------------------+-------------------------------
                                8232 |                           200
```

It then prints a command for terminal 2, for example:

```bash
docker exec -u postgres ce502-postgres bash /kit/labs/week01/scripts/04_waldump_range.sh 0/28FBF70 0/28FE060
```

Expected output (shortened):

```
rmgr: Heap  len (rec/tot): 65/8165, tx: 764, ... desc: HOT_UPDATE old_off: 121 ... new_off: 123, blkref #0: ... blk 0 FPW
rmgr: Transaction len (rec/tot): 34/34, tx: 764, ... desc: COMMIT ...
rmgr: Heap2 len (rec/tot): 61/61, tx: 0, ... desc: PRUNE ...
rmgr: Heap  len (rec/tot): 68/  68, tx: 765, ... desc: HOT_UPDATE old_off: 122 ... new_off: 121, blkref #0: ... blk 0
rmgr: Transaction len (rec/tot): 34/34, tx: 765, ... desc: COMMIT ...
```

The first UPDATE after the checkpoint ends with **FPW** (full-page write). Its total length is about 8 kB, because it carries a copy of the whole page. The second UPDATE to the same page has no FPW and is under 100 bytes.

**Why.** A page is 8 kB, but a disk may write it in smaller pieces. If the power fails in the middle, the page on disk is **torn**: half old, half new. A small change record cannot repair a torn page. After every checkpoint, PostgreSQL therefore logs a full copy of each page the first time that page changes. Recovery starts at the checkpoint, writes this clean copy back first, and then applies the later, small records. This links to Lesson 1-3 O4: checkpoints decide **where recovery starts**, and full-page images make sure it has a clean page to start from.

**Optional.** To see which parts of the DBMS wrote the most log in a file, run `scripts/05_wal_stats.sh <wal_file>`.

---

## Part C · Steps 5–6 · Break a transaction (20 min)

One order in our tiny shop is a **logical unit of work** of three steps:

1. take one cable (item 500) out of `stock`;
2. charge customer 1 the price of 25.00;
3. record the order in `orders`.

Step 3 will fail, because the program "forgot" the customer ID and `customer_id` is `NOT NULL`.

**Step 5. Run the transaction by hand** in terminal 1:

```sql
SELECT qty FROM stock WHERE item = 500;          -- 20
SELECT balance FROM customer WHERE id = 1;       -- 100.00

BEGIN;
UPDATE stock    SET qty = qty - 1          WHERE item = 500;
UPDATE customer SET balance = balance - 25 WHERE id = 1;
SELECT qty FROM stock WHERE item = 500;          -- 19: visible inside the transaction
INSERT INTO orders VALUES (1, NULL);             -- ERROR: not-null violation
SELECT 1;                                        -- ERROR: current transaction is aborted
```

After the error, PostgreSQL refuses every further command in this transaction. You must end it.

**Step 6. Roll back and prove that nothing remains:**

```sql
ROLLBACK;
SELECT * FROM stock WHERE item = 500;            -- qty 20
SELECT * FROM customer WHERE id = 1;             -- balance 100.00
SELECT count(*) FROM orders;                     -- 0
```

**Check your result with the script:** `\i /kit/labs/week01/sql/05_rollback.sql`. It runs the same steps and prints the state before, inside and after the transaction:

```
--- Before ---                      stock_qty 20 | customer_balance 100.00 | orders 0
--- Inside the transaction ---      stock_qty 19 | customer_balance  75.00
ERROR:  null value in column "customer_id" of relation "orders" violates not-null constraint
ERROR:  current transaction is aborted, commands ignored until end of transaction block
ROLLBACK
--- After ROLLBACK ---              stock_qty 20 | customer_balance 100.00 | orders 0
```

**What to think about for the report.** Suppose the server **crashed** after the two UPDATEs and before your ROLLBACK, and some changed pages had already been written to disk. What would recovery find in the log for this transaction? No COMMIT record. What would it do with those pages? Use the words *undo*, *atomicity* and *log* in your answer.

---

## Extension (optional, no extra points)

### Autocommit and SAVEPOINT

```sql
\i /kit/labs/week01/sql/06_autocommit_savepoint.sql
```

1. **Autocommit:** the same three steps without `BEGIN`. Each statement commits on its own, so after the failed INSERT the customer has paid and the stock is lower, but there is **no order**. This is exactly the inconsistency a transaction prevents.
2. **SAVEPOINT:** the failed INSERT is undone with `ROLLBACK TO SAVEPOINT`, a corrected INSERT follows, and all three steps commit together.

### What does a COMMIT cost? (Python)

At every COMMIT the DBMS must flush the log buffer to disk before it reports success. The script inserts 2,000 rows three ways and measures the time and the WAL produced. Run it from your laptop, not inside the container:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r setup/requirements.txt
python labs/week01/python/commit_cost.py
```

Example result:

```
Method                                             time            speed           log
1. COMMIT after every row                       1.519 s       1316 rows/s      348.6 kB WAL
2. one transaction, one COMMIT                  0.202 s       9902 rows/s      270.3 kB WAL
3. COMMIT every row, synchronous_commit=off     0.574 s       3485 rows/s      346.6 kB WAL
```

Explain the difference between methods 1 and 2 using the write-ahead rule. Then consider method 3: what could be lost in a crash, and for which kind of data would you accept that?

---

## What to submit

Fill in `report-template.md` and export it to PDF (at most 4 pages). It is marked out of 10:

| Deliverable | Points |
|---|---|
| WAL size vs table size, with your explanation (steps 1–3) | 3 |
| Screenshot of your transaction and its COMMIT record (step 4) | 2 |
| Screenshot of a full-page image after CHECKPOINT (step 4) | 2 |
| Evidence that ROLLBACK left no changes (steps 5–6) | 1 |
| Explanation: what recovery does after a crash before ROLLBACK | 2 |
| **Total** | **10** |

Most points go to **explanations**, not screenshots. Link every result to a concept from Lessons 1-3 and 1-4.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `pg_waldump: error: could not find file …` | Use the WAL file name printed by **your** `02_my_transaction.sql`. If a lot of time has passed, the file may have been recycled; run the script again. |
| pg_waldump prints nothing for your transaction | You used a transaction ID from another run. Run `02_my_transaction.sql` again and use the new values. |
| `invalid record length at …` at the end of the output | Normal. pg_waldump reached the unfinished end of the current WAL file. |
| No `FPW` in step 4b | Run `04_checkpoint_fpw.sql` again. Another session may have changed the page between the CHECKPOINT and your UPDATE. Also check `SHOW full_page_writes;` (must be `on`). |
| `relation "lab1" does not exist` | Run `\i /kit/labs/week01/sql/00_setup.sql` first. |
| psql shows `lab=!#` | Your transaction is aborted after an error. Type `ROLLBACK;`. |
| Python: `connection refused` | The container is not running, or port 5432 is taken by a local PostgreSQL. See `setup/SETUP.md`. |

## Clean up

Nothing is required. To start again: `\i /kit/labs/week01/sql/00_setup.sql`. To reset the whole container: `docker compose down -v` and then `docker compose up -d`.
