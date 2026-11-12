-- CE 502 · Week 4 · Course schema (single site)
-- Run (from the kit folder on your laptop):
--   docker exec -it ce502-postgres psql -U postgres -d lab -c "CREATE DATABASE week04"
--   docker exec -it ce502-postgres psql -U postgres -d week04 -f /kit/labs/week04/sql/01_schema.sql
-- Schema used throughout Course B: CUSTOMER, PART, ORDERS, MANUFACTURER
-- (ORDER is a reserved word in SQL, so the table is called ORDERS.)

DROP TABLE IF EXISTS orders, part, customer, manufacturer CASCADE;

CREATE TABLE manufacturer (
    manufacturer  text PRIMARY KEY,
    state         char(2) NOT NULL
);

CREATE TABLE customer (
    cno      int PRIMARY KEY,
    cname    text NOT NULL,
    address  text NOT NULL,
    state    char(2) NOT NULL
);

CREATE TABLE part (
    pno           int PRIMARY KEY,
    pname         text NOT NULL,
    manufacturer  text NOT NULL REFERENCES manufacturer,
    cost          numeric(8,2) NOT NULL
);

CREATE TABLE orders (
    cno  int REFERENCES customer,
    pno  int REFERENCES part,
    qty  int NOT NULL CHECK (qty > 0),
    PRIMARY KEY (cno, pno)
);

INSERT INTO manufacturer VALUES
  ('Acme Inc.',          'MD'),
  ('XYZ Enterprises',    'NY'),
  ('Prairie Tools',      'IL'),
  ('Pacific Components', 'CA');

INSERT INTO customer VALUES
  (1, 'Chesapeake Supply',  '12 Harbor St, Baltimore',     'MD'),
  (2, 'Annapolis Marine',   '4 Dock Rd, Annapolis',        'MD'),
  (3, 'Hudson Hardware',    '200 Broadway, New York',      'NY'),
  (4, 'Albany Builders',    '9 State St, Albany',          'NY'),
  (5, 'Windy City Repairs', '55 Lake St, Chicago',         'IL'),
  (6, 'Springfield Works',  '8 Capitol Ave, Springfield',  'IL'),
  (7, 'Golden Gate Labs',   '1 Market St, San Francisco',  'CA'),
  (8, 'LA Fabrication',     '700 Sunset Blvd, Los Angeles','CA'),
  (9, 'Inner Harbor Bakery','3 Pratt St, Baltimore',       'MD');   -- has no orders yet

INSERT INTO part VALUES
  (10, 'widget',       'Acme Inc.',          3.00),
  (11, 'thingamabob',  'Acme Inc.',          5.00),
  (12, 'doodad',       'XYZ Enterprises',    7.50),
  (13, 'tool chest',   'XYZ Enterprises',   15.00),
  (14, 'gear',         'Prairie Tools',      2.25),
  (15, 'sprocket',     'Prairie Tools',      4.75),
  (16, 'sensor',       'Pacific Components',22.00),
  (17, 'controller',   'Pacific Components',48.00);

INSERT INTO orders VALUES
  (1,10,100),(1,11,20),(2,10,15),(2,16,2),
  (3,12,40),(3,13,3),(4,10,60),(4,14,200),
  (5,14,500),(5,15,120),(6,11,10),(6,17,4),
  (7,16,30),(7,17,12),(8,13,6),(8,15,80);

SELECT 'manufacturer' AS tbl, count(*) FROM manufacturer
UNION ALL SELECT 'customer', count(*) FROM customer
UNION ALL SELECT 'part', count(*) FROM part
UNION ALL SELECT 'orders', count(*) FROM orders;
