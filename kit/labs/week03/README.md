# Practice 3 · Race Yourself: Two Sessions, One Database

**CE 502 · Week 3** · Individual · about 60–90 minutes · 10 points
**Lessons:** 3-1 Concurrency Problems, 3-2 Locking and Deadlocks, 3-3 ACID and Isolation Levels
**Submit:** one PDF report, at most 3 pages, before the Week 4 class. Use `report-template.md`.

In Lessons 3-1 to 3-3 you saw schedules on paper. Here you create them yourself: two psql sessions run against the same table and you choose exactly when each statement runs.

| Part | What you do | Lesson objective |
|---|---|---|
| A | Four two-session experiments: deadlock (E1), non-repeatable read (E2), lost update (E3), phantom (E4), at Read Committed and Repeatable Read | 3-1 O3 · 3-2 O4 · 3-3 O2 |
| B | A lost update in Python code with two threads, then two fixes | 3-1 O2 · 3-2 O1 |
| Extension | E5 write skew at Serializable; a retry loop for errors 40001 and 40P01 (optional, no extra points) | 3-3 O3, O4 |

---

## Before you start

```bash
docker compose up -d
docker exec -u postgres ce502-postgres bash /kit/setup/check_setup.sh      # all [ OK ]
```

Open **two terminals side by side**: session **A** on the left and session **B** on the right. In both, run:

```bash
docker exec -it ce502-postgres psql -U postgres -d lab
```

To tell them apart, you can set a prompt in each: `\set PROMPT1 'A %/%R%x%# '` on the left and `\set PROMPT1 'B %/%R%x%# '` on the right.

### How to run an experiment

Each experiment has two files, `sql/eN_…/session_a.sql` and `session_b.sql`. The statements are numbered **Step 1, Step 2, …** across both files. Open both files in an editor on your laptop and copy **one step at a time** into the right terminal, in step order.

> **Critical:** never run a session file as a whole with `\i`. The point is to interleave the two transactions.

**Reset before every experiment**, in either session:

```sql
\i /kit/labs/week03/sql/00_setup.sql
```

```
 id | bal
----+-----
  1 | 100
  2 | 100
```

> **Common mistake:** starting the next experiment while a session still has an open or aborted transaction. The psql prompt shows it: `lab=*#` means a transaction is open, and `lab=!#` means it was aborted by an error. Type `ROLLBACK;` in **both** sessions first. If `00_setup.sql` hangs, the other session still holds a lock.

---

## Part A · Four experiments (40 min)

Expected results (PostgreSQL 16):

| Experiment | Run at | What you should see |
|---|---|---|
| E1 Deadlock | Read Committed | One session gets `ERROR: deadlock detected`; the other finishes |
| E2 Non-repeatable read | RC, then RR | Second read: **500**, then **100** |
| E3 Lost update | RC, then RR | **150** (one +50 lost), then an **error** |
| E4 Phantom | RC, then RR | Count **2 → 3**, then **2 → 2** |

### E1 · Deadlock (`sql/e1_deadlock/`)

A transfers 10 from account 1 to account 2. At the same time, B transfers 10 from account 2 to account 1.

| Step | A | B |
|---|---|---|
| 1 | `BEGIN;` | `BEGIN;` |
| 2 | `UPDATE acc SET bal = bal - 10 WHERE id = 1;` locks row 1 | |
| 3 | | `UPDATE acc SET bal = bal - 10 WHERE id = 2;` locks row 2 |
| 4 | `UPDATE acc SET bal = bal + 10 WHERE id = 2;` **waits** for B | |
| 5 | | `UPDATE acc SET bal = bal + 10 WHERE id = 1;` waits for A: a **cycle** |
| 6 | `ROLLBACK;` (A was the victim) | `COMMIT;` |

About one second after step 5 (`deadlock_timeout`), PostgreSQL checks the waits, finds the cycle A → B → A and aborts one transaction:

```
ERROR:  deadlock detected
DETAIL:  Process 2187 waits for ShareLock on transaction 1043; blocked by process 2190.
Process 2190 waits for ShareLock on transaction 1042; blocked by process 2187.
HINT:  See server log for query details.
CONTEXT:  while updating tuple (0,2) in relation "acc"
```

In PostgreSQL the victim is usually **A**. A has waited longest, so its deadlock check runs first, finds the cycle, and aborts its own transaction. B's UPDATE then goes through. After both sessions finish, the table shows B's transfer only: row 1 = 110 and row 2 = 90.

**Think about it:** what single rule in the application code makes this deadlock impossible? Hint: both transfers lock the same two rows.

### E2 · Non-repeatable read (`sql/e2_nonrepeatable_read/`)

A reads row 1 twice. Between the two reads, B changes it to 500 in autocommit mode.

- **Read Committed:** A's second read shows **500**. Every statement sees the data committed before *that statement* started.
- **Repeatable Read:** A's second read still shows **100**. The whole transaction reads from one **snapshot**, taken at its first query.

Reset and run it twice, changing `READ COMMITTED` to `REPEATABLE READ` in step 1.

### E3 · Lost update (`sql/e3_lost_update/`)

Both sessions play an application that reads the balance, adds 50 *in its own code* and writes the result back:

| Step | A | B |
|---|---|---|
| 1 | `BEGIN ISOLATION LEVEL READ COMMITTED;` | `BEGIN ISOLATION LEVEL READ COMMITTED;` |
| 2–3 | `SELECT bal FROM acc WHERE id = 1;` returns 100 | `SELECT bal FROM acc WHERE id = 1;` returns 100 |
| 4–5 | `UPDATE acc SET bal = 150 WHERE id = 1; COMMIT;` | |
| 6–7 | | `UPDATE acc SET bal = 150 WHERE id = 1; COMMIT;` |
| 8 | `SELECT bal FROM acc WHERE id = 1;` returns **150, not 200** | |

