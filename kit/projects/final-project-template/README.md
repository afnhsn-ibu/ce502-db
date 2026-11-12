# CE 502 Final Project · Starter Template (RAG on Chroma)

A small, working RAG pipeline to copy into your team's repository and extend. It runs end to end on the three sample documents in `data/`; replace them with your own dataset of at least 1,000 documents or items. The brief is `projects/final-project.md`.

```
src/common.py     settings (.env), embeddings, the Chroma collection
src/ingest.py     the one-command pipeline: load -> chunk -> embed -> store (re-creates the collection)
src/query.py      retrieve top-k -> prompt -> LLM, or an extractive answer; "I do not know" below a threshold
src/eval.py       recall@k and MRR on eval/questions.csv; --settings compares chunking settings
data/             your documents (.txt / .md); 3 sample files included
eval/             questions.csv (question, expected_source): 20 labelled examples to replace with yours
.env.example      every setting; copy to .env
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                       # Windows: copy .env.example .env
python src/ingest.py
python src/query.py "How many students are in a project team?"
python src/eval.py
python src/eval.py --settings 300:60,500:100,800:0
```

Expected with the offline embeddings (`EMBED_MODE=hash`) and the sample data; the full output is in `eval/baseline_output_hash_embeddings.txt`:

```
3 documents -> 9 chunks stored (chunk size 500, overlap 100)
recall@1=0.70  recall@3=1.00  recall@5=1.00  MRR=0.83  (n=20)

chunk size  overlap  chunks  recall@1  recall@3  recall@5    MRR
       300       60      16      0.75      1.00      1.00   0.87
       500      100       9      0.70      1.00      1.00   0.83
       800        0       6      0.70      1.00      1.00   0.83
```

**Embeddings.** `sentence-transformers` (all-MiniLM-L6-v2, 384 dimensions) is used if it is installed and the model can be downloaded. Otherwise the template uses an offline hashing fallback, the same as the Week 10–12 labs, so the pipeline always runs. The fallback matches words, not meaning: **report your results with a real model** and say which one.

**LLM (optional) [test before class].** Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` and `LLM_MODEL` in `.env`, and install the client. Without one, `query.py` answers with the retrieved sentence closest to the question and its source number. If even the best chunk is farther than `NO_ANSWER_DISTANCE`, it answers "I do not know". Calibrate that threshold on your own labelled questions. Never commit `.env`; `.gitignore` excludes it.

## What your team must change (mapped to the rubric)

| Rubric item | In this template | Your job |
|---|---|---|
| Data pipeline (15) | `load_documents()` and `chunk()` in `src/ingest.py` | Load your dataset (CSV, PDF text, web pages, a database export). Keep useful metadata (date, category, language) for filters. Document cleaning and chunking choices. One command must rebuild everything. |
| Database and index design (15) | Chroma, cosine distance, default HNSW | Justify the database and index with measurements, e.g. recall and latency for two settings. Or switch to pgvector (below). |
| Application quality (15) | `src/query.py` prints sources and distances; "I do not know" | Build your interface (CLI, notebook or a simple web page). Show sources or scores. Handle "no answer". |
| Evaluation (20) | `eval/questions.csv` (20 examples), `src/eval.py` | At least 20 labelled cases **from your data**. Compare two settings: chunk size, embedding model or index parameters. Discuss the failures. For a recommender, label held-out items per test user and adapt `is_hit()`. |
| Link to an earlier topic (10) | – | Implement and **show live**: e.g. back up and restore the vector store, update vectors and metadata in one transaction, partition by date, or a usage cube. |
| Report and repository (5) | This README | Rewrite it so another student can run your project on a clean machine: prerequisites, database start, ingest, app, eval, expected numbers. |

## Switching to PostgreSQL + pgvector

The course container already has pgvector 0.8.0. In your own `docker-compose.yml`, you can use the image `pgvector/pgvector:0.8.0-pg16`.

1. Create a table with a `vector(384)` column plus your metadata columns, and an HNSW index:

   ```sql
   CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);
   ```

   See `labs/week12/sql/01_schema.sql`.
2. Replace `col.add` in `ingest.py` with inserts using `psycopg` and `pgvector.psycopg.register_vector`, inside one transaction (`labs/week12/python/load_courses_pg.py`).
3. Replace `retrieve` in `query.py` with:

   ```sql
   SELECT id, text, source, embedding <=> %s AS distance FROM chunks ORDER BY embedding <=> %s LIMIT %s
   ```

4. Your course link becomes easy to demonstrate. For example, back up with `pg_dump` and restore (Week 2), or update text and embedding in one transaction (Weeks 1 and 3).

## Course-link example: back up and restore the Chroma store (Week 2)

```bash
python src/ingest.py
mkdir -p backups && cp -r chroma_store backups/chroma_store_$(date +%Y%m%d)    # back up
rm -rf chroma_store                                                             # "disaster"
cp -r backups/chroma_store_* chroma_store                                       # restore
python src/eval.py                                                              # prove: same numbers as before
```

Chroma stores its data in files under `chroma_store/`. Copy it only while no process is writing to it, the same rule as a cold backup in Week 2.
