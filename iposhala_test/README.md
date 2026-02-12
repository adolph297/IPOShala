# iposhala_test (Scripts & Utilities)

This directory contains the data pipeline and testing utilities for the IPOShala platform.

## Core Components

- **[scripts](./iposhala_test/scripts)**:
  - `fetch_company_descriptions.py`: Fetches company-specific metadata.
  - `import_company_descriptions.py`: Ingests CSV data into MongoDB.
  - `bulk_fetch_nse_simple.py`: Mass fetcher for IPO data from NSE.
  - `debug_nse.py`: Utility for troubleshooting NSE connection issues.

## Data Workflow

1. **Fetching**: Scripts fetch JSON/CSV data from various financial portals.
2. **Processing**: Data is cleaned and structured for the frontend.
3. **Database**: Scripts interact with MongoDB to ensure data persistence and consistency.

## Usage

Most scripts are designed to be run as standalone modules:
```bash
python scripts/fetch_company_descriptions.py
```

## Logs & Debugging

Log files (stored in the root or local directory) track mass fetching operations and errors.
- `mass_fetch_log.txt`: Summary of mass operations.
- `nse_fetch_log.txt`: Specific logs for NSE API interactions.
