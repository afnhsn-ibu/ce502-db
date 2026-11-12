"""Ingest = the one-command pipeline: load .txt / .md files from DATA_DIR, chunk, embed, store in Chroma.

Run:  python src/ingest.py           (re-creates the collection from scratch every time)
TODO for your project: replace load_documents() with your own loader (CSV, PDF, web pages, a database),
choose a chunking strategy, and record your choices in the report.
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CHUNK_OVERLAP, CHUNK_SIZE, DATA_DIR, describe, embed, get_collection  # noqa: E402


def load_documents():
    docs = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "**", "*.*"), recursive=True)):
        if path.endswith((".txt", ".md")):
            docs.append({"source": os.path.relpath(path, DATA_DIR), "text": open(path, encoding="utf-8").read()})
    return docs


def chunk(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = " ".join(text.split())
    out, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            sp = text.rfind(" ", start, end)
            end = sp if sp > start else end
        out.append(text[start:end])
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return out


def build(size=CHUNK_SIZE, overlap=CHUNK_OVERLAP, path=None):
    """Load, chunk, embed and store. Returns the collection. Used by main() and by eval.py --settings."""
    docs = load_documents()
    if not docs:
        sys.exit(f"No .txt or .md files found in {DATA_DIR}")
    ids, texts, metas = [], [], []
    for d in docs:
        for i, c in enumerate(chunk(d["text"], size, overlap)):
            ids.append(f"{d['source']}#{i}")
            texts.append(c)
            metas.append({"source": d["source"], "chunk": i})
    col = get_collection(create=True, path=path)
    batch = 500
    for s in range(0, len(ids), batch):
        col.add(ids=ids[s:s + batch], documents=texts[s:s + batch],
                metadatas=metas[s:s + batch], embeddings=embed(texts[s:s + batch]).tolist())
    return col, len(docs)


def main():
    col, n_docs = build()
    print(describe())
    print(f"{n_docs} documents -> {col.count()} chunks stored (chunk size {CHUNK_SIZE}, overlap {CHUNK_OVERLAP})")


if __name__ == "__main__":
    main()
