# UAE Business Licenses - MXCP Project

This project provides a full-stack, enterprise-ready MXCP server for querying and analyzing a dataset of UAE business licenses. It features a dbt-powered data pipeline, robust data quality testing, and a suite of pre-built tools for search, aggregation, and geospatial analysis.

---

## Overview

This repository is a complete, self-contained solution for turning a raw CSV data file into a queryable, production-ready set of API endpoints. It is designed to be used with the **RAW Labs MXCP** platform and can be integrated with LLMs like Claude for natural language querying.

### Key Features

| Feature                  | Description                                                                                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **dbt Data Pipeline**    | Uses dbt to transform raw CSV data into a clean, analytics-ready data model in a local DuckDB database.                                      |
| **Robust Data Testing**  | Includes 17+ data tests (both schema and custom SQL tests) to ensure data quality and integrity.                                           |
| **MXCP Tools**           | Provides a suite of tools for searching, aggregating, and analyzing license data.                                                          |
| **Synthetic Data**       | Comes with a `seeds/licenses_sample.csv` and a script to generate larger, realistic datasets for development and testing.                    |
| **Role-Based Policies**  | Demonstrates data masking and access control policies for different user roles (e.g., `guest` vs. `admin`).                                  |
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

This workflow guides you through setting up the database and running the server using the default sample data.

### Step 1: Build the Database

The core of this project is its dbt pipeline, which reads a source CSV file and builds a DuckDB database (`db-prod.duckdb`).

```bash
# Build all models using the default sample file
dbt run --vars '{"licenses_file": "seeds/licenses_sample.csv"}'
```

This command tells dbt to execute all models, using the `licenses_file` variable to find the source data.

### Step 2: Run Data Quality Tests

After building the database, run the test suite to ensure the data is clean and valid.

```bash
# Test the models against the loaded data
dbt test --vars '{"licenses_file": "seeds/licenses_sample.csv"}'
```
This command executes all 17+ tests, including schema tests and the custom SQL tests found in the `tests/` directory.

### Step 3: Start the MXCP Server

With a clean, tested database, you can now start the MXCP server to expose the query tools.

```bash
# For standard development with full logging
mxcp serve

# OR, for clean LLM integration
./start-mcp.sh
```

---

## Advanced Topics

### Working with Different Data Files

The project is designed to work with any compatible CSV file.

-   **To generate a larger synthetic file:**
    ```bash
    ./scripts/generate_synthetic_data.py --output seeds/licenses_large_sample.csv --sample-size 10000
    ```
    Then run `dbt run` and `dbt test` with `--vars '{"licenses_file": "seeds/licenses_large_sample.csv"}'`.

-   **To use the real dataset (requires AWS access):**
    ```bash
    ./scripts/download_real_data.py --output seeds/licenses.csv
    ```
    Then run `dbt run` and `dbt test` with `--vars '{"licenses_file": "seeds/licenses.csv"}'`.

### Key Project Concepts

> #### Data Loading: No `dbt seed`
> This project **does not** use the `dbt seed` command. Instead, the staging models read CSV files directly from the `seeds/` directory using DuckDB's `read_csv_auto` function. This is a deliberate design choice for performance and flexibility.

> #### Data Testing: Schema and Custom Tests
> The project uses two types of dbt tests:
> 1.  **Schema Tests:** Defined in `.yml` files (e.g., `not_null`).
> 2.  **Custom Data Tests:** Custom SQL queries in the `tests/` directory that check for complex business rules. `dbt test` runs both types automatically.

---

## Project Structure and Key Files

This table provides a map of the repository to help you navigate the codebase.

| Path                          | Description                                                                                                                             |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `README.md`                   | **You are here.** The main entry point and guide for the project.                                                                       |
| `.cursor/`                    | **AI Assistant Configuration.** Contains rules and instructions for the AI assistant (e.g., Cursor) to ensure consistent behavior.        |
| `models/`                     | **dbt Models.** The core data transformation logic, organized into `staging` and `marts` layers.                                        |
| `seeds/`                      | **Source Data.** Holds the source CSV files. This project reads directly from this directory; it does **not** use `dbt seed`.             |
| `tests/`                      | **Custom dbt Tests.** Contains custom data tests written in SQL to enforce complex business rules.                                      |
| `tools/`                      | **MXCP Tools.** The primary API endpoints for querying data, defined in YAML and backed by SQL.                                         |
| `resources/` & `prompts/`     | Additional MXCP endpoint definitions for metadata and LLM prompts.                                                                      |
| `scripts/`                    | Helper scripts for generating synthetic data and downloading the real dataset.                                                          |
| `start-mcp.sh`                | A wrapper script to start the MXCP server with clean stdio output, ideal for LLM integration.                                           |
| `dbt_project.yml`             | The main configuration file for the dbt project.                                                                                        |
| `mxcp-site.yml`               | The main configuration file for the MXCP server.                                                                                        |

## Development Notes

### AI-Assisted Development

This project is configured for development with an AI assistant like Cursor. The `.cursor/` directory contains a rulebook (`MXCP_PROJECT_ASSISTANT.md`) that defines the project's specific protocols and design principles.

By committing these rules to the repository, we ensure that the AI assistant's behavior is consistent and reproducible for any developer working on the project.

### LLM Integration (Claude Desktop)

To integrate with Claude Desktop, add the following to your configuration:

```json
{
  "mxcpServers": {
    "uae": {
      "command": "bash",
      "args": [
        "-c",
        "cd /path/to/uae-mxcp && ./start-mcp.sh --role guest"
      ],
      "env": {
        "PATH": "/path/to/uae-mxcp/.env/bin:/usr/local/bin:/usr/bin",
        "HOME": "/home/your-username"
      }
    }
  }
}
```
> **Note:** The `--role` flag is for demonstration purposes. Role-based access control policies are defined in the tool YAMLs but require a proxy layer to enforce.

Replace `/path/to/uae-mxcp` and `/home/your-username` with your local paths.
