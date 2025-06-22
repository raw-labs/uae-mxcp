# UAE Business Licenses - MXCP Project

This project provides a full-stack, enterprise-ready MXCP server for querying and analyzing a dataset of UAE business licenses. It features a dbt-powered data pipeline, robust data quality testing, an advanced automated tool generation framework, and a comprehensive suite of pre-built tools for search, aggregation, and analysis.

---

## Overview

This repository is a complete, self-contained solution for turning a raw CSV data file into a queryable, production-ready set of API endpoints. It is designed to be used with the **RAW Labs MXCP** platform and can be integrated with LLMs like Claude for natural language querying.

### Key Features

| Feature                  | Description                                                                                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **dbt Data Pipeline**    | Uses dbt to transform raw CSV data into a clean, analytics-ready data model in a local DuckDB database.                                      |
| **Robust Data Testing**  | Includes 41 data tests (both schema and custom SQL tests) to ensure data quality and integrity with 90%+ column coverage.                |
| **Advanced Tool Generation** | Python framework with semantic analysis that automatically generates MXCP tools from dbt models with test preservation.              |
| **5 Pre-built Tools**    | Comprehensive search, aggregation, time series, geographic, and categorical analysis tools with 40+ parameters each.                      |
| **Test Preservation**    | Merge functionality preserves manually written tests during tool regeneration for safe iteration.                                          |
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
dbt run --vars '{"licenses_file": "data/licenses.csv"}'

# Or use the sample file for development
dbt run --vars '{"licenses_file": "data/licenses_sample.csv"}'
```

This creates the versioned table `dim_licenses_v1` with 3.19M records (or 1,000 for the sample).

### Step 2: Run Data Quality Tests

After building the database, run the test suite to ensure the data is clean and valid.

```bash
# Test the models against the loaded data
dbt test --vars '{"licenses_file": "data/licenses.csv"}'
```

### Step 3: Generate MXCP Tools

The project includes an advanced tool generation framework that creates MXCP tools from your dbt models:

```bash
# Generate fresh tools (creates generated_mxcp/ directory)
python generate_mxcp_tools.py

