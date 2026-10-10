import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

def run_gold_modeling():
    db_path = 'shopsphere_lakehouse.db'
    print("[INFO] Starting Gold Layer Dimensional Modeling (Single Fact Table)...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # ---------------------------------------------------------
        # 1. BUILD DIMENSION TABLES
        # ---------------------------------------------------------
        print("  -> Building dim_customers...")
        cursor.execute("DROP TABLE IF EXISTS dim_customers")
        cursor.execute("""
            CREATE TABLE dim_customers AS
            SELECT 
                customer_id, first_name, last_name, email, customer_segment,
                signup_date AS valid_from, '9999-12-31' AS valid_to, 1 AS is_current
            FROM customers_cleaned
        """)

        print("  -> Building dim_products...")
        cursor.execute("DROP TABLE IF EXISTS dim_products")
        cursor.execute("""
            CREATE TABLE dim_products AS
            SELECT product_id, product_name, category, supplier_id, unit_price, cost_price
            FROM products_cleaned
        """)

        print("  -> Building dim_suppliers...")
        cursor.execute("DROP TABLE IF EXISTS dim_suppliers")
        cursor.execute("""
            CREATE TABLE dim_suppliers AS
            SELECT supplier_id, supplier_name, country, rating, is_preferred
            FROM suppliers_cleaned
        """)

        # ---------------------------------------------------------
        # 2. BUILD SINGLE FACT TABLE (fact_sales)
        # ---------------------------------------------------------
        print("  -> Building single consolidated fact_sales table...")
        cursor.execute("DROP TABLE IF EXISTS fact_sales")
        
        # We join Order Items (base grain) with Orders, Returns, and aggregated Payments
        cursor.execute("""
            CREATE TABLE fact_sales AS
            SELECT 
                -- Identifiers
                oi.order_item_id,
                oi.order_id,
                o.customer_id,
                oi.product_id,
                
                -- Order Header Context
                o.order_date,
                o.order_status,
                o.channel,
                o.shipping_city,
                
                -- Sales Metrics
                oi.quantity,
                oi.unit_price,
                oi.discount_pct,
                oi.line_total AS gross_line_total,
                
                -- Return Metrics
                r.return_id,
                r.return_date,
                COALESCE(r.refund_amount, 0.0) AS refund_amount,
                r.return_status,
                
                -- Net Revenue Calculation (Gross minus Refunds)
                (oi.line_total - COALESCE(r.refund_amount, 0.0)) AS net_line_total,
                
                -- Payment Metrics (Aggregated to Order level, repeated per item)
                COALESCE(p.total_order_payment, 0.0) AS total_order_payment,
                p.primary_payment_status
                
            FROM order_items_cleaned oi
            JOIN orders_cleaned o 
                ON oi.order_id = o.order_id
            LEFT JOIN returns_cleaned r 
                ON oi.order_item_id = r.order_item_id
            LEFT JOIN (
                -- Pre-aggregate payments to the order level to avoid exploding row counts
                SELECT 
                    order_id, 
                    SUM(amount) AS total_order_payment, 
                    MAX(payment_status) AS primary_payment_status
                FROM payments_cleaned
                GROUP BY order_id
            ) p ON oi.order_id = p.order_id
        """)

        conn.commit()
        print("[SUCCESS] Gold Layer creation complete. 1 Fact Table and 3 Dimension Tables ready.")

    except sqlite3.OperationalError as e:
        print(f"[ERROR] Database error: {e}. (Did the Silver layer run successfully?)")
    except Exception as e:
        print(f"[ERROR] Pipeline failed: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_gold_modeling()