#!/usr/bin/env python3
"""Add the reading summaries of one or more weeks to the CE 502 source decks.

    python tools/reading_summaries/run_week.py 4            # week 4
    python tools/reading_summaries/run_week.py 1 2 3        # several weeks
    python tools/reading_summaries/run_week.py 4 --dry-run  # build the slides only

For each week: check wNN.json, find the "Optional" slide of the deck's Papers to Read
section, build two slides per paper numbered to fit the section, insert them after that
slide, and renumber the section. The deck is the source deck in ../ce_502_db/slides
(the newest "Week N –" file). A deck that already has summaries is skipped.

Needs Windows with PowerPoint, Node with pptxgenjs (npm install in this folder), and
python-pptx. Afterwards, republish released weeks with tools/prepare_decks.py --weeks N.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from pptx import Presentation

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SRC = ROOT.parent / "ce_502_db" / "slides"
BUILD = HERE / "build"


def source_deck(n):
    found = [p for p in SRC.glob("*.pptx") if re.search(rf"Week {n} –", p.name)]
    if not found:
        sys.exit(f"no source deck for week {n} in {SRC}")
    return max(found, key=lambda p: p.stat().st_mtime)


def find_optional_slide(deck, n):
    """1-based index of the Optional slide in the Papers to Read section, and its 'k / total'."""
    prs = Presentation(str(deck))
    hit = None
    for i, s in enumerate(prs.slides, 1):
        texts = [sh.text_frame.text.strip() for sh in s.shapes if sh.has_text_frame]
        # Summary slides carry the heading "WEEK N · REQUIRED|OPTIONAL READING k · LABEL";
        # no original slide does.
        if any(re.match(rf"WEEK {n} · (REQUIRED|OPTIONAL) READING \d+ ·", t.upper()) for t in texts):
            sys.exit(f"week {n}: {deck.name} already contains reading summaries (slide {i})")
        if f"CE 502 · Week {n} · Papers to Read" in texts and "Optional" in texts:
            counter = next((t for t in texts if re.fullmatch(r"\d+ / \d+", t)), None)
            hit = (i, counter)
    if not hit:
        sys.exit(f"week {n}: no 'Optional' slide in the Papers to Read section of {deck.name}")
    return hit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("weeks", type=int, nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    BUILD.mkdir(exist_ok=True)
    for n in args.weeks:
        js = HERE / f"w{n:02d}.json"
        subprocess.run([sys.executable, str(HERE / "check_summaries.py"), js.name], check=True)
        papers = json.loads(js.read_text(encoding="utf-8"))
        deck = source_deck(n)
        after, counter = find_optional_slide(deck, n)
        k, old_total = map(int, counter.split(" / "))
        added = 2 * len(papers)
        out = BUILD / f"w{n:02d}_papers.pptx"
        subprocess.run(["node", str(HERE / "build_readings_deck.js"), str(js), str(n), str(out),
                        str(k + 1), str(old_total + added)], check=True, cwd=HERE)
        print(f"week {n}: {added} slides after slide {after} ({counter} -> section of {old_total + added})")
        if args.dry_run:
            continue
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                        str(HERE / "merge_into_weekly.ps1"), "-Weekly", str(deck),
                        "-Summary", str(out), "-After", str(after)], check=True)


if __name__ == "__main__":
    main()
