-- CE 502 · Practice 5 · Part C · My fragmentation of ASG
-- Name: ______________   Student ID: ______________
--
-- Edit this file ON YOUR LAPTOP (the kit is mounted read-only in the container), then run:
--   docker exec -it ce502-postgres psql -U postgres -d week05 -f /kit/labs/week05/my_asg.sql
-- Predicates:  q1: dur >= 24     q2: resp = 'Manager'

DROP TABLE IF EXISTS asg_part CASCADE;

-- 1. Create asg_part and its partitions (one partition per minterm)
-- your SQL here


-- 2. Load the data
-- INSERT INTO asg_part SELECT * FROM asg;

\echo '=== Where did each assignment go?'
-- SELECT tableoid::regclass AS fragment, eno, pno, resp, dur FROM asg_part ORDER BY fragment, eno, pno;

\echo '=== Reconstruction: both differences must be 0'
-- SELECT (SELECT count(*) FROM (SELECT * FROM asg EXCEPT SELECT * FROM asg_part) a) AS missing,
--        (SELECT count(*) FROM (SELECT * FROM asg_part EXCEPT SELECT * FROM asg) b) AS extra;

\echo '=== Disjointness: expect 0 rows'
-- SELECT eno, pno, count(DISTINCT tableoid) FROM asg_part GROUP BY eno, pno HAVING count(DISTINCT tableoid) > 1;
