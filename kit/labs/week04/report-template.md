# Practice 4 Report · A Two-Site Database

**CE 502 · Week 4** · Name: ______________ · Student ID: ______________ · Date: ______________

> One PDF, at most 4 pages. Replace every *italic instruction* with your own text. Link every output to a concept from Lessons 4-1 to 4-3.

---

## 1. Part A · Relational algebra ↔ SQL · 3 points

*Paste your `my_answers.sql`, or attach it, together with the output of running it. A screenshot or copied text is fine.*

| Item | Relational algebra | SQL (short) | Rows returned | One sentence: how it is evaluated / what to watch out for |
|---|---|---|---|---|
| 1 | σ cost > 10 (PART) | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | 1 | |
| 5 | | | | |
| 6 | *your expression* | given | | |
| 7 | *your expression* | given | | |
| 8 | *your expression* | given | | |
| 9 | *your expression* | given | | |
| 10 | *your expression* | | | *which `state` your selection uses, and why a natural join gives the wrong answer* |

## 2. Part B · Two sites, one global schema · 3 points

**View definition.** *Paste the output of `\d+ customer`. Which relational-algebra operator rebuilds the global table from its fragments, and why that one? 1–2 sentences.*

**Plan with Remote SQL.** *Paste the `EXPLAIN (VERBOSE, COSTS OFF)` output. What was sent to each site? Was the selection pushed down? Why is New York queried at all? 2–3 sentences.*

**The two INSERTs.** *Paste the results. Why did Illinois succeed and Texas fail? Name the fragment predicate and the correctness rule (completeness) involved. Why is the global count 9? 2–3 sentences.*

## 3. Part C · A/D/H worksheet · 2 points

| # | System | A | D | H | Justification (one sentence) |
|---|---|---|---|---|---|
| 1 | A single PostgreSQL server used by a web application | | | | |
| 2 | Our `ddb_global` lab setup | | | | |
| 3 | PostgreSQL + Citus, one table sharded over 4 worker nodes | | | | |
| 4 | A MongoDB sharded cluster | | | | |
| 5 | Apache Cassandra, 6 peer nodes in 2 data centres | | | | |
| 6 | Trino over MySQL, PostgreSQL and Parquet files in S3 | | | | |
| 7 | University library (Oracle) + student system (SQL Server) behind a federated view layer | | | | |
| 8 | Google Spanner | | | | |

## 4. Reflection: transparency in `ddb_global` · 2 points

*Half a page. Go through the transparencies from Lesson 4-2: logical and physical data independence, network, location, replication and fragmentation. For each one, say whether `ddb_global` provides it for **queries** and for **updates**, with evidence from Part B. End with one change that would give more transparency, for example rules or triggers that route INSERTs to the right site, or a directory of fragment predicates.*

---

### Declaration

I did this practice myself. Any help (classmates, AI tools, websites) is listed here: ______________
