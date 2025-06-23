# UAE Business Licenses - MXCP Project

This project provides a full-stack, enterprise-ready MXCP server for querying and analyzing UAE business licenses with **multi-model relationship support**. It features a dbt-powered data pipeline, robust data quality testing, an advanced automated tool generation framework with relationship detection, and a comprehensive suite of pre-built tools for search, aggregation, and analysis.

---

## Overview

This repository is a complete, self-contained solution for turning raw CSV data into a queryable, production-ready set of API endpoints with **cross-entity relationship support**. It is designed to be used with the **RAW Labs MXCP** platform and can be integrated with LLMs like Claude for natural language querying.

### Key Features

| Feature                  | Description                                                                                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Multi-Model Framework** | Advanced relationship detection and dynamic embedding for cross-entity queries with lazy loading and ORM-inspired patterns.             |
| **dbt Data Pipeline**    | Uses dbt to transform raw CSV data into a clean, analytics-ready data model in a local DuckDB database.                                      |
| **Robust Data Testing**  | Includes 41+ data tests (both schema and custom SQL tests) to ensure data quality and integrity with 90%+ column coverage.                |
| **Advanced Tool Generation** | Python framework with semantic analysis that automatically generates MXCP tools from dbt models with relationship detection.              |
| **9 Pre-built Tools**    | Comprehensive search, aggregation, time series, geographic, and categorical analysis tools across multiple entities.                      |
| **Relationship Support** | Automatic detection of 1-N, N-1, and N-M relationships with dynamic embedding via `embed` parameter.                                      |
| **LLM-Friendly Design**  | Enum-based autocompletion for relationships, intelligent parameter suggestions, and comprehensive error handling.                          |
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

This creates the versioned tables:
- `dim_licenses_v1` with 3.19M records (or 1,000 for the sample)
- `fact_license_owners` with license ownership relationships

### Step 2: Run Data Quality Tests

After building the database, run the test suite to ensure the data is clean and valid.

```bash
# Test the models against the loaded data
dbt test --vars '{"licenses_file": "data/licenses.csv"}'
```

### Step 3: Generate MXCP Tools

The project includes an advanced tool generation framework with multi-model support that creates MXCP tools from your dbt models:

```bash
# Generate fresh tools (creates generated_mxcp/ directory)
python generate_mxcp_tools.py

# OR regenerate existing tools safely (preserves manual tests)
python generate_mxcp_tools.py --output-dir .
```

**Key Features:**
- **Multi-Model Relationship Detection**: Automatically detects relationships from dbt `relationships` tests
- **Dynamic Embedding**: Lazy-loading related entities via `embed` parameter with enum autocompletion
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

## Multi-Model Framework

### Relationship Support

The framework automatically detects relationships from dbt `relationships` tests and enables cross-entity queries:

**Example: Find licenses with their owners**
```bash
mxcp run tool find_licenses --param EmirateNameEn="Dubai" --param embed='["license_owners"]'
```

**Key Features:**
- **Lazy Loading**: Related data loaded only when requested via `embed` parameter
- **Enum Autocompletion**: LLMs can autocomplete valid relationship names
- **Chained Relationships**: Support for A→B→C patterns (e.g., `embed=["owners.addresses"]`)
- **Performance Safeguards**: Depth limits, timeout protection, intelligent caching

### Fetch Type Behaviors

- **LAZY (Default)**: On-demand embedding via `embed` parameter
- **EAGER**: Architectural guidance that recommends creating dbt views for always-joined data
- **NONE**: Completely disables relationships for security, performance, or circular dependency breaking

---

## MXCP Tools

The project includes **9 comprehensive tools** across multiple entities:

### License Tools (5 tools)

#### 1. **find_licenses** (`tools/find_licenses.yml`)
Comprehensive search tool with **multi-model embedding support**:
- **Multi-Model**: `embed=["license_owners"]` parameter for related data
- Text search with partial matching (ILIKE) for names, addresses, descriptions
- Exact matching for categorical fields (status, type, flags)
- Date range filters for temporal fields (From/To parameters)
- Min/max filters for numeric fields
- Pagination support with configurable limits

#### 2. **aggregate_licenses** (`tools/aggregate_licenses.yml`)
Dynamic aggregation tool supporting:
- Group by ANY combination of categorical/string fields using array parameter
- Common filters for data subsetting
- Returns counts and unique license counts
- Performance optimizations for large datasets

#### 3. **timeseries_licenses** (`tools/timeseries_licenses.yml`)
Time series analysis tool:
- Analyze trends by any temporal field (establishment/expiration dates)
- Configurable granularity (day, week, month, quarter, year)
- Date range filtering with dynamic field selection

#### 4. **geo_licenses** (`tools/geo_licenses.yml`)
Geographic analysis tool:
- Group by any geographic field (emirate, authority, address)
- Coordinate statistics (avg, min, max lat/lon)
- Bounding box filtering with coordinate ranges

#### 5. **list_licenses_categories** (`tools/list_licenses_categories.yml`)
Categorical value exploration:
- List distinct values for any categorical field
- Optional counts for each value
- Dynamic field selection from all categorical columns

### License Owner Tools (4 tools)

#### 6. **find_license_owners** (`tools/find_license_owners.yml`)
Search license ownership records with **multi-model embedding**:
- **Multi-Model**: `embed=["licenses"]` parameter for license details
- Filter by owner demographics, relationship types, contact information
- Cross-entity filtering capabilities

#### 7. **aggregate_license_owners** (`tools/aggregate_license_owners.yml`)
Ownership analytics and aggregation:
- Group by owner characteristics, relationship types, demographics
- Performance-optimized for large datasets

