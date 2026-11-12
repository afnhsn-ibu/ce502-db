#!/usr/bin/env python3
"""Build the CE 502 course site from course.yml.

    python tools/build_site.py                      -> docs/  (what GitHub Pages serves)
    python tools/build_site.py --preview --out F    -> one self-contained file

Adapted from the DS 501 site builder. Labs here are Docker + SQL/Python folders in
kit/, not Colab notebooks, so week pages link to the lab README on GitHub and to a
zip of the whole kit (docs/downloads/ce502-db-kit.zip).
"""
import argparse
import html
import json
import re
import shutil
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
C = yaml.safe_load((ROOT / "course.yml").read_text(encoding="utf-8"))
CO, WEEKS = C["course"], C["weeks"]
REPO = CO["repo_slug"]
RELEASED = int(CO.get("released_through", 0))
KIT_ZIP = "downloads/ce502-db-kit.zip"
# readings.yml: one entry per paper, keyed by the citation text used in course.yml.
_RP = ROOT / "readings.yml"
PAPERS = (yaml.safe_load(_RP.read_text(encoding="utf-8")) or {}) if _RP.exists() else {}

NAV = [("index", "Schedule"), ("syllabus", "Syllabus"), ("assessments", "Assessments"),
       ("readings", "Papers"), ("setup", "Setup"), ("resources", "Resources")]

