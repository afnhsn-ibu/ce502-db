# Practice 1 Report · Inside the WAL

**CE 502 · Week 1** · Name: ______________ · Student ID: ______________ · Date: ______________

> At most 4 pages as PDF. Replace every *italic instruction* with your own text. Each number or screenshot needs at least one sentence that says what it shows and which concept it proves.

---

## 1. WAL size vs table size (steps 1–3) · 3 points

| Measurement | Your value |
|---|---|
| LSN before the insert | |
| LSN after the insert | |
| WAL generated | |
| Table size (`pg_relation_size`) | |
| Index size (`pg_indexes_size`) | |
| Ratio WAL / (table + index) | |

*Explain in 5–8 sentences why the log is larger than the data. Name at least two reasons: record headers, index records, full-page images. Then explain why a DBMS accepts this cost, using the write-ahead rule and the needs of recovery.*

## 2. Your transaction in the log (step 4a) · 2 points

*Insert a screenshot of the `03_waldump.sh` output for your transaction ID.*

| Record | rmgr | What it describes (in your words) |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |

*In 2–3 sentences: which record makes the transaction durable, and why is it written last?*

## 3. A full-page image after CHECKPOINT (step 4b) · 2 points

*Insert a screenshot of the `04_waldump_range.sh` output with the `FPW` record visible.*

| | Bytes of WAL |
|---|---|
| First update after the checkpoint | |
| Second update, same page | |

*Explain in 4–6 sentences why the first number is about 8 kB and the second under 200 bytes. Use the terms checkpoint, torn page and full-page image.*

## 4. ROLLBACK left no changes (steps 5–6) · 1 point

*Insert a screenshot showing stock quantity, customer balance and order count before the transaction, inside it, and after ROLLBACK.*

## 5. What recovery does after a crash before ROLLBACK · 2 points

*Suppose the server crashed after the two UPDATEs of step 5, before ROLLBACK, and one changed page had already been written to disk. In 6–10 sentences, describe what PostgreSQL finds in the log at restart and what it does. Use: checkpoint, redo, undo (or "not committed"), COMMIT record, atomicity. You may note that PostgreSQL marks the transaction as aborted rather than physically undoing the page, because its row versions carry the transaction ID. Explaining this correctly earns full credit.*

---

### Optional: extension results (not marked)

*Results of `06_autocommit_savepoint.sql` and/or `commit_cost.py`, with one sentence each.*

### Declaration

I did this practice myself. Any help (classmates, AI tools, websites) is listed here: ______________
