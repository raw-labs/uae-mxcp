# UAE Business Licenses - MXCP Project

This project provides a full-stack, enterprise-ready MXCP server for querying and analyzing a dataset of UAE business licenses. It features a dbt-powered data pipeline, robust data quality testing, automated tool generation from dbt models, and a comprehensive suite of pre-built tools for search, aggregation, and analysis.

---

## Overview

This repository is a complete, self-contained solution for turning a raw CSV data file into a queryable, production-ready set of API endpoints. It is designed to be used with the **RAW Labs MXCP** platform and can be integrated with LLMs like Claude for natural language querying.

### Key Features

| Feature                  | Description                                                                                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **dbt Data Pipeline**    | Uses dbt to transform raw CSV data into a clean, analytics-ready data model in a local DuckDB database.                                      |
| **Robust Data Testing**  | Includes 20+ data tests (both schema and custom SQL tests) to ensure data quality and integrity.                                           |
| **Automated Tool Generation** | Python framework that automatically generates MXCP tools from dbt models with semantic analysis.                                       |
| **5 Pre-built Tools**    | Comprehensive search, aggregation, time series, geographic, and categorical analysis tools.                                                |
| **Separate SQL Files**   | Clean architecture with all SQL queries in separate files for better maintainability.                                                      |
| **Model Versioning**     | dbt model versioning support with contracts for backward compatibility.                                                                    |
| **LLM Integration Ready**| Includes a clean server startup script (`start-mcp.sh`) for easy integration with platforms like Claude Desktop.                           |

---

## Installation

> **Prerequisites:** You need Python 3.8+ and `git`.

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd uae-mxcp
    ```

2.  **Set Up Python Environment & Dependencies**
    ```bash
    python3 -m venv .env
    source .env/bin/activate
    pip install -r requirements.txt
    dbt deps
    ```

---

## Usage: A Step-by-Step Workflow

This workflow guides you through setting up the database and running the server.

### Step 1: Build the Database

The core of this project is its dbt pipeline, which reads a source CSV file and builds a DuckDB database (`db-prod.duckdb`).

```bash
# Build all models using the full dataset
dbt run --vars '{"licenses_file": "seeds/licenses.csv"}'

# Or use the sample file for development
dbt run --vars '{"licenses_file": "seeds/licenses_sample.csv"}'
```

This creates the versioned table `dim_licenses_v1` with 3.19M records (or 1,000 for the sample).

### Step 2: Run Data Quality Tests

After building the database, run the test suite to ensure the data is clean and valid.

```bash
# Test the models against the loaded data
dbt test --vars '{"licenses_file": "seeds/licenses.csv"}'
```

### Step 3: Generate MXCP Tools (Optional)

The project includes an automated tool generation framework that creates MXCP tools from your dbt models:

```bash
# Generate tools from dbt manifest
python generate_mxcp_tools.py --manifest target/manifest.json --output generated_tools

