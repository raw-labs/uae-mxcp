# Tool Generation Framework - Quick Start Guide

## Overview

The MXCP Tool Generation Framework automatically creates high-quality MXCP tools from your dbt models using semantic analysis and intelligent pattern recognition.

## Quick Start

```bash
# 1. Ensure dbt models are built
dbt run --vars '{"licenses_file": "seeds/licenses.csv"}'

# 2. Generate dbt manifest
dbt docs generate --vars '{"licenses_file": "seeds/licenses.csv"}'

# 3. Generate MXCP tools
python generate_mxcp_tools.py --manifest target/manifest.json --output generated_tools

# 4. Review and copy tools
cp generated_tools/tools/*.yml tools/
cp generated_tools/sql/*.sql sql/
```

## What Gets Generated

From each dbt mart model (e.g., `dim_licenses`), the framework generates:

### 1. **Search Tool** (`find_<entity>`)
- Comprehensive filters for ALL columns
- Intelligent filter types based on data type:
  - Text fields: Partial match with ILIKE
  - Dates: From/To range parameters
  - Numbers: Min/Max parameters
  - Enums: Exact match with dropdown values
- Pagination support

### 2. **Aggregation Tool** (`aggregate_<entity>`)
- Dynamic grouping by ANY categorical field
- All fields available as groupBy parameters
- Common filters for data subsetting
- Returns counts and unique counts

### 3. **Time Series Tool** (`timeseries_<entity>`)
- Analyze trends over time
- Configurable granularity (day/week/month/quarter/year)
- Multiple date field support
- Full filter capabilities

### 4. **Geographic Tool** (`geo_<entity>`)
- Group by geographic fields (emirate, authority, address)
- Coordinate statistics (avg, min, max)
- Bounding box filtering
- Coordinate field auto-detection

### 5. **Categorical Tool** (`list_<entity>_categories`)
- List distinct values for any categorical field
- Optional counts
- Dynamic field selection
- Useful for building UIs

## Architecture

```
mxcp_generator/
├── analyzers/
│   └── semantic_analyzer.py    # Classifies columns semantically
├── generators/
│   ├── tool_generator.py       # Creates MXCP tools
│   ├── resource_generator.py   # Creates resources
│   └── prompt_generator.py     # Creates LLM prompts
├── utils/
│   └── dbt_utils.py           # dbt manifest parsing
└── core.py                    # Main orchestration
```

## Column Classification

The semantic analyzer classifies columns to generate appropriate filters:

| Classification | Examples | Filter Type |
|----------------|----------|-------------|
| IDENTIFIER | license_pk, bl_number | Exact match |
| BUSINESS_STATUS | bl_status_en, is_active | Exact match with enum |
| TEMPORAL | bl_est_date, created_at | Date range (from/to) |
| GEOGRAPHIC | emirate_name, latitude | Exact/partial match |
| MONETARY | fee_amount, total_cost | Min/max range |
| DESCRIPTIVE | bl_name_en, description | Partial match (ILIKE) |
| METRIC | count, total_revenue | Min/max range |
| CATEGORICAL | bl_type_en, owner_gender | Exact match with enum |

## Customization

### Adding Custom Classification Rules

Edit `mxcp_generator/analyzers/semantic_analyzer.py`:

```python
CLASSIFICATION_PATTERNS = {
    ColumnClassification.IDENTIFIER: [
        r'.*_id$', r'.*_key$', r'.*_code$',
        # Add your patterns here
    ],
    # ...
}
```

### Modifying Tool Templates

Edit tool generation methods in `mxcp_generator/generators/tool_generator.py`:

```python
def _generate_search_tool(self, entity: BusinessEntity) -> Optional[Dict[str, Any]]:
    # Customize search tool generation
    pass
```

### Adding New Tool Types

1. Add generation method to `ToolGenerator`:
```python
def _generate_custom_tool(self, entity: BusinessEntity) -> Optional[Dict[str, Any]]:
    # Your custom tool logic
    pass
```

2. Call it from `generate_for_entity()`:
```python
def generate_for_entity(self, entity: BusinessEntity) -> List[Dict[str, Any]]:
    tools = []
    # ... existing tools ...
    
    custom_tool = self._generate_custom_tool(entity)
    if custom_tool:
        tools.append(custom_tool)
```

## Best Practices

1. **Run dbt first**: Always ensure your dbt models are built before generating tools
2. **Review generated SQL**: Check the `sql/` directory for generated queries
3. **Test thoroughly**: Use `mxcp test` to validate generated tools
4. **Customize as needed**: The framework provides a starting point - customize for your needs
5. **Version control**: Commit both YAML and SQL files

## Troubleshooting

### No tools generated
- Ensure dbt models are in the `marts/` directory
- Check that `manifest.json` exists and is recent
- Verify model names start with `dim_` or `fact_`

### Missing filters
- Check column data types in dbt schema.yml
- Add `accepted_values` tests for enum detection
- Review column classification in semantic analyzer

### SQL errors
- Check generated SQL in `sql/` directory
- Ensure all column names match your model
- Verify table references use `_v1` suffix for versioned models 