# CE 502 · Quiz 1 – Why Databases Matter & Transaction Logging

**Covers:** Lessons 1-1 to 1-4 · **Questions:** 15 multiple choice · **Time:** 25 minutes · **Due:** before the Week 2 lesson

**Instructions**

- Choose **one** answer (A, B, C or D) for each question.
- Each question is worth 1 point. There is no penalty for a wrong answer.
- You may not use notes, the slides or other people during the quiz. A calculator is allowed.
- Each question shows the lesson and objective it checks (for example *1-3 · O2*). Use these tags to revise from the objective slides of each lesson.

---

## Lesson 1-1 · Course Introduction and Careers

### Q1 · 1-1 · O1

Which list shows the four blocks of CE 502 in the correct order?

- **A.** Distributed databases → one database → AI-era databases → analytics and scale
- **B.** Analytics and scale → one database → distributed databases → AI-era databases
- **C.** One database → distributed databases → analytics and scale → AI-era databases
- **D.** One database → analytics and scale → AI-era databases → distributed databases

### Q2 · 1-1 · O2

Which statement correctly describes how CE 502 works?

- **A.** Each week has short lessons, a hands-on practice in Docker, a short quiz and research papers to read; the midterm covers Weeks 1 to 6.
- **B.** Each week has one long lecture; practical work happens only in the final project in Weeks 10 to 12.
- **C.** The practices are done on a shared university server, so no software is installed on your own computer.
- **D.** The research papers are optional in every week and are not connected to the lessons.

### Q3 · 1-1 · O3

In most organisations, a database administrator (DBA) who keeps the production databases running day to day works in which department?

- **A.** Application software
- **B.** Networks
- **C.** Data management
- **D.** Operations

---

## Lesson 1-2 · Database Management Challenges

### Q4 · 1-2 · O1

At 13:00 your card is declined at a shop, and the terminal shows "service unavailable". The shop's terminal and network work normally, but your bank's payment database is not responding. What is the best description of what has happened?

- **A.** Only the bank's website is down; card payments are not affected by the database.
- **B.** The business process stops, because the terminal is only a front end and cannot approve a payment without the records in the bank's database.
- **C.** The terminal has failed, because it stores the account balances itself.
- **D.** Nothing has stopped: the payment will be approved automatically when the database returns.

### Q5 · 1-2 · O2

An online shop earns about **€480,000 a day**, with orders arriving evenly around the clock. Its order database is down for **30 minutes**. What is the **direct** loss of sales, using the method from the lesson?

- **A.** About €5,000
- **B.** About €10,000
- **C.** About €20,000
- **D.** About €240,000

### Q6 · 1-2 · O2

At 02:14 the disk holding a database fills up, and the database server process stops suddenly in the middle of several transactions. Which failure mode is this, and which protection deals with it?

- **A.** Slow; query tuning and indexes
- **B.** Down; nothing can be done until a new server is bought
- **C.** Crashed; the transaction log, with backup and recovery
- **D.** No failure; the server simply needs to be restarted

### Q7 · 1-2 · O3

In a three-tier web application, why is the database tier much harder to scale than the web and application tiers?

- **A.** The database tier uses SQL, and SQL cannot run on more than one processor.
- **B.** Web and application servers are more expensive, so organisations buy fewer of them.
- **C.** The database tier receives fewer requests, so it is rarely worth scaling.
- **D.** The database is stateful: every copy must hold the same permanent data, so copies must coordinate, while stateless web and application servers can simply be added.

### Q8 · 1-2 · O4

A 2 TB database is protected only by a backup. The storage system copies data at about **500 MB/s**. If the database is lost, what is the **minimum** time needed just to copy the data back?

- **A.** About 1.1 hours
- **B.** About 7 minutes
- **C.** About 11 hours
- **D.** About 4 seconds

---

## Lesson 1-3 · Transaction Logging

### Q9 · 1-3 · O1

Which of the following is **not** something the transaction log makes possible?

- **A.** Making SELECT queries faster by keeping an index of every row
- **B.** Rolling back a transaction that fails
- **C.** Recovering the database after a server crash
- **D.** Keeping a standby copy of the database up to date on another server

### Q10 · 1-3 · O2

Which statement is the **write-ahead rule**?

- **A.** Every changed data page must be written to the data files before the transaction may commit.
- **B.** A changed data page may be written to the data files only after the log records describing its changes are on disk.
- **C.** Log records are written to disk only at checkpoints, to save disk writes.
- **D.** The log buffer is flushed to disk only when it is full.

### Q11 · 1-3 · O3

The server crashes immediately after LSN 206 of this log. Any of the changed pages may or may not have reached the data files.

| LSN | Tx | Operation | Object | Before | After |
|---|---|---|---|---|---|
| 201 | T5 | BEGIN | – | – | – |
| 202 | T5 | UPDATE | ACCOUNT 3 | bal=100 | bal=60 |
| 203 | T6 | BEGIN | – | – | – |
| 204 | T6 | UPDATE | ACCOUNT 4 | bal=50 | bal=90 |
| 205 | T5 | COMMIT | – | – | – |
| 206 | T6 | UPDATE | ACCOUNT 5 | bal=10 | bal=0 |

After recovery, what are the balances of accounts 3, 4 and 5?

- **A.** 60, 90, 0
- **B.** 100, 50, 10
- **C.** 60, 50, 10
- **D.** 60, 90, 10

### Q12 · 1-3 · O4

Why can crash recovery start reading the log at the **last checkpoint** instead of at the beginning of the log?

- **A.** Because the log before the checkpoint is deleted at every checkpoint.
- **B.** Because transactions are not allowed to run during a checkpoint.
- **C.** Because the checkpoint writes a full backup of the database.
- **D.** Because all changes logged before the checkpoint have already been written to the data files.

---

## Lesson 1-4 · Transaction Control

### Q13 · 1-4 · O1

Paying a salary needs three changes: a row in the cheque register, a debit to the cash account and a credit to salaries payable. Why should these three changes be **one** transaction rather than three?

- **A.** Because each change on its own leaves the books in a state that is wrong in business terms; only all three together move the data from one correct state to the next.
- **B.** Because one transaction is always faster than three.
- **C.** Because the DBMS automatically groups all statements that touch accounting tables.
- **D.** Because a transaction may contain at most three statements.

### Q14 · 1-4 · O2

A user runs `DELETE FROM orders WHERE id = 17;` and then `COMMIT;`. A minute later they realise it was the wrong order and type `ROLLBACK;`. What happens?

- **A.** Order 17 is restored, because ROLLBACK uses the before images in the log.
- **B.** Order 17 is restored, but only if no other user has changed the table since.
- **C.** The DBMS asks for confirmation and then restores order 17.
- **D.** Nothing is restored: the DELETE was committed, so it can only be reversed by a new (compensating) transaction or by restoring a backup.

### Q15 · 1-4 · O4

A Python program uses the psycopg driver with its default settings. It updates 50 rows and then exits **without** calling `conn.commit()`. What happens to the 50 changes?

- **A.** They are committed automatically when the program exits, because every statement is its own transaction.
- **B.** They disappear: psycopg does not autocommit by default, so the transaction was never committed and the DBMS rolls it back.
- **C.** Some rows are saved and others are not, depending on which pages reached the disk.
- **D.** They are saved, because the WAL writer flushes the log buffer to disk every few hundred milliseconds.

---

*End of Quiz 1. Check that you have answered all 15 questions before you submit.*
