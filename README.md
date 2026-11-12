# CE 502 · Advanced Topics in Database Systems — course site

Public course site and student lab kit for CE 502 at International Balkan University, Skopje.
Live at https://afnhsn-ibu.github.io/ce502-db/

## Students: get the lab kit

```bash
git clone https://github.com/afnhsn-ibu/ce502-db.git
cd ce502-db/kit
docker compose up -d --build
```

Then follow [kit/setup/SETUP.md](kit/setup/SETUP.md). Each week's lab is in `kit/labs/weekNN/`.
Labs are added as the weeks are released, so `git pull` each week.

## How it is put together

`course.yml` is the single source of truth: the 12 weeks, their lessons, practices,
papers, assessments and milestones. `readings.yml` holds the full citation and links for
every paper. `tools/build_site.py` turns them into the finished HTML in `docs/`. The site
uses the CE 502 deck identity: navy `#14213D`, orange `#B5491A` / `#F2A65A`, paper
`#F7F6F2`, IBM Plex Sans and JetBrains Mono.

```bash
pip install pyyaml
python tools/sync_kit.py               # student kit -> kit/ (released weeks only)
python tools/prepare_decks.py          # released decks -> slides/ (+ PDF, Windows + PowerPoint)
python tools/build_site.py             # writes docs/
python -m http.server -d docs 8000     # look at it locally
```

Never edit anything in `docs/` or `kit/` by hand; both are overwritten. Edit the kit in
`ce502-kit-student` (and the same file in `ce502-kit-instr`), then run `sync_kit.py`.

## Releasing the next week

1. Raise `released_through` in `course.yml`.
2. `python tools/sync_kit.py` (adds that week's lab to `kit/`).
3. `python tools/prepare_decks.py` (copies the deck, fills `[Instructor name]`, exports the PDF).
4. `python tools/build_site.py`, then commit `course.yml`, `kit/`, `slides/` and `docs/`.

## Setup

In **Settings → Pages**, set the source to branch `main`, folder `/docs`. There is nothing
to install on the server and no build step in the cloud. The included Action only checks
that `docs/` was rebuilt after `course.yml` or `kit/` changed.

## What is public and what is not

| Public, this repository | Private, `ce502-db-instructor` |
|---|---|
| Site pages, `course.yml`, `readings.yml` | Practice solutions and code keys |
| `kit/`: labs, setup, assignments, project template, sample midterm, quizzes | Quiz keys, reading answers, marking guides |
| Slide decks of released weeks | Instructor guides, reference runs (`sample-output/`) |

Nothing under `instructor/` belongs in this repository. `tools/sync_kit.py` refuses to
copy a kit that contains it.

## Corrections

Students and colleagues: open an issue or send a pull request. Corrections are welcome
and credited.
