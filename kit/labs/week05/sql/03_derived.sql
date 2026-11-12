-- CE 502 · Practice 5 · Part B · Derived horizontal fragmentation: EMP follows PAY
-- Owner:  PAY fragmented by salary   PAY1 = σ sal <= 100000 (PAY)   PAY2 = σ sal > 100000 (PAY)
-- Member: EMP fragmented by semi-join   EMPi = EMP ⋉ PAYi
-- Run in psql, connected to week05:   \i /kit/labs/week05/sql/03_derived.sql

DROP TABLE IF EXISTS pay1, pay2, emp1, emp2 CASCADE;

-- Primary fragments of the owner
CREATE TABLE pay1 AS SELECT * FROM pay WHERE sal <= 100000;
CREATE TABLE pay2 AS SELECT * FROM pay WHERE sal >  100000;

-- Derived fragments of the member: semi-join = keep EMP rows that have a match, add no columns
CREATE TABLE emp1 AS SELECT e.* FROM emp e WHERE EXISTS (SELECT 1 FROM pay1 p WHERE p.title = e.title);
CREATE TABLE emp2 AS SELECT e.* FROM emp e WHERE EXISTS (SELECT 1 FROM pay2 p WHERE p.title = e.title);

\echo '=== Site 1 holds PAY1 and EMP1, site 2 holds PAY2 and EMP2'
SELECT 'site 1' AS site, e.eno, e.ename, e.title, p.sal FROM emp1 e JOIN pay1 p USING (title)
UNION ALL
SELECT 'site 2', e.eno, e.ename, e.title, p.sal FROM emp2 e JOIN pay2 p USING (title)
ORDER BY site, eno;

\echo '=== Completeness = referential integrity: every EMP row lands in a fragment (expect 0)'
SELECT count(*) AS emp_without_fragment FROM emp
WHERE eno NOT IN (SELECT eno FROM emp1 UNION SELECT eno FROM emp2);

\echo '=== Reconstruction: EMP = EMP1 ∪ EMP2 (expect 0 and 0)'
SELECT (SELECT count(*) FROM (SELECT * FROM emp EXCEPT (SELECT * FROM emp1 UNION SELECT * FROM emp2)) a) AS missing,
       (SELECT count(*) FROM ((SELECT * FROM emp1 UNION SELECT * FROM emp2) EXCEPT SELECT * FROM emp) b) AS extra;

\echo '=== Disjointness: no employee in both fragments (expect 0)'
SELECT count(*) AS in_both FROM emp1 JOIN emp2 USING (eno);

-------------------------------------------------------------------------------
-- The same idea with declarative partitioning: if PAY and EMP are partitioned
-- the same way on the join key, PostgreSQL joins matching partitions only
-- (a "partition-wise join") – the local join that derived fragmentation buys us.
-------------------------------------------------------------------------------
DROP TABLE IF EXISTS pay_part, emp_part CASCADE;
CREATE TABLE pay_part (LIKE pay) PARTITION BY LIST (title);
CREATE TABLE pay_low  PARTITION OF pay_part FOR VALUES IN ('Syst. Anal.','Programmer');   -- sal <= 100000
CREATE TABLE pay_high PARTITION OF pay_part FOR VALUES IN ('Elect. Eng.','Mech. Eng.');   -- sal >  100000
CREATE TABLE emp_part (LIKE emp) PARTITION BY LIST (title);
CREATE TABLE emp_low  PARTITION OF emp_part FOR VALUES IN ('Syst. Anal.','Programmer');
CREATE TABLE emp_high PARTITION OF emp_part FOR VALUES IN ('Elect. Eng.','Mech. Eng.');
INSERT INTO pay_part SELECT * FROM pay;
INSERT INTO emp_part SELECT * FROM emp;
ANALYZE pay_part; ANALYZE emp_part;

\echo '=== Without partition-wise join: one big join over all partitions'
SET enable_partitionwise_join = off;
EXPLAIN (COSTS OFF) SELECT e.ename, p.sal FROM emp_part e JOIN pay_part p USING (title);

\echo '=== With partition-wise join: emp_low ⋈ pay_low and emp_high ⋈ pay_high, appended'
SET enable_partitionwise_join = on;
EXPLAIN (COSTS OFF) SELECT e.ename, p.sal FROM emp_part e JOIN pay_part p USING (title);
