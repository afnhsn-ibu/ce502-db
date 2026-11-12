# Practice 5 · Fragments as Partitions: From Minterms to PostgreSQL

**CE 502 · Week 5** · Individual · about 60 minutes in class, finished at home · 10 points
**Lessons:** 5-1 Distributed Design and Correctness, 5-2 Primary Horizontal Fragmentation, 5-3 Derived Horizontal Fragmentation
**Submit:** one PDF before the Week 6 class. Use `report-template.md`.

This practice turns the week's theory into PostgreSQL partitions that you can query and test. It uses the same company schema as the lessons:

```
PAY(title, sal) 1—N EMP(eno, ename, title) 1—N ASG(eno, pno, resp, dur) N—1 PROJ(pno, pname, budget, loc)
```

| Part | What you do | Lesson objective |
|---|---|---|
| Setup | Create the database `week05`: PAY 4 rows, EMP 8, PROJ 6, ASG 12 | – |
| A | Minterms for PROJ on paper; six fragments as LIST and RANGE partitions; correctness checks; the Tokyo error; partition pruning | 5-2 O2–O4 · 5-1 O4 |
| B | EMP derived from PAY with semi-joins; a partition-wise join in EXPLAIN | 5-3 O2, O4 |
| C | Fragment ASG on your own and choose its owner | 5-2 O4 · 5-3 O3 |

| File | Purpose |
|---|---|
| `sql/01_schema.sql` | Creates the database `week05` and loads the four relations |
| `sql/02_primary.sql` | Part A: PROJ as six partitions, correctness checks, Tokyo error, pruning |
| `sql/03_derived.sql` | Part B: PAY fragments, EMP derived with EXISTS, partition-wise join |
| `python/minterms.py` | Enumerates minterms and removes contradictory ones (runs on your laptop) |
| `minterm-worksheet.md` | Exercise 1 (PROJ, Part A) and Exercise 2 (ASG, Part C) |
| `my_asg.sql` | **Your** Part C SQL, a starter file. Edit it on your laptop |
| `report-template.md` | Structure of your report |

---

## Before you start

```bash
docker compose up -d
docker exec -u postgres ce502-postgres bash /kit/setup/check_setup.sh      # all [ OK ]
```

Open psql in the course container. You will stay in this one session for Parts A and B:

```bash
docker exec -it ce502-postgres psql -U postgres -d lab
```

> **Do Exercise 1 of `minterm-worksheet.md` on paper first.** The scripts in Part A show the answer.

---

## Setup (2 min)

In psql:

```sql
\i /kit/labs/week05/sql/01_schema.sql
```

The script drops and re-creates the database `week05`, **connects your session to it**, and loads the data:

```
You are now connected to database "week05" as user "postgres".
 tbl  | count
------+-------
 pay  |     4
 emp  |     8
 proj |     6
 asg  |    12
```

The data is small on purpose, so you can check every result by hand: `SELECT * FROM proj;`, `SELECT * FROM asg;`.

> **Common mistake:** running `02_primary.sql` before `01_schema.sql`, or in the `lab` database. The prompt must say `week05=#`. If it says `lab=#`, type `\c week05`.

---

## Part A · Six fragments of PROJ as partitions (25 min)

### A1 · Check your paper answer

On your laptop, from the kit folder (no database needed):

```bash
python3 labs/week05/python/minterms.py
```

```
4 simple predicates -> 16 minterms before elimination

  drop  loc='Montreal' ∧ loc='New York' ∧ loc='Paris' ∧ budget<=200000
  …
  keep  loc='Montreal' ∧ ¬(loc='New York') ∧ ¬(loc='Paris') ∧ budget<=200000
  …
6 minterms remain -> 6 fragments

  PROJ1: loc='Montreal' ∧ … ∧ budget<=200000      rows: P1
  PROJ2: loc='Montreal' ∧ … ∧ ¬(budget<=200000)   rows: P6
  PROJ3: … loc='New York' … ∧ budget<=200000      rows: P2
  PROJ4: … loc='New York' … ∧ ¬(budget<=200000)   rows: P3
  PROJ5: … loc='Paris' ∧ budget<=200000           rows: P5
  PROJ6: … loc='Paris' ∧ ¬(budget<=200000)        rows: P4

Completeness: OK
Disjointness: OK
```

16 = 2⁴ minterms. 8 are dropped because two or three cities would be true at once. 2 more are dropped because no city is true, and the company has only three offices. That leaves **6**. Compare the script with your implications from Exercise 1.

### A2 · Build the partitions and run the checks

```sql
\i /kit/labs/week05/sql/02_primary.sql
```

`proj_part` is partitioned **BY LIST (loc)**, one partition per city, giving predicates p1–p3. Inside each city it is partitioned **BY RANGE (budget)**, giving p4. The six leaf partitions `proj1` … `proj6` are the six fragments PROJ₁ … PROJ₆. `budget` is an integer, so `budget <= 200000` becomes the range `[MINVALUE, 200001)`.

