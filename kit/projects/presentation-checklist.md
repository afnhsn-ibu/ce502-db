# Final Project · Presentation and Demo Checklist

Use this the day before and 15 minutes before your slot (slides p12-overview and p12-demo).

## The day before

- [ ] **Five-part talk, 10 minutes:** problem 1 · data and pipeline 2 · database and index design + course link 2 · demo 3 · evaluation and lessons 2. Rehearsed with a timer.
- [ ] **Every team member speaks**, and each can explain any part of the system: questions go to everyone.
- [ ] **Course-topic link shown live in part 3**, not only described:
  - a backup and restore;
  - a transaction that updates vectors and metadata together, committing or rolling back as a whole;
  - partition pruning in a query plan;
  - a usage cube.
- [ ] **One evaluation slide:** metric, the settings compared, **test-set size** (≥ 20), results. 0.9 on 20 questions is a weaker claim than 0.9 on 200, so say n.
- [ ] **Two or three prepared queries**, including **one the system answers badly**, with your explanation of why.
- [ ] **Sources or scores visible** for every answer or recommendation: retrieved chunks with citations, similarity scores, or "because you liked X".
- [ ] **Fallback screen recording** (1–2 minutes) of the demo working, saved on the presentation machine.
- [ ] Demo tested **on the presentation machine**, on the network you will have there.
- [ ] Repository README tested on a clean machine, or by a classmate.

## 15 minutes before your slot

- [ ] Containers started (`docker compose up -d`, then `docker compose ps` shows healthy); data loaded; index built.
- [ ] One test query run successfully.
- [ ] Embedding model already downloaded and cached. **No downloads, installs or re-indexing during the talk.**
- [ ] API keys set in the environment if you use an LLM. Not visible on screen.
- [ ] Recording, slides and terminal windows open; font size large enough for the back row.

## Questions you should be able to answer

- Why this database and this index? What are its parameters, and how did you choose them?
- What happens if the database server fails during the demo? Where is your backup?
- What would change with ten times more data? With many users at the same time?
- Why did the failing test question fail? What would you change first?
- Which data did you **not** use, and why (licence, privacy, quality)?
