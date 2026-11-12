# Practice 5 Report · Fragments as Partitions

**CE 502 · Week 5** · Name: ______________ · Student ID: ______________ · Date: ______________

> One PDF. Replace every *italic instruction* with your own text. Every output needs one sentence that names the rule or idea it proves: completeness, reconstruction, disjointness, minterm, implication or semi-join.

---

## 1. Part A · Exercise 1 on paper · 3 points

*Insert your paper solution. A readable photo of a handwritten page is fine. It must show:*

1. *the four simple predicates and the application each one comes from;*
2. *the number of minterms before elimination;*
3. *the implications between p1, p2 and p3;*
4. *the contradictory minterms, and why each is impossible;*
5. *the six fragments written with σ, with their rows;*
6. *a short argument for completeness, reconstruction and disjointness.*

| Fragment | Definition (σ … (PROJ)) | Rows |
|---|---|---|
| PROJ1 | | |
| PROJ2 | | |
| PROJ3 | | |
| PROJ4 | | |
| PROJ5 | | |
| PROJ6 | | |

## 2. Part A · Output of `02_primary.sql` explained · 2 points

| Section | Your output (short) | One sentence: what it proves |
|---|---|---|
| 1. Where each row went | | |
| 2. Completeness counts | | |
| 2b / line 4. The Tokyo error and the DEFAULT fix | | |
| 3. Reconstruction | | |
| 4. Disjointness | | |
| 5 / line 5. Plan for cheap Paris projects | | |

*Which is the better fix for a company that keeps opening offices: a DEFAULT partition or a new predicate p5? One or two sentences.*

## 3. Part B · Derived fragments and the two plans · 2 points

*Paste the site 1 / site 2 listing, the three checks and `SELECT * FROM emp1;`. Which property of the schema guarantees completeness, and which guarantees disjointness?*

*Paste both EXPLAIN plans, with the partition-wise join off and on.*

*In 2–3 sentences: what changed in the plan, and why does it correspond to local joins in a distributed database?*

## 4. Part C · ASG fragments in SQL · 2 points

| Minterm | Definition (σ … (ASG)) | Rows (eno, pno) |
|---|---|---|
| m1 | | |
| m2 | | |
| m3 | | |
| m4 | | |

*Are any minterms contradictory? Why or why not?*

*Paste your `my_asg.sql`, and its output showing where each row went, the reconstruction check (0 and 0) and the disjointness check.*

*Third predicate q3: dur ≥ 12. Is the set {q1, q2, q3} still minimal? Answer in 2–3 sentences, using the access patterns.*

## 5. Part C · Owner choice for ASG · 1 point

*5–8 lines: should ASG be derived from EMP or from PROJ in this company? Use rule 1 from Lesson 5-3 and the application table in the worksheet (Exercise 2, question 5). Say what happens to the join with the other owner, and why the owner's key keeps the derived fragments disjoint.*

---

### Declaration

I did this practice myself. Any help (classmates, AI tools, websites) is listed here: ______________
