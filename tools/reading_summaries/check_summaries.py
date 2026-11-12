#!/usr/bin/env python3
"""Check reading-summary JSON files before building slides.

    python tools/reading_summaries/check_summaries.py            # every wNN.json present
    python tools/reading_summaries/check_summaries.py w04.json   # one file

Limits are the longest texts that fit the slide boxes (taken from the DS 501
summaries, which use the same layout). Exit code 1 if anything fails.
"""
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
C = yaml.safe_load((ROOT / "course.yml").read_text(encoding="utf-8"))
PAPERS = yaml.safe_load((ROOT / "readings.yml").read_text(encoding="utf-8"))

# field: (min chars, max chars)
STR = {
    "label": (4, 26), "short_title": (15, 54), "citation": (60, 330),
    "problem": (140, 235), "slide2_title": (25, 56), "course_link": (110, 190),
    "limitation": (90, 150), "note_question": (80, 135),
    "notes_slide1": (800, 1150), "notes_slide2": (800, 1150),
}
LIST = {"key_ideas": (60, 104), "findings": (60, 108)}
US = r"\b(analyz\w*|organiz\w*|optimiz\w*|normaliz\w*|characteriz\w*|summariz\w*|minimiz\w*|maximiz\w*|" \
     r"generaliz\w*|serializ\w*|materializ\w*|prioritiz\w*|categoriz\w*|visualiz\w*|behavior\w*|color\w*|" \
     r"center\w*|modeling|modeled|labeled|labeling|favor\w*|catalog|license[ds]?)\b"
ALLOWED_US = {"serializable", "serializability", "serialization", "serialized", "materialized",
              "license", "catalog"}  # SQL / product terms keep their official spelling


def check(path):
    errs = []
    n = int(re.search(r"w(\d+)\.json$", path.name).group(1))
    week = next(w for w in C["weeks"] if w["num"] == n)
    want = [("Required", k) for k in week["required"]] + [("Optional", k) for k in week["optional"]]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as ex:  # noqa: BLE001
        return [f"{path.name}: not valid JSON: {ex}"]
    if len(data) != len(want):
        errs.append(f"{len(data)} papers, course.yml has {len(want)}")
    for i, (p, (kind, key)) in enumerate(zip(data, want), 1):
        tag = f"paper {i} ({p.get('label', '?')})"
        if p.get("kind") != kind:
            errs.append(f"{tag}: kind {p.get('kind')!r}, expected {kind!r} (same order as course.yml)")
        if p.get("course_key") != key:
            errs.append(f"{tag}: course_key must be exactly the course.yml string {key!r}")
        for f, (lo, hi) in STR.items():
            v = p.get(f)
            if not isinstance(v, str) or not v.strip():
                errs.append(f"{tag}: missing {f}")
            elif not lo <= len(v) <= hi:
                errs.append(f"{tag}: {f} is {len(v)} chars, allowed {lo}-{hi}")
        for f, (lo, hi) in LIST.items():
            v = p.get(f)
            if not isinstance(v, list) or len(v) != 3:
                errs.append(f"{tag}: {f} must be a list of exactly 3")
                continue
            for j, s in enumerate(v, 1):
                if not lo <= len(s) <= hi:
                    errs.append(f"{tag}: {f}[{j}] is {len(s)} chars, allowed {lo}-{hi}")
        kt = p.get("key_term") or {}
        if not kt.get("term") or not kt.get("definition"):
            errs.append(f"{tag}: key_term needs term and definition")
        elif not (len(kt["term"]) <= 24 and 60 <= len(kt["definition"]) <= 115
                  and len(kt["term"]) + len(kt["definition"]) <= 133):
            errs.append(f"{tag}: key_term too long (term {len(kt['term'])}/24, "
                        f"definition {len(kt['definition'])}/115, together max 133)")
        ref = PAPERS.get(key, {}).get("citation")
        if ref and p.get("citation") and not p["citation"].startswith(ref[:40]):
            errs.append(f"{tag}: citation should start with the readings.yml citation")
        # Citations keep official titles exactly (e.g. "Generalizing", "Modeling"), so they
        # are left out of the spelling and placeholder checks.
        parts = []
        for f, v in p.items():
            if f in ("citation", "course_key"):
                continue
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, list):
                parts.extend(v)
            elif isinstance(v, dict):
                parts.extend(str(x) for x in v.values())
        text = " ".join(parts)
        for m in set(re.findall(US, text, re.I)):
            if m.lower() not in ALLOWED_US:
                errs.append(f"{tag}: US spelling {m!r} (course uses British spelling)")
        if re.search(r"\[[^\]]*\]", text):
            errs.append(f"{tag}: contains a [placeholder]")
    return [f"{path.name}: {e}" for e in errs]


def main():
    files = [HERE / a for a in sys.argv[1:]] or sorted(HERE.glob("w[0-9][0-9].json"))
    errs = [e for f in files for e in check(f)]
    print("\n".join(errs) if errs else f"OK: {', '.join(f.name for f in files)}")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
