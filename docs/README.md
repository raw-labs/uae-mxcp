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
pip install -r requirements.txt
```

---

### 3. **Data Setup**

The project uses UAE business license data. You have three options for setting up the data:

#### Option 1: Use Sample Data (Recommended)
A small, synthetic sample dataset (`seeds/licenses_sample.csv`) is included. This is the fastest way to get started. All commands below assume you are using this file.

#### Option 2: Generate a Larger Synthetic Dataset
If you need more data, you can generate a larger synthetic file:

```bash
# Generate 10,000 synthetic records
./scripts/generate_synthetic_data.py --output seeds/licenses_large_sample.csv --sample-size 10000
```
You would then use `--vars '{"licenses_file": "seeds/licenses_large_sample.csv"}'` in the subsequent dbt commands.

#### Option 3: Use Real Data (Requires AWS Access)
If you have access to the RAW Labs private S3 bucket, you can download the real dataset using the provided script.

```bash
# Download the real dataset to the seeds directory
./scripts/download_real_data.py --output seeds/licenses.csv
```
This requires:
- AWS credentials configured locally.
- Access to the `s3://rawlabs-private-test-data` S3 bucket.

Once `seeds/licenses.csv` is downloaded, you can run the dbt models against it:
```bash
dbt run --vars '{"licenses_file": "seeds/licenses.csv"}'
```

---

### 4. **Prepare the Database with dbt**

The project uses dbt (data build tool) to transform raw license data from a source CSV into analytics-ready models in a DuckDB database.

1. **Install dbt dependencies**
```bash
dbt deps
```

2. **Run the dbt models**

The staging model requires you to specify the path to your licenses CSV file using the `licenses_file` variable.

```bash
# Build all models using the default sample file
dbt run --vars '{"licenses_file": "seeds/licenses_sample.csv"}'

# If you generated a larger file, use this command instead
# dbt run --vars '{"licenses_file": "seeds/licenses_large_sample.csv"}'
```

The `dbt run` command executes the models that read the CSV and build the tables in your local DuckDB database (`db-prod.duckdb`).

3. **Test the data**
```bash
# Test the models against the data from the sample file
dbt test --vars '{"licenses_file": "seeds/licenses_sample.csv"}'
```

---

### 5. **Start the MXCP Server**

You have two options for starting the server:

#### Option 1: Standard Development Server
This is the best option for most development tasks. It shows full logs and debug information.
```bash
mxcp serve
```

#### Option 2: Clean Server for LLM Integration
This project includes a wrapper script, `start-mcp.sh`, which is optimized for LLM integration (like with Claude Desktop). It provides clean stdio output by suppressing logs.
```bash
# Start as guest user (default)
./start-mcp.sh

# Start as admin user (for demo purposes)
./start-mcp.sh --role admin

# See all options
./start-mcp.sh --help
```

The server provides a set of tools for querying the license data. Policies are in place to restrict access for a `guest` user, but role enforcement must be handled by a proxy layer.

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
- `models/` — dbt models for data transformation.
- `seeds/` — **Source Data Directory**. This directory holds the source CSV files (e.g., `licenses_sample.csv`). **This project does NOT use the `dbt seed` command.** The models in the `models/` directory read directly from these files.
- `db-prod.duckdb` — Main DuckDB database (generated by dbt).
- `scripts/` — Contains helper scripts, like the synthetic data generator.
- `start-mcp.sh` — Clean server startup script for LLM integration.

---

### 7. **Claude Desktop Integration**

To integrate with Claude Desktop, add the following to your Claude Desktop configuration:

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

> **Note:** Role-based access control is defined in the tool policies but is not enforced by `mxcp serve`. A proxy or gateway is required to pass user context (like `role`) to the server. The `--role` flag in the script and config is for demonstration purposes.

Replace:
- `/path/to/uae-mxcp` with your project path
- `/home/your-username` with your home directory

The server will start with clean stdio output suitable for LLM integration.
