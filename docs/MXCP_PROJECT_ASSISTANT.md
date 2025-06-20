# MXCP Project Assistant Guide

## 1. Core Purpose & AI Directives

This document contains the rules and guidelines for the AI assistant operating within this **MXCP (RAW Labs) project**. The presence of an `mxcp-site.yml` file signals that you, the AI assistant, must strictly adhere to these instructions.

Your primary purpose is to help:
1.  **Author YAML endpoints** (`tools/`, `resources/`, `prompts/`).
2.  **Write and manage the underlying logic** (e.g., DuckDB SQL) for each endpoint.
3.  **List, validate, and test** all endpoints using the `mxcp` CLI.
4.  **Operate the project** safely via the `mxcp` CLI (`init`, `serve`, `test`, etc.).

---

## 2. The AI Change Protocol (AICP)

This protocol is **non-negotiable**. Before proposing *any* change to a protected resource, you **must** follow these steps in order:

| Step | Action                 | Command / Verification                                                                                                                              |
| :--- | :--------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | **State Intent**       | Clearly describe the change you intend to make.                                                                                                     |
| 2    | **Verify Git Status**  | Confirm the git working directory is clean.                                                                                                         |
| 3    | **Run Pre-Change Tests** | Confirm all existing tests pass.                                                                                                                    |
| 4    | **Propose Change**     | Use the `edit_file` or `create_file` tool to make the change.                                                                                       |
| 5    | **Run Post-Change Tests** | After the change is applied, run tests again to ensure nothing has broken.                                                                        |
| 6    | **Verify Coverage**    | **If a dbt model in `models/marts/` was changed**, run the coverage script and ensure column coverage is at least 80%. |
| 7    | **Document & Conclude**  | Summarize the change and confirm all checks have passed.                                                                                            |

**Protected Resources:**
- **dbt Layer**: `models/`, `seeds/`, `tests/`, `macros/`, `dbt_project.yml`
- **MXCP Layer**: `tools/`, `resources/`, `prompts/`, `mxcp-site.yml`

---

## 3. Project-Specific Principles

This project has two core philosophies that you must follow:

### Data Loading Strategy
- **Principle**: The project **does not** use `dbt seed` to load data.
- **Implementation**: Source CSV files are read directly in the `models/staging/` layer using `read_csv_auto()`. The file path must always be passed as a dbt variable (e.g., `licenses_file`).

### Testing Philosophy
- **Principle**: The SQL code in the `models/` directory is the source of truth. Tests are written to validate and document the behavior of this code.
- **Implementation**: If a dbt test fails, the default assumption is that the **test is incorrect** or incomplete (e.g., `accepted_values` is missing a new value). The underlying SQL code should **not** be changed to make a test pass.

---

## 4. dbt & Testing Conventions

### Model Layers
The project follows a standard `staging` -> `marts` structure.
- **`models/staging/`**: Reads directly from source CSVs. Light cleaning and renaming.
- **`models/marts/`**: Final, user-facing models (dimensions and facts). This is where business logic, joins, and transformations occur.

### Test Coverage Requirements
- **Marts Layer**: All models in the `marts` layer **must** have a minimum of **80% column-level test coverage**.
- **Staging Layer**: While not mandatory, adding `not_null` and `unique` tests to primary keys in the staging layer is highly encouraged to catch data quality issues early.
- **Verification**: Use the `scripts/calculate_test_coverage.py` script to verify coverage.

---

## 5. MXCP Endpoint & CLI Reference

### Tool YAML Example
All endpoint files must start with `mxcp: "1.0.0"`.

```yaml
# File: tools/search_licenses.yml
mxcp: "1.0.0"
tool:
  name: "search_licenses"
  description: "Finds business licenses by name or activity"
  parameters:
    - name: "name"
      type: "string"
      description: "The business name to search for"
  return:
    type: "array"
    items:
      type: "object"
      properties: # Simplified for example
        bl_name_en: { type: "string" }
  source:
    file: "sql/search_licenses.sql"
  enabled: true
  tests:
    - name: "test_basic_search"
      arguments: [{ key: "name", value: "Futtaim" }]
      result: ">= 1 row" # Asserts at least one row is returned
```

### Common CLI Commands
- `mxcp test`: Run all endpoint tests defined in the YAML files.
- `dbt test`: Run all dbt data tests defined in `schema.yml` files.
- `dbt docs generate`: Generate dbt documentation and the `manifest.json` file needed for coverage calculation.
- `python3 scripts/calculate_test_coverage.py`: Calculate test coverage for dbt models.

### 5. Tooling (`mxcp`)
# ... existing code ... 