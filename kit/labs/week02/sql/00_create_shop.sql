-- CE 502 · Practice 2 · Setup: the shop database with 50,000 orders
-- Run from your laptop:
--   docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week02/sql/00_create_shop.sql
-- WARNING: drops and re-creates the databases shop and shop_restored.

DROP DATABASE IF EXISTS shop_restored;
DROP DATABASE IF EXISTS shop;
CREATE DATABASE shop;
\c shop

CREATE TABLE customers (
    id    int PRIMARY KEY,
    name  text NOT NULL,
    city  text NOT NULL
);

CREATE TABLE orders (
    id          serial PRIMARY KEY,
    customer_id int NOT NULL REFERENCES customers(id),
    amount      numeric(10,2) NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);

SELECT setseed(0.502);   -- same "random" data for every student
INSERT INTO customers
SELECT g, 'customer_' || g,
       (ARRAY['Skopje','Bitola','Tetovo','Ohrid','Kumanovo','Gostivar'])[1 + (g % 6)]
FROM generate_series(1, 5000) AS g;

INSERT INTO orders (customer_id, amount, created_at)
SELECT 1 + (g % 5000),
       round((5 + random() * 495)::numeric, 2),
       now() - (50000 - g) * interval '1 minute'
FROM generate_series(1, 50000) AS g;

ANALYZE;
\echo 'shop is ready:'
SELECT (SELECT count(*) FROM customers) AS customers,
       (SELECT count(*) FROM orders)    AS orders,
       (SELECT sum(amount) FROM orders) AS total_amount,
       pg_size_pretty(pg_database_size('shop')) AS database_size;
