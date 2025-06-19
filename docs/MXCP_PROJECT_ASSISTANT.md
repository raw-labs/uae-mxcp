# MXCP Project Assistant

## Table of Contents

- [Context](#context)
- [Purpose](#purpose)
- [Project Safety Rules](#project-safety-rules)
  - [Pre-change Requirements](#pre-change-requirements)
  - [Protected Resources](#protected-resources)
  - [Change Protocols](#change-protocols)
  - [Post-change Validation](#post-change-validation)
- [Endpoint YAML Reference](#endpoint-yaml-reference)
  - [Common Header](#common-header)
  - [Tool](#tool)
  - [Resource](#resource)
  - [Prompt](#prompt)
- [Type System Essentials](#type-system-essentials)
- [Tests](#tests)
- [Policies](#policies)
- [CLI Quick Sheet](#cli-quick-sheet)
- [Validation Checklist](#validation-checklist)
- [Example Workflow](#example-workflow)

## Context

This rule attaches automatically when an **`mxcp-site.yml`** file is present, signalling that the repository is an **MXCP** (RAW Labs) project.

## Purpose

The assistant helps you

1. **Author YAML endpoint files** (tools / resources / prompts) that comply with the MXCP spec.
2. **Write DuckDB SQL** (or Python, etc.) that implements each endpoint's logic.
3. **List & validate** endpoints for structure, type-safety and policy coverage.
4. **Define and run tests** for every endpoint.
5. **Operate the project** via the `mxcp` CLI (initialise, serve, drift-detect, etc.).

## Project Safety Rules

The assistant follows strict safety rules defined in [`.mxcp-rules.yml`](../.mxcp-rules.yml). These rules ensure safe and consistent changes to the project.

### Pre-change Requirements
- Clean git status
- Successful validation of existing endpoints
- All tests passing

### Protected Resources
- DBT layer: `models/`, `seeds/`, `tests/`, `macros/`, `dbt_project.yml`
- MXCP layer: `tools/`, `resources/`, `prompts/`, `mxcp-site.yml`

### Change Protocols
- Must preserve existing functionality
- Must include comprehensive tests
- Must document changes with:
  - Change reason
  - Data/API impact
  - Test coverage

### Post-change Validation
- Run all tests
- Validate endpoints
- Review git diff
- Document changes

---

## Endpoint YAML reference

### Common header

```yaml
mxcp: "1.0.0"        # required schema version
# exactly one of: tool / resource / prompt
```

### Tool

```yaml
tool:
  name: "search_licenses"              # snake_case or kebab-case, unique
  description: "Find business licenses by name or activity" # one-sentence summary
  tags: ["search", "license"]
  annotations:                       # optional UX hints
    title: "Search Business Licenses"
    readOnlyHint: true
    destructiveHint: false
    idempotentHint: true
    openWorldHint: false
  parameters:
    - name: "name"
      type: "string"
      description: "Business name to match"
      examples: ["Al Futtaim"]
  return:
    type: "array"
    items:
      $ref: "#/components/schemas/license"
  source:                            # choose **one**
    file: "sql/search_licenses.sql"    # external file
    # or
    code: |
      SELECT *
      FROM licenses
      WHERE trade_name_en ILIKE '%' || $name || '%'
  enabled: true
  tests:
    - name: "basic"
      arguments: [{ key: "name", value: "Al Futtaim" }]
      result: ">= 1 row"
  policies:                          # optional – see policies section
    input:
      - condition: "user.role == 'guest'"
        action: deny
        reason: "Guests must sign in"
```

### Resource

```yaml
resource:
  uri: "licenses://{id}"
  description: "Business license resource"
  mime_type: "application/json"
  parameters:
    - name: "id"
      type: "integer"
  return:
    $ref: "#/components/schemas/license"
  language: "sql"
  source:
    file: "sql/license_by_id.sql"
  enabled: true
  policies: { … }
```

### Prompt

```yaml
prompt:
  name: "license_status_checker"
  description: "Checks if a business license is valid"
  tags: ["validation"]
  parameters:
    - { name: "license_number", type: "string", description: "Business license number" }
  messages:
    - { role: "system", type: "text", prompt: "You are a license validation assistant." }
    - { role: "user",   type: "text", prompt: "Check status for license {{ license_number }}" }
  policies: { … }
```

## Type system essentials

| Base type | Extras & constraints                                   |
| --------- | ------------------------------------------------------ |
| string    | `minLength`, `maxLength`, `pattern`, `format`          |
| number    | `minimum`, `maximum`, `exclusiveMinimum`, …            |
| integer   | same as number but integral                            |
| boolean   | –                                                      |
| array     | `items`, `minItems`, `maxItems`, `uniqueItems`         |
| object    | `properties`, `required`, `additionalProperties=false` |

Use these fields for **both** `parameters` and `return` schemas.

## Tests

Each `tests:` entry supplies:

```yaml
- name: "edge_case"
  description: "Empty result for non-existent business"
  arguments:
    - { key: "name", value: "NONEXISTENT_BUSINESS_12345" }
  result: "0 rows"
```

`mxcp test` runs all tests and reports drift.

## Policies

Policies are CEL expressions evaluated at `input` and/or `output`.

| Stage  | Example action set                                                |
| ------ | ----------------------------------------------------------------- |
| input  | `deny`                                                            |
| output | `deny`, `filter_fields`, `mask_fields`, `filter_sensitive_fields` |

```yaml
policies:
  output:
    - condition: "response.status == 'Under Liquidation'"
      action: mask_fields
      fields: ["owner_details"]
```

`user` and `response` objects are available inside expressions.

## CLI quick sheet

```bash
mxcp init            # scaffold a new project
mxcp serve           # start the MCP server
mxcp test           # run endpoint tests
mxcp drift-detect    # detect schema or behaviour drift
```

Common options: `--profile`, `--json-output`, `--debug`, `--readonly`.

## Validation checklist

| Check                | Rule                                                                            |
| -------------------- | ------------------------------------------------------------------------------- |
| **Schema**           | Each YAML must parse and contain exactly one of `tool` / `resource` / `prompt`. |
| **Name**             | Unique, lowercase with hyphens or snake\_case.                                  |
| **Parameters ↔ SQL** | Number & names of `$param` or `$1` placeholders match `parameters`.             |
| **Return type**      | Fully defined and uses base types / refs.                                       |
| **Tests**            | At least one test per endpoint.                                                 |
| **Policies**         | Expressions compile; actions are valid.                                         |
| **Source**           | Provide either `file:` or multiline `code:`; not both.                          |

## Example workflow

1. **Create a tool**

   > "Create a tool `search_licenses_by_activity` with `activity_code` (string) input that returns matching licenses."
2. **Generate SQL automatically**
   The assistant drafts DuckDB code with `$activity_code` placeholder and inserts it under `source.code`.
3. **List endpoints**

   > "List endpoints" → bullet list with name, description, test status.
4. **Validate**

   > "Validate tools" → report any missing fields or mismatches.
5. **Serve & test**

   ```bash
   mxcp serve
   curl http://localhost:8000/search_licenses_by_activity?activity_code=4711001
   ```

## Related Documentation

- [Project README](../README.md) - Project overview and setup instructions
- [`.mxcp-rules.yml`](../.mxcp-rules.yml) - Detailed project safety rules 