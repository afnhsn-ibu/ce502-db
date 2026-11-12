-- CE 502 · Practice 5 · Part A · Primary horizontal fragmentation of PROJ with declarative partitioning
-- Fragments come from the minterms of
--   p1: loc = 'Montreal'   p2: loc = 'New York'   p3: loc = 'Paris'   p4: budget <= 200000
-- After removing contradictory minterms, six fragments remain (city × budget band).
-- Run in psql, connected to week05 (01_schema.sql leaves you there):   \i /kit/labs/week05/sql/02_primary.sql

DROP TABLE IF EXISTS proj_part CASCADE;

-- Level 1: LIST on loc (predicates p1–p3). Level 2: RANGE on budget (predicate p4).
CREATE TABLE proj_part (LIKE proj) PARTITION BY LIST (loc);

CREATE TABLE proj_montreal PARTITION OF proj_part FOR VALUES IN ('Montreal') PARTITION BY RANGE (budget);
CREATE TABLE proj_newyork  PARTITION OF proj_part FOR VALUES IN ('New York') PARTITION BY RANGE (budget);
CREATE TABLE proj_paris    PARTITION OF proj_part FOR VALUES IN ('Paris')    PARTITION BY RANGE (budget);

-- budget is an integer, so "budget <= 200000" is the range [MINVALUE, 200001).
CREATE TABLE proj1 PARTITION OF proj_montreal FOR VALUES FROM (MINVALUE) TO (200001);  -- m: Montreal ∧ budget ≤ 200000
CREATE TABLE proj2 PARTITION OF proj_montreal FOR VALUES FROM (200001) TO (MAXVALUE);  -- m: Montreal ∧ budget > 200000
CREATE TABLE proj3 PARTITION OF proj_newyork  FOR VALUES FROM (MINVALUE) TO (200001);
CREATE TABLE proj4 PARTITION OF proj_newyork  FOR VALUES FROM (200001) TO (MAXVALUE);
CREATE TABLE proj5 PARTITION OF proj_paris    FOR VALUES FROM (MINVALUE) TO (200001);
CREATE TABLE proj6 PARTITION OF proj_paris    FOR VALUES FROM (200001) TO (MAXVALUE);

INSERT INTO proj_part SELECT * FROM proj;

\echo '=== 1. Where did each row go?'
SELECT tableoid::regclass AS fragment, pno, pname, budget, loc
FROM proj_part ORDER BY fragment, pno;

\echo '=== 2. Completeness: every current row has a fragment (counts must match)'
SELECT (SELECT count(*) FROM proj) AS original, (SELECT count(*) FROM proj_part) AS fragmented;

\echo '=== 2b. Completeness for FUTURE rows: a project in Tokyo has no fragment yet'
INSERT INTO proj_part VALUES ('P7','Robotics',90000,'Tokyo');
\echo '    -> fails: the predicate set is not complete for loc = Tokyo. Fix with a DEFAULT partition:'
CREATE TABLE proj_other PARTITION OF proj_part DEFAULT;
INSERT INTO proj_part VALUES ('P7','Robotics',90000,'Tokyo');
SELECT tableoid::regclass AS fragment, pno, loc FROM proj_part WHERE pno = 'P7';
DELETE FROM proj_part WHERE pno = 'P7';   -- keep proj_part equal to PROJ for the checks below
DROP TABLE proj_other;                     -- removed again, so you can repeat the error and the fix by hand
\echo '    (proj_other was dropped again: repeat the Tokyo insert yourself, then fix it - see the README)'

\echo '=== 3. Reconstruction: PROJ = PROJ1 ∪ … ∪ PROJ6 (both differences must be empty)'
SELECT 'in proj, not in fragments' AS check, count(*) FROM
  (SELECT * FROM proj EXCEPT
   (SELECT * FROM proj1 UNION ALL SELECT * FROM proj2 UNION ALL SELECT * FROM proj3
    UNION ALL SELECT * FROM proj4 UNION ALL SELECT * FROM proj5 UNION ALL SELECT * FROM proj6)) d
UNION ALL
SELECT 'in fragments, not in proj', count(*) FROM
  ((SELECT * FROM proj1 UNION ALL SELECT * FROM proj2 UNION ALL SELECT * FROM proj3
    UNION ALL SELECT * FROM proj4 UNION ALL SELECT * FROM proj5 UNION ALL SELECT * FROM proj6)
   EXCEPT SELECT * FROM proj) d;

\echo '=== 4. Disjointness: no project appears in two fragments (expect 0 rows)'
SELECT pno, count(DISTINCT tableoid) AS fragments
FROM proj_part GROUP BY pno HAVING count(DISTINCT tableoid) > 1;

\echo '=== 5. Partition pruning: a query for cheap Paris projects reads only PROJ5'
EXPLAIN (COSTS OFF) SELECT * FROM proj_part WHERE loc = 'Paris' AND budget <= 200000;
