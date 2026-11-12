#!/usr/bin/env python3
"""Copy the student course kit into kit/, for released weeks only.

    python tools/sync_kit.py                       # default source folders
    python tools/sync_kit.py --src PATH --instr PATH

The student kit (ce502-kit-student) is the source. The instructor kit
(ce502-kit-instr) is used only as a check: every file the two kits share must be
identical, so a fix made in one copy is never missing from the other.

Labs for weeks after `released_through` in course.yml are left out, the same way
DS 501 only publishes the notebooks of released weeks. Run it again after raising
`released_through`, then run tools/build_site.py.
"""
import argparse
import filecmp
import re
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT.parent / "ce_502_db"
SKIP_DIRS = {".venv", "__pycache__", ".pytest_cache", ".git", "instructor"}
SKIP_FILES = re.compile(r".*\.pyc$")
# Anything that looks like instructor material stops the sync.
FORBIDDEN = re.compile(r"(^|/)instructor(/|$)|solution|_key\.|-key\.|reading-answers|model-answer|marking|sample-output",
                       re.I)


def files(base):
    for p in sorted(base.rglob("*")):
        rel = p.relative_to(base)
        if any(part in SKIP_DIRS for part in rel.parts) or p.is_dir() or SKIP_FILES.match(p.name):
            continue
        yield rel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(WORK / "ce502-kit-student"))
    ap.add_argument("--instr", default=str(WORK / "ce502-kit-instr"))
    args = ap.parse_args()
    src, instr = Path(args.src), Path(args.instr)
    if not (src / "docker-compose.yml").exists():
        sys.exit(f"not a course kit: {src}")

    released = int(yaml.safe_load((ROOT / "course.yml").read_text(encoding="utf-8"))
                   ["course"]["released_through"])

    # 1. Nothing instructor-only in the student kit.
    if (src / "instructor").exists():
        sys.exit(f"{src / 'instructor'} exists: the student kit must not contain it")
    bad = [r.as_posix() for r in files(src) if FORBIDDEN.search(r.as_posix())]
    if bad:
        sys.exit("instructor-looking files in the student kit:\n  " + "\n  ".join(bad))

    # 2. Shared files identical in both kits (READMEs differ on purpose).
    if instr.exists():
        drift = [r.as_posix() for r in files(src)
                 if r.as_posix() != "README.md" and (instr / r).exists()
                 and not filecmp.cmp(src / r, instr / r, shallow=False)]
        if drift:
            sys.exit("student and instructor kits differ; fix one of them first:\n  "
                     + "\n  ".join(drift))
    else:
        print(f"note: {instr} not found, skipped the drift check")

    # 3. Copy, leaving out unreleased labs.
    out = ROOT / "kit"
    shutil.rmtree(out, ignore_errors=True)
    n = held = 0
    for rel in files(src):
        m = re.match(r"labs/week(\d\d)/", rel.as_posix())
        if m and int(m.group(1)) > released:
            held += 1
            continue
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src / rel, dst)
        n += 1
    print(f"kit/: {n} files copied, {held} held back (labs after week {released})")


if __name__ == "__main__":
    main()