#### 8. **timeseries_license_owners** (`tools/timeseries_license_owners.yml`)
Temporal analysis of ownership patterns:
- Track ownership changes over time
- Analyze establishment patterns by owner demographics

#### 9. **list_license_owners_categories** (`tools/list_license_owners_categories.yml`)
Explore ownership categorical values:
- List distinct values for owner-related fields
- Useful for building dynamic UIs and exploring ownership data

---

## Advanced Topics

### Multi-Model Framework Architecture

The `mxcp_generator` package provides advanced automated tool generation with relationship support:

```bash
# Architecture
mxcp_generator/
├── analyzers/          # Semantic analysis with relationship detection
│   └── semantic_analyzer.py  # Column classification & relationship extraction
├── generators/         # Enhanced generators with multi-model support
│   ├── tool_generator.py     # Creates MXCP tools with embed parameters
│   ├── resource_generator.py # Generates pre-computed resources
│   └── prompt_generator.py   # AI guidance prompts
├── utils/             # dbt manifest parsing utilities
└── core.py            # Main orchestration with merge functionality
```

**Key Features:**
- **Relationship Detection**: Automatically analyzes dbt `relationships` tests
- **Dynamic Embedding**: Generates conditional SQL for related data inclusion
- **Cross-Entity Filtering**: Filter by related entity attributes using EXISTS subqueries
- **LLM Autocompletion**: Creates enum values for valid relationship names
- **Performance Safeguards**: Depth limits, lazy evaluation, timeout protection

### Test Preservation (Merge Functionality)

**Problem**: Regenerating tools would wipe out manually written tests and customizations.

**Solution**: Advanced merge strategy that preserves existing tests:

```bash
# Safe regeneration that preserves manual tests
python generate_mxcp_tools.py --output-dir .
```

**Current Status**: 9/9 tools successfully integrated with 3 manual tests preserved.

### Development Workflow

1. **Model Development**: Create dbt mart models with relationship tests
2. **Initial Generation**: Run tool generator to create base tools with relationship support
3. **Customization**: Add manual tests and customizations to tools
4. **Safe Iteration**: Use merge functionality to regenerate without losing customizations
5. **Validation**: Ensure all tools validate and tests pass

---

## Project Structure and Key Files

| Path                          | Description                                                                                                                             |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `README.md`                   | **You are here.** The main entry point and guide for the project.                                                                       |
| `.cursor/`                    | **AI Assistant Configuration.** Contains MXCP_PROJECT_ASSISTANT.md with project rules.                                                  |
| `models/`                     | **dbt Models.** Core data transformation logic with relationship tests (`staging/` and `marts/`).                                      |
| `data/`                       | **Source Data.** CSV files read directly by staging models (no `dbt seed`).                                                            |
| `tests/`                      | **Custom dbt Tests.** SQL tests for complex business rules.                                                                             |
| `tools/`                      | **MXCP Tool Definitions.** 9 YAML files defining API endpoints with multi-model support.                                               |
| `sql/`                        | **SQL Queries.** All SQL logic separated from YAML definitions with embedding support.                                                 |
| `resources/`                  | **MXCP Resources.** Pre-computed views and cached data.                                                                                 |
| `prompts/`                    | **AI Prompts.** Guidance for LLM interactions with the data.                                                                            |
| `mxcp_generator/`             | **Tool Generation Framework.** Advanced Python package with multi-model support.                                                       |
| `docs/`                       | **Documentation.** Strategy documents, implementation guides, and demo materials.                                                       |
| `docs/demos/`                 | **Demo Materials.** User prompts and demonstration examples.                                                                            |
| `docs/development/`           | **Development Scripts.** Testing and development utilities.                                                                             |
| `scripts/`                    | Helper scripts for data generation and analysis.                                                                                        |
| `generate_mxcp_tools.py`      | **Main CLI.** Tool generation script with merge functionality and relationship detection.                                               |
| `dbt_project.yml`             | Main dbt configuration.                                                                                                                 |
| `mxcp-site.yml`               | Main MXCP server configuration.                                                                                                        |

---

## Documentation

| Document | Description |
|----------|-------------|
| `docs/multi_model_framework_specification.md` | **Comprehensive multi-model framework specification and design** |
| `docs/tool_generation_strategy.md` | Comprehensive strategy and design philosophy |
| `docs/implementation_guide.md` | Practical implementation guide and troubleshooting |
| `docs/mcp_resource_best_practices.md` | Best practices for MCP resources |
| `docs/resource_generation_rules.md` | Rules for automatic resource generation |
| `docs/demos/` | **Demo prompts and examples showcasing multi-model capabilities** |
| `docs/development/` | **Development scripts and testing utilities** |

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

- **🚀 Multi-Model Framework**: Complete relationship detection and dynamic embedding system
- **🔗 Cross-Entity Queries**: Support for lazy-loading related data with `embed` parameter
- **🤖 LLM Autocompletion**: Enum-based relationship suggestions for better AI interaction
- **📊 9 Production Tools**: Extended from 5 to 9 tools across multiple entities
- **🧪 Advanced Testing**: Enhanced tool generation with comprehensive test preservation
- **📁 Organized Documentation**: Restructured docs with dedicated demo and development sections
- **⚡ Performance Optimization**: Intelligent query limiting and performance safeguards
- **🔧 Enhanced Tool Generation**: Relationship-aware tool generation with merge functionality

This project represents a significant advancement in automated multi-model data tooling, enabling developers to focus on dbt models while automatically generating sophisticated, production-ready data access tools with cross-entity relationship support.
