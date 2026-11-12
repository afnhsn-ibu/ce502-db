# CE 502 · Advanced Topics in Database Systems · Sample Midterm (Weeks 1–6)

**Duration:** [__] minutes · **Total:** 100 points · **Allowed:** [closed book / one A4 sheet of notes], a pen and a calculator without network access.

This sample has the same structure as the real midterm (Lesson 6-3, "Four Kinds of Midterm Questions"): **concepts**, a **schedule trace**, a **design** and **computations**. The numbers in the real exam will be different. Show every intermediate value: partial credit is given for correct steps.

| Section | Kind | Weeks | Points |
|---|---|---|---|
| A · Multiple choice (10 × 2) | Concepts | 1–6 | 20 |
| B · Short answers (3 × 6) | Concepts | 1, 2, 6 | 18 |
| C · Schedule trace | Trace | 3 | 14 |
| D · Backup and recovery plan | Design | 2 | 14 |
| E1 · Horizontal fragmentation | Compute | 5 | 14 |
| E2 · Vertical fragmentation and allocation | Compute + design | 6 | 20 |

**Formulas you may use:**

- aff(Ai, Aj) = Σ over queries using both Ai and Aj of their total frequency;
- bond(Ax, Ay) = Σ_z aff(Az, Ax) · aff(Az, Ay), with bond(A0, ·) = bond(·, A(n+1)) = 0;
- cont(Ai, Ak, Aj) = 2·bond(Ai, Ak) + 2·bond(Ak, Aj) − 2·bond(Ai, Aj);
- z = CTQ · CBQ − COQ².

---

## Section A · Multiple choice (2 points each)

1. **(W1)** Under the write-ahead rule, before a COMMIT is reported to the client the DBMS must:
   a) write all changed data pages to disk
   b) force the transaction's log records, including the commit record, to disk
   c) take a checkpoint
   d) copy the change to the standby server

2. **(W1)** After a crash, a checkpoint makes recovery faster because:
   a) it deletes the log
   b) recovery can start reading the log from the last checkpoint instead of from the beginning
   c) it undoes all open transactions
   d) it stops new transactions from starting

3. **(W2)** A database has a full backup on Sunday and a **differential** backup every other night. To restore Thursday night's state you need:
   a) Sunday's full backup only
   b) Sunday's full backup and every differential from Monday to Thursday
   c) Sunday's full backup and Thursday's differential
   d) Thursday's differential only

4. **(W2)** "We may lose at most 5 minutes of orders" defines the:
   a) RTO
   b) RPO
   c) checkpoint interval
   d) replication lag

5. **(W2)** With **synchronous** replication to one standby:
   a) the primary never waits for the standby
   b) a committed transaction is not lost when the primary's disk fails
   c) the standby protects against an accidental DROP TABLE
   d) commits are faster than with asynchronous replication

6. **(W3)** A transaction reads the same row twice and sees two different committed values. This is a:
   a) dirty read
   b) non-repeatable read
   c) phantom read
   d) lost update

7. **(W3)** In PostgreSQL, transaction A at REPEATABLE READ counts the rows of a table, transaction B inserts a row and commits, and A counts again. A's second count:
   a) is one higher: a phantom
   b) is the same as the first: A reads from its snapshot
   c) fails with a serialization error
   d) waits until A commits

8. **(W4)** A user at the New York site runs `SELECT * FROM customer WHERE state = 'MD'` without knowing which site stores the Maryland customers. This is:
   a) network transparency
   b) location (distribution) transparency
   c) physical data independence
   d) execution autonomy

9. **(W5)** The fragments of a member relation ORDERS that follow the horizontal fragments of its owner CUSTOMER are computed with a:
   a) projection of ORDERS
   b) union of the CUSTOMER fragments
   c) semi-join of ORDERS with each CUSTOMER fragment
   d) Cartesian product

10. **(W6)** How many different ways are there to group the 4 non-key attributes of a relation into non-empty vertical fragments (Bell number B(4))?
    a) 4
    b) 8
    c) 15
    d) 24

---

## Section B · Short answers (6 points each, about 5–8 sentences)

11. **(W1) COMMIT and the log.** Why does COMMIT wait for the log to reach disk but not for the changed data pages? Explain what would happen after a crash one second after COMMIT, and name the recovery step that restores the change.

