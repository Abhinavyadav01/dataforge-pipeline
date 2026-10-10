
-- KPI 1: Net Revenue by Product Category, per Month
-- Database: shopsphere_lakehouse.db

WITH item_sales AS (
    SELECT
        fs.order_item_id,
        fs.order_date,
        fs.product_id,
        MAX(fs.gross_line_total) AS gross_line_total

    FROM fact_sales AS fs

    WHERE LOWER(TRIM(fs.order_status)) IN (
        'complete',
        'completed',
        'complted',
        'returned'
    )

    GROUP BY
        fs.order_item_id,
        fs.order_date,
        fs.product_id
),

refunds_by_item AS (
    SELECT
        r.order_item_id,
        SUM(r.refund_amount) AS approved_refund

    FROM returns_cleaned AS r

    WHERE LOWER(TRIM(r.return_status)) = 'approved'

    GROUP BY r.order_item_id
),

category_revenue AS (
    SELECT
        strftime('%Y-%m', i.order_date) AS month,

        CASE
            WHEN LOWER(TRIM(p.category)) IN (
                'electronics',
                'electornics'
            ) THEN 'Electronics'

            WHEN LOWER(TRIM(p.category)) IN (
                'home and kitchen',
                'home & kitchen'
            ) THEN 'Home & Kitchen'

            WHEN p.category IS NULL
                OR TRIM(p.category) = ''
                THEN 'Unknown'

            ELSE TRIM(p.category)
        END AS category,

        SUM(
            i.gross_line_total
            - COALESCE(r.approved_refund, 0)
        ) AS net_revenue

    FROM item_sales AS i

    JOIN dim_products AS p
        ON i.product_id = p.product_id

    LEFT JOIN refunds_by_item AS r
        ON i.order_item_id = r.order_item_id

    GROUP BY
        strftime('%Y-%m', i.order_date),

        CASE
            WHEN LOWER(TRIM(p.category)) IN (
                'electronics',
                'electornics'
            ) THEN 'Electronics'

            WHEN LOWER(TRIM(p.category)) IN (
                'home and kitchen',
                'home & kitchen'
            ) THEN 'Home & Kitchen'

            WHEN p.category IS NULL
                OR TRIM(p.category) = ''
                THEN 'Unknown'

            ELSE TRIM(p.category)
        END
)

SELECT
    month,
    category,
    ROUND(net_revenue, 2) AS net_revenue

FROM category_revenue

ORDER BY month, category;
