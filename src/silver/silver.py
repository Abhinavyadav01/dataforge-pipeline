
import pandas as pd
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

def quarantine_records(df, pk_col, date_col=None):
    """Safely separates valid rows from duplicates and bad dates."""
    if df.empty or pk_col not in df.columns:
        return df, pd.DataFrame()

    rejected_list = []
    
    # 1. Duplicates
    dupes = df[df.duplicated(subset=[pk_col], keep='last')].copy()
    if not dupes.empty:
        dupes['reject_reason'] = 'Duplicate Primary Key'
        rejected_list.append(dupes)
        
    df_clean = df.drop_duplicates(subset=[pk_col], keep='last').copy()
    
    # 2. Invalid Dates
    if date_col and date_col in df_clean.columns:
        parsed_dates = pd.to_datetime(df_clean[date_col], format='mixed', errors='coerce')
        bad_date_mask = parsed_dates.isna() & df_clean[date_col].notna() & (df_clean[date_col].astype(str).str.strip() != '')
        
        bad_dates = df_clean[bad_date_mask].copy()
        if not bad_dates.empty:
            bad_dates['reject_reason'] = f'Unparseable date in {date_col}'
            rejected_list.append(bad_dates)
            
        df_clean = df_clean[~bad_date_mask].copy()
        df_clean[date_col] = pd.to_datetime(df_clean[date_col], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d')

    df_rejected = pd.concat(rejected_list, ignore_index=True) if rejected_list else pd.DataFrame()
    return df_clean, df_rejected

def save_tables(conn, df_clean, df_rejected, base_name):
    # UPDATED: Changed output table names to match requested convention
    clean_table_name = f'{base_name}_cleaned'
    rejected_table_name = f'{base_name}_rejected'
    
    df_clean.to_sql(clean_table_name, conn, if_exists='replace', index=False)
    print(f"  -> Saved {len(df_clean)} clean records to {clean_table_name}")
    
    if not df_rejected.empty:
        df_rejected.to_sql(rejected_table_name, conn, if_exists='replace', index=False)
        print(f"  -> Quarantined {len(df_rejected)} records to {rejected_table_name}")

def run_silver_cleansing():
    db_path = 'shopsphere_lakehouse.db'
    conn = sqlite3.connect(db_path)
    print("[INFO] Starting Bulletproof Silver Pipeline...")

    # Helper to check if table exists
    def table_exists(name):
        return conn.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{name}'").fetchone()[0] > 0

    # --- 1. Suppliers ---
    try:
        if table_exists('raw_suppliers'):
            print("\nProcessing Suppliers...")
            df_sup = pd.read_sql("SELECT * FROM raw_suppliers", conn)
            df_sup_clean, df_sup_rej = quarantine_records(df_sup, 'supplier_id', 'contract_start_date')
            
            if 'country' in df_sup_clean.columns:
                df_sup_clean['country'] = df_sup_clean['country'].fillna('Unknown')
            if 'is_preferred' in df_sup_clean.columns:
                df_sup_clean['is_preferred'] = df_sup_clean['is_preferred'].apply(lambda x: True if str(x).lower() in ['y', 'true', '1'] else False)
            if 'rating' in df_sup_clean.columns:
                df_sup_clean['rating'] = pd.to_numeric(df_sup_clean['rating'], errors='coerce')
                df_sup_clean['rating'] = df_sup_clean['rating'].apply(lambda x: x / 2 if pd.notnull(x) and x > 5.0 else x)
            save_tables(conn, df_sup_clean, df_sup_rej, 'suppliers')
    except Exception as e: print(f"[ERROR] Suppliers failed: {e}")

    # --- 2. Customers ---
    try:
        if table_exists('raw_customers'):
            print("\nProcessing Customers...")
            df_cust = pd.read_sql("SELECT * FROM raw_customers", conn)
            df_cust_clean, df_cust_rej = quarantine_records(df_cust, 'customer_id', 'signup_date')
            
            if 'email' in df_cust_clean.columns:
                df_cust_clean['email'] = df_cust_clean['email'].astype(str).str.lower().replace('nan', 'unknown@email.com')
            if 'customer_segment' in df_cust_clean.columns:
                df_cust_clean['customer_segment'] = df_cust_clean['customer_segment'].astype(str).str.title().replace('Nan', 'Unassigned')
            save_tables(conn, df_cust_clean, df_cust_rej, 'customers')
    except Exception as e: print(f"[ERROR] Customers failed: {e}")

    # --- 3. Products ---
    try:
        if table_exists('raw_products'):
            print("\nProcessing Products...")
            df_prod = pd.read_sql("SELECT * FROM raw_products", conn)
            df_prod_clean, df_prod_rej = quarantine_records(df_prod, 'product_id', 'launch_date' if 'launch_date' in df_prod.columns else None)
            
            for col in ['unit_price', 'cost_price']:
                if col in df_prod_clean.columns:
                    df_prod_clean[col] = pd.to_numeric(df_prod_clean[col], errors='coerce').fillna(0.0).abs()
            if 'category' in df_prod_clean.columns:
                df_prod_clean['category'] = df_prod_clean['category'].astype(str).str.title().replace('Nan', 'Unknown')
            save_tables(conn, df_prod_clean, df_prod_rej, 'products')
    except Exception as e: print(f"[ERROR] Products failed: {e}")

    # --- 4. Orders ---
    try:
        if table_exists('raw_orders'):
            print("\nProcessing Orders...")
            df_ord = pd.read_sql("SELECT * FROM raw_orders", conn)
            df_ord_clean, df_ord_rej = quarantine_records(df_ord, 'order_id', 'order_date')
            
            for col, fill in [('order_status', 'Pending'), ('channel', 'Unknown'), ('shipping_city', 'Unknown')]:
                if col in df_ord_clean.columns:
                    df_ord_clean[col] = df_ord_clean[col].astype(str).str.title().replace('Nan', fill)
            save_tables(conn, df_ord_clean, df_ord_rej, 'orders')
    except Exception as e: print(f"[ERROR] Orders failed: {e}")

    # --- 5. Order Items ---
    try:
        if table_exists('raw_order_items'):
            print("\nProcessing Order Items...")
            df_items = pd.read_sql("SELECT * FROM raw_order_items", conn)
            df_items_clean, df_items_rej = quarantine_records(df_items, 'order_item_id')
            
            if 'quantity' in df_items_clean.columns:
                df_items_clean['quantity'] = pd.to_numeric(df_items_clean['quantity'], errors='coerce').fillna(1)
                df_items_clean['quantity'] = df_items_clean['quantity'].apply(lambda x: x if x > 0 else 1)
            
            if 'discount_pct' in df_items_clean.columns:
                df_items_clean['discount_pct'] = pd.to_numeric(df_items_clean['discount_pct'], errors='coerce').fillna(0.0)
                df_items_clean['discount_pct'] = df_items_clean['discount_pct'].apply(lambda x: x if 0 <= x <= 1 else (x/100 if x > 1 else 0.0))
            
            if 'unit_price' in df_items_clean.columns:
                df_items_clean['unit_price'] = pd.to_numeric(df_items_clean['unit_price'], errors='coerce').fillna(0.0).abs()
                
            if all(c in df_items_clean.columns for c in ['quantity', 'unit_price', 'discount_pct']):
                df_items_clean['line_total'] = round((df_items_clean['quantity'] * df_items_clean['unit_price']) * (1 - df_items_clean['discount_pct']), 2)
            
            save_tables(conn, df_items_clean, df_items_rej, 'order_items')
    except Exception as e: print(f"[ERROR] Order Items failed: {e}")

    # --- 6. Payments ---
    try:
        if table_exists('raw_payments'):
            print("\nProcessing Payments...")
            df_pay = pd.read_sql("SELECT * FROM raw_payments", conn)
            df_pay_clean, df_pay_rej = quarantine_records(df_pay, 'payment_id', 'payment_date')
            
            if 'amount' in df_pay_clean.columns:
                df_pay_clean['amount'] = pd.to_numeric(df_pay_clean['amount'], errors='coerce').fillna(0.0).abs()
            if 'payment_status' in df_pay_clean.columns:
                df_pay_clean['payment_status'] = df_pay_clean['payment_status'].astype(str).str.title().replace('Nan', 'Unknown')
            save_tables(conn, df_pay_clean, df_pay_rej, 'payments')
    except Exception as e: print(f"[ERROR] Payments failed: {e}")

    # --- 7. Returns ---
    try:
        if table_exists('raw_returns'):
            print("\nProcessing Returns...")
            df_ret = pd.read_sql("SELECT * FROM raw_returns", conn)
            df_ret_clean, df_ret_rej = quarantine_records(df_ret, 'return_id', 'return_date')
            
            if 'refund_amount' in df_ret_clean.columns:
                df_ret_clean['refund_amount'] = pd.to_numeric(df_ret_clean['refund_amount'], errors='coerce').fillna(0.0).abs()
            if 'return_status' in df_ret_clean.columns:
                df_ret_clean['return_status'] = df_ret_clean['return_status'].astype(str).str.title().replace('Nan', 'Unknown')
            save_tables(conn, df_ret_clean, df_ret_rej, 'returns')
    except Exception as e: print(f"[ERROR] Returns failed: {e}")

    print("\n[SUCCESS] Bulletproof Pipeline execution finished. Data saved in '_cleaned' and '_rejected' tables.")
    conn.close()

if __name__ == "__main__":
    run_silver_cleansing()