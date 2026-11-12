-- CE 502 · Practice 1 · Setup
-- Creates the tables used in Parts A, B and C. Safe to run again: it starts from scratch.
-- Run inside psql:   \i /kit/labs/week01/sql/00_setup.sql

DROP TABLE IF EXISTS lab1, orders, customer, stock;

-- Parts A and B: a simple table that we fill and then inspect in the log
CREATE TABLE lab1 (
    id  int PRIMARY KEY,
    v   text
);

-- Part C: a tiny shop. One order = take an item from stock, charge the customer, record the order.
CREATE TABLE stock (
    item  int PRIMARY KEY,
    name  text NOT NULL,
    qty   int  NOT NULL CHECK (qty >= 0)
);

CREATE TABLE customer (
    id       int PRIMARY KEY,
    name     text    NOT NULL,
    balance  numeric(10,2) NOT NULL
);

CREATE TABLE orders (
    id           int PRIMARY KEY,
    customer_id  int NOT NULL REFERENCES customer(id),
    item         int REFERENCES stock(item),
    amount       numeric(10,2)
);

INSERT INTO stock    VALUES (500, 'USB-C cable', 20);
INSERT INTO customer VALUES (1, 'Ana Petrovska', 100.00);

\echo 'Setup complete: lab1 (empty), stock, customer, orders.'
SELECT 'stock' AS tbl, count(*) FROM stock
UNION ALL SELECT 'customer', count(*) FROM customer
UNION ALL SELECT 'orders',   count(*) FROM orders;