# Copy generated tools to project
cp generated_tools/tools/*.yml tools/
cp generated_tools/sql/*.sql sql/
```

### Step 4: Start the MXCP Server

With a clean, tested database, you can now start the MXCP server to expose the query tools.

```bash
# For standard development with full logging
mxcp serve

# OR, for clean LLM integration
./start-mcp.sh
```

---

## MXCP Tools

The project includes 5 comprehensive tools, all querying the versioned table `dim_licenses_v1`:

### 1. **find_licenses** (`tools/find_licenses.yml`)
Comprehensive search tool with filters for ALL 40+ columns including:
- Text search with partial matching (ILIKE) for names, addresses, descriptions
- Exact matching for categorical fields (status, type, flags)
- Date range filters for temporal fields
- Min/max filters for numeric fields
- Pagination support

### 2. **aggregate_licenses** (`tools/aggregate_licenses.yml`)
Dynamic aggregation tool supporting:
- Group by ANY combination of 36 categorical/string fields
- Common filters for data subsetting
- Returns counts and unique license counts

### 3. **timeseries_licenses** (`tools/timeseries_licenses.yml`)
Time series analysis tool:
- Analyze trends by establishment or expiration dates
- Configurable granularity (day, week, month, quarter, year)
- Date range filtering
- Additional categorical filters

### 4. **geo_licenses** (`tools/geo_licenses.yml`)
Geographic analysis tool:
- Group by emirate, authority, or address
- Coordinate statistics (avg, min, max lat/lon)
- Bounding box filtering
- Full filter support

### 5. **list_licenses_categories** (`tools/list_licenses_categories.yml`)
Categorical value exploration:
- List distinct values for any categorical field
- Optional counts for each value
- Useful for building dynamic UIs

---

## Advanced Topics

### Tool Generation Framework

The `mxcp_generator` package provides automated tool generation from dbt models:

```bash
# Components
mxcp_generator/
├── analyzers/          # Semantic analysis of dbt models
├── generators/         # Tool, resource, and prompt generators
├── utils/             # dbt manifest parsing
└── core.py            # Main orchestration

# Key features:
- Semantic column classification (identifier, temporal, geographic, etc.)
- Intelligent filter generation based on data types
- Separate SQL file generation for maintainability
- Test generation for all tools
```

### SQL File Organization

All SQL queries are stored separately in the `sql/` directory:
- **Better maintainability** - SQL can be edited independently
- **Syntax highlighting** - Editors properly highlight `.sql` files
- **Version control** - Cleaner diffs for SQL changes
- **Reusability** - SQL files can be shared between tools

### Key Project Concepts

> #### Data Loading: No `dbt seed`
> This project **does not** use the `dbt seed` command. Instead, the staging models read CSV files directly using DuckDB's `read_csv_auto` function with the path passed as a dbt variable.

> #### Model Versioning
> All models use dbt's versioning feature. The current version creates tables with `_v1` suffix (e.g., `dim_licenses_v1`). When breaking changes are needed, increment the version in `schema.yml`.

> #### Contracts
> All mart models have enforced contracts to ensure schema stability. If the model output doesn't match the contract, dbt will raise an error.

---

## Project Structure and Key Files

| Path                          | Description                                                                                                                             |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `README.md`                   | **You are here.** The main entry point and guide for the project.                                                                       |
| `.cursor/`                    | **AI Assistant Configuration.** Contains MXCP_PROJECT_ASSISTANT.md with project rules.                                                  |
| `models/`                     | **dbt Models.** Core data transformation logic (`staging/` and `marts/`).                                                              |
| `seeds/`                      | **Source Data.** CSV files read directly by staging models (no `dbt seed`).                                                            |
| `tests/`                      | **Custom dbt Tests.** SQL tests for complex business rules.                                                                             |
| `tools/`                      | **MXCP Tool Definitions.** YAML files defining API endpoints.                                                                           |
| `sql/`                        | **SQL Queries.** All SQL logic separated from YAML definitions.                                                                         |
| `mxcp_generator/`             | **Tool Generation Framework.** Python package for auto-generating tools.                                                                |
| `docs/design/`                | **Design Documentation.** Architecture decisions and strategies.                                                                        |
| `scripts/`                    | Helper scripts for data generation and analysis.                                                                                        |
| `dbt_project.yml`             | Main dbt configuration.                                                                                                                 |
| `mxcp-site.yml`               | Main MXCP server configuration.                                                                                                        |

---

## Development Notes

### AI-Assisted Development

This project follows the AI Change Protocol (AICP) defined in `.cursor/MXCP_PROJECT_ASSISTANT.md`. Key principles:
1. Always verify git status before changes
2. Run tests before and after modifications
3. Maintain 90%+ test coverage for mart models
4. Document all changes

### LLM Integration (Claude Desktop)

To integrate with Claude Desktop, add the following to your configuration:

```json
{
  "mxcpServers": {
    "uae": {
      "command": "bash",
      "args": [
        "-c",
        "cd /path/to/uae-mxcp && ./start-mcp.sh"
      ],
      "env": {
        "PATH": "/path/to/uae-mxcp/.env/bin:/usr/local/bin:/usr/bin",
        "HOME": "/home/your-username"
      }
    }
  }
}
```

Replace `/path/to/uae-mxcp` and `/home/your-username` with your local paths.

---

## Recent Updates

- **Tool Generation Framework**: Automated generation of MXCP tools from dbt models
- **SQL Separation**: All SQL queries moved to `sql/` directory
- **5 Comprehensive Tools**: Search, aggregate, timeseries, geographic, and categorical analysis
- **Enhanced Filters**: All tools support comprehensive filtering options
- **Model Versioning**: Using dbt versioned models (`dim_licenses_v1`)
