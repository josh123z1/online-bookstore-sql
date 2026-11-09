-- Business insight queries
-- Each query answers one of the five business questions.

-- ============================================================
-- E.1 Genre Revenue and Year-Over-Year Share
-- ============================================================
-- This query calculates each genre's total revenue and percentage share of
-- annual revenue for each year. A CTE computes per-genre revenue grouped by
-- year, a second CTE derives annual totals, and the final SELECT calculates
-- the revenue share percentage. Only orders with payment_status = 'Success'
-- are included.

WITH genre_revenue AS (
    SELECT
        strftime('%Y', o.order_date) AS order_year,
        g.genre_name,
        SUM(oi.quantity * oi.unit_price) AS genre_revenue
    FROM Orders o
    JOIN Payment p
        ON o.order_id = p.order_id
    JOIN Order_Item oi
        ON o.order_id = oi.order_id
    JOIN Book b
        ON oi.book_id = b.book_id
    JOIN Genre g
        ON b.genre_id = g.genre_id
    WHERE p.payment_status = 'Success'
    GROUP BY strftime('%Y', o.order_date), g.genre_name
),
year_totals AS (
    SELECT
        order_year,
        SUM(genre_revenue) AS total_year_revenue
    FROM genre_revenue
    GROUP BY order_year
)
SELECT
    gr.order_year,
    gr.genre_name,
    ROUND(gr.genre_revenue, 2)                             AS genre_revenue,
    ROUND(100.0 * gr.genre_revenue / yt.total_year_revenue, 2) AS revenue_share_pct
FROM genre_revenue gr
JOIN year_totals yt
    ON gr.order_year = yt.order_year
ORDER BY gr.order_year, genre_revenue DESC;

-- ============================================================
-- E.2 Top 10 Best-Selling Books and Selling Price Comparison
-- ============================================================
-- This query identifies the top 10 books by units sold among successfully paid
-- orders and compares their weighted average selling price against the
-- catalogue list price. The price_difference and discount_pct columns quantify
-- the discount applied at the transaction level.

WITH valid_sales AS (
    SELECT
        oi.book_id,
        oi.quantity,
        oi.unit_price
    FROM Orders o
    JOIN Payment p  ON o.order_id = p.order_id
    JOIN Order_Item oi ON o.order_id = oi.order_id
    WHERE p.payment_status = 'Success'
)
SELECT
    b.title,
    g.genre_name,
    SUM(vs.quantity)                                              AS total_units_sold,
    ROUND(SUM(vs.quantity * vs.unit_price) * 1.0 / SUM(vs.quantity), 2)
                                                                  AS avg_selling_price,
    ROUND(b.list_price, 2)                                        AS list_price,
    ROUND(
        b.list_price - (SUM(vs.quantity * vs.unit_price) * 1.0 / SUM(vs.quantity)),
        2
    )                                                             AS price_difference,
    ROUND(
        (b.list_price - (SUM(vs.quantity * vs.unit_price) * 1.0 / SUM(vs.quantity)))
        * 100.0 / b.list_price,
        2
    )                                                             AS discount_pct
FROM valid_sales vs
JOIN Book b  ON vs.book_id = b.book_id
JOIN Genre g ON b.genre_id = g.genre_id
GROUP BY b.book_id, b.title, g.genre_name, b.list_price
ORDER BY total_units_sold DESC, avg_selling_price DESC
LIMIT 10;

-- ============================================================
-- E.3 Monthly Order Volume and Revenue Trends
-- ============================================================
-- This query aggregates monthly order volume and book-level revenue across the
-- full dataset, restricted to successfully paid orders. Grouping by
-- STRFTIME('%Y-%m') enables month-by-month trend analysis and identification
-- of seasonal demand patterns.

WITH valid_sales AS (
    SELECT
        o.order_id,
        o.order_date,
        oi.quantity,
        oi.unit_price,
        (oi.quantity * oi.unit_price) AS item_revenue
    FROM Orders o
    JOIN Payment p  ON o.order_id = p.order_id
    JOIN Order_Item oi ON o.order_id = oi.order_id
    WHERE p.payment_status = 'Success'
)
SELECT
    STRFTIME('%Y-%m', date(order_date)) AS year_month,
    COUNT(DISTINCT order_id)            AS total_orders,
    ROUND(SUM(item_revenue), 2)         AS total_revenue
