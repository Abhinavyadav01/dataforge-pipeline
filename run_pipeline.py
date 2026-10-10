# import sqlite3
# import pandas as pd

# # Connect to the database
# conn = sqlite3.connect("shopsphere_lakehouse.db")

# try:
#     # Run all 8 KPIs in sequence
#     for i in range(1, 9):
#         file_name = f"analytics/kpi{i}.sql"

#         print("\n" + "=" * 60)
#         print(f"KPI {i} RESULTS")
#         print("=" * 60)

#         try:
#             # Read the SQL query
#             with open(file_name, "r") as f:
#                 query = f.read()

#             # Execute the query
#             result = pd.read_sql_query(query, conn)

#             # Display results
#             print(result.to_string(index=False))

#         except Exception as e:
#             print(f"Error running KPI {i}: {e}")

# finally:
#     # Close database connection
#     conn.close()







import subprocess
import sys
import time
import os

# Force UTF-8 encoding for Windows terminals to prevent charmap errors
sys.stdout.reconfigure(encoding='utf-8')

def run_script(script_path):
    print(f"\n{'='*50}")
    print(f"[EXECUTING] {script_path}")
    print(f"{'='*50}")
    
    if not os.path.exists(script_path):
        print(f"[ERROR] Could not find {script_path}. Please check the filename.")
        sys.exit(1)
        
    start_time = time.time()
    result = subprocess.run([sys.executable, script_path], capture_output=False)
    duration = round(time.time() - start_time, 2)
    
    if result.returncode != 0:
        print(f"\n[CRITICAL ERROR] Pipeline halted. {script_path} failed.")
        sys.exit(1)
        
    print(f"[FINISHED] {script_path} in {duration} seconds.")

def run_full_pipeline():
    print("=== STARTING DATAFORGE END-TO-END PIPELINE ===")
    
    # 1. Bronze Layer (Raw Data Ingestion)
    run_script("src/bronze/bronze.py")
    
    # 2. Silver Layer (Cleansing & Standardization)
    run_script("src/silver/silver.py")
    
    # 3. Gold Layer (Dimensional Modeling & Single Fact Table)
    run_script("src/gold/gold.py")
    
    # 4. Analytics / KPIs (Executes SQL, saves CSVs to /reports)
    run_script("analytics/kpi_analytics.py")
    
    print("\n" + "="*50)
    print("SUCCESS: FULL PIPELINE COMPLETED")
    print("="*50)
    
    # 5. Launch Streamlit Dashboard in the browser
    print("\n[INFO] Launching Streamlit Dashboard in your browser...")
    print("       (Press Ctrl+C in this terminal to stop the dashboard server later)")
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])

if __name__ == "__main__":
    run_full_pipeline()