# Colours and fonts follow the CE 502 deck template (course_template.md, section 11).
CSS = """
:root{
  --navy:#14213D; --navy-card:#22335A; --accent:#B5491A; --accent-dark:#8F3712;
  --accent-light:#F2A65A; --paper:#F7F6F2; --card:#FFFFFC; --line:#DDD8CC;
  --ink:#22252B; --ink-soft:#2F3640; --muted:#5A6478;
  --green:#2E6B5E; --green-bg:#E9F2EE; --green-ink:#1E4D43;
  --chip:#E6E1D6; --band:#F1EFE8; --check:#EEF1F6; --on-dark:#F7F6F2; --on-dark-2:#C9D3E3;
  box-sizing:border-box;
  padding-top:env(safe-area-inset-top,0px); padding-bottom:env(safe-area-inset-bottom,0px);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#10151F; --card:#171E2B; --line:#2C3547;
    --ink:#EEF1F6; --ink-soft:#DCE2EC; --muted:#9AA6BA; --accent-dark:#F2A65A;
    --chip:#263047; --band:#151B27; --check:#1A2232; --green-bg:#16241F; --green-ink:#9FD3C5;
  }
}
:root[data-theme="dark"]{
  --paper:#10151F; --card:#171E2B; --line:#2C3547;
  --ink:#EEF1F6; --ink-soft:#DCE2EC; --muted:#9AA6BA; --accent-dark:#F2A65A;
  --chip:#263047; --band:#151B27; --check:#1A2232; --green-bg:#16241F; --green-ink:#9FD3C5;
}
*,*::before,*::after{box-sizing:inherit}
html{scroll-padding-top:calc(72px + env(safe-area-inset-top,0px));-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink-soft);
  font-family:"IBM Plex Sans",system-ui,sans-serif;
  font-size:18px;line-height:1.6;-webkit-font-smoothing:antialiased}
.mono{font-family:"JetBrains Mono",ui-monospace,monospace}
a{color:var(--accent-dark);text-underline-offset:2px}
.wrap{max-width:1060px;margin:0 auto;padding:0 28px}

body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);
  background:var(--navy);z-index:40}

header.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:30;background:var(--navy);
  color:var(--on-dark);border-bottom:3px solid var(--accent)}
.bar .wrap{display:flex;align-items:center;gap:22px;min-height:66px;flex-wrap:wrap}
.brand{font-weight:600;font-size:19px;color:var(--on-dark);text-decoration:none;
  display:flex;align-items:baseline;gap:10px}
.brand .code{font-family:"JetBrains Mono",monospace;color:var(--accent-light);letter-spacing:1px;
  white-space:nowrap}
nav.main{display:flex;gap:4px;margin-left:auto;flex-wrap:wrap}
nav.main a{color:var(--on-dark-2);text-decoration:none;font-size:16px;padding:7px 13px;
  border-radius:999px}
nav.main a:hover{background:var(--navy-card);color:#fff}
nav.main a[aria-current]{background:var(--accent-light);color:var(--navy);font-weight:600}
a:focus-visible,button:focus-visible{outline:3px solid var(--accent-light);outline-offset:2px}

.hero{background:var(--navy);color:var(--on-dark);padding:56px 0 48px}
.hero .eyebrow{font-family:"JetBrains Mono",monospace;color:var(--accent-light);
  letter-spacing:2px;font-size:14px;text-transform:uppercase;margin:0 0 14px}
.hero h1{font-size:clamp(34px,5.2vw,54px);line-height:1.08;margin:0 0 14px;font-weight:600;
  color:var(--on-dark);max-width:18ch}
.hero .sub{color:var(--on-dark-2);max-width:62ch;margin:0 0 34px;font-size:19px}
.path{display:flex;flex-wrap:wrap;align-items:center;gap:10px}
.path span{background:var(--navy-card);border:1px solid rgba(242,166,90,.35);
  border-radius:999px;padding:8px 17px;font-size:16px;color:var(--on-dark)}
.path span:last-child{background:var(--accent-light);color:var(--navy);font-weight:600;
  border-color:var(--accent-light)}
.path i{color:var(--accent-light);font-style:normal}
.meta{margin-top:30px;color:var(--on-dark-2);font-size:16px;
  border-top:1px solid rgba(247,246,242,.22);padding-top:18px}

main{padding:46px 0 70px}
h2{font-size:30px;font-weight:600;color:var(--navy);margin:46px 0 14px;
  padding-bottom:7px;border-bottom:2px solid var(--chip)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) h2{color:#C9D3E3}}
:root[data-theme="dark"] h2{color:#C9D3E3}
h2:first-child{margin-top:0}
h3{font-size:21px;font-weight:600;color:var(--ink);margin:30px 0 8px}
p{max-width:72ch}

.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px}
table.sched{width:100%;border-collapse:collapse;font-size:16px;min-width:720px}
table.sched th{background:var(--navy);color:var(--on-dark);text-align:left;
  padding:13px 15px;font-weight:600}
table.sched td{padding:14px 15px;border-bottom:1px solid var(--line);vertical-align:top}
table.sched tr:nth-child(even) td{background:var(--band)}
table.sched tr:last-child td{border-bottom:none}
.wk a{font-family:"JetBrains Mono",monospace;color:var(--accent);text-decoration:none;
  font-weight:600;white-space:nowrap}
.wk a:hover{text-decoration:underline}
.topic b{color:var(--ink);font-size:17px}
.lessonlist{color:var(--muted);font-size:15px;line-height:1.5}
.lessonlist .mono{color:var(--accent)}
.due{font-family:"JetBrains Mono",monospace;font-size:14px;color:var(--muted)}
.mats a{display:inline-block;margin-right:9px;font-size:15px}

.weekhead{display:flex;gap:34px;align-items:flex-start;background:var(--navy);
  color:var(--on-dark);border-radius:16px;padding:34px 38px;margin-bottom:8px}
.weekhead .n{font-family:"JetBrains Mono",monospace;font-size:76px;font-weight:600;
  line-height:.85;color:var(--accent-light)}
.weekhead h1{margin:0 0 8px;font-size:34px;font-weight:600;color:var(--on-dark)}
.weekhead p{margin:0;color:var(--on-dark-2);max-width:60ch}
.lesson{display:flex;gap:16px;align-items:baseline;padding:13px 2px;border-bottom:1px solid var(--line)}
.lesson .c{font-family:"JetBrains Mono",monospace;color:var(--accent);font-weight:600;
  min-width:52px;white-space:nowrap}
ul{max-width:72ch}
li{margin:5px 0}

.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px 26px;
  margin:14px 0}
.card h3{margin:0 0 4px}
.card .chips{font-family:"JetBrains Mono",monospace;font-size:14px;color:var(--muted)}
.keypoint{background:var(--navy);color:var(--on-dark);border-radius:14px;padding:20px 26px}
.keypoint b{color:var(--accent-light)}
.keypoint p{color:var(--on-dark);margin:0}
.practice{background:var(--green-bg);border-left:7px solid var(--green);border-radius:10px;
  padding:20px 26px}
.practice b{color:var(--green-ink)}
.btn{display:inline-block;margin-top:12px;background:var(--navy);color:var(--on-dark);
  text-decoration:none;font-family:"JetBrains Mono",monospace;font-size:15px;
  padding:10px 20px;border-radius:999px;margin-right:8px}
.btn:hover{background:var(--accent);color:#fff}
.btn.alt{background:transparent;color:var(--navy);border:2px solid var(--navy)}
.btn.alt:hover{background:var(--navy);color:var(--on-dark)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .btn.alt{color:var(--accent-light);border-color:var(--accent-light)}
  :root:not([data-theme="light"]) .btn{background:var(--navy-card)}}
:root[data-theme="dark"] .btn.alt{color:var(--accent-light);border-color:var(--accent-light)}
.soon{color:var(--muted);font-style:italic}
.plinks{display:block;font-size:14px;margin-top:2px;color:var(--muted)}
.plinks a{margin-right:2px}
.plinks .free{color:var(--green-ink);font-weight:600}
code,pre{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:.88em}
code{background:var(--chip);padding:1px 6px;border-radius:5px}
pre{background:var(--navy);color:var(--on-dark);padding:16px 20px;border-radius:10px;
  overflow-x:auto;max-width:100%}
pre code{background:none;padding:0;color:inherit}
.pager{display:flex;justify-content:space-between;gap:14px;margin-top:44px;
  border-top:1px solid var(--line);padding-top:20px;font-size:16px}

footer{background:var(--navy);color:var(--on-dark-2);padding:34px 0;font-size:15px}
footer a{color:var(--accent-light)}
footer .wrap{display:flex;gap:18px;flex-wrap:wrap;justify-content:space-between}

@media (max-width:640px){
  body{font-size:17px}
  .wrap{padding:0 16px}
  .weekhead{flex-direction:column;gap:14px;padding:26px}
  .weekhead .n{font-size:54px}
  .hero{padding:40px 0 34px}
  nav.main{margin-left:0;width:100%}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=IBM+Plex+Sans:ital,wght@0,400;0,600;0,700;1,400&'
         'family=JetBrains+Mono:wght@400;600&display=swap">')


def e(s):
    return html.escape(str(s), quote=False)


def gh(path):
    """A file or folder of the repository, as GitHub renders it."""
    kind = "tree" if path.endswith("/") else "blob"
    return f'{CO["repo"]}/{kind}/main/{path.rstrip("/")}'


def released(w):
    return w["num"] <= RELEASED


def deck(w, ext):
    return f"slides/{w['deck']}.{ext}" if w.get("deck") else None


def nav(active, single):
    out = []
    for key, label in NAV:
        href = f"#{key}" if single else ("index.html" if key == "index" else f"{key}.html")
        cur = ' aria-current="page"' if key == active else ""
        out.append(f'<a href="{href}"{cur}>{e(label)}</a>')
    return "".join(out)


def link(key, single):
    return f"#{key}" if single else f"{key}.html"


def kit_link(single):
    # The preview is one file with nowhere to put the zip, so it points at GitHub.
    return f'{CO["repo"]}/archive/refs/heads/main.zip' if single else KIT_ZIP


# ------------------------------------------------------------------ pages
def page_index(single):
    rows = []
    for w in WEEKS:
        n = w["num"]
        ms = C["milestones"].get(n)
        extra = f"<br>{e(ms)}" if ms else ""
        href = link(f"week{n:02d}", single)
        rows.append(
            f'<tr><td class="wk"><a href="{href}">Week {n}</a></td>'
            f'<td class="topic"><b>{e(w["title"])}</b>'
            f'<div class="lessonlist">P{n} · {e(w["practice"])}</div></td>'
            f'<td class="lessonlist">'
            + "<br>".join(f'<span class="mono">{c}</span> {e(t)}' for c, t in w["lessons"])
            + "</td>"
            + (f'<td class="mats"><a href="{deck(w, "pdf")}">Slides</a>'
               f'<a href="{gh("kit/labs/" + w["lab"] + "/README.md")}">Lab</a></td>'
               if released(w) else '<td class="mats"><span class="soon">Coming soon</span></td>')
            + f'<td class="due">Practice [date]<br>Quiz [date]{extra}</td></tr>'
        )
    chips = '<i>→</i>'.join(f"<span>{e(s)}</span>" for s in CO["story"])
    return (
        f'<section class="hero"><div class="wrap">'
        f'<p class="eyebrow">{e(CO["code"])} · {e(CO["level"])}</p>'
        f'<h1>{e(CO["title"])}</h1>'
        f'<p class="sub">{e(CO["blurb"])}</p>'
        f'<div class="path">{chips}</div>'
        f'<p class="meta">{e(CO["meeting"])} &nbsp;·&nbsp; '
        f'{e(CO["institution"])}, {e(CO["city"])} &nbsp;·&nbsp; {e(CO["semester"])}</p>'
        f"</div></section>"
        f'<main><div class="wrap">'
        f"<h2>Schedule</h2>"
        f"<p>Everything for a week is on that week’s page: the deck, the practice, the quiz "
        f"and the papers. Dates are placeholders until the semester calendar is fixed.</p>"
        f'<div class="tablewrap"><table class="sched">'
        f'<tr><th style="width:9%">Week</th><th style="width:30%">Topic and practice</th>'
        f'<th style="width:30%">Lessons</th><th style="width:12%">Materials</th>'
        f'<th style="width:19%">Due</th></tr>'
        + "".join(rows) + "</table></div>"
        f"<h2>Before the first class</h2>"
        f'<p>Install Docker and start the course database by following the '
        f'<a href="{link("setup", single)}">setup guide</a>. It takes about 20 minutes, '
        f"most of it waiting for the first download, and Practice 1 starts from a running "
        f'container. Then read the <a href="{link("syllabus", single)}">syllabus</a>.</p>'
        f'<div class="keypoint"><p><b>Key point:</b> every week answers one question: what '
        f"does the database have to do so that the data is still correct, still there and "
        f"still fast when something goes wrong or grows?</p></div>"
        f"</div></main>"
    )


def page_syllabus(single):
    arows = "".join(
        f'<tr><td><b>{e(a["item"])}</b></td><td class="due">{e(a["weight"])}</td>'
        f'<td>{e(a["detail"])}</td></tr>' for a in C["assessment"])
    books = "".join(
        f'<li>{e(b["citation"])}'
        f'<span class="plinks"><b>{e(b["weeks"])}</b>'
        + (f' · <span class="free">{e(b["free"])}</span>' if b.get("free")
           else ' · <span class="soon">IBU library access</span>')
        + "".join(f' · <a href="{e(u)}">{e(t)}</a>' for t, u in b["links"])
        + "</span></li>" for b in C["books"])
    return (
        f'<main><div class="wrap"><h2>Syllabus</h2>'
        f'<p>{e(CO["code"])} is a {e(CO["level"].lower())} course at {e(CO["institution"])}, '
        f'{e(CO["city"])}. It assumes an undergraduate databases course: you can design a '
        f"relational schema and write SQL joins and aggregates. Everything beyond that is "
        f"built in the lessons.</p>"
        f"<p>The course follows one story: <b>one database</b> that must survive crashes and "
        f"concurrent users (Weeks 1–3), <b>many databases</b> that must behave like one "
        f"(Weeks 4–6), <b>analytics and scale</b> (Weeks 7–9), and <b>AI-era databases</b> "
        f"that search by meaning (Weeks 10–12).</p>"
        f'<p>{e(CO["meeting"])}</p>'
        f"<h3>How a week runs</h3>"
        f"<ul><li>Three lessons of 45 minutes, each with a scenario worked in pairs and one "
        f"Check Your Understanding question.</li>"
        f"<li>One practice in the course database, started in class and finished as homework, "
        f"with a short report.</li>"
        f"<li>A quiz of 15–16 multiple-choice questions, plus one short design question "
        f"from Week 2 on.</li>"
        f"<li>Two or three required papers, with a half-page note due at the next class.</li></ul>"
        f"<h2>Marking</h2>"
        f'<div class="tablewrap"><table class="sched">'
        f'<tr><th style="width:24%">Component</th><th style="width:12%">Weight</th>'
        f'<th style="width:64%">Notes</th></tr>{arows}</table></div>'
        f"<p>Weights come from the syllabus document and must match this table before "
        f'the semester starts. The briefs and rubrics are on the '
        f'<a href="{link("assessments", single)}">Assessments</a> page.</p>'
        f"<h2>Using AI tools</h2>"
        f"<p>You may use an AI assistant to explain concepts, debug your own code and SQL, "
        f"and improve your writing. You must be able to explain every line you submit. Work "
        f"you cannot explain is treated as work you did not do.</p>"
        f"<p>State in your submission which tool you used and what for. That statement "
        f"costs you no marks. Omitting it does. Lab reports ask for numbers you measured in "
        f"your own container; numbers that do not match your run are marked as missing.</p>"
        f"<h2>Companion texts</h2><ul>{books}</ul>"
        f"<p>None is required to buy; all are in the IBU library. The weeks next to each book "
        f"show where it supports the course.</p>"
        f"<h2>Tools</h2>"
        f'<p>{e(CO["tools"])} Everything runs in Docker on your own laptop, on Windows, '
        f'macOS or Linux. See <a href="{link("setup", single)}">Setup</a>.</p>'
        f"</div></main>"
    )


def page_assessments(single):
    cards = []
    for a in C["assignments"]:
        extra = "".join(f'<a class="btn alt" href="{gh("kit/" + p)}">{e(t)}</a>'
                        for t, p in a.get("extra", []))
        cards.append(
            f'<div class="card"><h3>{e(a["title"])}</h3>'
            f'<p class="chips">Set in Week {a["set"]} · due {e(a["due"])} · '
            f'{e(a["points"])} points</p>'
            f'<p>{e(a["summary"])}</p>'
            f'<a class="btn" href="{gh("kit/" + a["file"])}">Read the brief</a>{extra}</div>')
    return (
        f'<main><div class="wrap"><h2>Assessments</h2>'
        f"<p>Besides the weekly practices and quizzes, the course has four assignments, a "
        f"midterm and a final project. Each brief states the task, what to submit and the "
        f"rubric it is marked with. Dates are set in class.</p>"
        + "".join(cards)
        + f"<h2>Practices</h2>"
        f"<p>Every week has a practice in the course database. Each lab README lists every "
        f"command with the output you should see, and ends with a report template. Submit "
        f"the report with the numbers you measured in your own container. Find each one on "
        f'its week page from the <a href="{link("index", single)}">schedule</a>.</p>'
        f"<h2>Peer review</h2>"
        f"<p>The careers, big data and relational-problem assignments are peer-reviewed. "
        f"You review three classmates’ reports against the published rubric, and the "
        f"instructor moderates the marks. A review with scores but no reasons costs the "
        f"reviewer marks.</p>"
        f"</div></main>"
    )


def paper_li(key):
    """One reading-list entry: the citation plus its PDF / free copy / DOI links."""
    p = PAPERS.get(key)
    if not p:
        return f"<li>{e(key)}</li>"
    links = []
    if p.get("pdf"):
        lic = f" ({e(p['license'])})" if p.get("license") else ""
        links.append(f'<a href="readings/{e(p["pdf"])}">PDF{lic}</a>')
    if p.get("free_url"):
        links.append(f'<a href="{e(p["free_url"])}">Free full text</a>')
    if p.get("doi"):
        links.append(f'<a href="https://doi.org/{e(p["doi"])}">DOI {e(p["doi"])}</a>')
    elif p.get("url"):
        links.append(f'<a href="{e(p["url"])}">Publisher page</a>')
    if not p.get("pdf") and not p.get("free_url"):
        links.append('<span class="soon">IBU library access</span>')
    return (f'<li>{e(p.get("citation", key))}'
            f'<span class="plinks">{" · ".join(links)}</span></li>')


def guide_html(w):
    if not (released(w) and w.get("reading_guide")):
        return ""
    return (f'<p class="plinks" style="font-size:16px;margin-top:10px">'
            f'<b>Reading guide:</b> what to read in each paper, what to skip and the '
            f'questions to answer · <a href="{gh("kit/" + w["reading_guide"])}">Open the guide</a></p>')


def page_readings(single):
    out = []
    for w in WEEKS:
        req = "".join(paper_li(r) for r in w["required"])
        opt = "".join(paper_li(r) for r in w["optional"])
        out.append(
            f'<h3>Week {w["num"]} · {e(w["title"])}</h3>'
            f"<p><b>Required</b></p><ul>{req}</ul>"
            f'<p style="color:var(--muted)"><b>Optional</b></p><ul>{opt}</ul>'
            + guide_html(w))
    return (
        f'<main><div class="wrap"><h2>Papers to read</h2>'
        f"<p>Each week has two or three required papers and two or three optional ones. "
        f"The deck says which sections to read. For every required paper, bring a half-page "
        f"note to the next class: the problem, the key idea, and how it connects to the "
        f'week. Use the <a href="{gh("kit/readings/paper-note-template.md")}">paper note '
        f"template</a>. One quiz question each week may refer to the required reading.</p>"
        f'<div class="practice"><p><b>In practice</b> Week 1 teaches Keshav’s three-pass '
        f"method. Use the first pass on every paper here, and all three on the ones you "
        f"build your final project on.</p></div>"
        + "".join(out)
        + "<p><b>Finding the papers.</b> <i>Free full text</i> links go to a legal free "
          "copy on the publisher’s, author’s or arXiv site. Papers marked <i>IBU library "
          "access</i> have no legal free copy: open the DOI link from the university "
          "network or ask the IBU library.</p></div></main>"
    )


def page_setup(single):
    return (
        f'<main><div class="wrap"><h2>Setup</h2>'
        f"<p>Do this <b>before the Week 1 class</b>. It takes about 20 minutes, mostly "
        f"waiting for the first image download. You do not install PostgreSQL itself: "
        f"everything runs in a container.</p>"
        f"<h3>What you need</h3>"
        f"<ul><li><b>Docker:</b> Docker Desktop on Windows or macOS, or Docker Engine with "
        f"the Compose plugin on Linux.</li>"
        f"<li><b>About 2 GB</b> of free disk for Weeks 1–8. Week 9 adds MongoDB and "
        f"Cassandra (about 1.5 GB more, and at least 4 GB of RAM for Docker). Weeks 10–12 "
        f"add Python AI packages (about 2 GB).</li>"
        f"<li><b>Python 3.10 or later</b> from Week 3 on.</li></ul>"
        f"<h3>Get the course kit</h3>"
        f"<p>The kit holds the Docker setup, every lab, the assignments and the project "
        f"template. Labs are added as the weeks are released, so download it again, or "
        f"<code>git pull</code>, each week.</p>"
        f'<a class="btn" href="{kit_link(single)}" download>Download the kit (zip)</a>'
        f'<a class="btn alt" href="{gh("kit/")}">Browse it on GitHub</a>'
        f"<p>Or clone the repository:</p>"
        f'<pre><code>git clone {e(CO["repo"])}.git\ncd {e(REPO.split("/")[1])}/kit</code></pre>'
        f"<h3>Start the database</h3>"
        f"<p>In a terminal (PowerShell on Windows) opened in the kit folder, the one that "
        f"contains <code>docker-compose.yml</code>:</p>"
        f"<pre><code>docker compose up -d --build\ndocker compose ps</code></pre>"
        f"<p>Wait until <code>ce502-postgres</code> shows <b>healthy</b>, then run the setup "
        f"check described in the full guide.</p>"
        f'<a class="btn" href="{gh("kit/setup/SETUP.md")}">Full setup guide and troubleshooting</a>'
        f"<h3>Extra services later in the course</h3>"
        f'<div class="tablewrap"><table class="sched">'
        f"<tr><th>When</th><th>Command</th><th>Adds</th></tr>"
        f"<tr><td>Week 2 demo</td><td><code>docker compose --profile replication up -d</code></td>"
        f"<td>A streaming replica</td></tr>"
        f"<tr><td>Weeks 9 and 11</td><td><code>docker compose --profile nosql up -d</code></td>"
        f"<td>MongoDB and Cassandra</td></tr>"
        f"<tr><td>Week 11, optional</td><td><code>docker compose --profile atlas up -d</code></td>"
        f"<td>Local MongoDB with vector search</td></tr>"
        f"<tr><td>Week 3 on</td><td><code>pip install -r setup/requirements.txt</code></td>"
        f"<td>Python packages for the labs</td></tr>"
        f"<tr><td>Week 10 on</td><td><code>pip install -r setup/requirements-ai.txt</code></td>"
        f"<td>Chroma and sentence-transformers</td></tr></table></div>"
        f'<div class="keypoint" style="margin-top:26px"><p><b>Key point:</b> '
        f"<code>docker compose down</code> stops the containers and keeps your data. "
        f"<code>docker compose down -v</code> deletes all of it.</p></div>"
        f"</div></main>"
    )


def page_resources(single):
    docs = [("PostgreSQL 16 documentation", "https://www.postgresql.org/docs/16/"),
            ("pgvector", "https://github.com/pgvector/pgvector"),
            ("MongoDB manual", "https://www.mongodb.com/docs/manual/"),
            ("Apache Cassandra documentation", "https://cassandra.apache.org/doc/latest/"),
            ("DuckDB documentation", "https://duckdb.org/docs/"),
            ("Chroma documentation", "https://docs.trychroma.com/"),
            ("Docker documentation", "https://docs.docker.com/")]
    return (
        f'<main><div class="wrap"><h2>Resources</h2>'
        f"<h3>Running the labs</h3>"
        f'<p>Every lab runs in the course containers; see <a href="{link("setup", single)}">'
        f"Setup</a>. Each command is a single <code>docker exec …</code> line or a Python "
        f"command on your laptop, so it works the same on Windows, macOS and Linux. "
        f"Generated data uses fixed seeds: everyone gets the same counts and totals, so use "
        f"them to check your report.</p>"
        f"<h3>References you will use every week</h3><ul>"
        + "".join(f'<li><a href="{u}">{e(t)}</a></li>' for t, u in docs)
        + "</ul>"
        f"<h3>Getting help</h3>"
        f"<p>Ask in class, in the course channel, or in office hours. If a lab command "
        f"fails, bring the command, the full error message and the output of "
        f"<code>docker compose ps</code>.</p>"
        f"<h3>Fixing this site</h3>"
        f'<p>This site is a public repository. Found a broken link, a wrong date or a '
        f'typo? <a href="{e(CO["repo"])}/issues">Open an issue</a> or send a pull '
        f"request. Corrections are welcome and credited.</p>"
        f"</div></main>"
    )


def page_week(w, single):
    n = w["num"]
    lessons = "".join(
        f'<div class="lesson"><span class="c">{c}</span><span>{e(t)}</span></div>'
        for c, t in w["lessons"])
    req = "".join(paper_li(r) for r in w["required"])
    opt = "".join(paper_li(r) for r in w["optional"])
    ms = C["milestones"].get(n)
    msline = f"<li><b>{e(ms)}:</b> [date]</li>" if ms else ""
    lab = f'kit/labs/{w["lab"]}/'
    act = w.get("activity")
    acthtml = (f'<p>In class: <a href="{gh("kit/" + act[1])}">{e(act[0])}</a></p>'
               if act and released(w) else "")
    prev = (f'<a href="{link(f"week{n-1:02d}", single)}">← Week {n-1}: '
            f'{e(WEEKS[n-2]["title"])}</a>') if n > 1 else "<span></span>"
    nxt = (f'<a href="{link(f"week{n+1:02d}", single)}">Week {n+1}: '
           f'{e(WEEKS[n]["title"])} →</a>') if n < len(WEEKS) else "<span></span>"
    return (
        f'<main><div class="wrap">'
        f'<div class="weekhead"><div class="n">{n:02d}</div><div>'
        f"<h1>{e(w['title'])}</h1><p>{e(w['purpose'])}</p></div></div>"
        f"<h2>Lessons</h2>{lessons}{acthtml}"
        f"<h2>Slides</h2>"
        f"<p>One deck covers all the lessons, the practice and the papers. The speaker notes "
        f"are written as student reading text, so the deck and its notes together are the "
        f"week’s handout.</p>"
        + (f'<a class="btn" href="{deck(w, "pdf")}">View slides (PDF)</a>'
           f'<a class="btn alt" href="{deck(w, "pptx")}" download>'
           f'PowerPoint with speaker notes</a>'
           if released(w) and w.get("deck") else
           '<p class="soon">Slides are posted before the class.</p>')
        + f"<h2>Practice {n}</h2>"
        f'<div class="practice"><p><b>{e(w["practice"])}</b> — {e(w["services"])}</p>'
        f"<p>Follow the lab README in the course kit. It lists every command with the "
        f"output you should see. Submit the report template with the numbers you measured "
        f"in your own container.</p>"
        + (f'<a class="btn" href="{gh(lab + "README.md")}">Open the lab</a>'
           f'<a class="btn alt" href="{gh(lab + "report-template.md")}">Report template</a>'
           f'<a class="btn alt" href="{kit_link(single)}" download>Download the kit</a>'
           if released(w) else '<p class="soon">The lab is posted before the class.</p>')
        + "</div>"
        f"<h2>Quiz</h2>"
        f"<p>15–16 multiple-choice questions, 25–30 minutes, covering lessons "
        f"{w['lessons'][0][0]} to {w['lessons'][-1][0]}. Questions use the wording of the "
        f"Key Terms slides. <i>[Link]</i></p>"
        f"<h2>Papers</h2><p><b>Required</b></p><ul>{req}</ul>"
        f'<p style="color:var(--muted)"><b>Optional</b></p><ul>{opt}</ul>'
        + guide_html(w) +
        f"<h2>Due this week</h2>"
        f"<ul><li><b>Practice {n} report:</b> [date]</li>"
        f"<li><b>Quiz {n}:</b> [date]</li>"
        f"<li><b>Paper notes:</b> at the next class</li>{msline}</ul>"
        f'<div class="pager">{prev}{nxt}</div>'
        f"</div></main>"
    )


def shell(title, body, active, single, router=""):
    css_ref = f"<style>{CSS}</style>" if single else '<link rel="stylesheet" href="assets/ce502.css">'
    return (
        f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1, '
        f'viewport-fit=cover">'
        f"<title>{e(title)}</title>"
        f'<meta name="description" content="{e(CO["code"])} {e(CO["title"])} at '
        f'{e(CO["institution"])}: schedule, slides, labs, assessments and papers.">'
        f"{FONTS}{css_ref}</head><body>"
        f'<header class="bar"><div class="wrap">'
        f'<a class="brand" href="{link("index", single)}">'
        f'<span class="code">{e(CO["code"])}</span>'
        f'<span>{e(CO["title"])}</span></a>'
        f'<nav class="main">{nav(active, single)}</nav></div></header>'
        f'<div id="root">{body}</div>'
        f'<footer><div class="wrap">'
        f'<span>{e(CO["institution"])}, {e(CO["city"])}</span>'
        f'<span><a href="{e(CO["instructor_page"])}">{e(CO["instructor"])}</a> · '
        f'{e(CO["semester"])}</span>'
        f'<span><a href="{e(CO["repo"])}">Source on GitHub</a></span>'
        f"</div></footer>{router}</body></html>"
    )


def build_bodies(single):
    pages = {
        "index": (f'{CO["code"]} · {CO["title"]}', page_index(single)),
        "syllabus": (f'Syllabus · {CO["code"]}', page_syllabus(single)),
        "assessments": (f'Assessments · {CO["code"]}', page_assessments(single)),
        "readings": (f'Papers to read · {CO["code"]}', page_readings(single)),
        "setup": (f'Setup · {CO["code"]}', page_setup(single)),
        "resources": (f'Resources · {CO["code"]}', page_resources(single)),
    }
    for w in WEEKS:
        pages[f"week{w['num']:02d}"] = (
            f'Week {w["num"]} · {w["title"]} · {CO["code"]}', page_week(w, single))
    return pages


def write_kit_zip(dest):
    """kit/ as ce502-db-kit/..., stored uncompressed with fixed timestamps and LF line
    endings, so the same kit gives the same bytes on every machine."""
    kit = ROOT / "kit"
    if not kit.exists():
        raise SystemExit("kit/ is missing: run tools/sync_kit.py first")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_STORED) as z:
        for p in sorted(kit.rglob("*")):
            if p.is_dir():
                continue
            data = p.read_bytes()
            if b"\0" not in data:
                data = data.replace(b"\r\n", b"\n")
            info = zipfile.ZipInfo("ce502-db-kit/" + p.relative_to(kit).as_posix(),
                                   (1980, 1, 1, 0, 0, 0))
            info.create_system = 3  # Unix, whatever machine builds it
            info.external_attr = (0o755 if p.suffix == ".sh" else 0o644) << 16
            z.writestr(info, data)


def check_papers():
    missing = [k for w in WEEKS for k in w["required"] + w["optional"] if k not in PAPERS]
    if missing:
        print(f"note: {len(missing)} papers have no readings.yml entry yet "
              f"(shown as plain text)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true",
                    help="write one self-contained file instead of docs/")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    check_papers()

    if args.preview:
        pages = build_bodies(True)
        bodies = {k: v[1] for k, v in pages.items()}
        router = (
            "<script>(function(){var P=" + json.dumps(bodies).replace("</", "<\\/") + ";"
            "var r=document.getElementById('root');"
            "function go(){var k=(location.hash||'#index').slice(1);"
            "if(!P[k])k='index';r.innerHTML=P[k];"
            "var base=k.indexOf('week')===0?'index':k;"
            "document.querySelectorAll('nav.main a').forEach(function(a){"
            "a.toggleAttribute('aria-current',a.getAttribute('href')==='#'+base)});"
            "window.scrollTo(0,0);}"
            "window.addEventListener('hashchange',go);go();})();</script>")
        out = Path(args.out or ROOT / "ce502-preview.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(shell(pages["index"][0], "", "index", True, router), encoding="utf-8")
        print(f"{out}  {out.stat().st_size/1024:.0f} kB")
        return

    docs = ROOT / "docs"
    (docs / "assets").mkdir(parents=True, exist_ok=True)
    (docs / "assets" / "ce502.css").write_text(CSS, encoding="utf-8", newline="\n")
    (docs / ".nojekyll").write_text("", encoding="utf-8")
    write_kit_zip(docs / KIT_ZIP)
    # Openly licensed papers: copy readings/<file>.pdf into docs/readings/.
    rout = docs / "readings"
    shutil.rmtree(rout, ignore_errors=True)
    for key, pp in PAPERS.items():
        if pp.get("pdf"):
            src = ROOT / "readings" / pp["pdf"]
            if not src.exists():
                raise SystemExit(f"missing readings/{pp['pdf']} for {key}")
            rout.mkdir(exist_ok=True)
            shutil.copyfile(src, rout / src.name)
    # Published decks: copy slides/<deck>.pdf|.pptx for released weeks into docs/slides/.
    out = docs / "slides"
    shutil.rmtree(out, ignore_errors=True)
    for w in WEEKS:
        if not (released(w) and w.get("deck")):
            continue
        out.mkdir(exist_ok=True)
        for ext in ("pdf", "pptx"):
            src = ROOT / f"slides/{w['deck']}.{ext}"
            if not src.exists():
                raise SystemExit(f"missing {src.relative_to(ROOT)} for week {w['num']}")
            shutil.copyfile(src, out / src.name)
    for key, (title, body) in build_bodies(False).items():
        active = "index" if key.startswith("week") else key
        (docs / f"{key}.html").write_text(shell(title, body, active, False),
                                          encoding="utf-8", newline="\n")
        print("wrote docs/" + key + ".html")


if __name__ == "__main__":
    main()
