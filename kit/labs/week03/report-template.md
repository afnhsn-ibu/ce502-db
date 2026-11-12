# Practice 3 Report · Race Yourself

**CE 502 · Week 3** · Name: ______________ · Student ID: ______________ · Date: ______________

> One PDF, at most 3 pages. Replace every *italic instruction* with your own text. Link every observation to a concept from Lessons 3-1 to 3-3.

---

## 1. E1 · Deadlock · 2 points

*Insert a screenshot of the `deadlock detected` error, with both terminals visible if possible.*

| Question | Your answer |
|---|---|
| Which session was aborted? | |
| Final balances of rows 1 and 2 | |

*In 4–6 sentences: draw or describe the wait-for graph at step 5. Why was one session aborted and why did the other finish? Which ordering rule in the application would prevent this deadlock?*

## 2. Anomaly table from your own runs · 3 points

| Experiment | Read Committed: what you saw | Anomaly? | Repeatable Read: what you saw | Anomaly? |
|---|---|---|---|---|
| E2 Non-repeatable read | second read = | | second read = | |
| E3 Lost update | final balance = | | B's UPDATE: | |
| E4 Phantom | count = __ → __ | | count = __ → __ | |

*One sentence per experiment: which mechanism produced the result at each level? Use statement snapshot, transaction snapshot, row lock or serialization failure.*

## 3. E4 at Repeatable Read · 1 point

*In 3–4 sentences: the SQL standard allows phantoms at Repeatable Read. Why did PostgreSQL show none? Name the technique PostgreSQL uses and the anomaly it still allows. Hint: optional experiment E5.*

## 4. Part B · Lost update in Python · 2 points

| Mode | Final balance |
|---|---|
| naive | |
| for_update | |
| atomic | |

*Why does `naive` lose updates without any error? Write out the interleaving of two threads that loses one increment. Why does each fix reach 500? 5–8 sentences.*

## 5. Handling `deadlock detected` and `could not serialize access` · 2 points

*Explain what an application should do when it receives SQLSTATE `40P01` (deadlock) or `40001` (serialization failure). Cover: which work must be repeated, how many times, what to do between attempts, and what must **not** happen inside the transaction because it might run twice, for example sending an e-mail. Pseudo-code or a short code excerpt is welcome. 6–10 sentences.*

---

### Optional: extension results (not marked)

*E5 results at the three levels, and/or the output of `retry_demo.py`, with one sentence each.*

### Declaration

I did this practice myself. Any help (classmates, AI tools, websites) is listed here: ______________
