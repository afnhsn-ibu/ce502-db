"""Query: retrieve top-k chunks for a question and answer with an LLM (or extractively).

Run:  python src/query.py "your question"
Optional LLM [test before class]: set ANTHROPIC_API_KEY or OPENAI_API_KEY and LLM_MODEL in .env.
Without one, the answer is the retrieved sentence closest to the question, with its source number.
"""
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import NO_ANSWER_DISTANCE, TOP_K, embed, get_collection  # noqa: E402


def retrieve(question, k=TOP_K, where=None, col=None):
    col = col or get_collection()
    res = col.query(query_embeddings=embed(question).tolist(), n_results=k, where=where)
    return [{"id": i, "text": d, "source": m["source"], "distance": dist}
            for i, d, m, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0])]


def make_prompt(question, hits):
    ctx = "\n\n".join(f"[{n}] ({h['source']}) {h['text']}" for n, h in enumerate(hits, 1))
    return ("Answer using ONLY the context. If the answer is not there, say you do not know. "
            f"Cite sources like [1].\n\nContext:\n{ctx}\n\nQuestion: {question}\nAnswer:")


def llm(prompt):
    model = os.environ.get("LLM_MODEL")
    if os.environ.get("ANTHROPIC_API_KEY") and model:
        import anthropic
        r = anthropic.Anthropic().messages.create(model=model, max_tokens=500,
                                                  messages=[{"role": "user", "content": prompt}])
        return r.content[0].text
    if os.environ.get("OPENAI_API_KEY") and model:
        from openai import OpenAI
        r = OpenAI().chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}])
        return r.choices[0].message.content
    return None


def extractive(question, hits):
    sents = [(s, n) for n, h in enumerate(hits, 1)
             for s in re.split(r"(?<=[.!?])\s+", h["text"]) if len(s) > 20]
    if not sents:
        return "I do not know."
    scores = embed([s for s, _ in sents]) @ embed(question)[0]
    s, n = sents[int(np.argmax(scores))]
    return f"{s} [{n}]"


def answer(question):
    hits = retrieve(question)
    if not hits or hits[0]["distance"] > NO_ANSWER_DISTANCE:      # handle "no answer" (rubric: application quality)
        return "I do not know: nothing in the collection is close to this question.", hits
    out = llm(make_prompt(question, hits))
    return (out if out else "(extractive) " + extractive(question, hits)), hits


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What is this collection about?"
    a, hits = answer(q)
    for n, h in enumerate(hits, 1):
        print(f"[{n}] {h['id']}  distance={h['distance']:.3f}")
    print(f"\nQ: {q}\nA: {a}")
