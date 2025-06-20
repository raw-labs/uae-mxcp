# MXCP Project Assistant Guide

## 1. Core Purpose

This document contains the rules and guidelines for the AI assistant operating within this **MXCP (RAW Labs) project**. The presence of an `mxcp-site.yml` file signals that you, the AI assistant, must strictly adhere to these instructions.

Your primary purpose is to help:
1.  **Author YAML endpoints** (`tools/`, `resources/`, `prompts/`) that comply with the MXCP specification.
2.  **Write and manage the underlying logic** (e.g., DuckDB SQL) for each endpoint.
3.  **List, validate, and test** all endpoints using the `mxcp` CLI.
4.  **Operate the project** safely via the `mxcp` CLI (`init`, `serve`, `test`, etc.).

---

## 2. Project Safety Rules & Protocols

These rules are **non-negotiable**. They ensure safe, consistent, and testable changes to the project.

### Project-Specific Design Principles

This project adheres to two additional core principles:

1.  **Data Loading Strategy**:
    - **Principle**: The project **does not** use `dbt seed` to load data.
    - **Implementation**: Source CSV files are read directly in the staging layer (`models/staging/`) using the `read_csv_auto()` or `read_csv()` function. The file path must be passed as a dbt variable (e.g., `licenses_file`).

2.  **Testing Philosophy**:
    - **Principle**: The SQL code in the `models/` directory is the source of truth. Tests are written to validate and document the behavior of this code against the provided data.
    - **Implementation**: If a dbt test fails, the default assumption is that the **test is incorrect** or incomplete (e.g., a list of `accepted_values` is missing a new value). The underlying SQL code should **not** be changed to make a test pass.

### Protected Resources
You must treat the following directories and files as **protected**. Do not modify them directly without following the specific protocols outlined below.
- **dbt Layer**: `models/`, `seeds/`, `tests/`, `macros/`, `dbt_project.yml`
- **MXCP Layer**: `tools/`, `resources/`, `prompts/`, `mxcp-site.yml`

### AI Change Protocol (AICP)
Before proposing any change, you **must** follow this protocol:

1.  **State Your Intent**: Clearly describe the tool, resource, or change you intend to create or modify.
2.  **Verify Pre-conditions**:
    - Confirm the git status is clean (`git status`).
    - Confirm all tests pass (`mxcp test`).
3.  **Propose the Change**:
    - For new endpoints, create a new YAML file in the appropriate directory (`tools/`, etc.).
    - For new SQL/Python logic, create a new file in a corresponding implementation directory (e.g., `sql/`).
    - The new endpoint YAML **must** include at least one test case.
4.  **Run Post-change Validation**:
    - After the change is applied, run `mxcp test` again to ensure your new endpoint is valid and that no existing functionality has broken.
5.  **Document the Change**: In your response, summarize the change, its impact, and confirm that all tests pass.

---

## 3. Endpoint YAML Reference

### Common Header
All endpoint files must start with this header:
```yaml
mxcp: "1.0.0"        # Required schema version
# Followed by exactly one of: tool / resource / prompt
```

### Tool Example
```yaml
# File: tools/search-licenses.yml
mxcp: "1.0.0"
tool:
  name: "search_licenses"              # Unique, snake_case or kebab-case
  description: "Finds business licenses by name or activity" # One-sentence summary
  parameters:
    - name: "name"
      type: "string"
      description: "The business name to search for"
      examples: ["Al Futtaim"]
  # The return schema defines the shape of the output.
  # For complex objects, this would typically reference a central schema in mxcp-site.yml.
  return:
    type: "array"
    items:
      type: "object"
      properties:
        license_pk: { type: "string" }
        bl_name_en: { type: "string" }
  # The source can be an external file (best practice) or inline code.
  source:
    file: "sql/search_licenses.sql"
  enabled: true
  # Every tool MUST have at least one test.
  tests:
    - name: "test_basic_search"
      description: "Ensures a known business can be found"
      arguments: [{ key: "name", value: "Al Futtaim" }]
      result: ">= 1 row" # Asserts at least one row is returned
  # Policies provide fine-grained access control.
  policies:
    input:
      - condition: "user.role == 'guest'"
        action: deny
        reason: "Guests cannot use this tool."
```

---

## 4. CLI Quick Reference

Use the `mxcp` command-line tool to manage the project.

- `mxcp test`: Run all endpoint tests.
- `mxcp serve`: Start the local MCP server for manual testing.
- `mxcp drift-detect`: Detect schema or behavioral drift over time.

---

## 5. Validation Checklist for the AI

Before committing a change, ensure it meets these criteria:

| Check                | Rule                                                                |
| -------------------- | ------------------------------------------------------------------- |
| **Schema Compliant** | YAML is valid and contains exactly one of `tool`, `resource`, or `prompt`. |
| **Unique Name**      | The endpoint `name` is unique within the project.                   |
| **Params Match SQL** | All `$param` placeholders in the SQL are defined in `parameters`.   |
| **Return Defined**   | The `return` schema is clearly defined.                             |
| **Test Coverage**    | At least one test case is included in the endpoint definition.      |
| **Source Defined**   | `source` block correctly points to a `file` or contains `code`.     |
| **Protocol Followed**| All steps in the **AI Change Protocol (AICP)** have been followed.  |
