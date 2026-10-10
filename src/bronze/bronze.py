import pandas as pd
import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
def ingest_to_bronze():
    # 1. Connect to local SQLite database (creates it if it doesn't exist)
    # Saving it in the root folder so all scripts can access it easily
    db_path = 'shopsphere_lakehouse.db'
    conn = sqlite3.connect(db_path)
    
    print("[INFO] Starting Bronze layer ingestion...")
    
    # 2. Map the raw CSV files to their Bronze table names
    datasets = {
        'datasets/raw_data/customers.csv': 'raw_customers',
        'datasets/raw_data/order_items.csv': 'raw_order_items',
        'datasets/raw_data/orders.csv': 'raw_orders',
        'datasets/raw_data/products.csv': 'raw_products',
        'datasets/raw_data/payments.csv': 'raw_payments',
        'datasets/raw_data/returns.csv': 'raw_returns',
    }
    
    # 3. Ingest each file
    for file_path, table_name in datasets.items():
        try:
            # Read the raw CSV exactly as it is
            df = pd.read_csv(file_path)
            
            # Save to SQLite. if_exists='replace' makes this idempotent (re-runnable)
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            print(f"[SUCCESS] Loaded {len(df)} rows from {file_path} into '{table_name}'.")
        except Exception as e:
            print(f"[ERROR] Failed to load {file_path}: {str(e)}")

    try:
        # Read the raw JSON exactly as it is
        df = pd.read_json('datasets/raw_data/suppliers_json.txt')
                
        # Save to SQLite. if_exists='replace' makes this idempotent (re-runnable)
        df.to_sql('raw_suppliers', conn, if_exists='replace', index=False)
                
        print(f"[SUCCESS] Loaded {len(df)} rows from 'datasets/raw_data/suppliers_json.txt' into 'raw_suppliers'.")
    except Exception as e:
        print(f"[ERROR] Failed to load 'datasets/raw_data/suppliers_json.txt': {str(e)}")    
    conn.close()
    print("[INFO] Bronze layer complete.")

if __name__ == "__main__":
    # Ensure the data/raw folder exists and has files before running
    if os.path.exists('datasets/raw_data'):
        ingest_to_bronze()
    else:
        print("[FATAL] data/raw directory not found. Are you in the root folder?")