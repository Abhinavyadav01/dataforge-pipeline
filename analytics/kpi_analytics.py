
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect("shopsphere_lakehouse.db")

try:
    # Run all 8 KPIs in sequence
    for i in range(1, 9):
        file_name = f"analytics/kpi{i}.sql"

        print("\n" + "=" * 60)
        print(f"KPI {i} RESULTS")
        print("=" * 60)

        try:
            # Read the SQL query
            with open(file_name, "r") as f:
                query = f.read()

            # Execute the query
            result = pd.read_sql_query(query, conn)

            # Display results
            print(result.to_string(index=False))

        except Exception as e:
            print(f"Error running KPI {i}: {e}")

finally:
    # Close database connection
    conn.close()
