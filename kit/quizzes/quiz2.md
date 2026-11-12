# CE 502 · Week 2 · Quiz 2 – Backup, Recovery & Replication

**Time:** 30 minutes · **Format:** 16 multiple-choice questions (1 point each) + 1 short design question (4 points) · **Total:** 20 points
**Covers:** Lesson 2-1 Database Backups, Lesson 2-2 Replication and High Availability, Lesson 2-3 Database Recovery
**Due:** before the Week 3 class

Choose **one** answer (A–D) for each multiple-choice question. The tag after each question shows the lesson and objective it checks; use the objective slides of each lesson to review the ones you miss. The definitions used in the questions are the ones on the Key Terms slides.

---

## Part 1 · Multiple choice

### Lesson 2-1 · Database Backups

**Q1.** `[2-1 · O1]` A PostgreSQL server restarts after a power cut and recovers automatically by replaying its write-ahead log. Why does the organisation still need backups?

- A. Crash recovery replays only uncommitted transactions, so committed work must come from a backup.
- B. Crash recovery works only if the data files and the log are still on the server; backups protect against losing them.
- C. Crash recovery works only for read-only databases.
- D. Backups make crash recovery faster, because the log no longer has to be replayed.

**Q2.** `[2-1 · O1]` A DBA copies the database files every night to a second disk inside the same server. Which statement is correct?

- A. This is a good backup, because the copy is on a different disk.
- B. This is a good backup, as long as the copy is taken while the database is offline.
- C. This is not a real backup: a fire, the loss of the server or ransomware would destroy both copies.
- D. This is not a real backup, because backups must always be logical (SQL) dumps.

**Q3.** `[2-1 · O2]` A university runs two PostgreSQL databases. The *room booking* database is 2 GB and changes a few times a week; losing a week of bookings would be annoying but easy to re-enter. The *exam registration* database is 300 GB, thousands of students change it every hour during registration, and lost registrations would have legal consequences. Which plan best fits the four factors (size, users, rate of change, criticality)?

- A. Both databases: a weekly full backup, because they run on the same DBMS.
- B. Room booking: a weekly full backup. Exam registration: nightly backups plus continuous log archiving.
- C. Room booking: continuous log archiving. Exam registration: a weekly full backup, because it is too large to back up more often.
- D. Both databases: hourly full backups, because more backups are always better.

**Q4.** `[2-1 · O3]` Which definition describes a **differential** backup?

- A. A copy of the entire database that can be restored on its own.
- B. A copy of all changes since the last backup of any kind.
- C. A copy of all changes since the last full backup.
- D. A copy of the transaction log files written since the last checkpoint.

**Q5.** `[2-1 · O3]` A shop takes a full backup on Sunday night and a **differential** backup on every other night. The database fails on Saturday morning. Which files are needed to restore the state of Friday night?

- A. Sunday's full backup + Friday's differential
- B. Sunday's full backup + the differentials of Monday, Tuesday, Wednesday, Thursday and Friday, in order
- C. Friday's differential only
- D. Sunday's full backup only

**Q6.** `[2-1 · O3]` A company takes a full backup on Sunday night and an **incremental** backup on every other night. On Friday morning the database fails, and the DBA discovers that Wednesday's incremental file is damaged. No transaction logs were archived. What is the latest state that can be restored?

- A. Thursday night, using Sunday's full backup and Thursday's incremental
- B. Thursday night, using Sunday's full backup and the Monday, Tuesday and Thursday incrementals
- C. Tuesday night
- D. Sunday night only, because one damaged file makes the whole chain unusable

**Q7.** `[2-1 · O4]` An online pharmacy takes orders 24 hours a day and cannot stop its database for backups. Which statement is correct?

- A. It must use cold backups, because only a cold backup is consistent.
- B. It can use warm (online) backups; these need the transaction log written during the backup to make the copy consistent.
- C. It can use warm backups; these are consistent on their own because the DBMS locks every table during the copy.
- D. It cannot take backups at all without a maintenance window.

**Q8.** `[2-1 · O4]` A team must move one 5 GB database from PostgreSQL 15 to a new server running PostgreSQL 17, and also wants to be able to restore a single table on its own. Which kind of backup suits this task best?

- A. A physical backup with `pg_basebackup`, because it copies the data files block by block
- B. A logical backup with `pg_dump`, because it is portable across versions and can restore a single table
- C. A cold physical backup, because it is consistent by itself
- D. Archived WAL files only, because they contain every change

### Lesson 2-2 · Replication and High Availability

