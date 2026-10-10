
-- KPI 6: Supplier Performance Scorecard
-- Assumed weights:
-- Revenue = 40%, Return Performance = 40%, Supplier Rating = 20%

WITH item_sales AS (
    SELECT
        fs.order_item_id,
        fs.product_id,
        MAX(fs.gross_line_total) AS gross_line_total,
        MAX(fs.quantity) AS quantity
    FROM fact_sales AS fs
    WHERE LOWER(TRIM(fs.order_status)) IN (
        'complete',
        'completed',
        'complted',
        'returned'
    )
    GROUP BY
        fs.order_item_id,
        fs.product_id
),

item_returns AS (
    SELECT
        r.order_item_id,
        SUM(
            CASE
                WHEN LOWER(TRIM(r.return_status)) = 'approved'
                THEN 1
                ELSE 0
            END
        ) AS approved_return_records
    FROM returns_cleaned AS r
    GROUP BY r.order_item_id
),

supplier_metrics AS (
    SELECT
        s.supplier_id,
        s.supplier_name,
        s.rating,

        SUM(i.gross_line_total) AS revenue,
        SUM(i.quantity) AS total_units_ordered,

        SUM(
            COALESCE(ir.approved_return_records, 0)
        ) AS approved_return_records

    FROM dim_suppliers AS s

    JOIN dim_products AS p
        ON s.supplier_id = p.supplier_id

    LEFT JOIN item_sales AS i
        ON p.product_id = i.product_id

    LEFT JOIN item_returns AS ir
        ON i.order_item_id = ir.order_item_id

    GROUP BY
        s.supplier_id,
        s.supplier_name,
        s.rating
),

normalized AS (
    SELECT
        *,

        COALESCE(revenue, 0) AS total_revenue,

        100.0 * COALESCE(revenue, 0)
            / NULLIF(MAX(COALESCE(revenue, 0)) OVER (), 0)
            AS revenue_score,

        100.0 * (
            1.0 -
            COALESCE(approved_return_records, 0) * 1.0
            / NULLIF(total_units_ordered, 0)
        ) AS return_score,

        CASE
            WHEN rating IS NOT NULL
                 AND rating BETWEEN 0 AND 5
                THEN rating * 20.0
            ELSE NULL
        END AS rating_score

    FROM supplier_metrics
)

SELECT
    supplier_id,
    supplier_name,
    ROUND(total_revenue, 2) AS revenue,
    total_units_ordered,
    approved_return_records,
    rating,

    ROUND(revenue_score, 2) AS revenue_score,
    ROUND(return_score, 2) AS return_score,
    ROUND(rating_score, 2) AS rating_score,

    ROUND(
        0.40 * revenue_score
        + 0.40 * return_score
        + 0.20 * rating_score,
        2
    ) AS supplier_performance_score

FROM normalized

ORDER BY supplier_performance_score DESC;