At **Read Committed**, B's UPDATE succeeds and overwrites A's change without any error. One +50 is **lost**.

At **Repeatable Read**, B's UPDATE in step 6 fails:

```
ERROR:  could not serialize access due to concurrent update
```

The row changed after B's snapshot was taken, so PostgreSQL refuses the write (SQLSTATE `40001`) rather than lose an update. B must roll back and run the whole transaction again.

**Two fixes that work even at Read Committed.** Try them after the main runs:

- `UPDATE acc SET bal = bal + 50 WHERE id = 1;` The DBMS reads and writes the row under one lock.
- `SELECT … FOR UPDATE` in step 3. B waits for A's lock, then reads 150.

### E4 · Phantom (`sql/e4_phantom/`)

A counts the accounts with a balance of at least 100. Between two counts, B inserts a third account in autocommit mode.

- **Read Committed:** the count goes **2 → 3**. A new row, a **phantom**, appeared.
- **Repeatable Read:** the count stays **2 → 2**.

The SQL standard *allows* phantoms at Repeatable Read; only Serializable forbids them. PostgreSQL implements Repeatable Read as **snapshot isolation**, which also hides rows inserted after the snapshot. Explaining this difference is report item 3.

---

## Part B · A lost update in Python (15 min)

Two threads ("cashiers") each add 1 to the same balance 200 times, starting from 100, so the correct result is 500. Run this on your **laptop**, not in the container:

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r setup/requirements.txt
python labs/week03/python/lost_update_threads.py
```

```
naive       final balance =  304   expected = 500   lost updates = 196
for_update  final balance =  500   expected = 500   lost updates = 0
atomic      final balance =  500   expected = 500   lost updates = 0
```

| Mode | What each transaction does | Result |
|---|---|---|
| `naive` | `SELECT bal …`, then `UPDATE acc SET bal = <value computed in Python>` | Far below 500. **No error at all**: the lost updates are silent |
| `for_update` | `SELECT bal … FOR UPDATE`, then the same UPDATE | 500: the row lock makes the other thread wait until the first commits |
| `atomic` | `UPDATE acc SET bal = bal + 1 WHERE id = 1` | 500: the read and the write are one statement under one row lock |

Your `naive` number will differ from run to run. Anything well below 500 is the expected result.

The script connects to `postgresql://postgres:lab@localhost:5432/lab`. To use another address, set the `PGDSN` environment variable.

---

## Extension (optional, no extra points)

### E5 · Write skew (`sql/e5_write_skew/`)

The rule is: at least one of the two accounts must keep money, like "at least one doctor must stay on call". Each session checks the rule with `SELECT sum(bal)`, sees 200, and empties a **different** account. Run it at three levels:

| Level | Result |
|---|---|
| Read Committed | Both accounts end at 0. The rule is broken |
| Repeatable Read | Both accounts end at 0. Snapshot isolation does **not** prevent write skew: the two transactions write different rows |
| Serializable | B's COMMIT fails: `could not serialize access due to read/write dependencies among transactions` (40001). Only row 1 is 0 |

This is the anomaly that separates snapshot isolation from true serializability, and the topic of the Ports & Grittner paper.

### Retrying 40001 and 40P01 (`python/retry_demo.py`)

```bash
python labs/week03/python/retry_demo.py
```

```
no retry         final =  204 (expected 300)   40001/40P01 errors =  96   increments given up = 96
with retry loop  final =  300 (expected 300)   40001/40P01 errors =   9   increments given up = 0
```

At Repeatable Read no update is lost silently: a conflicting transaction **fails** instead. The application is responsible for catching the error and running the **whole** transaction again, usually after a short random wait. The script shows that pattern in about 15 lines. It is a good basis for report item 5.

### Self-check: all experiments at once

```bash
python labs/week03/python/run_experiments.py
```

This runs E1–E5 automatically and prints what each session saw. Use it to check your manual results, **after** you have done them by hand.

---

## What to submit

One PDF, at most 3 pages, from `report-template.md`:

| Report item | Points |
|---|---|
| E1: screenshot of the deadlock error; which session was aborted, why the other finished, and how to prevent it | 2 |
| Anomaly table from your own runs: E2, E3, E4 at Read Committed and Repeatable Read | 3 |
| E4 at Repeatable Read: why PostgreSQL showed no phantom, although the standard allows one | 1 |
| Part B: the three final balances; why naive loses updates and why each fix works | 2 |
| How an application should handle `deadlock detected` and `could not serialize access` | 2 |
| **Total** | **10** |

**Key point:** most points are for explanations. Link every observation to a concept from Lessons 3-1 to 3-3.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `00_setup.sql` hangs | The other session holds a lock on `acc`. Type `ROLLBACK;` there. |
| `ERROR: current transaction is aborted, commands ignored until end of transaction block` | An earlier statement failed. Type `ROLLBACK;` and start the experiment again. |
| E1: no deadlock, B simply waits | You ran step 5 before step 4, or skipped step 3. Reset and follow the step numbers exactly. |
| E3 at Repeatable Read: no error | B's transaction started *after* A committed. Both `BEGIN` statements and both SELECTs (steps 1–3) must come before A's UPDATE. |
| Python: `connection refused` | The container is not running, or port 5432 is used by a local PostgreSQL (see `setup/SETUP.md`). |
| Python: `ModuleNotFoundError: psycopg` | Activate your virtual environment and run `pip install -r setup/requirements.txt`. |

## Clean up

Nothing is required. `00_setup.sql` resets the table. The Python scripts recreate `acc` with a single row, so run `00_setup.sql` again before going back to Part A.
