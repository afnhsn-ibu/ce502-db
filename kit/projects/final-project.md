# CE 502 Final Project · An AI Application on a Vector Database

**Weeks 10–12** · **Teams:** 2–3 students · **Weight:** [__%] of the final grade (see the syllabus; the default plan is 30%) · **100 points**
**Starter code:** `projects/final-project-template/` · **Starting lab:** `labs/week12/` · **Checklist:** `projects/presentation-checklist.md`

## The task

Build a working **retrieval-augmented generation (RAG) application** or a **recommender system** on a vector database of your choice:

- Chroma;
- PostgreSQL + pgvector;
- MongoDB Atlas Vector Search;
- Cassandra 5.0;
- another system, with the instructor's approval.

Use a **real dataset of at least 1,000 documents or items**, with a licence that allows your use.

- **RAG:** answers questions by retrieving relevant passages and giving them to a language model, or, without a model, by quoting the best passage.
- **Recommender:** suggests items similar to what a user likes, or to an item the user is viewing.

## Requirements

1. **Data pipeline.** Load, clean, chunk (RAG) or choose the item text (recommender), embed and store. **One command** rebuilds everything from the raw data. Document your cleaning and chunking choices.
2. **Database and index design.** Schema or collection, metadata fields, the vector index (HNSW, IVF, …) and its parameters. Justify the choices **with measurements**, for example recall and latency for two index settings.
3. **Application.** A command-line tool, notebook or simple web page that answers questions or returns recommendations, **showing sources or scores**, and handling "no answer" sensibly: it says so instead of inventing an answer.
4. **Evaluation.**
   - **At least 20 labelled test questions or test users.**
   - RAG metrics: recall@k and MRR. Recommender metrics: a hit rate or precision@k.
   - **At least two settings compared:** chunk size, embedding model or index parameters.
   - An honest discussion of the failures.
5. **Link to an earlier course topic, implemented and demonstrated**, not only described. For example:
   - transactions when updating vectors and metadata together (Weeks 1, 3);
   - backup and restore of the vector store (Week 2);
   - partitioning or sharding the data (Weeks 4–6, 9);
   - a warehouse-style analytics view or cube of usage (Week 7);
   - a streaming ingestion design (Week 8).
6. **Responsible use.** Data licence, privacy (for example, removing personal data from documents), and a list of any AI assistance used while building the project.

## Milestones

| When | Deliverable | Points |
|---|---|---|
| Week 10 | Form your team and choose your dataset | – |
| **Week 11** | **Proposal, 1 page:** problem and users, dataset and licence, database choice, evaluation plan, team roles (template below) | **10** |
| **Week 12** | **Demo and presentation:** 10 minutes + 5 minutes of questions, in your slot | **30** |
| **Week 12** | **Repository** (code, requirements, one-command pipeline, test set, evaluation script, README) **and report** (at most 6 pages) | **60** |

Due dates: proposal [date] · presentations [date / slot list] · repository and report [date].

## Rubric (100 points)

| Criterion | Excellent work shows | Points |
|---|---|---|
| Proposal | Clear problem, dataset with licence, realistic plan, roles | 10 |
| Data pipeline | Reproducible with one command; choices documented | 15 |
| Database and index design | Schema fits the queries; index choice justified with measurements | 15 |
| Application quality | Reliable demo; sources or scores; handles "no answer" | 15 |
| Evaluation | ≥ 20 labelled cases, correct metrics, two settings compared, failures discussed | 20 |
| Link to earlier course topic | Implemented and demonstrated, not only described | 10 |
| Presentation | Clear story, on time, good answers to questions | 10 |
| Report and repository | README lets another student run it; responsible-use section | 5 |

Evaluation is the largest item. Half of the points reward engineering discipline (pipeline, design justification, evaluation), not the look of the application. A modest demo with honest measurements beats a polished interface with none.

## Presentation format: 10 minutes + 5 minutes of questions

| # | Part | Time |
|---|---|---|
| 1 | Problem and users: who has the problem, why it matters | 1 min |
| 2 | Data and pipeline: source, licence, size, cleaning, chunking or item text | 2 min |
| 3 | Database and index design, **with your link to an earlier course topic** | 2 min |
| 4 | Live demo: two or three real queries, sources or scores visible | 3 min |
| 5 | Evaluation results and lessons learned, including failures | 2 min |

**Every team member speaks**, and part 3 must **show** the course-topic link. Questions usually test understanding:

- why this index and these parameters;
- what happens if the server fails;
- how you would handle ten times more data;
- why a particular test question failed.

Prepare with `projects/presentation-checklist.md`.

## Repository and report

**Repository.**

- Code and a requirements file with pinned versions.
- A one-command pipeline, the labelled test set and the evaluation script.
- A README that takes another student **from an empty machine to the same evaluation numbers**: database and version, how to start it (for example `docker compose up -d`), how to load the data, run the application and run the evaluation, and a table of the expected results.
- No secrets: explain how to set API keys instead.

**Report (at most 6 pages):**

1. Problem and users.
2. Data, licence and pipeline.
3. Database and index design, with its justification and measurements.
4. Evaluation: the test set and its size, the metrics, the comparison of settings, and the failures.
5. The link to an earlier course topic and how you demonstrated it.
6. Responsible use: licence, privacy and AI assistance.

## Proposal template (Week 11, 1 page)

```
Team name and members (with roles: data / database / application / evaluation)
Type: RAG application  |  recommender system
Problem and users (3-4 sentences)
Dataset: source, licence, size (>= 1,000 documents or items), language(s), personal data? how removed?
Database and index: which one and why (1-2 sentences); planned metadata filters
Evaluation plan: how you will label >= 20 questions or test users; metrics; the two settings you will compare
Course-topic link: which earlier topic, and how you will demonstrate it live
Risks and plan B (e.g. the dataset is too small, the model is too slow)
```

## Sample project ideas

1. **Course advisor assistant:** RAG over a course catalogue and regulations; cites the rule it used; recommends courses.
2. **Legal or policy assistant:** RAG over public laws or company policies, with article-level citations and metadata filters by chapter.
3. **Research paper finder:** embeddings of open-access abstracts in pgvector; "papers like this one" plus filters by year and category.
4. **Job matcher:** match CVs to job postings in both directions; links to the Week 1 careers assignment.
5. **Support ticket assistant:** retrieve similar past tickets and their solutions; evaluate with held-out tickets.
6. **Multilingual news recommender:** Macedonian, Albanian, Turkish and English articles with a multilingual embedding model; recommend similar articles across languages.

## Getting started

1. Run `labs/week12/` (RAG, evaluation, recommender in pgvector). It contains every technique the rubric asks for, at small scale.
2. Copy `projects/final-project-template/` into your team repository. Replace the data, labelled questions and README.
3. Measure early: run `python src/eval.py` from the first week, not the night before the deadline.