# OR regenerate existing tools safely (preserves manual tests)
python generate_mxcp_tools.py --output-dir .
```

**Key Features:**
- **Semantic Analysis**: Automatically understands business meaning of data fields
- **Test Preservation**: Safely regenerates tools without losing manual customizations
- **Smart Parameters**: All 40+ fields become optional parameters with `default: null`
- **Business-Friendly Names**: Converts `emirate_name_en` to `EmirateNameEn`

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
- Date range filters for temporal fields (From/To parameters)
- Min/max filters for numeric fields
- Pagination support with configurable limits
- **All parameters optional** with `default: null`

### 2. **aggregate_licenses** (`tools/aggregate_licenses.yml`)
Dynamic aggregation tool supporting:
- Group by ANY combination of categorical/string fields using boolean flags
- Common filters for data subsetting
- Returns counts and unique license counts
- Dynamic SQL generation based on grouping parameters

### 3. **timeseries_licenses** (`tools/timeseries_licenses.yml`)
Time series analysis tool:
- Analyze trends by any temporal field (establishment/expiration dates)
- Configurable granularity (day, week, month, quarter, year)
- Date range filtering with dynamic field selection
- Additional categorical filters

### 4. **geo_licenses** (`tools/geo_licenses.yml`)
Geographic analysis tool:
- Group by any geographic field (emirate, authority, address)
- Coordinate statistics (avg, min, max lat/lon)
- Bounding box filtering with coordinate ranges
- Dynamic geographic field selection

### 5. **list_licenses_categories** (`tools/list_licenses_categories.yml`)
Categorical value exploration:
- List distinct values for any categorical field
- Optional counts for each value
- Dynamic field selection from all categorical columns
- Useful for building dynamic UIs and exploring data

---

## Advanced Topics

### Tool Generation Framework

The `mxcp_generator` package provides advanced automated tool generation:

```bash
# Architecture
mxcp_generator/
├── analyzers/          # Semantic analysis of dbt models
│   └── semantic_analyzer.py  # Column classification & business entity extraction
├── generators/         # Tool, resource, and prompt generators
│   ├── tool_generator.py     # Creates MXCP tool definitions
│   ├── resource_generator.py # Generates pre-computed resources
│   └── prompt_generator.py   # AI guidance prompts
├── utils/             # dbt manifest parsing utilities
└── core.py            # Main orchestration with merge functionality
```

**Key Features:**
- **Semantic Column Classification**: Automatically detects identifiers, temporal, geographic, categorical, and metric fields
- **Test Preservation**: Merge functionality preserves manual tests during regeneration
- **Intelligent Parameter Generation**: Creates business-friendly parameter names and types
- **Enum Detection**: Extracts categorical values from dbt `accepted_values` tests
- **SQL Generation**: Creates efficient, parameterized SQL queries
- **Comprehensive Testing**: Generates test suites for all tools

### Test Preservation (Merge Functionality)

**Problem**: Regenerating tools would wipe out manually written tests and customizations.

**Solution**: Advanced merge strategy that preserves existing tests:

```bash
# Safe regeneration that preserves manual tests
python generate_mxcp_tools.py --output-dir .
```

**How it works:**
1. Checks for existing tool files before writing
2. Extracts and preserves all existing tests
3. Merges new tool definitions with preserved tests
4. Logs detailed information about what tests are preserved

### Parameter Handling Innovation

All generated tools use advanced parameter handling:
- **Optional by Default**: Every parameter has `default: null`
- **Enum Support**: Categorical fields include all valid values plus `null`
- **Range Parameters**: Date and numeric fields get From/To and Min/Max parameters
- **Smart Naming**: Business-friendly parameter names (e.g., `EmirateNameEn`)

### Development Workflow

1. **Model Development**: Focus on creating high-quality dbt mart models
2. **Initial Generation**: Run tool generator to create base tools
3. **Customization**: Add manual tests and customizations to tools
4. **Safe Iteration**: Use merge functionality to regenerate without losing customizations
5. **Validation**: Ensure all tools validate and tests pass

---

## Project Structure and Key Files

| Path                          | Description                                                                                                                             |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `README.md`                   | **You are here.** The main entry point and guide for the project.                                                                       |
| `.cursor/`                    | **AI Assistant Configuration.** Contains MXCP_PROJECT_ASSISTANT.md with project rules.                                                  |
| `models/`                     | **dbt Models.** Core data transformation logic (`staging/` and `marts/`).                                                              |
| `data/`                       | **Source Data.** CSV files read directly by staging models (no `dbt seed`).                                                            |
| `tests/`                      | **Custom dbt Tests.** SQL tests for complex business rules.                                                                             |
| `tools/`                      | **MXCP Tool Definitions.** YAML files defining API endpoints with embedded tests.                                                       |
| `sql/`                        | **SQL Queries.** All SQL logic separated from YAML definitions.                                                                         |
| `resources/`                  | **MXCP Resources.** Pre-computed views and cached data.                                                                                 |
| `prompts/`                    | **AI Prompts.** Guidance for LLM interactions with the data.                                                                            |
| `mxcp_generator/`             | **Tool Generation Framework.** Advanced Python package for auto-generating tools.                                                       |
| `docs/`                       | **Documentation.** Strategy documents and implementation guides.                                                                        |
| `scripts/`                    | Helper scripts for data generation and analysis.                                                                                        |
| `generate_mxcp_tools.py`      | **Main CLI.** Tool generation script with merge functionality.                                                                          |
| `dbt_project.yml`             | Main dbt configuration.                                                                                                                 |
| `mxcp-site.yml`               | Main MXCP server configuration.                                                                                                        |

---

## Documentation

| Document | Description |
|----------|-------------|
| `docs/tool_generation_strategy.md` | Comprehensive strategy and design philosophy |
| `docs/implementation_guide.md` | Practical implementation guide and troubleshooting |
| `docs/mcp_resource_best_practices.md` | Best practices for MCP resources |
| `docs/resource_generation_rules.md` | Rules for automatic resource generation |

---

## Development Notes

### AI-Assisted Development

This project follows the AI Change Protocol (AICP) defined in `.cursor/MXCP_PROJECT_ASSISTANT.md`. Key principles:
1. Always verify git status before changes
2. Run tests before and after modifications
3. Maintain 90%+ test coverage for mart models (currently 90% - 36/40 columns)
4. Document all changes comprehensively

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

- **Advanced Tool Generation Framework**: Complete rewrite with semantic analysis and merge functionality
- **Test Preservation**: Safe regeneration that preserves manual tests and customizations
- **Parameter Innovation**: All 40+ parameters optional with smart defaults and business-friendly naming
- **Enhanced Documentation**: Comprehensive guides and strategy documents
- **AICP Compliance**: Full adherence to AI Change Protocol for production readiness
- **Production Validation**: All 41 dbt tests passing, 8 MXCP endpoints validated

This project represents a significant advancement in automated data tooling, enabling developers to focus on dbt models while automatically generating sophisticated, production-ready data access tools.
