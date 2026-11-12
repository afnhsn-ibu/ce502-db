# CE 502 · Week 2 · Reading Guide
## Papers on Replication, Cloud Recovery and Consensus

**Due:** before the Week 3 class · **Hand in:** a half-page note per **required** paper, using `readings/paper-note-template.md` (problem · key idea · link to this week)
**Method:** the three-pass method from Week 1. Pass 1 (about 10 minutes): title, abstract, introduction, headings, conclusion. Pass 2 (about 1 hour): the sections listed below. Skip proofs and formulas you do not need.

---

## Required papers

### 1. The Dangers of Replication and a Solution

J. Gray, P. Helland, P. O'Neil, D. Shasha · *ACM SIGMOD 1996*, pp. 173–182
**Read:** sections 1–3 · **Links to:** Lesson 2-2 (synchronous vs asynchronous replication)

**Why it matters.** Replication looks like a simple way to get availability and read capacity: just add more copies. This paper shows, with a simple analytical model, that the obvious ways of replicating updates scale very badly as nodes are added. Its vocabulary (eager vs lazy, group vs master) is still used to describe replication today.

**Focus while reading**

- The two dimensions of the design space: **when** updates propagate (*eager*: inside the transaction; *lazy*: after commit) and **who** may update an item (*group*: any copy, "update anywhere"; *master*: only the item's owner).
- How the authors estimate the rate of **waits, deadlocks and reconciliations** as the number of nodes grows, and the headline result: a ten-fold increase in nodes and traffic can give about a thousand-fold increase in deadlocks or reconciliations.
- What lazy replication gives up: copies can be stale, and conflicting updates on different nodes must be **reconciled** after the fact.
- The proposed solution at the end of the paper, **two-tier replication** (only skim if you have time): always-connected base nodes hold master copies; disconnected mobile nodes run *tentative* transactions that are re-executed on the base nodes when they reconnect.

**Guiding questions**

1. Map eager/lazy onto the synchronous/asynchronous replication of Lesson 2-2. Which of PostgreSQL's options corresponds to which?
2. Why does making each transaction touch more nodes increase the chance of deadlock so sharply?
3. PostgreSQL streaming replication has a single primary. In Gray's terms, is it *group* or *master*? Why does that avoid reconciliation?
4. Which problem from this paper does the bank/social-feed scenario (slide l22-syncscen) illustrate?

**Key terms:** eager replication · lazy replication · update anywhere (group) · master (primary-copy) ownership · reconciliation · tentative transaction · two-tier replication

---

### 2. Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases

A. Verbitski et al. · *ACM SIGMOD 2017*, pp. 1041–1052
**Read:** sections 1–3 · **Links to:** Week 1 (the write-ahead log), Lessons 2-2 and 2-3

**Why it matters.** Aurora shows what happens when a relational database is redesigned around the log. It is the clearest example of the slogan "the log is the database", and it explains why cloud databases can offer continuous backup and point-in-time recovery without a nightly backup job.

**Focus while reading**

- The problem: in a traditional mirrored set-up, every change causes many network writes (log, data pages, double-write buffers, binlog, mirror copies), and the network becomes the bottleneck.
- The key decision: the database engine sends **only redo log records** to a distributed storage service; storage nodes apply them to pages in the background ("the log is the database").
- Durability by **quorum**: 6 copies of the data across 3 availability zones (2 per zone); a write needs 4 of 6, a read 3 of 6. Why this survives the loss of a whole zone plus one more node for reads.
- Data split into **10 GB segments** (protection groups), so a failed segment can be repaired quickly.
- Backups stream **continuously to Amazon S3**, and crash recovery no longer needs a long replay at start-up.

**Guiding questions**

1. Which Week 1 idea makes it possible to send only log records instead of pages?
2. Why is a quorum of 4 of 6 preferred over "write to all 6"?
3. How does Aurora change the RPO and RTO compared with "nightly backup + WAL archiving" (slide l23-rposcen)?
4. Aurora's copies are all updated by the same log. Would its 6 copies protect against a mistaken `DROP TABLE`? What does?

**Key terms:** redo log record · storage service · quorum (write quorum, read quorum) · availability zone · segment / protection group · continuous backup

---

### 3. In Search of an Understandable Consensus Algorithm (Raft)

D. Ongaro, J. Ousterhout · *USENIX ATC 2014*, pp. 305–319
**Read:** sections 1–2 and 5.1–5.3 · **Links to:** Lesson 2-2 (failover and split brain)

**Why it matters.** Automatic failover is only safe if the servers can agree on **one** primary, even when the network splits. Raft is the algorithm behind etcd and Consul, which tools such as Patroni use to decide which PostgreSQL server is the primary.

**Focus while reading**

- Section 2: what a **replicated state machine** is, and why a replicated log is the core of it (compare with streaming replication).
- 5.1: server roles (follower, candidate, leader) and **terms**, numbered periods that each have at most one leader.
- 5.2: **leader election**. A candidate needs votes from a **majority**; each server votes **at most once per term**; **randomised election timeouts** make split votes rare.
- 5.3: **log replication**. An entry is committed once a majority stores it; the **log matching** property keeps logs consistent.

**Guiding questions**

1. Why must two majorities of the same cluster always overlap? What does that guarantee?
2. What happens to an old leader that was cut off from the others and then comes back with a lower term?
3. Why does Raft need at least three servers to tolerate one failure, and how is this related to the "witness" on slide l22-split?
4. Compare step 2, *fence*, of the failover procedure (slide l22-failover) with Raft's rule that a leader without a majority cannot commit.

**Key terms:** consensus · replicated state machine · leader · follower · candidate · term · majority (quorum) · election timeout · log matching

---

## Optional papers (not examined)

Choose at most one this week.

| Paper | Read for |
|---|---|
| D. Patterson, G. Gibson, R. Katz, **"A Case for Redundant Arrays of Inexpensive Disks (RAID)"**, *ACM SIGMOD 1988*, pp. 109–116 | What disk-level redundancy protects against (a failed disk) and what it does not (a mistaken `DROP TABLE` is written to every disk at once). The RAID levels and their reliability calculations. |
| B. Kemme, G. Alonso, **"Don't Be Lazy, Be Consistent: Postgres-R, A New Way to Implement Database Replication"**, *VLDB 2000*, pp. 134–143 | A reply to Gray et al.: eager, update-anywhere replication can perform well if each transaction runs locally and its write set is then delivered to all replicas in one **total order** by group communication. Built inside PostgreSQL. |
| P. Bernstein, V. Hadzilacos, N. Goodman, ***Concurrency Control and Recovery in Database Systems***, Addison-Wesley 1987, chapters 6–8 (freely available from Microsoft Research) | The formal theory: ch. 6 centralised recovery (logging, checkpoints, undo/redo algorithms), ch. 7 distributed recovery (atomic commitment, two-phase commit), ch. 8 replicated data. Read after the lessons. |

---

## Reading questions for class discussion

Answer each in two or three sentences before the Week 3 class. These are the questions on slide **rd-questions**.

**Q1** (Gray et al.) Why do waits and deadlocks grow so quickly with eager replication, and what does lazy replication give up?

**Q2** (Verbitski et al.) Why does Aurora send only redo log records over the network, and what does this change for backup and recovery?

**Q3** (Ongaro, Ousterhout) How does Raft guarantee that a cluster never has two leaders at once?

**Q4** (all papers) A bank needs RPO = 0 and RTO under one minute. Which ideas from this week's papers and lessons would you combine?

---

## Your half-page note

Use `readings/paper-note-template.md`. For each required paper write:

1. **Problem:** what was wrong or missing before this paper? (2–3 sentences)
2. **Key idea:** the one mechanism or result to remember. (2–3 sentences)
3. **Link to this week:** which slide or lesson does it explain, and how? (2–3 sentences)

A good note is in your own words and fits on half a page. Do not copy the abstract.
