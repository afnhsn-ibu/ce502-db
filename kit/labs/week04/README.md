# Practice 4 · Build and Query a Two-Site Database

**CE 502 · Week 4** · Individual · about 90 minutes · 10 points
**Lessons:** 4-1 What a Distributed Database Is, 4-2 Transparency and Architecture, 4-3 Relational Algebra for Distribution
**Submit:** one PDF, at most 4 pages, before the Week 5 class. Use `report-template.md`.

You play the distributed DBMS: two sites, one global schema, and a look at the SQL that is actually sent to each site.

| Part | What you do | Lesson objective |
|---|---|---|
| Setup | Create the database `week04` and load the course schema | – |
| A | Translate 10 items between relational algebra and SQL, and run your SQL | 4-3 O2–O4 |
| B | Build two sites with `postgres_fdw` and query them through one global schema | 4-1 O3 · 4-2 O1 |
| C | Classify 8 real systems on autonomy, distribution and heterogeneity | 4-2 O3 |

| File | Purpose |
|---|---|
| `sql/01_schema.sql` | The course schema: 4 manufacturers, 9 customers, 8 parts, 16 orders |
| `ra-exercises.md` | The 10 items of Part A |
| `my_answers.sql` | **Your** answers, one section per item. Edit this file on your laptop |
| `sql/03_distributed_sim.sql` | Builds the two sites and the global layer for Part B |
| `adh-worksheet.md` | The Part C worksheet |
| `report-template.md` | Structure of your report |

---

## Before you start

```bash
docker compose up -d
docker exec -u postgres ce502-postgres bash /kit/setup/check_setup.sh      # all [ OK ]
```

> **Common mistake:** editing files inside the container. The kit is mounted **read-only** at `/kit`. Edit `my_answers.sql` on your laptop, in the kit folder. The container sees the change immediately.

---

## Setup (5 min)

Run these from the kit folder. Each command is one line; the slides break them with `\` only for space.

```bash
docker exec -it ce502-postgres psql -U postgres -d lab -c "CREATE DATABASE week04"
docker exec -it ce502-postgres psql -U postgres -d week04 -f /kit/labs/week04/sql/01_schema.sql
```

```
     tbl      | count
--------------+-------
 manufacturer |     4
 customer     |     9
 part         |     8
 orders       |    16
```

The schema follows the lessons: MANUFACTURER(manufacturer, state), CUSTOMER(cno, cname, address, state), PART(pno, pname, manufacturer, cost) and ORDERS(cno, pno, qty). The table is called `orders` because `ORDER` is a reserved word in SQL. Customer 9, Inner Harbor Bakery, has no orders yet.

To look around interactively:

```bash
docker exec -it ce502-postgres psql -U postgres -d week04
```

Useful commands are `\dt`, `\d part`, and `SELECT * FROM customer;`.

---

## Part A · Relational algebra ↔ SQL (35 min)

Open `ra-exercises.md`:

- **Items 1–5:** relational algebra → SQL.
- **Items 6–10:** SQL → relational algebra.

Write everything in `my_answers.sql`. The file already has a section header for each item, and for items 6–10 it already contains the SQL; you add the algebra as a comment. Then run it:

```bash
docker exec -it ce502-postgres psql -U postgres -d week04 -f /kit/labs/week04/my_answers.sql
```

**Check yourself:** item 4, `π cno (CUSTOMER) − π cno (ORDERS)`, must return exactly **one** customer:

```
 cno
-----
   9
```

Hints, linked to Lesson 4-3:

- **Sets vs bags.** Relational algebra works on *sets*, but SQL keeps duplicates. Use `DISTINCT` where a projection could produce duplicates (items 2, 3 and 5). `EXCEPT`, `INTERSECT` and `UNION` remove duplicates on their own.
- **Union compatibility.** `−`, `∩` and `∪` need the same columns in the same order on both sides (items 4 and 7).
- **Item 10.** CUSTOMER and MANUFACTURER **both** have a column called `state`. A natural join over all four tables silently equates *those* two columns as well, so you get 3 rows instead of 5. Write the join conditions explicitly, or project before you join. Explain in your report which state your selection refers to.

---

## Part B · Two sites, one global schema (35 min)

### B1 · Build the sites

```bash
docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week04/sql/03_distributed_sim.sql
```

The script creates three databases on the same server and pretends that they are three machines:

| Database | Role | Holds |
|---|---|---|
| `site_baltimore` | Site 1 | Customers in **MD** and **IL** and their orders; full copies of PART and MANUFACTURER |
| `site_newyork` | Site 2 | Customers in **NY** and **CA** and their orders; full copies of PART and MANUFACTURER; a read-only replica of the MD customers |
| `ddb_global` | The "distributed DBMS" | No data of its own: **foreign tables** for every table at both sites (schemas `bal` and `nyc`), and **views** that rebuild the global tables |

Each site table has a `CHECK` constraint on `state`. That constraint *is* the **fragment predicate**: it defines which rows belong to the fragment. `postgres_fdw` is a PostgreSQL extension that makes a table in another database look like a local table, and it plays the role of the network layer.

The script prints:

- which site holds which customer;
- the global Maryland-manufacturer query from Lesson 4-2, which returns **5 rows**: the same answer as the single-site database in Part A;
- the total quantity per site;
- a query plan with one `Foreign Scan` per site;
- the New York replica.

### B2 · Query through the global schema

```bash
docker exec -it ce502-postgres psql -U postgres -d ddb_global
```

Then, inside psql:

```sql
\d+ customer
```

The view definition shows how the global CUSTOMER is rebuilt: `bal.customer UNION ALL nyc.customer`. Horizontal fragments are recombined with **union**, as in Lesson 4-3.

```sql
EXPLAIN (VERBOSE, COSTS OFF) SELECT * FROM customer WHERE state = 'MD';
```

```
 Append
   ->  Foreign Scan on bal.customer customer_1
         Remote SQL: SELECT cno, cname, address, state FROM public.customer WHERE ((state = 'MD'))
   ->  Foreign Scan on nyc.customer customer_2
         Remote SQL: SELECT cno, cname, address, state FROM public.customer WHERE ((state = 'MD'))
