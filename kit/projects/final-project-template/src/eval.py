"""Evaluate retrieval: recall@k and MRR on the labelled set eval/questions.csv (question, expected_source).

A hit = a retrieved chunk whose source file equals expected_source; adapt is_hit() to your data
(e.g. a document id, a section, or for a recommender a held-out item of the test user).

Run:  python src/eval.py                              # the current collection (after ingest.py)
      python src/eval.py --settings 300:60,500:100,800:0   # compare chunking settings (rebuilds temporary copies)
The brief requires >= 20 labelled cases and at least two settings compared.
"""
import csv
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, describe, get_collection  # noqa: E402
from query import retrieve  # noqa: E402

KS = (1, 3, 5)


def load_rows():
    with open(os.path.join(ROOT, "eval", "questions.csv"), newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r["question"].strip()]


def is_hit(hit, row):
    return hit["source"] == row["expected_source"]


def score(col, rows, verbose=False):
    found = {k: 0 for k in KS}
    rr = 0.0
    for r in rows:
        hits = retrieve(r["question"], k=max(KS), col=col)
        rank = next((n for n, h in enumerate(hits, 1) if is_hit(h, r)), None)
        rr += 1 / rank if rank else 0
        for k in KS:
            found[k] += 1 if rank and rank <= k else 0
        if verbose:
            print(f"{'ok  ' if rank == 1 else 'MISS' if not rank else f'@{rank}  '} {r['question']}")
    n = len(rows)
    return {k: found[k] / n for k in KS}, rr / n


def main():
    rows = load_rows()
    print(describe())
    if len(rows) < 20:
        print(f"note: only {len(rows)} labelled questions; the brief requires at least 20")
    if "--settings" in sys.argv:
        from ingest import build
        spec = sys.argv[sys.argv.index("--settings") + 1]
        print(f"\n{'chunk size':>10} {'overlap':>8} {'chunks':>7} " + " ".join(f"{'recall@' + str(k):>9}" for k in KS) + f" {'MRR':>6}")
        for item in spec.split(","):
            size, overlap = (int(x) for x in item.split(":"))
            path = os.path.join(ROOT, f"chroma_eval_{size}_{overlap}")
            col, _ = build(size, overlap, path=path)
            rec, mrr = score(col, rows)
            print(f"{size:>10} {overlap:>8} {col.count():>7} " + " ".join(f"{rec[k]:>9.2f}" for k in KS) + f" {mrr:>6.2f}")
            shutil.rmtree(path, ignore_errors=True)
        print(f"(n = {len(rows)} labelled questions)")
        return
    rec, mrr = score(get_collection(), rows, verbose=True)
    print("\n" + "  ".join(f"recall@{k}={rec[k]:.2f}" for k in KS) + f"  MRR={mrr:.2f}  (n={len(rows)})")


if __name__ == "__main__":
    main()
