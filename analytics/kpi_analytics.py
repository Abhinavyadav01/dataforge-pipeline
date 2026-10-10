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










import sqlite3
import pandas as pd
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# Force pandas to display wide columns neatly without wrapping
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def generate_reports():
    print("[INFO] Generating KPI Reports from Gold Layer...")
    
    # Automatically create a 'reports' folder in your root directory
    os.makedirs("reports", exist_ok=True)
    
    conn = sqlite3.connect("shopsphere_lakehouse.db")

    try:
        for i in range(1, 9):
            file_name = f"analytics/kpi{i}.sql"
            
            print("\n" + "=" * 80)
            print(f"KPI {i} RESULTS")
            print("=" * 80)

            try:
                with open(file_name, "r") as f:
                    query = f.read()
                    
                result = pd.read_sql_query(query, conn)
                
                # 1. Save the full table as a CSV file for Power BI
                export_path = f"reports/kpi_{i}_export.csv"
                result.to_csv(export_path, index=False)
                
                # 2. Print a clean summary to the terminal
                print(f"✅ Full report saved successfully to: {export_path}")
                print("\n--- Data Preview (Top 10 Rows) ---")
                
                # .head(10) ensures the terminal doesn't get flooded
                print(result.head(10).to_string(index=False))
                
            except FileNotFoundError:
                print(f"[ERROR] Could not find {file_name}")
            except Exception as e:
                print(f"[ERROR] Failed running KPI {i}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    generate_reports()