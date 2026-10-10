
import sqlite3
import pandas as pd

conn = sqlite3.connect("shopsphere_lakehouse.db")

with open("analytics/kpi5.sql", "r") as f:
    query = f.read()

result = pd.read_sql_query(query, conn)

print(result.head(20))

conn.close()
