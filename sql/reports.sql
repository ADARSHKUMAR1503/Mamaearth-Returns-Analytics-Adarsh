
-- ============================================================
-- Mamaearth Returns & Growth Intelligence Pipeline
-- Part 1, Task 3: SQL Reports
-- Database: SQLite
--
-- IMPORTANT:
-- 1. Run schema.sql and seed_data.sql before this file.
-- 2. Run reports against the RAW 180-row orders table.
-- 3. The output comments below document the expected results.
-- 4. Enable foreign keys when opening the database connection.
-- ============================================================

PRAGMA foreign_keys = ON;


-- ============================================================
-- REPORT (a): ORDER TOTALS
-- Expected output:
-- total_orders | total_revenue | avg_order_value
-- 180          | 99860.20      | 554.78
-- ============================================================

SELECT
    COUNT(o.order_id) AS total_orders,
    ROUND(
        SUM(
            o.quantity * p.price
            * (1 - COALESCE(o.discount_pct, 0) / 100.0)
        ),
        2
    ) AS total_revenue,
    ROUND(
        AVG(
            o.quantity * p.price
            * (1 - COALESCE(o.discount_pct, 0) / 100.0)
        ),
        2
    ) AS avg_order_value
FROM orders AS o
JOIN products AS p
    ON o.product_id = p.product_id;


-- ============================================================
-- REPORT (b): COUNT(*) VS COUNT(rating)
-- Expected output:
-- total_orders | rated_orders | unrated_orders
-- 180          | 165          | 15
-- ============================================================

SELECT
    COUNT(*) AS total_orders,
    COUNT(rating) AS rated_orders,
    COUNT(*) - COUNT(rating) AS unrated_orders
FROM orders;


-- ============================================================
-- REPORT (c1): LEFT JOIN TO FIND CUSTOMERS WITH ZERO ORDERS
-- Expected output:
-- customer_id | name
-- C045        | Vihaan
-- ============================================================

SELECT
    c.customer_id,
    c.name
FROM customers AS c
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.name
HAVING COUNT(o.order_id) = 0
ORDER BY c.customer_id;


-- ============================================================
-- REPORT (c2): INDEPENDENT ZERO-ORDER CHECK USING NOT IN
-- Expected output:
-- customer_id | name
-- C045        | Vihaan
-- ============================================================

SELECT
    c.customer_id,
    c.name
FROM customers AS c
WHERE c.customer_id NOT IN (
    SELECT DISTINCT customer_id
    FROM orders
)
ORDER BY c.customer_id;


-- ============================================================
-- REPORT (d): CITY RETURN RATE ABOVE 20%
-- Expected output:
-- city      | total_orders | returned_orders | return_rate_pct
-- Jaipur    | 19           | 8               | 42.1
-- Lucknow   | 49           | 15              | 30.6
-- Bangalore | 33           | 8               | 24.2
-- ============================================================

SELECT
    c.city,
    COUNT(o.order_id) AS total_orders,
    SUM(o.returned) AS returned_orders,
    ROUND(
        100.0 * SUM(o.returned) / COUNT(o.order_id),
        1
    ) AS return_rate_pct
FROM orders AS o
JOIN customers AS c
    ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING
    ROUND(
        100.0 * SUM(o.returned) / COUNT(o.order_id),
        1
    ) > 20
ORDER BY
    return_rate_pct DESC,
    c.city ASC;


-- ============================================================
-- REPORT (e1): TOP 5 CUSTOMERS BY TOTAL SPEND
-- Tie-break rule: customer_id ASC makes equal-spend rankings
-- deterministic and reproducible.
--
-- Expected output:
-- customer_id | name    | total_spend
-- C043        | Reyansh | 12920.00
-- C026        | Isha    | 8371.60
-- C008        | Meera   | 4564.60
-- C011        | Arjun   | 4111.00
-- C042        | Sanya   | 3785.00
-- ============================================================

SELECT
    c.customer_id,
    c.name,
    ROUND(
        SUM(
            o.quantity * p.price
            * (1 - COALESCE(o.discount_pct, 0) / 100.0)
        ),
        2
    ) AS total_spend
FROM orders AS o
JOIN products AS p
    ON o.product_id = p.product_id
JOIN customers AS c
    ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id,
    c.name
ORDER BY
    total_spend DESC,
    c.customer_id ASC
LIMIT 5;


-- ============================================================
-- REPORT (e2): RANKS 3 TO 5 USING LIMIT AND OFFSET
-- Expected output:
-- customer_id | name  | total_spend
-- C008        | Meera | 4564.60
-- C011        | Arjun | 4111.00
-- C042        | Sanya | 3785.00
-- ============================================================

SELECT
    c.customer_id,
    c.name,
    ROUND(
        SUM(
            o.quantity * p.price
            * (1 - COALESCE(o.discount_pct, 0) / 100.0)
        ),
        2
    ) AS total_spend
FROM orders AS o
JOIN products AS p
    ON o.product_id = p.product_id
JOIN customers AS c
    ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id,
    c.name
ORDER BY
    total_spend DESC,
    c.customer_id ASC
LIMIT 3 OFFSET 2;


-- ============================================================
-- REPORT (f): CATEGORY REVENUE USING THREE-TABLE JOIN
-- Expected output:
-- category      | order_count | category_revenue
-- Haircare      | 54          | 44956.10
-- Skincare      | 60          | 27346.00
-- Babycare      | 30          | 16805.00
-- PersonalCare  | 36          | 10753.10
-- ============================================================

SELECT
    p.category,
    COUNT(o.order_id) AS order_count,
    ROUND(
        SUM(
            o.quantity * p.price
            * (1 - COALESCE(o.discount_pct, 0) / 100.0)
        ),
        2
    ) AS category_revenue
FROM orders AS o
JOIN products AS p
    ON o.product_id = p.product_id
JOIN customers AS c
    ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY
    category_revenue DESC,
    p.category ASC;


-- ============================================================
-- REPORT (g): CUSTOMERS WHOSE NAME STARTS WITH 'A'
-- Expected output: exactly 10 rows.
-- customer_id | name
-- C001        | Aarav
-- C003        | Aditi
-- C004        | Ananya
-- C011        | Arjun
-- C021        | Aryan
-- C030        | Anika
-- C031        | Aditya
-- C036        | Aisha
-- C041        | Ayaan
-- C044        | Aria
-- ============================================================

SELECT
    customer_id,
    name
FROM customers
WHERE name LIKE 'A%'
ORDER BY customer_id;


-- ============================================================
-- REPORT (h): DISTINCT ACQUISITION SOURCES
-- Expected output: exactly 4 values.
-- acquisition_source
-- Ad
-- Organic
-- Referral
-- Social
-- ============================================================

SELECT DISTINCT acquisition_source
FROM customers
ORDER BY acquisition_source;


-- ============================================================
-- REPORT (i): LOYALTY TIER — ALTER TABLE + UPDATE CASE
--
-- Expected grouped output:
-- loyalty_tier | customer_count
-- Gold         | 28
-- Silver       | 17
--
-- IMPORTANT:
-- SQLite cannot add the same column twice. Run the ALTER TABLE
-- and UPDATE once on a fresh database. If loyalty_tier already
-- exists, skip the ALTER TABLE line and run the UPDATE + SELECT.
-- ============================================================

-- Run once only if the column does not already exist:
-- ALTER TABLE customers ADD COLUMN loyalty_tier VARCHAR(10);

UPDATE customers
SET loyalty_tier =
    CASE
        WHEN city_tier = 1 THEN 'Gold'
        ELSE 'Silver'
    END;

SELECT
    loyalty_tier,
    COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier;
