-- CE 502 · Practice 4 · Part B · Simulating a two-site distributed database with postgres_fdw
--
-- We create three databases on ONE PostgreSQL server:
--   site_baltimore  – local database at the Baltimore site
--   site_newyork    – local database at the New York site
--   ddb_global      – the "distributed DBMS" layer: it sees both sites through
--                     postgres_fdw and gives users ONE global schema (transparency)
--
-- Run (from the kit folder on your laptop):
--   docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week04/sql/03_distributed_sim.sql
-- Safe to run again: it drops and re-creates the three databases.
-- (If it fails with "database ... is being accessed by other users", quit every psql session
--  connected to ddb_global, site_baltimore or site_newyork first.)
-- pghost/pgport/pgpass = how the global layer reaches the sites; defaults below suit the course container.

\if :{?pghost} \else \set pghost localhost \endif
\if :{?pgport} \else \set pgport 5432 \endif
\if :{?pgpass} \else \set pgpass lab \endif

DROP DATABASE IF EXISTS ddb_global;
DROP DATABASE IF EXISTS site_baltimore;
DROP DATABASE IF EXISTS site_newyork;
CREATE DATABASE site_baltimore;
CREATE DATABASE site_newyork;
CREATE DATABASE ddb_global;

-------------------------------------------------------------------------------
-- Site 1: Baltimore stores Maryland and Illinois customers (and their orders).
-------------------------------------------------------------------------------
\c site_baltimore
CREATE TABLE customer (cno int PRIMARY KEY, cname text, address text, state char(2)
                       CHECK (state IN ('MD','IL')));
CREATE TABLE orders   (cno int REFERENCES customer, pno int, qty int, PRIMARY KEY (cno, pno));
CREATE TABLE part     (pno int PRIMARY KEY, pname text, manufacturer text, cost numeric(8,2));
CREATE TABLE manufacturer (manufacturer text PRIMARY KEY, state char(2));

INSERT INTO customer VALUES
  (1,'Chesapeake Supply','12 Harbor St, Baltimore','MD'),
  (2,'Annapolis Marine','4 Dock Rd, Annapolis','MD'),
  (5,'Windy City Repairs','55 Lake St, Chicago','IL'),
  (6,'Springfield Works','8 Capitol Ave, Springfield','IL');
INSERT INTO orders VALUES (1,10,100),(1,11,20),(2,10,15),(2,16,2),(5,14,500),(5,15,120),(6,11,10),(6,17,4);

-------------------------------------------------------------------------------
-- Site 2: New York stores New York and California customers (and their orders)
-- plus a READ-ONLY REPLICA of the Maryland customers (locality of reference).
-------------------------------------------------------------------------------
\c site_newyork
CREATE TABLE customer (cno int PRIMARY KEY, cname text, address text, state char(2)
                       CHECK (state IN ('NY','CA')));
CREATE TABLE customer_md_replica (cno int PRIMARY KEY, cname text, address text, state char(2));
CREATE TABLE orders   (cno int REFERENCES customer, pno int, qty int, PRIMARY KEY (cno, pno));
CREATE TABLE part     (pno int PRIMARY KEY, pname text, manufacturer text, cost numeric(8,2));
CREATE TABLE manufacturer (manufacturer text PRIMARY KEY, state char(2));

INSERT INTO customer VALUES
  (3,'Hudson Hardware','200 Broadway, New York','NY'),
  (4,'Albany Builders','9 State St, Albany','NY'),
  (7,'Golden Gate Labs','1 Market St, San Francisco','CA'),
  (8,'LA Fabrication','700 Sunset Blvd, Los Angeles','CA');
INSERT INTO customer_md_replica VALUES
  (1,'Chesapeake Supply','12 Harbor St, Baltimore','MD'),
  (2,'Annapolis Marine','4 Dock Rd, Annapolis','MD');
INSERT INTO orders VALUES (3,12,40),(3,13,3),(4,10,60),(4,14,200),(7,16,30),(7,17,12),(8,13,6),(8,15,80);

