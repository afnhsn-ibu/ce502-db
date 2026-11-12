# CE 502 · Paper Note Template

Write **one note per required paper**, about **half a page** (150–250 words). Bring your notes to the next lesson: they are the basis of the class discussion and of the reading questions. Notes are not graded separately, but they will save you a great deal of time when you revise for the quizzes and the midterm.

Write in your own words. Copying sentences from the abstract does not help you understand the paper.

---

**Paper:** *Title* – Authors, Venue, Year

**Week:** __ · **Sections read:** ______ · **Passes completed:** ☐ 1 ☐ 2 ☐ 3 · **Date:** ______

### 1. The problem (2–3 sentences)

What problem does the paper address? What was wrong, slow, unsafe or missing before it? Who had this problem?

> 

### 2. The key idea (3–4 sentences)

What is the main contribution? Explain it as you would to a classmate who has not read the paper. If there is one figure or example that explains it best, name it.

> 

### 3. Link to this week (2–3 sentences)

Which lesson, slide or practice step does this paper explain? Where do you see its idea in a real system today (for example in PostgreSQL)?

> 

### 4. One question (1 sentence)

Something you did not understand, disagree with, or want to discuss in class.

> 

### Key terms I met (optional)

| Term | My one-line definition |
|---|---|
| | |
| | |

---

## Example (Week 1, shortened)

**Paper:** *Principles of Transaction-Oriented Database Recovery* – T. Haerder, A. Reuter, ACM Computing Surveys, 1983 · **Sections read:** 1–3 · **Passes:** 1, 2

1. **Problem.** In the early 1980s every database system recovered from failures in its own way, described with its own vocabulary, so it was hard to compare designs or to say what "recovery" should guarantee.
2. **Key idea.** The authors define what a transaction must guarantee, summarised as ACID, and classify the failures a system must survive (transaction, system and media failures) and the recovery actions each needs. With this framework, any recovery design can be described by what it logs and when it writes pages to disk.
3. **Link.** Lessons 1-3 and 1-4: undo with before images gives atomicity, redo with after images gives durability. Media failure is the topic of Week 2.
4. **Question.** Why is consistency in ACID the application's job as well as the DBMS's?
