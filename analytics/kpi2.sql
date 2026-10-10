
-- KPI 2: Top 10 Customers by Net Lifetime Value

WITH item_sales AS (
    SELECT
        fs.order_item_id,
        fs.order_id,
        fs.customer_id,
        MAX(fs.gross_line_total) AS gross_line_total
    FROM fact_sales AS fs
    WHERE LOWER(TRIM(fs.order_status)) IN (
        'complete',
        'completed',
        'complted'
    )
    GROUP BY
        fs.order_item_id,
        fs.order_id,
        fs.customer_id
),

refunds_by_item AS (
    SELECT
        r.order_item_id,
        SUM(r.refund_amount) AS approved_refund
    FROM returns_cleaned AS r
    WHERE LOWER(TRIM(r.return_status)) = 'approved'
    GROUP BY r.order_item_id
)

SELECT
    i.customer_id,
    COALESCE(
        TRIM(c.first_name || ' ' || c.last_name),
        'Unknown Customer'
    ) AS customer_name,

    ROUND(
        SUM(
            i.gross_line_total
            - COALESCE(r.approved_refund, 0)
        ),
        2
    ) AS net_lifetime_value

FROM item_sales AS i

LEFT JOIN refunds_by_item AS r
    ON i.order_item_id = r.order_item_id

LEFT JOIN dim_customers AS c
    ON i.customer_id = c.customer_id

GROUP BY
    i.customer_id,
    c.first_name,
    c.last_name

ORDER BY net_lifetime_value DESC

LIMIT 10;
