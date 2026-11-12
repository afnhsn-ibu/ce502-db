#!/usr/bin/env python3
"""Copy the released weeks' decks into slides/ under their course.yml names, and export PDFs.

    python tools/prepare_decks.py               # every released week that is missing
    python tools/prepare_decks.py --weeks 3 4   # just these weeks (overwrites)
    python tools/prepare_decks.py --no-pdf      # skip the PowerPoint export

Source decks are "CE 502 · Week N – Title*.pptx" in ../ce_502_db/slides. The newest
file wins when there are several copies, e.g. "(3)" and "(4)".
Only [Instructor name] is filled in; [Semester], [date] and [__%] stay as placeholders
until the semester is fixed (set FILL below when they are).

The PDF export drives PowerPoint through COM, so it needs Windows with PowerPoint and the
deck fonts (IBM Plex Sans, JetBrains Mono) installed. Without them PowerPoint substitutes
a font and the PDF can repeat words at line breaks.
"""
import argparse
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT.parent / "ce_502_db" / "slides"
C = yaml.safe_load((ROOT / "course.yml").read_text(encoding="utf-8"))
FILL = {"[Instructor name]": C["course"]["instructor"]}


def source_deck(n):
    found = [p for p in SRC.glob("*.pptx")
             if re.search(rf"Week {n} –", p.name)]
    if not found:
        sys.exit(f"no source deck for week {n} in {SRC}")
    return max(found, key=lambda p: p.stat().st_mtime)


def copy_filled(src, dst):
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith(".xml"):
                text = data.decode("utf-8")
                for k, v in FILL.items():
                    text = text.replace(k, v)
                data = text.encode("utf-8")
            zout.writestr(item, data)


PS_EXPORT = r"""
$ErrorActionPreference = 'Stop'
$pp = New-Object -ComObject PowerPoint.Application
try {
  foreach ($f in $args) {
    # PowerPoint occasionally fails a COM call on one deck; one retry is enough.
    foreach ($try in 1, 2) {
      try {
        $p = $pp.Presentations.Open($f, $true, $false, $false)
        $p.SaveAs([IO.Path]::ChangeExtension($f, '.pdf'), 32)
        $p.Close()
        Write-Output ('pdf: ' + [IO.Path]::GetFileName($f))
        break
      } catch {
        if ($p) { try { $p.Close() } catch {} }
        if ($try -eq 2) { throw }
        Start-Sleep -Seconds 2
      }
    }
  }
} finally { $pp.Quit() }
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weeks", type=int, nargs="*")
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()
    rel = int(C["course"]["released_through"])
    weeks = [w for w in C["weeks"]
             if (w["num"] in args.weeks if args.weeks else w["num"] <= rel)]
    out = ROOT / "slides"
    out.mkdir(exist_ok=True)
    todo = []
    for w in weeks:
        dst = out / f"{w['deck']}.pptx"
        if dst.exists() and not args.weeks:
            continue
        src = source_deck(w["num"])
        copy_filled(src, dst)
        print(f"week {w['num']}: {src.name} -> slides/{dst.name}")
        todo.append(str(dst))
    if todo and not args.no_pdf:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-Command", f"& {{{PS_EXPORT}}} " + " ".join(f"'{t}'" for t in todo)],
                       check=True)


if __name__ == "__main__":
    main()
