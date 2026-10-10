
-- KPI 7: Customer Repeat-Purchase Rate
-- Definition: Another completed order within 90 days
-- of the customer's first completed order.

WITH completed_orders AS (
    SELECT DISTINCT
        fs.customer_id,
        fs.order_id,
        DATE(fs.order_date) AS order_date

    FROM fact_sales AS fs

    WHERE LOWER(TRIM(fs.order_status)) IN (
        'complete',
        'completed',
        'complted'
    )

    AND fs.customer_id IS NOT NULL
),

first_order AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date

    FROM completed_orders

    GROUP BY customer_id
),

repeat_customers AS (
    SELECT DISTINCT
        f.customer_id

    FROM first_order AS f

    JOIN completed_orders AS o
        ON f.customer_id = o.customer_id

    WHERE o.order_date > f.first_order_date

      AND o.order_date <= DATE(
          f.first_order_date,
          '+90 days'
      )
)

SELECT
    COUNT(*) AS total_customers,

    (SELECT COUNT(*)
     FROM repeat_customers) AS repeat_customers,

    ROUND(
        100.0 * (SELECT COUNT(*) FROM repeat_customers)
        / NULLIF(COUNT(*), 0),
        2
    ) AS repeat_purchase_rate_pct

FROM first_order;
