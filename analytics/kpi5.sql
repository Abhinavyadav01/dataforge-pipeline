
-- KPI 5: Product Return Rate - Top 10 and Bottom 10
-- Minimum volume threshold: 20 units ordered

WITH item_returns AS (
    SELECT
        r.order_item_id,
        COUNT(*) AS approved_return_records
    FROM returns_cleaned AS r
    WHERE LOWER(TRIM(r.return_status)) = 'approved'
    GROUP BY r.order_item_id
),

product_metrics AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,

        SUM(fs.quantity) AS total_units_ordered,

        SUM(
            COALESCE(ir.approved_return_records, 0)
        ) AS approved_return_records

    FROM fact_sales AS fs

    JOIN dim_products AS p
        ON fs.product_id = p.product_id

    LEFT JOIN item_returns AS ir
        ON fs.order_item_id = ir.order_item_id

    WHERE LOWER(TRIM(fs.order_status)) IN (
        'complete',
        'completed',
        'complted',
        'returned'
    )

    GROUP BY
        p.product_id,
        p.product_name,
        p.category
),

return_rates AS (
    SELECT
        product_id,
        product_name,
        category,
        total_units_ordered,
        approved_return_records,

        ROUND(
            100.0 * approved_return_records
            / NULLIF(total_units_ordered, 0),
            2
        ) AS return_rate_pct

    FROM product_metrics

    WHERE total_units_ordered >= 20
),

ranked_products AS (
    SELECT
        *,

        ROW_NUMBER() OVER (
            ORDER BY return_rate_pct DESC, product_id
        ) AS highest_rank,

        ROW_NUMBER() OVER (
            ORDER BY return_rate_pct ASC, product_id
        ) AS lowest_rank

    FROM return_rates
)

SELECT
    product_id,
    product_name,
    category,
    total_units_ordered,
    approved_return_records,
    return_rate_pct,

    CASE
        WHEN highest_rank <= 10
            THEN 'Top 10 - Highest Returns'
        WHEN lowest_rank <= 10
            THEN 'Bottom 10 - Lowest Returns'
    END AS return_group

FROM ranked_products

WHERE highest_rank <= 10
   OR lowest_rank <= 10

ORDER BY return_rate_pct DESC, product_id;
