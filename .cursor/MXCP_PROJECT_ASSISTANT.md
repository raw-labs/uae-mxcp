# MXCP Project Assistant Guide

## 1. Core Purpose & AI Directives

This document contains the rules and guidelines for the AI assistant operating within this **MXCP (RAW Labs) project**. The presence of an `mxcp-site.yml` file signals that you, the AI assistant, must strictly adhere to these instructions.

Your primary purpose is to help:
1.  **Author YAML endpoints** (`tools/`, `resources/`, `prompts/`).
2.  **Write and manage the underlying logic** (e.g., DuckDB SQL) for each endpoint.
3.  **Generate tools automatically** from dbt models using the advanced tool generation framework.
4.  **List, validate, and test** all endpoints using the `mxcp` CLI.
5.  **Operate the project** safely via the `mxcp` CLI (`init`, `serve`, `test`, etc.).

---

## 2. The AI Change Protocol (AICP)

This protocol is **non-negotiable**. Before proposing *any* change to a protected resource, you **must** follow these steps in order:

| Step | Action                 | Command / Verification                                                                                                                              |
| :--- | :--------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | **State Intent**       | Clearly describe the change you intend to make.                                                                                                     |
| 2    | **Verify Git Status**  | Confirm the git working directory is clean.                                                                                                         |
| 3    | **Run Pre-Change Tests** | Confirm all existing tests pass (`dbt test` and `mxcp validate`).                                                                                                                    |
| 4    | **Propose Change**     | Use the `edit_file` or `create_file` tool to make the change.                                                                                       |
| 5    | **Run Post-Change Tests** | After the change is applied, run tests again to ensure nothing has broken.                                                                        |
| 6    | **Verify Coverage**    | **If a dbt model in `models/marts/` was changed**, run the coverage script and ensure column coverage is at least 90%. |
| 7    | **Document & Conclude**  | Summarize the change and confirm all checks have passed.                                                                                            |

**Protected Resources:**
- **dbt Layer**: `models/`, `data/`, `tests/`, `macros/`, `dbt_project.yml`
- **MXCP Layer**: `tools/`, `resources/`, `prompts/`, `sql/`, `mxcp-site.yml`
- **Generation Framework**: `mxcp_generator/`, `generate_mxcp_tools.py`

---

## 3. Project-Specific Principles

This project has core philosophies that you must follow:

### Data Loading Strategy
- **Principle**: The project **does not** use `dbt seed` to load data.
- **Implementation**: Source CSV files are read directly in the `models/staging/` layer using `read_csv_auto()`. The file path must always be passed as a dbt variable (e.g., `licenses_file`).

### Testing Philosophy
- **Principle**: The SQL code in the `models/` directory is the source of truth. Tests are written to validate and document the behavior of this code.
- **Implementation**: If a dbt test fails, the default assumption is that the **test is incorrect** or incomplete (e.g., `accepted_values` is missing a new value). The underlying SQL code should **not** be changed to make a test pass.

### Tool Generation Philosophy
- **Principle**: Focus on dbt model quality; let the framework generate tools automatically.
- **Implementation**: Use the advanced tool generation framework (`python generate_mxcp_tools.py`) to create MXCP tools from dbt models. Manual tool creation should be rare.

---

## 4. Tool Generation Framework

### Overview
The project includes an advanced tool generation framework that automatically creates MXCP tools, resources, and prompts from dbt mart models using semantic analysis.

### Key Features
- **Semantic Analysis**: Automatically understands business meaning of data fields
- **Test Preservation**: Merge functionality preserves manual tests during regeneration
- **Smart Parameters**: All fields become optional parameters with `default: null`
- **Business-Friendly Naming**: Converts technical names to business-friendly parameters

### Usage Patterns

#### Initial Generation
```bash
# Generate fresh tools (creates generated_mxcp/ directory)
python generate_mxcp_tools.py
```

#### Safe Regeneration (Preserves Manual Tests)
```bash
# Write directly to current directory to preserve existing tests
python generate_mxcp_tools.py --output-dir .
```

#### Generated Artifacts
The framework automatically creates:
- **5 Tool Types**: Search, aggregation, time series, geographic, and categorical analysis
- **Resources**: Pre-computed views based on status fields and metrics
- **Prompts**: AI guidance for data exploration
- **Tests**: Comprehensive test suites for all generated components

### Manual Customization
After generation, you can safely add:
- **Manual Tests**: Add custom test cases to tool YAML files
- **Parameter Modifications**: Adjust parameter descriptions or constraints
- **Custom Logic**: Modify SQL files for specific business requirements