```

Read the **Remote SQL** lines. They show what was actually sent over the "network" to each site.

- The selection `state = 'MD'` is **pushed down**, so each site filters locally and only matching rows travel.
- New York is still queried, although it can never hold a Maryland customer. The global layer does not know the fragment predicates, which are hidden in the sites' CHECK constraints. A real distributed DBMS uses its **directory** (Lesson 4-1) to skip fragments that cannot contain the answer. Weeks 5 and 6 build on this.

### B3 · Insert through the sites

```sql
INSERT INTO bal.customer VALUES (10, 'Peoria Pumps', 'Peoria', 'IL');    -- succeeds
INSERT INTO nyc.customer VALUES (11, 'Austin Air',   'Austin', 'TX');    -- must FAIL
SELECT count(*) FROM customer;                                           -- 9: the 8 site customers + Peoria
```

```
INSERT 0 1
ERROR:  new row for relation "customer" violates check constraint "customer_state_check"
DETAIL:  Failing row contains (11, Austin Air, Austin, TX).
CONTEXT:  remote SQL command: INSERT INTO public.customer(cno, cname, address, state) VALUES ($1, $2, $3, $4)
 count
-------
     9
```

- The global count is 9. The script did not copy customer 9 (Inner Harbor Bakery) to either site, so the sites start with 8 customers. Check it with `SELECT * FROM customer ORDER BY cno;`.
- The Texas insert fails **at the remote site**. The CHECK constraint is the fragment predicate, and Texas belongs to no site: the fragmentation is not **complete** for that value.
- To insert, you had to name the site (`bal.` or `nyc.`). The global view gives **no** insert transparency. Report item 4 asks you to list such gaps.

Leave psql with `\q`. To start Part B again, run `03_distributed_sim.sql` again; it drops and rebuilds everything.

---

## Part C · Classify real systems (15 min)

Open `adh-worksheet.md`. For each of the 8 systems, give a value on each of the three dimensions from Lesson 4-2, and one sentence of justification:

- **A**utonomy: A0, A1 or A2;
- **D**istribution: D0, D1 or D2;
- **H**eterogeneity: H0 or H1.

Borderline answers are normal. The justification is what earns the points.

---

## What to submit

One PDF, at most 4 pages, from `report-template.md`:

| Report item | Points |
|---|---|
| Part A: `my_answers.sql` with output; algebra for the SQL items, with one sentence each | 3 |
| Part B: view definition, plan with Remote SQL, both INSERTs, each explained in 1–2 sentences | 3 |
| Part C: the completed A/D/H worksheet with a justification per system | 2 |
| Reflection (half a page): which transparencies `ddb_global` provides, and which it does not | 2 |
| **Total** | **10** |

**Key point:** most points are for explanations. Link every output to a concept from Lessons 4-1 to 4-3.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `database "week04" already exists` | Fine. Just run the `01_schema.sql` line; it drops and recreates the tables. |
| `psql: error: … /kit/labs/week04/my_answers.sql: No such file` | You saved `my_answers.sql` somewhere else. It must be in the kit folder, in `labs/week04/`. |
| `03_distributed_sim.sql`: `database "ddb_global" is being accessed by other users` | Quit every psql session connected to `ddb_global` or a site (`\q`), then run the script again. |
| `could not connect to server "baltimore"` / `password authentication failed` | The global layer connects to `localhost:5432` as `postgres` with password `lab`. If you changed the password in `docker-compose.yml`, pass it: `… -v pgpass=<password> -f /kit/labs/week04/sql/03_distributed_sim.sql`. |
| `ERROR: extension "postgres_fdw" is not available` | You are not using the course container. Run `setup/check_setup.sh`. |
| PowerShell rejects the `\` line breaks from the slides | Use the single-line commands in this README. |

## Clean up (optional)

```bash
docker exec -it ce502-postgres psql -U postgres -d lab -c "DROP DATABASE ddb_global" -c "DROP DATABASE site_baltimore" -c "DROP DATABASE site_newyork"
```
