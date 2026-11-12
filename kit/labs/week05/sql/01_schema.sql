-- CE 502 · Practice 5 · Setup: the engineering-company schema (in the style of Özsu & Valduriez)
--   PAY(title, sal)  1—N  EMP(eno, ename, title)  1—N  ASG(eno, pno, resp, dur)  N—1  PROJ(pno, pname, budget, loc)
-- Run inside psql (any database):   \i /kit/labs/week05/sql/01_schema.sql
-- It (re)creates the database week05 and leaves your psql session CONNECTED to week05.
-- WARNING: drops week05 and everything you built in it. Your Part C SQL is safe in my_asg.sql on your laptop.

\c lab
DROP DATABASE IF EXISTS week05;
CREATE DATABASE week05;
\c week05

CREATE TABLE pay (
    title  text PRIMARY KEY,
    sal    int  NOT NULL
);

CREATE TABLE emp (
    eno    text PRIMARY KEY,
    ename  text NOT NULL,
    title  text NOT NULL REFERENCES pay
);

CREATE TABLE proj (
    pno     text PRIMARY KEY,
    pname   text NOT NULL,
    budget  int  NOT NULL,
    loc     text NOT NULL
);

CREATE TABLE asg (
    eno   text REFERENCES emp,
    pno   text REFERENCES proj,
    resp  text NOT NULL,
    dur   int  NOT NULL,          -- months
    PRIMARY KEY (eno, pno)
);

INSERT INTO pay VALUES
  ('Elect. Eng.', 110000),
  ('Mech. Eng.',  105000),
  ('Syst. Anal.',  95000),
  ('Programmer',   80000);

INSERT INTO emp VALUES
  ('E1','J. Doe','Elect. Eng.'),   ('E2','M. Smith','Syst. Anal.'),
  ('E3','A. Lee','Mech. Eng.'),    ('E4','J. Miller','Programmer'),
  ('E5','B. Casey','Syst. Anal.'), ('E6','L. Chu','Elect. Eng.'),
  ('E7','R. Davis','Mech. Eng.'),  ('E8','J. Jones','Syst. Anal.');

INSERT INTO proj VALUES
  ('P1','Instrumentation',   150000,'Montreal'),
  ('P2','Database Develop.', 135000,'New York'),
  ('P3','CAD/CAM',           250000,'New York'),
  ('P4','Maintenance',       310000,'Paris'),
  ('P5','Analytics',         180000,'Paris'),
  ('P6','Cloud Migration',   400000,'Montreal');

INSERT INTO asg VALUES
  ('E1','P1','Manager',12),   ('E2','P1','Analyst',24),
  ('E2','P2','Analyst',6),    ('E3','P3','Consultant',10),
  ('E3','P4','Engineer',48),  ('E4','P2','Programmer',18),
  ('E5','P2','Manager',24),   ('E6','P4','Manager',48),
  ('E7','P3','Engineer',36),  ('E8','P3','Manager',40),
  ('E1','P6','Engineer',20),  ('E5','P5','Analyst',15);

SELECT 'pay' AS tbl, count(*) FROM pay UNION ALL SELECT 'emp', count(*) FROM emp
UNION ALL SELECT 'proj', count(*) FROM proj UNION ALL SELECT 'asg', count(*) FROM asg;
