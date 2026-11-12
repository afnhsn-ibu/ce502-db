# Reading summaries

Two slides per paper, placed in the **Papers to Read** section of each weekly deck,
after the optional-reading slide and before the reading questions.

- `w01.json` to `w12.json`: the text of each summary (two slides per paper, with speaker
  notes), one object per paper in course.yml order (required first). `course_key` is the
  exact course.yml string.
- `check_summaries.py`: checks every file against the box sizes, the course.yml order,
  British spelling and the readings.yml citations. Run it after every edit.
- `build_readings_deck.js`: turns one file into slides in the CE 502 deck style.
- `merge_into_weekly.ps1`: inserts those slides into a deck and renumbers the section.
- `run_week.py`: does all of it for one or more weeks, on the source decks in
  `../ce_502_db/slides` (the private instructor repository).

```bash
npm install                                        # pptxgenjs 3.12.0, once
python tools/reading_summaries/check_summaries.py  # all weeks
python tools/reading_summaries/run_week.py 6       # add week 6's summaries to its deck
python tools/prepare_decks.py --weeks 6            # republish a released week
```

`run_week.py` refuses a deck that already has summaries. To change a summary after it
has been merged, restore the deck from the instructor repository's history, edit the JSON
and run it again. It needs Windows with PowerPoint, and the deck fonts (IBM Plex Sans,
JetBrains Mono) installed.