FROM valid_sales
GROUP BY year_month
ORDER BY year_month;

-- ============================================================
-- E.4 Customer Lifetime Spending by Quartile
-- ============================================================
-- This query segments customers into four equal spending quartiles using the
-- NTILE(4) window function applied to each customer's total lifetime book-
-- level spend on successful orders. A SUM() window function in the final
-- SELECT derives each quartile's share of total revenue.

WITH customer_spending AS (
    SELECT
        o.customer_id,
        SUM(oi.quantity * oi.unit_price) AS lifetime_spend
    FROM Orders o
    JOIN Payment p  ON o.order_id = p.order_id
    JOIN Order_Item oi ON o.order_id = oi.order_id
    WHERE p.payment_status = 'Success'
    GROUP BY o.customer_id
),
quartile_assigned AS (
    SELECT
        customer_id,
        lifetime_spend,
        NTILE(4) OVER (ORDER BY lifetime_spend) AS quartile
    FROM customer_spending
),
quartile_summary AS (
    SELECT
        quartile,
        COUNT(customer_id)          AS num_customers,
        ROUND(SUM(lifetime_spend), 2) AS total_revenue,
        ROUND(AVG(lifetime_spend), 2) AS avg_spend
    FROM quartile_assigned
    GROUP BY quartile
)
SELECT
    CASE quartile
        WHEN 1 THEN 'Q1 (Lowest spend)'
        WHEN 2 THEN 'Q2'
        WHEN 3 THEN 'Q3'
        WHEN 4 THEN 'Q4 (Highest spend)'
    END                                                AS spending_quartile,
    num_customers,
    total_revenue,
    avg_spend,
    ROUND(total_revenue * 100.0 / SUM(total_revenue) OVER (), 2) AS revenue_share_pct
FROM quartile_summary
ORDER BY quartile;

-- ============================================================
-- E.5 Repeat Purchase Rate and Average Order Value by Customer Type
-- ============================================================
-- This query calculates the repeat purchase rate and compares average order
-- value between first-time and returning customers. ROW_NUMBER() partitioned
-- by customer_id and ordered by order_date labels each customer's earliest
-- order as 'First-Time' and all subsequent orders as 'Returning'. The repeat
-- purchase rate is computed in a separate CTE and appended via CROSS JOIN.

WITH successful_orders AS (
    SELECT
        o.customer_id,
        o.order_id,
        date(o.order_date) AS order_date,
        o.total_amount
    FROM Orders o
    JOIN Payment p ON o.order_id = p.order_id
    WHERE p.payment_status = 'Success'
),
customer_order_counts AS (
    SELECT
        customer_id,
        COUNT(order_id) AS successful_order_count
    FROM successful_orders
    GROUP BY customer_id
),
repeat_rate AS (
    SELECT
        ROUND(
            100.0 * SUM(CASE WHEN successful_order_count > 1 THEN 1 ELSE 0 END)
            / COUNT(*),
            2
        ) AS repeat_purchase_rate_pct
    FROM customer_order_counts
),
labelled_orders AS (
    SELECT
        customer_id,
        order_id,
        total_amount,
        CASE
            WHEN ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY order_date
            ) = 1 THEN 'First-Time'
            ELSE 'Returning'
        END AS customer_type
    FROM successful_orders
),
aov_summary AS (
    SELECT
        customer_type,
        COUNT(DISTINCT customer_id) AS num_customers,
        COUNT(order_id)             AS num_orders,
        ROUND(AVG(total_amount), 2) AS avg_order_value
    FROM labelled_orders
    GROUP BY customer_type
)
SELECT
    a.customer_type,
    a.num_customers,
    a.num_orders,
    a.avg_order_value,
    r.repeat_purchase_rate_pct
FROM aov_summary a
CROSS JOIN repeat_rate r
ORDER BY a.customer_type DESC;
