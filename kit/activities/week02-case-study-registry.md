# CE 502 · Week 2 · Lesson 2-3 · Case Study Worksheet
## The University Registry: Design a Backup and Recovery Strategy

**Objective:** 2-3 · O4 – design and test a backup and recovery strategy for given requirements
**Work in pairs · 8 minutes in class** (finish the schedule table at home if needed)
**Names:** ______________________ · ______________________

---

### The situation

The registry database holds **20 years of grades for 15,000 students**. It is **400 GB**. During exam weeks it changes all day as lecturers enter grades; in summer it changes very little.

The rector's office says:

> "We can accept losing **at most 5 minutes** of grade entries, and the system must be **back within 1 hour**."

The budget allows **one extra server** and **off-site cloud storage**.

Useful slides: *RPO and RTO* (l23-rporto), *How Each Technique Changes RPO and RTO* (l23-rposcen), *Designing a Strategy* (l23-design), and from Lesson 2-1 *Full, Differential and Incremental* and *Storing Backups Safely*.

---

### Question 1 · What are the RPO and RTO?

| Target | Value | In your own words: what does it limit? |
|---|---|---|
| RPO (recovery point objective) | | |
| RTO (recovery time objective) | | |

---

### Question 2 · Which backup types and schedule?

Fill in the weekly schedule. For each backup, say its **type** (full / differential / incremental), **form** (physical / logical), **where it is taken from** (primary or standby) and **where it is stored**.

| Day / time | Backup type | Physical or logical | Taken from | Stored where | Kept for how long |
|---|---|---|---|---|---|
| Sun | | | | | |
| Mon | | | | | |
| Tue | | | | | |
| Wed | | | | | |
| Thu | | | | | |
| Fri | | | | | |
| Sat | | | | | |
| Continuous | | | | | |

**Restore chain check:** under your schedule, which files are needed to restore the state of **Thursday night**? How many files is that?

> ______________________________________________________________

---

### Question 3 · Is nightly backup alone enough? What must you add?

a) If the only protection were a nightly backup at 01:00 and the disk failed at 17:00 on an exam day, how much data would be lost? Does that meet the RPO?

> ______________________________________________________________

b) What do you add to meet the **RPO**? Name the setting you would use in PostgreSQL and the value you would choose.

> ______________________________________________________________

c) What do you add to meet the **RTO** for a server failure? (Hint: what is the extra server for?) Is restoring 400 GB from cloud storage likely to finish within one hour? Show a rough calculation.

> 400 GB ÷ ______ MB/s ≈ ______ minutes, plus log replay and checks ≈ ______

d) A lecturer accidentally deletes all grades of one course at 11:20. Does your answer to (c) help? What does?

> ______________________________________________________________

---

### Question 4 · How will you prove the plan works?

Complete the test plan.

| Test | How often | What you measure or check | Who signs off |
|---|---|---|---|
| Restore of the latest backup on a test server | | | |
| Point-in-time recovery to a chosen moment | | | |
| Standby failover rehearsal | | | |
| Check of the WAL archive for gaps | | | |

---

### Storage check (3-2-1)

| Rule | How your plan meets it |
|---|---|
| 3 copies of the data | |
| 2 different types of storage | |
| 1 copy off-site | |
| 1 immutable or offline copy | |
| Encrypted, keys stored separately | |

---

### Blank backup-schedule template (for Practice 2 and the quiz)

Use this table whenever you design a backup plan.

| Database | Size | RPO | RTO | Full backup | Partial backups | Log archiving | Replication | Off-site / immutable copy | Restore test |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |
| | | | | | | | | | |
