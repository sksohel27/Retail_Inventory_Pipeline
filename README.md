# Retail Inventory ETL Pipeline

An end-to-end data engineering project that simulates a real-world retail inventory pipeline — from raw data ingestion to automated transformation, star schema modelling in PostgreSQL, and live KPI dashboards in Power BI. Fully containerised with Docker.

---

## Project Architecture

```
Raw CSV Files → Extract → Validate → Transform → Load → PostgreSQL → Power BI
                                                            ↑
                                                      APScheduler
                                                    (Daily at 8 AM)
```

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data Generation | Python, NumPy, Pandas |
| Extraction and Transformation | Pandas, Python |
| Data Quality | Custom validation checks |
| Storage | PostgreSQL (Star Schema) |
| Orchestration | APScheduler |
| Reporting | Power BI |
| Containerisation | Docker, Docker Compose |

---

## Project Structure

```
inventory_etl_pipeline/
│
├── data/
│   └── raw/                  # Raw CSV files
│
├── etl/
│   ├── generate_data.py      # Generates realistic raw data
│   ├── transform.py          # Extract, validate, transform
│   ├── load.py               # Load into PostgreSQL
│   ├── pipeline.py           # Main pipeline runner
│   └── scheduler.py          # Daily scheduler
│
├── logs/                     # Pipeline run logs
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Data Model — Star Schema

```
               dim_supplier
                    |
     dim_date — dim_product — fact_stock
                    |
               fact_sales
```

### Tables

- dim_supplier — supplier details (name, city, contact)
- dim_product — product details (category, price, reorder level)
- dim_date — date breakdown (year, month, quarter)
- fact_sales — one row per sale (revenue, quantity, city)
- fact_stock — current stock levels with low stock flag

---

## Power BI Dashboard

Connects live to PostgreSQL and tracks:

- Total Revenue (Card)
- Revenue by Month (Line Chart)
- Top 10 Products by Revenue (Bar Chart)
- Revenue by Category (Pie Chart)
- Low Stock Alerts (Table — filtered to is_low_stock = true)

---

## How To Run

### Option 1 — Docker (Recommended)

Make sure Docker Desktop is running, then:

```bash
docker-compose up --build
```

This spins up PostgreSQL and runs the full ETL pipeline automatically in one command.

### Option 2 — Run Locally

Step 1 — Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

Step 3 — Create a .env file in the root folder

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=inventory_db
DB_USER=postgres
DB_PASSWORD=your_password
```

Step 4 — Generate raw data

```bash
python etl/generate_data.py
```

Step 5 — Run the pipeline

```bash
python etl/pipeline.py
```

Step 6 — Run the scheduler for daily auto-run

```bash
python etl/scheduler.py
```

---

## Data Quality Checks

The pipeline validates at every stage:

- Row count assertions after each load
- Null checks on critical columns (product_id, sale_id)
- Duplicate detection on all primary keys
- Pipeline stops immediately and logs error if any check fails

---

## Logs

Every pipeline run is logged automatically in the logs/ folder:

- pipeline.log — ETL run details, row counts, errors
- scheduler.log — scheduler start, stop, run history

---

## Key Features

- Modular ETL pipeline with separate extract, validate, transform and load steps
- Star schema design with fact and dimension tables
- Automated daily scheduling without any manual trigger
- Full Docker containerisation — runs anywhere with one command
- Data quality validation built into every stage
- Power BI dashboard connected live to PostgreSQL