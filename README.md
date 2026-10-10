# 🛒 ShopSphere DataForge Pipeline

An end-to-end, automated data engineering pipeline that transforms raw e-commerce data into actionable business intelligence. Built using a strict **Medallion Architecture**, this pipeline cleanses data, tracks historical changes using SCD Type 2 frameworks, models the data into a high-performance One Big Table (OBT), and serves business-critical KPIs through an interactive Streamlit dashboard.

---

## 🏗️ Architecture & Pipeline Flow

The pipeline is orchestrated by a single master script (`run_pipeline.py`) that executes four distinct layers:

### 🥉 1. Bronze Layer (Raw Data)
* **Objective:** Ingest raw, messy data from upstream systems (orders, customers, products, payments, returns, and suppliers).
* **Process:** Loads raw data into the `shopsphere_lakehouse.db` SQLite database with zero transformations to maintain an immutable history of source data.

### 🥈 2. Silver Layer (Cleansing & Standardization)
* **Objective:** Create a trusted, filtered, and standardized single source of truth.
* **Process:** Handles missing values, standardizes date formats, cleans up inconsistent categorical text (e.g., standardizing "broze" and "glod" to "Bronze" and "Gold"), and drops duplicate records.

### 🥇 3. Gold Layer (Dimensional Modeling)
* **Objective:** Optimize data for fast, aggregated BI reporting and historical accuracy.
* **Process:** 
  * **SCD Type 2 Foundation:** Builds dimension tables (e.g., `dim_customers`) engineered with `valid_from`, `valid_to`, and `is_current` columns to support tracking customer attributes over time without losing historical context.
  * **One Big Table (OBT):** Joins Orders, Order Items, Returns, and Payments into a single consolidated `fact_sales` table to eliminate complex joins during the analytics phase.

### 📊 4. Analytics & Presentation Layer
* **Objective:** Serve automated business insights.
* **Process:** Executes 8 complex SQL scripts against the Gold layer, exports the final tables to CSV reports, and automatically spins up a clean, wide-format **Streamlit Dashboard** for stakeholder consumption.

---

## 📈 Key Business KPIs Tracked

The analytics engine automatically generates 8 critical reports designed for executive decision-making:

1. **Net Revenue by Product Category:** Tracks true monthly retained earnings by subtracting approved refunds from gross category sales.
2. **Top 10 Customers by Net Lifetime Value:** Identifies VIP heavy-spenders for targeted loyalty retention.
3. **Customer Segment Profile:** Measures the volume and Average Order Value (AOV) across Bronze, Silver, and Gold loyalty tiers.
4. **MoM Growth by Channel:** Calculates Month-over-Month percentage growth in volume and revenue across Web, App, and In-Store channels.
5. **Product Return Rate:** Highlights the Top 10 worst-performing and Top 10 best-performing products based on return volume.
6. **Supplier Performance Scorecard:** Ranks vendors using a weighted composite score (40% Revenue, 40% Return Performance, 20% Supplier Rating).
7. **Customer Repeat-Purchase Rate:** Measures retention by tracking the percentage of users who place a second order within 90 days.
8. **Automated Payment Reconciliation:** Acts as an automated financial auditor, flagging exact dollar anomalies like underpayments, overpayments, and missing payment records.

---

## 🚀 Quickstart Guide

### Prerequisites
Ensure you have Python installed, then install the required libraries:
```bash
pip install pandas streamlit
```

### Execution
Run the entire pipeline—from raw data ingestion to dashboard deployment—with a single command:
```bash
python run_pipeline.py
```

**What happens next?**
1. The terminal will output the execution status of the Bronze, Silver, and Gold layers.
2. The Analytics engine will execute the KPI queries and save the results in a new `reports/` directory.
3. A Streamlit web server will automatically start and open the interactive dashboard in your default web browser.

---

## 📂 Project Structure

```text
dataforge-pipeline/
│
├── datasets/
│   └──raw_data/               # All 7 datasets
├── analytics/
│   ├── kpi_analytics.py       # SQL execution and CSV export engine
│   ├── kpi1.sql               # Net Revenue by Category
│   ├── kpi2.sql               # Top 10 Customers (LTV)
│   ├── kpi3.sql               # Customer Segment Profile
│   ├── kpi4.sql               # MoM Growth by Channel
│   ├── kpi5.sql               # Product Return Rates
│   ├── kpi6.sql               # Supplier Scorecard
│   ├── kpi7.sql               # Repeat-Purchase Rate
│   └── kpi8.sql               # Payment Reconciliation
│
├── src/
│   ├── bronze/
│   │   └── bronze.py          # Raw data ingestion
│   ├── silver/
│   │   └── silver.py          # Cleansing and standardization
│   └── gold/
│       └── gold.py            # Dimensional modeling (SCD Type 2 & OBT)
│
├── reports/                   # Auto-generated CSV KPI outputs
├── dashboard.py               # Streamlit presentation layer
├── run_pipeline.py            # Master orchestration script
└── shopsphere_lakehouse.db    # Local SQLite Data Lakehouse
```