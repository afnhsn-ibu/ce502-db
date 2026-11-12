-- CE 502 · Practice 3 · Setup: run in ONE session before EACH experiment to reset the data.
--   \i /kit/labs/week03/sql/00_setup.sql
-- If psql shows  lab=!#  or  lab=*#  you still have an open transaction: type ROLLBACK; first.
DROP TABLE IF EXISTS acc;
CREATE TABLE acc (id int PRIMARY KEY, bal int NOT NULL);
INSERT INTO acc VALUES (1, 100), (2, 100);
SELECT * FROM acc ORDER BY id;
