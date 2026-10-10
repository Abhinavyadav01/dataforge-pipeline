
-- KPI 3: Standardized Customer Segment Profile

WITH order_values AS (
    SELECT
        fs.order_id,
        fs.customer_id,
        MAX(fs.order_date) AS order_date,
        SUM(fs.gross_line_total) AS order_value

    FROM fact_sales AS fs

    WHERE LOWER(TRIM(fs.order_status)) IN (
        'complete',
        'completed',
        'complted'
    )

    GROUP BY
        fs.order_id,
        fs.customer_id
),

customer_segments AS (
    SELECT
        c.customer_id,

        CASE
            WHEN LOWER(TRIM(c.customer_segment))
                IN ('bronze', 'broze')
                THEN 'Bronze'

            WHEN LOWER(TRIM(c.customer_segment))
                IN ('silver', 'silverr')
                THEN 'Silver'

            WHEN LOWER(TRIM(c.customer_segment))
                IN ('gold', 'glod')
                THEN 'Gold'

            WHEN c.customer_segment IS NULL
                OR TRIM(c.customer_segment) = ''
                OR LOWER(TRIM(c.customer_segment)) = 'unassigned'
                THEN 'Unassigned'

            ELSE TRIM(c.customer_segment)
        END AS customer_segment

    FROM dim_customers AS c
)

SELECT
    cs.customer_segment,

    COUNT(DISTINCT cs.customer_id) AS customer_count,

    ROUND(AVG(ov.order_value), 2) AS average_order_value

FROM customer_segments AS cs

LEFT JOIN order_values AS ov
    ON cs.customer_id = ov.customer_id

GROUP BY cs.customer_segment

ORDER BY customer_count DESC;
