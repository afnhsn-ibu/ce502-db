# CE 502 Advanced Topics in Database Systems · Course Kit

The hands-on materials for all 12 weeks: every practice (lab), the assignments, the final project and the sample midterm. Weeks 1–2 also include their quizzes, reading guides and case study. The slide decks, reading lists and schedule are on the course site, https://afnhsn-ibu.github.io/ce502-db/; each practice section of a deck points to the matching `labs/weekNN/README.md`.

## Start here (students)

1. **Before Week 1:** follow `setup/SETUP.md`. Install Docker, run `docker compose up -d --build` and run the setup check.
2. **Each week:** open `labs/weekNN/README.md`. It has every command, with the output you should see, and links to its report template.
3. **Python:** `pip install -r setup/requirements.txt` from Week 3 on. From Week 10, run `pip install -r setup/requirements-ai.txt` instead (it adds Chroma and sentence-transformers).

## The 12 practices

| Week | Topic | Practice | Services | Points |
|---|---|---|---|---|
| 1 | Why Databases Matter & Transaction Logging | P1 Inside the WAL: log volume, pg_waldump, full-page images, ROLLBACK | postgres | 10 |
| 2 | Backup, Recovery & Replication | P2 dump/restore, point-in-time recovery; replication demo | postgres (+ replica) | 10 + 2 |
| 3 | Concurrency Control & ACID | P3 two-session anomalies and deadlock; lost update in Python | postgres | 10 |
| 4 | Distributed Database Systems | P4 relational algebra ↔ SQL; two-site database with postgres_fdw; A/D/H | postgres | 10 |
| 5 | Horizontal Fragmentation | P5 minterms, fragments as partitions, derived fragmentation | postgres | 10 |
| 6 | Vertical Fragmentation & Midterm Review | P6 Bond Energy Algorithm in Python (pytest), vertical fragments in SQL | postgres | 10 |
| 7 | Data Warehousing & Data Cubes | P7 star schema, ETL, OLAP with ROLLUP/CUBE, materialised view, snowflake | postgres | 10 |
| 8 | Big Data & the Data Explosion | P8 5 million taxi trips: DuckDB vs PostgreSQL, the V's, batch vs stream | postgres | 10 |
| 9 | The Relational Problem & NoSQL | P9 MongoDB documents and transactions; Cassandra query-first tables | mongo, cassandra | 10 |
| 10 | Vector Database Foundations | P10 similarity by hand, cost of exact k-NN, semantic search with Chroma | – (Python only) | 10 |
| 11 | Vector Search in NoSQL & PostgreSQL | P11 pgvector, HNSW vs IVFFlat recall/latency; MongoDB and Cassandra vector search | postgres (+ nosql/atlas) | 10 |
| 12 | RAG, Recommenders & Wrap-up | Lab: RAG pipeline, retrieval evaluation, recommender, as the base for the final project | postgres | – |

Start optional services with `docker compose --profile replication up -d` (Week 2 demo), `docker compose --profile nosql up -d` (Weeks 9 and 11) or `docker compose --profile atlas up -d` (Week 11, optional).

## Assignments, project and exam

| File | When | Points |
|---|---|---|
| `assignments/careers-assignment.md` (+ peer-review form) | Week 1 → due Week 3 | 20 |
| `assignments/dw-project.md` | Week 7 | 20 |
| `assignments/bigdata-assignment.md` | Week 8 | 20 |
| `assignments/relational-problem-assignment.md` | Week 9 | 20 |
| `projects/final-project.md` + `projects/final-project-template/` + `projects/presentation-checklist.md` | Week 10 → Week 12 | 100 |
| `exams/midterm-sample.md` | Week 6 | – |

Weeks 1–2 also contain `quizzes/quiz1.md` and `quiz2.md`, the reading guides in `readings/`, and the case study in `activities/`.

## Conventions

- Every lab command is a single `docker exec …` line or a Python command run on the laptop, so it works on Windows, macOS and Linux. The kit is mounted read-only at `/kit` in the containers. Students edit files on the laptop; the containers only read them.
- Scripts are numbered in the order they are run, and every setup script can be run again from the start.
- Generated data uses fixed seeds, so every student gets the same counts and totals. Use them to check reports.
