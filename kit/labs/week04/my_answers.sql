-- CE 502 · Practice 4 · Part A · My answers
-- Name: ______________   Student ID: ______________
--
-- Edit this file ON YOUR LAPTOP (the kit is mounted read-only inside the container), then run:
--   docker exec -it ce502-postgres psql -U postgres -d week04 -f /kit/labs/week04/my_answers.sql
-- Items 1-5: write the SQL.  Items 6-10: write the relational algebra in the comment AND keep the SQL,
-- so that its output appears in your report.

\echo '--- 1. σ cost > 10 (PART)'
-- your SQL here

\echo '--- 2. π cname, state (CUSTOMER)'
-- your SQL here

\echo '--- 3. π pname (σ manufacturer = ''Acme Inc.'' (PART))'
-- your SQL here

\echo '--- 4. π cno (CUSTOMER) − π cno (ORDERS)        (check: exactly one row)'
-- your SQL here

\echo '--- 5. π pname (PART ⋈ σ state = ''CA'' (MANUFACTURER))'
-- your SQL here

\echo '--- 6. algebra: '
-- algebra: 
SELECT cname FROM customer WHERE state = 'MD' OR state = 'NY';

\echo '--- 7. algebra: '
-- algebra: 
SELECT pno FROM orders WHERE qty >= 100 INTERSECT SELECT pno FROM part WHERE cost < 5;

\echo '--- 8. algebra: '
-- algebra: 
SELECT c.cname, p.pname, o.qty FROM customer c JOIN orders o ON c.cno = o.cno JOIN part p ON p.pno = o.pno;

\echo '--- 9. algebra: '
-- algebra: 
SELECT c.cname, m.manufacturer FROM customer c JOIN manufacturer m ON c.state = m.state;

\echo '--- 10. customer name, part name and quantity for parts made by manufacturers in Maryland'
-- algebra: 
-- your SQL here (careful: CUSTOMER and MANUFACTURER both have a column called state)
