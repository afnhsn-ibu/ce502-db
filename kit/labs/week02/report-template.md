# Practice 2 Report · Backup and Restore

**CE 502 · Week 2** · Name: ______________ · Student ID: ______________ · Date: ______________

> One to two pages as PDF, plus your runbook (`runbook-template.md`). Every number needs one sentence that says what it proves.

---

## 1. Part A: backup and restore measurements · 2 points

| Measurement | Your value |
|---|---|
| Database size (`00_create_shop.sql`) | |
| Backup time (`pg_dump -Fc`) | |
| Dump file size | |
| Restore time (`pg_restore` into `shop_restored`) | |

*In 2–4 sentences: why is the dump much smaller than the database? What does that tell you about what a logical backup contains?*

## 2. Part A: row counts before and after · 2 points

| Point in time | Database | Orders | Total amount |
|---|---|---|---|
| After setup | shop | | |
| After the accident | shop | | |
| After restore | shop_restored | | |
| *(optional)* after repair | shop | | |

*One sentence of interpretation: what proves that the restore is complete?*

## 3. RTO and RPO · 2 points

**Measured RTO.** *Restore time from section 1, plus your estimate of the other parts.*

| Part of the recovery | Estimated time |
|---|---|
| Noticing the problem and deciding to restore | |
| Restoring the backup (measured) | |
| Checking the restored copy | |
| Switching the application / copying rows back | |
| **Total RTO** | |

**RPO of a nightly pg_dump.** *State it and explain it with an example: what is lost if the accident happens just before the next backup?*

*In 2–3 sentences: what would you add to reduce the RPO to a few minutes? Use what you learned in Lesson 2-3, or in Part B.*

## 4. Recovery runbook · 2 points

*Attach `runbook-template.md`, filled in: 5–8 numbered steps that a colleague could follow at 3 a.m. without you.*

## 5. Bonus, Part B: point-in-time recovery · +2 points

| Item | Your value |
|---|---|
| Base backup size | |
| Recovery target time | |
| Orders in the recovered server | |
| Recovery time (start + replay) | |

*Paste the recovery lines from the server log ("starting point-in-time recovery", "restored log file", "recovery stopping before commit", "selected new timeline").*

*In 3–5 sentences: why are the 3 orders inserted after the base backup present? Why did the DROP not come back? What is a timeline?*

---

### Declaration

I did this practice myself. Any help (classmates, AI tools, websites) is listed here: ______________
