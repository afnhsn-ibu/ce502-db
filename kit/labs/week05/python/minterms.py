"""CE 502 · Practice 5 · Minterm generator for primary horizontal fragmentation.

A minterm is a conjunction of EVERY simple predicate, each taken as-is or negated
(Özsu & Valduriez). With n predicates there are 2**n minterms before elimination.

This script:
  1. enumerates all 2**n minterms,
  2. removes minterms that are contradictory for the attribute domains
     (implications such as loc='Montreal' -> loc != 'Paris'),
  3. applies the remaining minterms to the rows, so you can also see which
     fragments are empty for the current data.

Run on your laptop (no database needed), from the kit folder:
    python3 labs/week05/python/minterms.py

Exercise 2 (ASG): copy this file, replace PROJ, PREDICATES and the domain samples
with ASG's data and q1/q2, and use it to check your answer.
"""
from itertools import product

# --- The relation (PROJ from 01_schema.sql) ---------------------------------
PROJ = [
    ("P1", "Instrumentation",   150000, "Montreal"),
    ("P2", "Database Develop.", 135000, "New York"),
    ("P3", "CAD/CAM",           250000, "New York"),
    ("P4", "Maintenance",       310000, "Paris"),
    ("P5", "Analytics",         180000, "Paris"),
    ("P6", "Cloud Migration",   400000, "Montreal"),
]

# --- Simple predicates --------------------------------------------------------
PREDICATES = {
    "p1: loc='Montreal'": lambda r: r[3] == "Montreal",
    "p2: loc='New York'": lambda r: r[3] == "New York",
    "p3: loc='Paris'":    lambda r: r[3] == "Paris",
    "p4: budget<=200000": lambda r: r[2] <= 200000,
}

# --- Attribute domains, used to decide which minterms are contradictory --------
LOC_DOMAIN = ["Montreal", "New York", "Paris"]          # all locations that may ever exist
BUDGET_SAMPLES = [0, 200000, 200001, 10**9]              # values on both sides of the cut


def satisfiable(signs):
    """A minterm is satisfiable if SOME possible tuple makes it true."""
    preds = list(PREDICATES.values())
    for loc in LOC_DOMAIN:
        for budget in BUDGET_SAMPLES:
            row = ("?", "?", budget, loc)
            if all(p(row) == s for p, s in zip(preds, signs)):
                return True
    return False


def label(signs):
    names = [n.split(": ")[1] for n in PREDICATES]
    return " ∧ ".join(n if s else f"¬({n})" for n, s in zip(names, signs))


def main():
    n = len(PREDICATES)
    all_minterms = list(product([True, False], repeat=n))
    print(f"{n} simple predicates -> {len(all_minterms)} minterms before elimination\n")

    valid = []
    for signs in all_minterms:
        ok = satisfiable(signs)
        print(f"  {'keep' if ok else 'drop'}  {label(signs)}")
        if ok:
            valid.append(signs)

    print(f"\n{len(valid)} minterms remain -> {len(valid)} fragments\n")
    preds = list(PREDICATES.values())
    for i, signs in enumerate(valid, 1):
        rows = [r[0] for r in PROJ if all(p(r) == s for p, s in zip(preds, signs))]
        print(f"  PROJ{i}: {label(signs):60s} rows: {', '.join(rows) or '(empty)'}")

    # Correctness checks on the current data
    assigned = [r[0] for r in PROJ for signs in valid
                if all(p(r) == s for p, s in zip(preds, signs))]
    print("\nCompleteness:", "OK" if sorted(set(assigned)) == sorted(r[0] for r in PROJ) else "FAIL")
    print("Disjointness:", "OK" if len(assigned) == len(set(assigned)) else "FAIL")


if __name__ == "__main__":
    main()
