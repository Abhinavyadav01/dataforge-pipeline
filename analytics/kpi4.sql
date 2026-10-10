
-- KPI 4: MoM Order Volume & Revenue Growth by Channel

WITH monthly_channel AS (
    SELECT
        strftime('%Y-%m', fs.order_date) AS month,

        CASE
            WHEN LOWER(TRIM(fs.channel))
                IN ('web', 'website', 'online')
                THEN 'Web'
            WHEN LOWER(TRIM(fs.channel))
                IN ('app', 'mobile app')
                THEN 'App'
            WHEN LOWER(TRIM(fs.channel))
                IN ('store', 'in-store', 'instore')
                THEN 'Store'
            ELSE 'Other'
        END AS channel,

        COUNT(DISTINCT fs.order_id) AS order_volume,
        SUM(fs.gross_line_total) AS revenue

    FROM fact_sales AS fs

    WHERE LOWER(TRIM(fs.order_status)) IN (
        'complete',
        'completed',
        'complted'
    )

    GROUP BY
        strftime('%Y-%m', fs.order_date),
        CASE
            WHEN LOWER(TRIM(fs.channel))
                IN ('web', 'website', 'online')
                THEN 'Web'
            WHEN LOWER(TRIM(fs.channel))
                IN ('app', 'mobile app')
                THEN 'App'
            WHEN LOWER(TRIM(fs.channel))
                IN ('store', 'in-store', 'instore')
                THEN 'Store'
            ELSE 'Other'
        END
),

monthly_growth AS (
    SELECT
        month,
        channel,
        order_volume,
        revenue,

        LAG(order_volume) OVER (
            PARTITION BY channel
            ORDER BY month
        ) AS previous_month_orders,

        LAG(revenue) OVER (
            PARTITION BY channel
            ORDER BY month
        ) AS previous_month_revenue

    FROM monthly_channel
)

SELECT
    month,
    channel,
    order_volume,
    ROUND(revenue, 2) AS revenue,
    previous_month_orders,
    ROUND(previous_month_revenue, 2) AS previous_month_revenue,

    ROUND(
        100.0 * (order_volume - previous_month_orders)
        / NULLIF(previous_month_orders, 0),
        2
    ) AS order_volume_growth_pct,

    ROUND(
        100.0 * (revenue - previous_month_revenue)
        / NULLIF(previous_month_revenue, 0),
        2
    ) AS revenue_growth_pct

FROM monthly_growth

ORDER BY month, channel;
