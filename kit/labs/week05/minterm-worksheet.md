# Practice 5 · Minterm Worksheet

**Definition.** A *simple predicate* compares one attribute with a value (`loc = 'Paris'`, `budget <= 200000`). A *minterm* is a conjunction of **every** simple predicate in the set, each taken either as-is or negated. With n predicates there are 2ⁿ minterms. Contradictory minterms are removed. Each remaining minterm defines one horizontal fragment.

A predicate set is **complete** if, inside every fragment, all rows have the same probability of being accessed by every application. It is **minimal** if every predicate splits some fragment into parts that are accessed differently. Drop a predicate that changes nothing.

## Exercise 1 · PROJ (Part A, on paper first)

PROJ(pno, pname, budget, loc), data in `01_schema.sql`. Locations are only Montreal, New York and Paris.

- p1: loc = 'Montreal'
- p2: loc = 'New York'
- p3: loc = 'Paris'
- p4: budget ≤ 200000

1. How many minterms exist before elimination?
2. Write the implications between p1, p2 and p3.
3. Which minterms are contradictory? How many remain?
4. Write each remaining fragment as a selection σ…(PROJ) and list its rows.
5. Show that the fragmentation is complete, reconstructable and disjoint.
6. A new project in Tokyo is added. Which correctness rule breaks, and how do you fix it?

## Exercise 2 · ASG (Part C, on your own)

ASG(eno, pno, resp, dur), data in `01_schema.sql`. Two applications:

- the HR application reads long assignments (dur ≥ 24 months) far more often than short ones;
- the project office reads assignments where resp = 'Manager' far more often than others.

Simple predicates: q1: dur ≥ 24 and q2: resp = 'Manager'.

1. List all minterms. Are any contradictory?
2. Write each fragment as σ…(ASG) and list its rows (eno, pno).
3. A third predicate q3: dur ≥ 12 is suggested. Using the access patterns above, argue whether keeping q3 keeps the set *minimal*.
4. Implement your fragments in PostgreSQL with `PARTITION BY LIST (resp)` and sub-partitions `BY RANGE (dur)`, or another layout you can justify. Write the SQL in `labs/week05/my_asg.sql` (a starter is provided) and run it:

   ```bash
   docker exec -it ce502-postgres psql -U postgres -d week05 -f /kit/labs/week05/my_asg.sql
   ```

   Show that the reconstruction check returns 0 and 0.

5. **Owner choice.** ASG has two owners: EMP (through eno) and PROJ (through pno). The company runs these applications that join ASG with another relation:

   | Application | Joins ASG with | Runs per day |
   |---|---|---|
   | Project dashboard: team, roles and months per project | PROJ | 400 |
   | Project cost report, run by each project site | PROJ | 60 |
   | HR: assignments of one employee, for appraisals | EMP | 30 |
   | Payroll check of assignment months | EMP | 10 |

   Should ASG be derived from EMP or from PROJ? Answer in 5–8 lines, using rule 1 from Lesson 5-3 (follow the join used by more applications, weighted by frequency). Mention what happens to the other join, and how the primary key of the owner keeps the derived fragments disjoint.

Check Exercise 1 on your laptop with `python3 labs/week05/python/minterms.py`. To check Exercise 2, copy the script and adapt PROJ, PREDICATES and the domain samples to ASG.