**Q9.** `[2-2 · O1]` In PostgreSQL streaming replication, what does the primary send to the standby after the standby has been set up?

- A. A full copy of every changed data page, every few seconds
- B. The SQL statements that the applications sent, which the standby executes again
- C. Write-ahead log (WAL) records, which the standby replays
- D. A new `pg_dump` file every hour

**Q10.** `[2-2 · O1]` A user connected to a hot standby runs `SELECT bal FROM accounts WHERE id = 1;` and then `UPDATE accounts SET bal = 0 WHERE id = 1;`. What happens, and why?

- A. Both succeed; the standby forwards the UPDATE to the primary.
- B. The SELECT succeeds; the UPDATE is rejected because the standby is read-only and may change data only through the log it replays.
- C. Both fail, because a standby in recovery accepts no connections.
- D. The SELECT fails because the data may be old; the UPDATE succeeds.

**Q11.** `[2-2 · O2]` A payments company wants to be sure that no transfer the application has reported as complete can ever be lost when the primary fails. Its standby is in the same data centre. Which replication mode should it use, and what is the main cost?

- A. Asynchronous; the cost is a small risk of losing recent commits.
- B. Synchronous; the cost is about one network round trip added to every commit.
- C. Synchronous; the cost is that the standby can no longer answer read-only queries.
- D. Asynchronous; the cost is that failover becomes impossible.

**Q12.** `[2-2 · O2]` A primary has exactly **one** synchronous standby. The network link to that standby breaks. With the usual configuration (no other synchronous candidates), what happens on the primary?

- A. Nothing changes; the primary continues as if replication were asynchronous.
- B. Commits wait, so writes stop until the standby is reachable again or the configuration is changed.
- C. The primary promotes itself to a second primary.
- D. The primary automatically drops all tables that were not yet replicated.

**Q13.** `[2-2 · O3]` During a failover, the monitoring system promotes the standby but does not fence the old primary, which is still reachable by some application servers. What is the risk?

- A. Replication lag increases on the new primary.
- B. Split brain: both servers accept writes and their data diverges.
- C. A switchover: the roles swap without data loss.
- D. The new primary returns to recovery mode.

**Q14.** `[2-2 · O4]` At 10:15:02 a developer runs `DELETE FROM customers;` on the primary. The company has a synchronous standby but no backups. What is the situation one second later?

- A. Safe: fail over to the standby, which still has the customers.
- B. Safe: synchronous replication delays deletes until a DBA approves them.
- C. Lost: the standby replayed the DELETE as well; only a backup with archived logs could return to 10:15:01.
- D. Lost: but only on the standby; the primary can roll the DELETE back automatically.

### Lesson 2-3 · Database Recovery

**Q15.** `[2-3 · O1]` Which situation requires **media recovery** rather than crash recovery?

- A. The operating system crashes and the server reboots; the disks are intact.
- B. A power cut stops the server for five minutes.
- C. The storage array holding the data files and the log fails and must be replaced.
- D. A transaction fails with a constraint error and is rolled back.

**Q16.** `[2-3 · O3]` A hospital manager says: "We can afford to lose at most 10 minutes of lab results, and the system must be working again within 2 hours of a failure." Which statement is correct?

- A. RPO = 2 hours, RTO = 10 minutes
- B. RPO = 10 minutes, RTO = 2 hours; nightly backups alone would meet both targets
- C. RPO = 10 minutes, RTO = 2 hours; continuous log archiving is needed, because nightly backups alone give an RPO of up to 24 hours
- D. RPO and RTO are the same thing, so the target is 10 minutes

---

## Part 2 · Short design question `[2-3 · O4]` (4 points)

**Scenario: a concert ticket platform.** A ticket-sales company runs one 600 GB PostgreSQL database. When a big concert goes on sale, thousands of tickets are sold per minute; otherwise traffic is moderate. Management says: *"A ticket that a customer has paid for must never disappear, and the shop must be selling again within 5 minutes of a server failure."* The company has two data centres in the same city (about 1 ms apart) and a cloud storage account in another region. Last year a faulty release overwrote the seat map of one concert; it took two days to fix by hand.

In **150–250 words**, propose a backup and recovery strategy. Your answer must:

1. state the RPO and RTO;
2. say which replication mode you would use and where, and how failover is made safe;
3. say which backups, log archiving and storage rules you would use, and why replication alone would not have fixed last year's incident;
4. say how you would prove that the plan works.

Write your answer below.

> &nbsp;
>
> &nbsp;
>
> &nbsp;
