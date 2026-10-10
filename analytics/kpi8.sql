
-- KPI 8: Payment Reconciliation & Anomaly Report

WITH order_totals AS (
    SELECT
        oi.order_id,
        ROUND(SUM(oi.line_total), 2) AS calculated_order_total
    FROM order_items_cleaned AS oi
    GROUP BY oi.order_id
),

payment_summary AS (
    SELECT
        p.order_id,
        COUNT(*) AS payment_record_count,

        COUNT(DISTINCT ROUND(p.amount, 2))
            AS distinct_payment_amounts,

        ROUND(SUM(p.amount), 2) AS total_recorded_payment,

        SUM(
            CASE
                WHEN LOWER(TRIM(p.payment_status))
                     IN ('success', 'succeeded', 'succeded')
                THEN 1
                ELSE 0
            END
        ) AS successful_payment_count,

        ROUND(
            SUM(
                CASE
                    WHEN LOWER(TRIM(p.payment_status))
                         IN ('success', 'succeeded', 'succeded')
                    THEN p.amount
                    ELSE 0
                END
            ), 2
        ) AS successful_payment_amount

    FROM payments_cleaned AS p
    GROUP BY p.order_id
),

reconciliation AS (
    SELECT
        o.order_id,
        o.calculated_order_total,

        COALESCE(p.payment_record_count, 0)
            AS payment_record_count,

        COALESCE(p.distinct_payment_amounts, 0)
            AS distinct_payment_amounts,

        COALESCE(p.total_recorded_payment, 0)
            AS total_recorded_payment,

        COALESCE(p.successful_payment_count, 0)
            AS successful_payment_count,

        COALESCE(p.successful_payment_amount, 0)
            AS successful_payment_amount,

        ROUND(
            COALESCE(p.successful_payment_amount, 0)
            - o.calculated_order_total,
            2
        ) AS payment_difference

    FROM order_totals AS o
    LEFT JOIN payment_summary AS p
        ON o.order_id = p.order_id
)

SELECT
    order_id,
    calculated_order_total,
    payment_record_count,
    total_recorded_payment,
    successful_payment_count,
    successful_payment_amount,
    payment_difference,

    CASE
        WHEN payment_record_count = 0
            THEN 'NO PAYMENT RECORD'

        WHEN successful_payment_count = 0
            THEN 'NO SUCCESSFUL PAYMENT'

        WHEN payment_record_count > 1
             AND distinct_payment_amounts > 1
            THEN 'DUPLICATE/CONFLICTING PAYMENT AMOUNTS'

        WHEN successful_payment_amount
             < calculated_order_total - 0.01
            THEN 'UNDERPAYMENT'

        WHEN successful_payment_amount
             > calculated_order_total + 0.01
            THEN 'OVERPAYMENT'

        WHEN payment_record_count > 1
            THEN 'MULTIPLE PAYMENT RECORDS - REVIEW'

        ELSE 'RECONCILED'
    END AS anomaly_status

FROM reconciliation

WHERE
       payment_record_count = 0
    OR successful_payment_count = 0
    OR (payment_record_count > 1 AND distinct_payment_amounts > 1)
    OR ABS(payment_difference) > 0.01
    OR payment_record_count > 1

ORDER BY order_id;