The script prints five sections:

| Section | Expected | Rule it proves |
|---|---|---|
| 1. Where did each row go? | P1→proj1, P6→proj2, P2→proj3, P3→proj4, P5→proj5, P4→proj6 | – |
| 2. Completeness | `original 6 · fragmented 6` | Completeness for the current rows |
| 2b. Tokyo | `ERROR: no partition of relation "proj_part" found for row`, then a DEFAULT partition fixes it | Completeness for **future** rows |
| 3. Reconstruction | `0` and `0` | PROJ = PROJ₁ ∪ … ∪ PROJ₆ |
| 4. Disjointness | `(0 rows)` | No project in two fragments |
| 5. Pruning | `Seq Scan on proj5` only | The benefit of fragmenting |

The only ERROR in the output is the intended Tokyo insert. At the end of section 2b, the script drops the DEFAULT partition again so that you can repeat the experiment yourself in A3.

### A3 · The slide commands, by hand

**Line 3: which fragment holds each project?** `tableoid::regclass` is the name of the partition that stores the row.

```sql
SELECT tableoid::regclass, pno FROM proj_part;
```

```
 tableoid | pno
----------+-----
 proj1    | P1
 proj2    | P6
 proj3    | P2
 proj4    | P3
 proj5    | P5
 proj6    | P4
```

**Line 4: a project in Tokyo.** This insert **fails**:

```sql
INSERT INTO proj_part VALUES ('P7', 'Robotics', 90000, 'Tokyo');
```

```
ERROR:  no partition of relation "proj_part" found for row
DETAIL:  Partition key of the failing row contains (loc) = (Tokyo).
```

**Think about it.** Which correctness rule breaks? The predicate set assumed that only three offices exist, so the minterms with "no city true" were removed as contradictory. The new row breaks that assumption, and completeness must also hold for **future** rows.

**Fix it with a DEFAULT partition**, which stands for the removed "no city true" minterms, then insert again:

```sql
CREATE TABLE proj_other PARTITION OF proj_part DEFAULT;
INSERT INTO proj_part VALUES ('P7', 'Robotics', 90000, 'Tokyo');
SELECT tableoid::regclass, pno, loc FROM proj_part WHERE pno = 'P7';
```

```
INSERT 0 1
  tableoid  | pno |  loc
------------+-----+-------
 proj_other | P7  | Tokyo
```

The other fix is to add a predicate p5: `loc = 'Tokyo'` and derive the minterms again. Say in your report which fix is better for a company that will keep opening offices.

**Line 5: partition pruning.**

```sql
EXPLAIN SELECT * FROM proj_part WHERE loc = 'Paris' AND budget <= 200000;
```

```
 Seq Scan on proj5 proj_part  (cost=0.00..19.45 rows=1 width=100)
   Filter: ((budget <= 200000) AND (loc = 'Paris'::text))
```

Only `proj5` is scanned; the other five fragments and `proj_other` are pruned. In a distributed database, the query would go to one site only. Copy this plan into your report.

---

## Part B · EMP follows PAY (15 min)

Still in psql, connected to `week05`:

```sql
\i /kit/labs/week05/sql/03_derived.sql
```

**The script, step by step:**

- It fragments the **owner** PAY by salary: PAY₁ = σ sal ≤ 100000 (PAY), PAY₂ = σ sal > 100000 (PAY).
- It derives the **member** EMP with semi-joins, EMPᵢ = EMP ⋉ PAYᵢ, written in SQL as `WHERE EXISTS (…)`.
- It prints the two "sites" side by side: site 1 holds E2, E4, E5, E8 (Syst. Anal., Programmer) and site 2 holds E1, E3, E6, E7 (Elect. Eng., Mech. Eng.).
- It runs the three checks:

  | Check | Expected | Why |
  |---|---|---|
  | `emp_without_fragment` | 0 | Completeness, guaranteed by the foreign key `emp.title → pay` |
  | `missing \| extra` | 0 \| 0 | Reconstruction: EMP = EMP₁ ∪ EMP₂ |
  | `in_both` | 0 | Disjointness: the join is on PAY's key `title` |

- It partitions PAY and EMP **BY LIST (title)** with the same value lists: `pay_low`/`emp_low` for Syst. Anal. and Programmer, and `pay_high`/`emp_high` for Elect. Eng. and Mech. Eng.

**Line 2: one derived fragment.**

```sql
SELECT * FROM emp1;
```

```
 eno |   ename   |    title
-----+-----------+-------------
 E2  | M. Smith  | Syst. Anal.
 E4  | J. Miller | Programmer
 E5  | B. Casey  | Syst. Anal.
 E8  | J. Jones  | Syst. Anal.
```

**Lines 3–4: partition-wise join OFF.**

```sql
SET enable_partitionwise_join = off;
EXPLAIN SELECT ename, sal FROM emp_part JOIN pay_part USING (title);
```

