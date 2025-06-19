# UAE Business Licenses MCP Project

This project provides a full-stack, enterprise-ready MCP (MXCP) server for querying UAE business license data, with LLM (Claude Desktop) integration, dbt data pipeline, and robust filter/value discovery.

---

## **Quickstart**

### 1. **Clone the Repository**

```bash
git clone <your-repo-url>
cd uae-mxcp
```

---

### 2. **Set Up Python Environment**

> **Note:** You need Python 3.8+ and `virtualenv` or `venv`.

```bash
python3 -m venv .env
source .env/bin/activate
pip install mxcp
```

---

### 3. **Data Setup**

The project uses UAE business license data. You have three options for setting up the data:

#### Option 1: Use Sample Data (Quick Start)
A small sample dataset (`seeds/licenses_sample.csv`) is included in the repository for testing and development. This contains synthetic data that maintains the same patterns and distributions as the real data.

#### Option 2: Generate Synthetic Data
Generate your own synthetic dataset of any size:

```bash
# Generate 1000 synthetic records
./scripts/generate_synthetic_data.py \
  --pattern-file seeds/licenses_sample.csv \
  --output seeds/licenses.csv \
  --sample-size 1000
```

The synthetic data:
- Maintains real patterns and distributions
- Uses realistic but fake business names and addresses
- Preserves real emirate locations and business codes
- Randomizes sensitive information (owner details, exact coordinates)

#### Option 3: Use Real Data
If you have access to the RAW Labs private test data bucket, you can download the real dataset:

```bash
# Download the real dataset
./scripts/download_real_data.py --output seeds/licenses.csv
```

Requirements:
- AWS credentials configured
- Access to `s3://rawlabs-private-test-data/projects/uae_business_licenses/`
- Sufficient disk space (~3GBs)

The staging model (`models/staging/src_licenses.sql`) will automatically use whichever data file you choose to provide.

---

### 4. **Prepare the Database with dbt**

The project uses dbt (data build tool) to transform raw license data into analytics-ready models. Follow these steps:

1. **Configure your dbt profile**

The project expects a profile named `uaeme_licenses_prod` in your `profiles.yml`.

2. **Provide the licenses data file path**

The staging model requires you to specify the path to your licenses CSV file using the `licenses_file` variable:

```bash
dbt run --vars '{"licenses_file": "/path/to/your/licenses.csv"}'
```

3. **Understanding the data pipeline**

The project uses a three-layer transformation approach:
- `models/staging/src_licenses.sql`: Sources raw data from CSV
- `models/staging/stg_licenses_raw.sql`: Initial data cleaning and type casting
- `models/marts/`: Business-level transformations

4. **Run the models**

```bash
# Run all models
dbt run

# Run specific model
dbt run --select staging.src_licenses
```

5. **Verify the setup**

```bash
# Test all models
dbt test

# Show documentation
dbt docs generate
dbt docs serve
```

The models will create tables/views in your DuckDB database (`db-prod.duckdb`).

> **Note:** The project uses DuckDB's `read_csv_auto` function with specific parameters (delimiter='|', all_varchar=true) for optimal data loading. Make sure your CSV file matches this format.

---

### 5. **Start the MXCP Server**

#### **Option 1: Standard (recommended for development)**
```bash
mxcp serve
```

#### **Option 2: Clean Server with Role-Based Access**

The project includes role-based data redaction policies and provides clean stdio output (suitable for LLM integration). Start the server with a specific role:

```bash
# Start as guest user (restricted access)
./start-mcp.sh --role guest

# Start as admin user (full access)
./start-mcp.sh --role admin

# Show all options
./start-mcp.sh --help
```

> **Note:** The `--role` flag is for documentation and demonstration purposes only. The current MXCP server does **not** enforce this flag or perform data redaction based on it. Actual role-based redaction requires a proxy or future MXCP feature.

The following sensitive information is protected for guest users:

1. **Personal Information:**
   - Owner nationality (EN/AR)
   - Owner gender
   - Full address

2. **Business Information:**
   - Trade names (EN/AR)
   - CBLS number
   - Business activity codes and descriptions
   - Parent license numbers

3. **Relationship Information:**
   - Relationship types (EN/AR)
   - Parent license authorities (EN/AR)

4. **Location Information:**
   - Precise coordinates (latitude/longitude)
   - Exact location data

**Restrictions by Tool:**
- **Search Tool:** All sensitive fields are masked
- **Geo Tool:** Sensitive fields and precise locations are masked
- **Aggregate Tool:** Cannot aggregate by sensitive fields
- **Timeseries Tool:** Cannot filter by sensitive fields
- **Categorical Values Tool:** Cannot access sensitive field categories

Admin users have full access to all fields and functionality.

### 6. **Project Structure**

- `prompts/` — LLM prompt YAMLs (e.g., onboarding, guidance)
- `tools/` — MXCP tool YAMLs and SQLs (search, aggregate, timeseries, geo, categorical values, etc.)
- `resources/` — Resource YAMLs and SQLs (e.g., metadata endpoints)
- `models/` — dbt models (including staging models for raw data loading)
- `seeds/` — (optional, not used by default) dbt seed data; you can omit or rename this if not using dbt seed
- `db-prod.duckdb` — Main DuckDB database (generated by dbt)
- `start-mcp.sh` — Clean server startup for LLM integration

---

### 7. **Claude Desktop Integration**

To integrate with Claude Desktop, add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
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

> **Note:** The `--role` flag in the config is for documentation/demo only and is not enforced by the server.

Replace:
- `/path/to/uae-mxcp` with your project path
- `/home/your-username` with your home directory
- Adjust `--role` based on desired access level (`guest` or `admin`)

The server will start with clean stdio output suitable for LLM integration.

### 8. **Requirements**

```
pip install mxcp
```

Only `mxcp` is required to run the MCP server. If you are developing dbt models or using other tools, install them as needed (e.g., `dbt`, `duckdb`).

Data is loaded using a staging model (not `dbt seed`).

**How to load raw data:**

1. Place your raw data file (e.g., `data/licenses.csv`) in a location accessible to DuckDB.
2. Reference it in a staging model (e.g., `models/staging/stg_licenses.sql`).

Example:

```sql
-- models/staging/stg_licenses.sql
select * from read_csv_auto('data/licenses.csv', header=True)
```

You do not need a `seeds/` directory unless you use `dbt seed`. It is safe to omit or rename it if not used.