# Project Design Principles

This document outlines the core, non-negotiable design principles for this project. The AI assistant is required to understand and adhere to these rules at all times.

## 1. Data Loading Strategy

- **Principle**: The project **does not** use `dbt seed` to load data.
- **Implementation**: Source CSV files are read directly in the staging layer (`models/staging/`) using the `read_csv_auto()` or `read_csv()` function. The file path should be passed as a dbt variable (e.g., `licenses_file`).

## 2. Testing Philosophy

- **Principle**: The SQL code in the `models/` directory is the source of truth. Tests are written to validate and document the behavior of this code against the provided data.
- **Implementation**: If a dbt test fails, the default assumption is that the **test is incorrect** or incomplete.
    - For `unique` tests, it means the column is not unique by design. The test should be re-evaluated or removed.
    - For `accepted_values` tests, it means the list of values is incomplete. The test should be updated to include the missing values.
    - The underlying SQL code should **not** be changed to make a test pass.

--- 