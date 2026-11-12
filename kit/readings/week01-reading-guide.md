# Week 1 Reading – Why Databases Matter & Transaction Logging

**Read before:** the Week 2 lesson · **Required:** 3 papers (listed sections only) · **Optional:** 3 papers · **Bring:** a half-page note per required paper (use `paper-note-template.md`)

This guide helps you read this week's papers efficiently. For each required paper it tells you what to focus on, what to skip, which terms to learn and which questions to answer while you read. The four self-check questions at the end are the same as on the last slide of the "Papers to Read" section.

All papers are available through the university library's access to the ACM Digital Library or USENIX, or as free author copies; the links are in the course repository.

---

## 1. How to read a paper: three passes

Research papers are written for other researchers. Reading one from the first word to the last is slow and usually ineffective. Use the three-pass method, adapted from S. Keshav, "How to Read a Paper" (2007):

| Pass | Time | What you do | What you should know afterwards |
|---|---|---|---|
| **1 · Get the idea** | about 10 min | Read the title, abstract and introduction carefully; read only the headings; glance at the figures; read the conclusion. | What problem the paper addresses, what it contributes, whether its assumptions seem reasonable. |
| **2 · Understand the content** | about 1 hour | Read the listed sections carefully. Skip long proofs. Study the figures and examples. Mark what you do not understand. | The main argument, well enough to explain it to a classmate. |
| **3 · Recreate it** | optional | Re-derive the argument yourself, questioning every assumption. | Only for papers central to your thesis or project. |

For this week, **two passes are enough**. After the second pass, write your half-page note: the problem, the key idea, the link to this week, and one question.

---

## 2. Required papers

### Paper 1 · Codd (1970)

**E. F. Codd, "A Relational Model of Data for Large Shared Data Banks."** *Communications of the ACM* 13(6), pp. 377–387, 1970.
**Read:** sections 1.1–1.4. **Skip:** section 2 (redundancy and consistency) and the detailed operations, unless you are curious.
**Links to:** Lessons 1-1 and 1-2 (why relational databases are the foundation of every system in this course).

**Why it matters.** This is the paper that founded relational databases. Every relational DBMS you will use in CE 502, from PostgreSQL to the cloud warehouses of Week 7, descends from it. It is surprisingly short and readable.

**What to focus on**

- **Section 1.1 (introduction).** Codd's goal: users of large shared data banks should not need to know how the data is organised inside the machine. Note the term *data independence*.
- **Section 1.2 (data dependencies in present systems).** The heart of the problem. Codd describes three ways in which programs of his time depended on the physical organisation of data. Make a list of the three as you read; they are self-check question Q1.
- **Section 1.3 (a relational view of data).** The solution: describe data only as *relations* (tables), defined over *domains*, with rows that have no required order. Note how he defines a primary key and the idea we now call a foreign key.
- **Section 1.4 (normal form).** Why relations should contain only simple (atomic) values, and how a nested structure is turned into several flat relations. You know this as normalisation from your first database course.

**Guiding questions**

1. What problem did programs have when the storage of data was changed (for example, a new index was added or the order of records changed)?
2. In Codd's model, what does a user need to know to retrieve data, and what does the user *not* need to know?
3. Why does Codd say that the order of rows in a relation does not matter, and why is this important for data independence?
4. How does this paper connect to the claim in Lesson 1-1 that "using a database and running one are different skills"?

**Key terms:** data independence · relation · domain · tuple (row) · degree · primary key · foreign key · normal form · data sublanguage.

---

### Paper 2 · Haerder and Reuter (1983)

**T. Haerder and A. Reuter, "Principles of Transaction-Oriented Database Recovery."** *ACM Computing Surveys* 15(4), pp. 287–317, 1983.
**Read:** sections 1–3. **Skip:** the detailed comparison of recovery schemes in the later sections (optional for students who want depth).
**Links to:** Lessons 1-3 and 1-4 (ACID, transaction log, undo and redo), and Week 2 (media failure).

**Why it matters.** This survey gave the field a common vocabulary for recovery. It is where the acronym **ACID** was introduced, and it classifies failures and recovery actions so precisely that textbooks still use its categories.

**What to focus on**

- **Section 1 (introduction).** Why recovery needs a systematic framework: different systems used different, incompatible ideas.
- **Section 2 (what recovery is expected to do).** The definition of a transaction and the four ACID properties. Then the **types of failure** a system must anticipate and the **recovery actions** each requires. Draw a small table as you read: failure type → what is lost → what log information is needed. This is self-check question Q2.
- **Section 3 (the mapping hierarchy of a DBMS).** How the database the user sees is mapped onto pages and files, and why the database on disk is not always the same as the database in memory. This explains *why* both before images and after images are needed, as in Lesson 1-3.
- If you continue beyond section 3, you will meet the classification of buffer policies (whether uncommitted pages may be written to disk before commit, and whether committed pages must be written at commit). Lesson 1-3 described the combination used by most modern systems: pages are written later, in the background, and the log carries both undo and redo information.