The merge functionality will preserve these customizations during future regenerations.

---

## 5. dbt & Testing Conventions

### Model Layers
The project follows a standard `staging` -> `marts` structure.
- **`models/staging/`**: Reads directly from source CSVs. Light cleaning and renaming.
- **`models/marts/`**: Final, user-facing models (dimensions and facts). This is where business logic, joins, and transformations occur.

### Test Coverage Requirements
- **Marts Layer**: All models in the `marts` layer **must** have a minimum of **90% column-level test coverage**.
- **Current Status**: 90% coverage achieved (36/40 columns tested)
- **Staging Layer**: While not mandatory, adding `not_null` and `unique` tests to primary keys in the staging layer is highly encouraged to catch data quality issues early.

### Data Quality Standards
- **41 Total Tests**: Comprehensive test suite covering data integrity
- **Accepted Values Tests**: Define categorical values that become enum parameters in generated tools
- **Contract Enforcement**: All mart models have enforced contracts for schema stability

---

## 6. MXCP Endpoint & CLI Reference

### Tool YAML Example (Generated)
All endpoint files must start with `mxcp: "1.0.0"`. Generated tools include embedded tests:

```yaml
# File: tools/find_licenses.yml
mxcp: "1.0.0"
tool:
  name: "find_licenses"
  description: "Search and filter licenses records"
  parameters:
    - name: "EmirateNameEn"
      type: "string"
      description: "Filter by emirate_name_en"
      enum: ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain", null]
      default: null
    - name: "BlStatusEn"
      type: "string"
      description: "Filter by bl_status_en"
      enum: ["Current", "Expired", "Cancelled", null]
      default: null
    - name: "limit"
      type: "integer"
      description: "Maximum number of records to return"
      default: 100
  required: []
  return:
    type: "array"
    items:
      type: "object"
      properties:
        license_pk: { type: "string" }
        bl_name_en: { type: "string" }
        emirate_name_en: { type: "string" }
  source:
    file: "../sql/find_licenses.sql"
  enabled: true
  tests:
    - name: "test_manual_search"
      description: "Manual test preserved during regeneration"
      arguments:
        - key: "EmirateNameEn"
          value: "Dubai"
        - key: "limit"
          value: 5
      result: "success"
```

### Parameter Innovation
Generated tools use advanced parameter handling:
- **All Optional**: Every parameter has `default: null`
- **Enum Support**: Categorical fields include valid values plus `null`
- **Range Parameters**: Date and numeric fields get From/To and Min/Max parameters
- **Smart Naming**: Business-friendly names (e.g., `EmirateNameEn` instead of `emirate_name_en`)

### Common CLI Commands
- `mxcp validate`: Validate all MXCP endpoints (currently 8 valid endpoints)
- `mxcp test tool <name>`: Test specific tool with embedded test cases
- `dbt test --vars '{"licenses_file": "data/licenses.csv"}'`: Run all 41 dbt data tests
- `dbt docs generate`: Generate dbt documentation and manifest for tool generation
- `python generate_mxcp_tools.py --output-dir .`: Safe tool regeneration with test preservation

### Development Workflow
1. **Focus on dbt Models**: Create high-quality mart models with proper tests
2. **Generate Tools**: Use the framework to automatically create MXCP tools
3. **Customize**: Add manual tests and customizations as needed
4. **Iterate Safely**: Regenerate tools without losing customizations
5. **Validate**: Ensure all tools and tests pass

---

## 7. Current Project Status

### Validated Components
- **dbt Models**: 3 models (staging + marts) with contracts
- **Data Tests**: 41 tests passing (90% column coverage)
- **MXCP Tools**: 5 comprehensive tools with 40+ parameters each
- **MXCP Resources**: 1 active licenses resource
- **MXCP Prompts**: 2 AI guidance prompts
- **Database**: 3.19M records in `dim_licenses_v1` table

### Key Files
- **Main Data**: `data/licenses.csv` (3.19M records)
- **Sample Data**: `data/licenses_sample.csv` (1K records for development)
- **Generated Tools**: All in `tools/` directory with embedded tests
- **SQL Queries**: All in `sql/` directory for maintainability
- **Generation Framework**: `mxcp_generator/` package with semantic analysis

This project represents a significant advancement in automated data tooling, enabling focus on dbt model quality while automatically generating production-ready MXCP tools.