-- PART and MANUFACTURER are small and read-mostly: fully replicated at both sites.
\c site_baltimore
INSERT INTO manufacturer VALUES ('Acme Inc.','MD'),('XYZ Enterprises','NY'),('Prairie Tools','IL'),('Pacific Components','CA');
INSERT INTO part VALUES (10,'widget','Acme Inc.',3.00),(11,'thingamabob','Acme Inc.',5.00),
  (12,'doodad','XYZ Enterprises',7.50),(13,'tool chest','XYZ Enterprises',15.00),
  (14,'gear','Prairie Tools',2.25),(15,'sprocket','Prairie Tools',4.75),
  (16,'sensor','Pacific Components',22.00),(17,'controller','Pacific Components',48.00);
\c site_newyork
INSERT INTO manufacturer VALUES ('Acme Inc.','MD'),('XYZ Enterprises','NY'),('Prairie Tools','IL'),('Pacific Components','CA');
INSERT INTO part VALUES (10,'widget','Acme Inc.',3.00),(11,'thingamabob','Acme Inc.',5.00),
  (12,'doodad','XYZ Enterprises',7.50),(13,'tool chest','XYZ Enterprises',15.00),
  (14,'gear','Prairie Tools',2.25),(15,'sprocket','Prairie Tools',4.75),
  (16,'sensor','Pacific Components',22.00),(17,'controller','Pacific Components',48.00);

-------------------------------------------------------------------------------
-- The global layer: foreign tables for every fragment, then views that hide
-- where the data lives (distribution, fragmentation and replication transparency).
-------------------------------------------------------------------------------
\c ddb_global
CREATE EXTENSION postgres_fdw;

CREATE SERVER baltimore FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host :'pghost', port :'pgport', dbname 'site_baltimore');
CREATE SERVER newyork   FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host :'pghost', port :'pgport', dbname 'site_newyork');
CREATE USER MAPPING FOR CURRENT_USER SERVER baltimore OPTIONS (user 'postgres', password :'pgpass');
CREATE USER MAPPING FOR CURRENT_USER SERVER newyork   OPTIONS (user 'postgres', password :'pgpass');

CREATE SCHEMA bal;
CREATE SCHEMA nyc;
IMPORT FOREIGN SCHEMA public FROM SERVER baltimore INTO bal;
IMPORT FOREIGN SCHEMA public FROM SERVER newyork   INTO nyc;

-- Global conceptual schema = reconstruction of the fragments.
-- Horizontal fragments are rebuilt with UNION ALL (they are disjoint).
CREATE VIEW customer AS
  SELECT * FROM bal.customer UNION ALL SELECT * FROM nyc.customer;
CREATE VIEW orders AS
  SELECT * FROM bal.orders   UNION ALL SELECT * FROM nyc.orders;
-- Replicated tables: read ONE copy (here the Baltimore copy).
CREATE VIEW part AS SELECT * FROM bal.part;
CREATE VIEW manufacturer AS SELECT * FROM bal.manufacturer;

\echo '=== Which site holds which customer? (the user never needs to know)'
SELECT 'baltimore' AS site, cno, cname, state FROM bal.customer
UNION ALL
SELECT 'newyork', cno, cname, state FROM nyc.customer
ORDER BY cno;

\echo '=== Global query (transparency lecture): customer, part, qty for Maryland manufacturers'
SELECT c.cname, p.pname, o.qty
FROM customer c
JOIN orders o       ON o.cno = c.cno
JOIN part p         ON p.pno = o.pno
JOIN manufacturer m ON m.manufacturer = p.manufacturer
WHERE m.state = 'MD'
ORDER BY c.cname, p.pname;

\echo '=== Cross-site check: total quantity ordered per site'
SELECT 'baltimore' AS site, sum(qty) FROM bal.orders
UNION ALL SELECT 'newyork', sum(qty) FROM nyc.orders;

\echo '=== Plan of the global query: note the Foreign Scan nodes, one per site'
EXPLAIN (COSTS OFF)
SELECT c.cname, o.qty FROM customer c JOIN orders o ON o.cno = c.cno WHERE c.state = 'MD';

\echo '=== Locality of reference: New York reads Maryland customers from its LOCAL replica'
SELECT cno, cname FROM nyc.customer_md_replica ORDER BY cno;

\echo ''
\echo 'Done. Now connect to the global database:'
\echo '  docker exec -it ce502-postgres psql -U postgres -d ddb_global'
