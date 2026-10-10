import streamlit as st
import pandas as pd
import os

# Configure page to use full width for clean tables
st.set_page_config(page_title="DataForge KPIs", layout="wide")
st.title("DataForge Pipeline: Final KPI Reports")

# Loop through and display all 8 reports
for i in range(1, 9):
    file_path = f"reports/kpi_{i}_export.csv"
    
    st.subheader(f"KPI {i} Results")
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Display as a clean, interactive table
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning(f"Report {file_path} not found. Did the analytics script run?")
        
    st.divider()