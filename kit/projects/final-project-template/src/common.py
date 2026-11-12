"""Shared settings and helpers for the CE 502 final project template (settings come from .env)."""
import hashlib
import os
import re

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_env():
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_env()

DATA_DIR = os.path.join(ROOT, os.environ.get("DATA_DIR", "data"))
CHROMA_DIR = os.path.join(ROOT, os.environ.get("CHROMA_DIR", "chroma_store"))
COLLECTION = os.environ.get("COLLECTION", "docs")
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "100"))
TOP_K = int(os.environ.get("TOP_K", "4"))
NO_ANSWER_DISTANCE = float(os.environ.get("NO_ANSWER_DISTANCE", "0.9"))
DIM = 384

# ---- embeddings: sentence-transformers if available, else offline hashing fallback ----
_model = None
MODE = "hash"
if os.environ.get("EMBED_MODE", "auto") != "hash":
    try:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2"))
        MODE = "sentence-transformers"
    except Exception:
        _model = None


_STOP = set(
    "a an and the of to in on for with by as at is are be or from into that this "
    "such using use how what which their its it we you they our".split()
)


def _tokens(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    words = [w[:-1] if len(w) > 4 and w.endswith("s") else w for w in words]
    words = [w for w in words if w not in _STOP]
    bigrams = [a + "_" + b for a, b in zip(words, words[1:])]
    grams = ["#" + w[i:i + 4] for w in words if len(w) >= 5 for i in range(len(w) - 3)]
    return words + bigrams + grams


def _hash_vec(text):
    """Offline fallback (same as the course labs' embed.py): hashed words, word pairs and 4-letter pieces.
    It matches shared words, not meaning: use a real model for your reported results."""
    v = np.zeros(DIM, dtype=np.float32)
    for tok in _tokens(text):
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        sign = 1.0 if (h >> 20) & 1 else -1.0
        weight = 0.5 if "_" in tok else (0.35 if tok.startswith("#") else 1.0)
        v[h % DIM] += sign * weight
    n = np.linalg.norm(v)
    return v / n if n else v


def embed(texts):
    if isinstance(texts, str):
        texts = [texts]
    if _model is not None:
        return np.asarray(_model.encode(list(texts), normalize_embeddings=True), dtype=np.float32)
    return np.vstack([_hash_vec(t) for t in texts])


def describe():
    return f"embedding mode: {MODE} ({DIM} dims)"


def get_collection(create=False, path=None):
    """Open the Chroma collection (cosine distance, HNSW). create=True drops and re-creates it."""
    import chromadb

    client = chromadb.PersistentClient(path=path or CHROMA_DIR)
    if create:
        try:
            client.delete_collection(COLLECTION)
        except Exception:
            pass
        # older Chroma versions: metadata={"hnsw:space": "cosine"} instead of configuration=
        return client.create_collection(COLLECTION, configuration={"hnsw": {"space": "cosine"}},
                                        embedding_function=None)
    return client.get_collection(COLLECTION, embedding_function=None)