```
 Hash Join
   Hash Cond: (emp_part.title = pay_part.title)
   ->  Append
         ->  Seq Scan on emp_high emp_part_1
         ->  Seq Scan on emp_low emp_part_2
   ->  Hash
         ->  Append
               ->  Seq Scan on pay_high pay_part_1
               ->  Seq Scan on pay_low pay_part_2
```

One join over everything: all EMP partitions are appended, all PAY partitions are appended, then they are joined. In a distributed database, data from both sites would have to meet in one place.

**Line 5: partition-wise join ON, then the same EXPLAIN again.**

```sql
SET enable_partitionwise_join = on;
EXPLAIN SELECT ename, sal FROM emp_part JOIN pay_part USING (title);
```

```
 Append
   ->  Hash Join
         Hash Cond: (emp_part_1.title = pay_part_1.title)
         ->  Seq Scan on emp_high emp_part_1
         ->  Hash
               ->  Seq Scan on pay_high pay_part_1
   ->  Hash Join
         Hash Cond: (emp_part_2.title = pay_part_2.title)
         ->  Seq Scan on emp_low emp_part_2
         ->  Hash
               ->  Seq Scan on pay_low pay_part_2
```

(Your plan also shows `cost=…` numbers; they do not matter here.)

Now there are **two small joins**, emp_high ⋈ pay_high and emp_low ⋈ pay_low, and an Append that unions their results. Each join pairs an EMP fragment only with the PAY fragment it was derived from. This is exactly why derived fragmentation exists: the join becomes **local** to each site. Partition-wise join is off by default in PostgreSQL, because planning it costs time on tables with many partitions.

---

## Part C · Fragment ASG on your own (at home)

Follow **Exercise 2** of `minterm-worksheet.md`. The two access patterns are:

- **q1:** `dur >= 24`. HR reads long assignments far more often than short ones.
- **q2:** `resp = 'Manager'`. The project office reads managers' assignments far more often than others.

Steps:

1. Build the minterms of q1 and q2, check them for contradictions, and write each fragment as σ…(ASG) with its rows (eno, pno). You can check your answer with a copy of `minterms.py` adapted to ASG.
2. Answer the question on a third predicate, `q3: dur >= 12`. Does the set stay **minimal**?
3. Implement the fragments in PostgreSQL in `labs/week05/my_asg.sql`, on your laptop. The starter file has the checks ready as comments. Run it:

   ```bash
   docker exec -it ce502-postgres psql -U postgres -d week05 -f /kit/labs/week05/my_asg.sql
   ```

   The reconstruction check must return `0` and `0`, and the disjointness check `(0 rows)`.
4. Write 5–8 lines on whether ASG should be **derived from EMP or from PROJ**. Use rule 1 from Lesson 5-3 and the table of applications in Exercise 2, question 5.

> Part C is the part most often forgotten in reports. Plan time for it.

**Hints.** `PARTITION BY LIST (resp)` with a partition for `'Manager'` and a **DEFAULT** partition for "not Manager". Then sub-partition each one `BY RANGE (dur)`, with `24` as the boundary. Remember that a range upper bound is exclusive.

---

## What to submit

One PDF, from `report-template.md`:

| Report item | Points |
|---|---|
| Part A: Exercise 1 on paper (minterms, implications, fragments, rules) | 3 |
| Part A: output of `02_primary.sql` explained, incl. the Tokyo error and pruning | 2 |
| Part B: derived fragments and the two EXPLAIN plans compared | 2 |
| Part C: ASG fragments in SQL with the reconstruction check | 2 |
| Part C: owner choice for ASG, 5–8 lines | 1 |
| **Total** | **10** |

**Key point:** every output in the report needs one sentence that names the rule or idea it proves, for example: *"the Tokyo insert fails because the predicate set is not complete for future rows; the DEFAULT partition represents the minterm in which no location predicate is true"*.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `relation "proj" does not exist` | You are in the `lab` database. Type `\c week05`, or run `01_schema.sql` again. |
| `01_schema.sql`: `database "week05" is being accessed by other users` | Another session is connected to `week05`. Quit it (`\q`), then run the script again. |
| Line 4 succeeds instead of failing | `proj_other` already exists, because you created it earlier. Run `DROP TABLE proj_other;` to repeat the experiment, or simply run `02_primary.sql` again. |
| Line 4: `duplicate key` or P7 appears twice | P7 is already in `proj_other`. `DELETE FROM proj_part WHERE pno = 'P7';` |
| The plan with the setting ON still shows one Hash Join | You ran the EXPLAIN before `SET enable_partitionwise_join = on;`, or in a different psql session. The setting only applies to the current session. |
| `my_asg.sql: No such file` | Save `my_asg.sql` in the kit folder, in `labs/week05/`. The container sees the kit read-only at `/kit`. |
| `python3: command not found` (Windows) | Use `python` or `py` instead of `python3`. |

## Clean up (optional)

```bash
docker exec -it ce502-postgres psql -U postgres -d lab -c "DROP DATABASE week05"
```

Running `01_schema.sql` again also resets everything.
