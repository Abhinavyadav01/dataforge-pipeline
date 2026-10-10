import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

def run_bronze_validation():
    # Connect to the exact database created by your ingest_to_bronze script
    db_path = 'shopsphere_lakehouse.db'
    
    if not os.path.exists(db_path):
        print(f"[FATAL] Database {db_path} not found. Run your bronze ingestion script first.")
        return

    conn = sqlite3.connect(db_path)
    
    # Queries updated to use your exact 'raw_' table names
    queries = {
        "Suppliers: Duplicates": "SELECT COUNT(*) FROM (SELECT supplier_id FROM raw_suppliers GROUP BY supplier_id HAVING COUNT(*) > 1)",
        "Suppliers: Null Countries": "SELECT COUNT(*) FROM raw_suppliers WHERE country IS NULL",
        "Suppliers: Ratings > 5.0": "SELECT COUNT(*) FROM raw_suppliers WHERE CAST(rating AS FLOAT) > 5.0",
        "Customers: Null Segments": "SELECT COUNT(*) FROM raw_customers WHERE customer_segment IS NULL",
        "Products: Negative Prices": "SELECT COUNT(*) FROM raw_products WHERE unit_price < 0 OR cost_price < 0",
        "Order Items: Math Mismatch": "SELECT COUNT(*) FROM raw_order_items WHERE ABS(((quantity * unit_price) * (1 - discount_pct)) - line_total) > 0.01",
        "Ref Integrity: Orphan Orders": "SELECT COUNT(*) FROM raw_orders o LEFT JOIN raw_customers c ON o.customer_id = c.customer_id WHERE c.customer_id IS NULL"
    }

    print("\n--- BRONZE DATA QUALITY ANOMALIES ---")
    for desc, query in queries.items():
        try:
            result = conn.execute(query).fetchone()[0]
            print(f"{desc}: {result}")
        except sqlite3.OperationalError:
            print(f"{desc}: [SKIPPED - Table not found]")
            
    conn.close()

if __name__ == "__main__":
    run_bronze_validation()