**Guiding questions**

1. How do the authors define each of the four ACID properties? Compare their wording with the ACID slide in Lesson 1-4.
2. What are the three types of failure, and how do they differ in what is lost (one transaction's work, the contents of memory, or the disk itself)?
3. Which recovery actions (undo of one transaction, undo of all unfinished transactions, redo of committed work) does each failure type need?
4. Why must the log on disk contain before images if the system is allowed to write changed pages to disk before a transaction commits?

**Key terms:** transaction · ACID (atomicity, consistency, isolation, durability) · transaction failure · system failure · media failure · undo · redo · before image · after image · archive copy and archive log.

---

### Paper 3 · ARIES (1992)

**C. Mohan, D. Haderle, B. Lindsay, H. Pirahesh and P. Schwarz, "ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging."** *ACM Transactions on Database Systems* 17(1), pp. 94–162, 1992.
**Read:** sections 1 and 2 and the overview of the method. **Skip:** the detailed algorithms, data structures and proofs that make up most of the 69 pages.
**Links to:** Lesson 1-3 (LSNs, page LSN, checkpoints, the three recovery phases) and Practice 1 (pg_waldump).

**Why it matters.** ARIES is the recovery method on which most modern relational DBMSs are based. The three phases you met on the "Going deeper" slide of Lesson 1-3 (analysis, redo, undo) come from this paper.

**What to focus on**

- **Section 1 (introduction).** The write-ahead logging protocol, log sequence numbers (LSNs) and the idea of storing the LSN of the last change on each page (the page LSN). Note why this lets recovery skip changes that are already on disk.
- **Section 2 (goals).** The list of properties the authors wanted: support for fine-grained (row-level) locking, partial rollbacks to savepoints, flexible buffer management (pages may be written before or after commit), and recovery that works even if the system crashes again during recovery.
- **Overview of the method.** The three phases: **analysis** (from the last checkpoint, find the unfinished transactions and the pages that may be out of date), **redo** ("repeating history": reapply every logged change, for all transactions) and **undo** (roll back the unfinished transactions, following each one's chain of previous LSNs). Note the **compensation log records (CLRs)** written during undo and why they guarantee that work is never undone twice. Note also that ARIES uses **fuzzy checkpoints**, which do not stop normal work.

**Guiding questions**

1. What information does the page LSN give recovery, and how is it used during redo?
2. Why does ARIES redo the changes of transactions that will later be undone ("repeating history")? This is self-check question Q3.
3. What is a compensation log record, and what would go wrong after a second crash during recovery without it?
4. How do the three phases of ARIES map onto the hand recovery you did on the sample log in Lesson 1-3 (T1, T2 committed; T3 not)?

**Key terms:** write-ahead logging (WAL) · log sequence number (LSN) · page LSN · previous LSN (per-transaction backward chain) · analysis / redo / undo · repeating history · compensation log record (CLR) · fuzzy checkpoint · dirty page table · transaction table · savepoint and partial rollback.

---

## 3. Optional papers

Not tested in Quiz 1. Recommended if you want a broader view, or if you are considering a thesis topic in databases.

| Paper | Why read it |
|---|---|
| **J. Gray, "The Transaction Concept: Virtues and Limitations."** *VLDB* 1981, pp. 144–154. | The classic, readable introduction to transactions, explained with everyday contracts. Short and clear. Read it **first** if Haerder and Reuter feels hard. |
| **M. Stonebraker and A. Pavlo, "What Goes Around Comes Around… And Around…"** *SIGMOD Record* 53(2), 2024. | Fifty years of data models: key-value, document, column, graph and vector databases, and why the relational model and SQL keep absorbing their best ideas. A map of the rest of CE 502. |
| **S. Keshav, "How to Read a Paper."** *ACM SIGCOMM Computer Communication Review* 37(3), pp. 83–84, 2007. | Two pages. The source of the three-pass method above, with advice on doing a literature survey for a thesis. |

---

## 4. Self-check questions

Answer each question in writing, in two or three sentences, **before** comparing with the reading notes of the last slide of the "Papers to Read" section.

- **Q1 · Codd.** Which three kinds of data dependence did programs suffer from before the relational model?
- **Q2 · Haerder and Reuter.** Name the three types of failure and the log information each one needs.
- **Q3 · ARIES.** Why does redo "repeat history", even for transactions that will be undone?
- **Q4 · Link.** Which ARIES ideas can you see in the pg_waldump output of Practice 1?

**Remember:** read the listed sections, not the whole paper. Codd explains why relational databases exist, Haerder and Reuter name the guarantees, and ARIES shows how they are delivered.