12. **(W2) Replication is not a backup.** A company runs a primary with an asynchronous streaming standby and no backups. Give two kinds of failure the standby protects against and two it does not, and explain what the RPO of this setup is when the primary server fails.

13. **(W4–W6) Correctness of fragments.** For **horizontal** and for **vertical** fragmentation, state how the original relation is reconstructed, and what *disjointness* means in each case. Why is the primary key the exception for vertical fragments?

---

## Section C · Schedule trace (14 points)

Item 500 has `qty = 120`. Transaction **T1** (goods received) adds 12; transaction **T2** (a sale) subtracts 10. Each transaction reads the quantity, computes the new value in the application, and writes it back.

| Time | T1 | T2 |
|---|---|---|
| t1 | read qty (item 500) | |
| t2 | | read qty (item 500) |
| t3 | write qty = 132 | |
| t4 | COMMIT | |
| t5 | | write qty = 110 |
| t6 | | COMMIT |

a) Without any locks, as at Read Committed in PostgreSQL: what is the final value, what should it be, and which anomaly occurred? (4 pts)

b) Now each transaction takes a **shared (S)** lock to read and an **exclusive (X)** lock to write, and holds every lock until COMMIT (two-phase locking). Trace the schedule step by step: which locks are held after t2, what happens at t3 and at t5, and why? (6 pts)

c) How does the DBMS resolve the situation in (b)? Which transaction does PostgreSQL abort, and what must the application do so that the final value is correct? Give the correct final value. (4 pts)

---

## Section D · Backup and recovery plan (14 points)

An online shop runs PostgreSQL. The database is **200 GB** and changes all day. The management sets **RPO ≤ 5 minutes** and **RTO ≤ 30 minutes**. You have one data centre, a budget for **one extra server**, and off-site cloud object storage.

a) Define RPO and RTO in one sentence each, for this shop. (2 pts)

b) Propose a backup and replication strategy: backup types and schedule, what happens to the transaction log, where copies are stored, and what the extra server is used for. Justify each choice with the RPO or the RTO. (8 pts)

c) A developer runs `DELETE FROM orders` without a WHERE clause at 14:03. Which part of your plan recovers the data, and up to which point in time? (2 pts)

d) How will you prove that the plan meets the RTO? (2 pts)

---

## Section E1 · Horizontal fragmentation (14 points)

A bank stores ACCOUNT(ano, branch, type, balance). There are only two branches: **Skopje** and **Ohrid**. Each branch application reads its own branch's accounts; the loans department reads accounts with balance ≥ 10,000 far more often than smaller ones.

| ano | branch | type | balance |
|---|---|---|---|
| 1 | Skopje | savings | 25,000 |
| 2 | Skopje | current | 1,200 |
| 3 | Ohrid | savings | 9,999 |
| 4 | Ohrid | current | 40,000 |
| 5 | Skopje | savings | 10,000 |
| 6 | Ohrid | savings | 300 |

Simple predicates: p1: branch = 'Skopje' · p2: branch = 'Ohrid' · p3: balance ≥ 10000.

a) How many minterm predicates exist before elimination? (2 pts)

b) Write the implications between the predicates and list the contradictory minterms. (4 pts)

c) Write each remaining fragment as a selection and list its rows (by ano). (5 pts)

d) Show that this fragmentation is complete and disjoint for this data, and give the expression that reconstructs ACCOUNT. (3 pts)

---

## Section E2 · Vertical fragmentation and allocation (20 points)

R(key, A1, A2, A3, A4) is used by four queries at two sites (accesses per hour):

| Query | Attributes | Site S1 | Site S2 |
|---|---|---|---|
| Q1 | A1, A3 | 30 | 20 |
| Q2 | A2, A4 | 10 | 40 |
| Q3 | A1, A2 | 5 | 5 |
| Q4 | A3, A4 | 2 | 0 |

a) Compute the attribute affinity matrix AA. (4 pts)

b) Start the bond energy algorithm with the order A1 A2. Compute cont() for every possible position of A3 and choose its place. (4 pts)

c) Place A4 the same way and give the final order. On a tie, keep the leftmost position. (4 pts)

d) Compute z for every single cut of the final order, choose the best cut and write the two fragments. (5 pts)

e) Allocate each fragment to S1 or S2 and name the queries that still need a join, with their frequency. (3 pts)
