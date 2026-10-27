# Resilient Incremental Crypto Data Pipeline

## Technical & Business Goal

Build a robust, production-grade, and containerized data pipeline that extracts real-time market data from a live API (CoinGecko), performs incremental state tracking via watermarks, and guarantees idempotency through atomic upserts into a PostgreSQL database. 

This project transitions away from traditional file-based workflows, utilizing a single-file unified pipeline managed entirely within a Docker Compose environment.

---

## Project Structure

Your project workspace is organized as follows:

```text
retail-data-engines/
├── docs/                 # Documentation assets
├── logs/                 # Runtime log files                  # SQL scripts and query templates
├── src/
│   └── main.py          # Unified pipeline script (state management, API ingestion, upserts)
├── venv_retail/          # Local Python virtual environment (ignored in git)
├── .dockerignore         # Excludes local files/environments from Docker builds
├── .env                  # Environment variables configuration
├── .gitignore            # Git exclusion patterns
├── docker-compose.yaml   # Multi-container orchestration & healthchecks
├── Dockerfile            # Multi-stage build setup for the application
├── README.md             # Project documentation
└── reqs.txt              # Python package dependencies
```

---

## Key Architecture & Design Patterns

- **Unified Python Script (`src/main.py`)**: Merges extraction, transformation, and database loading into a single coherent workflow.
- **Incremental Extraction & Watermarking**: Maintains a dedicated `pipeline_state` metadata table to track the high-water mark timestamp of the last processed batch, ensuring only new data is fetched on subsequent runs.
- **Idempotency via Upserts**: Utilizes PostgreSQL's `INSERT ... ON CONFLICT (coin_id) DO UPDATE` clause to guarantee safe, repeatable execution without creating duplicate rows or throwing key constraint errors.
- **Containerized Infrastructure**: 
  - **Multi-stage Docker Builds**: Keeps runtime images lightweight, fast, and secure.
  - **Healthcheck Dependencies**: Uses Docker Compose `service_healthy` conditions to ensure PostgreSQL is fully initialized and ready before the application container starts.

---

## Tech Stack

- **Language**: Python 3.12 (slim runtime)
- **Database**: PostgreSQL 15 (Alpine)
- **Containerization**: Docker & Docker Compose
- **Database Driver**: `psycopg2`

---

## Getting Started & Running Locally

1. **Configure Environment Variables**:
   Create a `.env` file in the root directory with your database configurations:
   ```env
   POSTGRES_DB=retail
   POSTGRES_USER=retail_user
   POSTGRES_PASSWORD=retail_dev_password
   POSTGRES_PORT=5432
   POSTGRES_HOST=retail_db
   ```

2. **Build and Run the Pipeline**:
   ```bash
   docker compose up --build
   ```

3. **Inspect the Database**:
   Connect to the running PostgreSQL container to verify state and data tables:
   ```bash
   docker exec -it retail_db_container psql -U retail_user -d retail
   ```
   * Useful SQL queries inside `psql`:
     ```sql
     -- Check pipeline watermarks
     SELECT * FROM pipeline_state;

     -- View loaded coin records
     SELECT coin_id, symbol, current_price, last_updated FROM coingecko_coins;
     ```