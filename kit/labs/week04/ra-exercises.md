# Practice 4 · Part A · Relational Algebra Exercises

Schema (`01_schema.sql`): MANUFACTURER(manufacturer, state), CUSTOMER(cno, cname, address, state),
PART(pno, pname, manufacturer, cost), ORDERS(cno, pno, qty).

Notation: σ selection, π projection, ∪ union, − difference, × Cartesian product, ∩ intersection, ⋈ natural join, ⋈θ theta join.

Write your answers in `labs/week04/my_answers.sql` on your laptop (a starter file with one section per item is provided) and run it:

```bash
docker exec -it ce502-postgres psql -U postgres -d week04 -f /kit/labs/week04/my_answers.sql
```

For items 1–5 write the SQL. For items 6–10 write the relational-algebra expression as a SQL comment **and** keep the SQL so its output appears. Check yourself: item 4 returns exactly one customer, cno 9.

## Items 1–5 · Relational algebra → SQL

1. σ cost > 10 (PART)
2. π cname, state (CUSTOMER)
3. π pname (σ manufacturer = 'Acme Inc.' (PART))
4. π cno (CUSTOMER) − π cno (ORDERS)
5. π pname (PART ⋈ σ state = 'CA' (MANUFACTURER))

## Items 6–10 · SQL → relational algebra

6. `SELECT cname FROM customer WHERE state = 'MD' OR state = 'NY';`
7. `SELECT pno FROM orders WHERE qty >= 100 INTERSECT SELECT pno FROM part WHERE cost < 5;`
8. `SELECT c.cname, p.pname, o.qty FROM customer c JOIN orders o ON c.cno = o.cno JOIN part p ON p.pno = o.pno;`
9. `SELECT c.cname, m.manufacturer FROM customer c JOIN manufacturer m ON c.state = m.state;`
10. The query from the transparency lecture: customer name, part name and quantity for parts made by manufacturers in Maryland.

In the report, give for every item 6–10 the expression and one sentence on how it is evaluated (see the deliverables table in the README).
