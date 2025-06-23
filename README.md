# UAE Business Licenses - Embedded SQL Tools Demo

This is a **minimal example** demonstrating MXCP's embedded SQL tools functionality. It shows how to go from a CSV file to a queryable system with just a few files and zero tool configuration.

---

## Overview

This ultra-simplified setup demonstrates the **embedded SQL tools** approach where you can query data directly using SQL without creating custom tool definitions. Perfect for rapid prototyping and simple data exploration.

### Key Features

| Feature                  | Description                                                                                    |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| **Embedded SQL Tools**  | Direct SQL querying via `mxcp query` command - no YAML configuration needed                   |
| **Minimal Setup**       | Single dbt model reading CSV data - 3 core files total                                        |
| **Sample Data**         | 1,000 UAE business license records for fast demos                                             |
| **JSON Output**         | Structured API responses with `--json-output` flag                                            |
| **Real Business Data**  | Actual UAE license data with emirates, business types, and ownership information              |

---

## Quick Start

### Prerequisites
- Python 3.8+
- dbt and MXCP installed

### Setup (3 steps)

1. **Build the data model**
   ```bash
   dbt run --vars '{"licenses_file": "seeds/licenses_sample.csv"}'
   ```

2. **Test basic query**
   ```bash
   mxcp query "SELECT COUNT(*) as total_records FROM licenses"
   ```

3. **Try complex queries**
   ```bash
   mxcp query "SELECT \"Emirate Name En\", COUNT(*) as count FROM licenses GROUP BY \"Emirate Name En\" ORDER BY count DESC LIMIT 5" --json-output
   ```

---

## Usage Examples

### Basic Queries
```bash
# Count all records
mxcp query "SELECT COUNT(*) FROM licenses"

# Show first few records
mxcp query "SELECT * FROM licenses LIMIT 3"
```

### Business Analysis
```bash
# Licenses by emirate
mxcp query "SELECT \"Emirate Name En\", COUNT(*) as count FROM licenses GROUP BY \"Emirate Name En\" ORDER BY count DESC"

# Business types
mxcp query "SELECT \"BL Type En\", COUNT(*) as count FROM licenses GROUP BY \"BL Type En\" ORDER BY count DESC"

# License status
mxcp query "SELECT \"BL Status EN\", COUNT(*) as count FROM licenses GROUP BY \"BL Status EN\""
```

### JSON Output
Add `--json-output` to any query for structured API responses:
```bash
mxcp query "SELECT \"Emirate Name En\", COUNT(*) as licenses FROM licenses GROUP BY \"Emirate Name En\" LIMIT 3" --json-output
```

---

## Project Structure

```
uae-mxcp/
├── mxcp-site.yml              # MXCP config with sql_tools: enabled: true
├── dbt_project.yml            # Basic dbt configuration  
├── models/
│   └── licenses.sql           # Single model reading CSV data
├── seeds/
│   └── licenses_sample.csv    # 1,000 sample license records
└── db-prod.duckdb            # Generated DuckDB database
```

---

## What This Demonstrates

### Embedded SQL Tools Benefits
- ✅ **Zero configuration** - No YAML tool definitions needed
- ✅ **Direct SQL access** - Query any way you want
- ✅ **Rapid prototyping** - From CSV to queryable in minutes
- ✅ **JSON API ready** - Structured responses for applications
- ✅ **Real data insights** - Immediate business value

### Perfect For
- **Data exploration** - Quick analysis of CSV files
- **Prototyping** - Test ideas before building custom tools
- **Simple demos** - Show data value immediately
- **Learning MXCP** - Understand core functionality

---

## Sample Data

The `seeds/licenses_sample.csv` contains 1,000 real UAE business license records with:
- **Emirates**: Dubai, Abu Dhabi, Sharjah, Ajman, etc.
- **Business Types**: Commercial, Professional, Industrial
- **License Status**: Current, Expired, Cancelled
- **Ownership Info**: Nationalities, relationship types
- **Business Activities**: Detailed activity descriptions

---

## Next Steps

This minimal setup shows embedded SQL tools. For a full-featured example with:
- Custom tool definitions
- Multi-model relationships  
- Data quality testing
- Advanced tool generation

Check out the `main` branch which demonstrates the complete MXCP toolkit.

---

**This branch demonstrates the simplest possible path from CSV to queryable system using MXCP's embedded SQL tools!** 🚀
