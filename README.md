# ASG Airlines — End-to-End Data Engineering

A reproducible airline data-engineering pipeline that ingests operational flight data, validates data quality, quarantines hard failures, standardises timestamps and routes, handles overnight flights, produces a curated analytical model, and exposes KPIs for Power BI.

> **Public-repository safety:** the original source workbook and raw passenger/booking/payment extracts are intentionally excluded because they contain sensitive-looking fields. A synthetic sample is provided so the pipeline can be executed end-to-end.

## Solution

```text
Source Workbook
      ↓
Ingestion
      ↓
Raw / Landing (local only)
      ↓
Validation & Data Quality
      ├──────────────→ Quarantine + reason codes
      ↓
Cleaning & Transformation
      ↓
Curated / Star-schema-ready data
      ↓
SQL / KPI layer
      ↓
Power BI
```

## Key engineering features
- Schema and field validation
- Explicit reason codes for rejected records
- Quarantine rather than silent deletion
- Duplicate detection
- Timestamp standardisation
- Cross-day/overnight duration handling
- Duration quality classification
- Reconciliation control: input = curated + quarantined
- Data Quality Score covering completeness, validity, uniqueness and consistency
- PII masking before analytical consumption
- Modular Python source code plus executable tests

## KPIs
- Total Flights
- Average Flight Duration
- Route-wise Traffic
- Airline Distribution
- Overnight Flight Share
- Anomaly Rate
- Data Quality Score

Delay minutes are **not fabricated** when scheduled-vs-actual timestamps are unavailable. In that case the dashboard reports data/operational anomalies instead.

## Repository

```text
ASG-Airlines-Data-Engineering/
├── README.md
├── .gitignore
├── requirements.txt
├── run_pipeline.py
├── data/
│   ├── sample/
│   ├── cleaned/
│   ├── curated/
│   └── quarantine/
├── src/
│   ├── ingestion/
│   ├── validation/
│   ├── transformation/
│   └── utils/
├── tests/
├── notebooks/
├── sql/
├── powerbi/
└── docs/
```

## Run

```bash
pip install -r requirements.txt
python run_pipeline.py
pytest -q
```

## Production evolution
The current implementation is deliberately reproducible with Python/pandas and SQL. At production scale, the same contracts can be moved to Azure Data Factory for orchestration, ADLS Gen2 for storage, Databricks/Spark for distributed transformation, and a warehouse/lakehouse for serving.

## Assumptions & limitations
- Validation thresholds are dataset-informed and documented rather than universal aviation rules.
- Overnight logic respects full datetime values when supplied and defensively rolls a negative time-only gap forward by one day.
- Passenger/booking/payment PII is not required for the core flight KPIs and is protected before analytical use.
