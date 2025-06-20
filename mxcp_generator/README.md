# MXCP Tool Generator

Automatically generates MXCP tools, resources, and prompts from dbt mart models using semantic analysis and business-oriented patterns.

## Features

- **Semantic Analysis**: Automatically classifies columns based on naming patterns and data types
- **Business-Oriented Tools**: Generates tools with natural language names and descriptions
- **Smart SQL Generation**: Creates optimized queries that leverage dbt model relationships
- **Comprehensive Coverage**: Generates tools, resources, prompts, and tests
- **Zero Configuration**: Works out of the box with standard dbt projects

## Installation

```bash
# Install required dependencies
pip install pyyaml

# Make the generator executable
chmod +x generate_mxcp_tools.py
```

## Quick Start

1. First, generate your dbt manifest:
```bash
dbt docs generate
```

2. Run the generator:
```bash
python generate_mxcp_tools.py
```

3. Review generated files in `generated_mxcp/` directory

4. Copy desired tools to your MXCP project:
```bash
cp generated_mxcp/tools/*.yml tools/
cp generated_mxcp/resources/*.yml resources/
cp generated_mxcp/prompts/*.yml prompts/
```

5. Validate and test:
```bash
mxcp validate
mxcp test
```

## How It Works

### 1. Semantic Analysis

The generator analyzes your dbt models to understand:

- **Column Classifications**: Identifies identifiers, business status, temporal, geographic, monetary, descriptive, and metric columns
- **Business Entities**: Detects primary entities (usually `dim_` tables) and their relationships
- **Data Patterns**: Recognizes common patterns like status fields, date ranges, and hierarchies

### 2. Tool Generation Patterns

For each entity, the generator creates:

- **Search Tools**: Find records by name, ID, or other descriptive fields
- **Filter Tools**: Filter by status, date ranges, or categories
- **Analytics Tools**: Aggregate metrics and analyze trends
- **Relationship Tools**: Navigate between related entities

Example generated tool:
```yaml
mxcp: "1.0.0"
tool:
  name: find_licenses
  description: "Search for licenses records with intelligent filtering"
  parameters:
    - name: BusinessName
      type: string
      description: "Search by BusinessName (partial match supported)"
      required: false
    - name: Status
      type: string
      enum: ["Active", "Expired", "Suspended"]
      description: "Filter by Status"
      required: false
  source:
    code: |
      SELECT *
      FROM {{ schema }}.dim_licenses
      WHERE 1=1
      {% if BusinessName %}
        AND bl_name_en ILIKE '%' || $BusinessName || '%'
      {% endif %}
      {% if Status %}
        AND license_status = $Status
      {% endif %}
      ORDER BY issue_date DESC
      LIMIT 100
```

### 3. Resource Generation

Creates pre-computed views for common queries:

- **Active Records**: Filters for currently valid/active records
- **Summary Views**: Pre-aggregated metrics by dimension
- **Overview Resources**: Cross-entity dashboards

### 4. Prompt Generation

Generates AI-friendly prompts that:

- Guide exploration of the data
- Explain available operations
- Provide example queries
- Document best practices

## Command Line Options

```bash
python generate_mxcp_tools.py [OPTIONS]

Options:
  --manifest PATH      Path to dbt manifest.json (default: target/manifest.json)
  --output-dir PATH    Output directory for generated files (default: generated_mxcp)
  --verbose           Enable verbose logging
  --dry-run           Generate but do not write files
  --help              Show help message
```

## Advanced Usage

### Custom Column Classification

Add metadata to your dbt schema.yml:

```yaml
models:
  - name: dim_customers
    columns:
      - name: customer_segment
        meta:
          classification: categorical
          business_name: "Customer Segment"
```

### Relationship Hints

The generator automatically detects foreign keys, but you can provide hints:

```yaml
models:
  - name: fact_sales
    columns:
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customers')
              field: customer_id
```

## Architecture

```
mxcp_generator/
├── analyzers/          # Semantic analysis of dbt models
│   └── semantic_analyzer.py
├── generators/         # MXCP artifact generators
│   ├── tool_generator.py
│   ├── resource_generator.py
│   └── prompt_generator.py
├── patterns/          # Reusable generation patterns
├── utils/             # Utility functions
│   └── dbt_utils.py
└── core.py           # Main orchestration logic
```

## Integration with MXCP

The generator is designed to work seamlessly with MXCP's features:

- Uses MXCP's YAML format (version 1.0.0)
- Generates tests compatible with `mxcp test`
- Follows MXCP naming conventions
- Integrates with MXCP's validation

## Future Enhancements

- [ ] Support for custom generation templates
- [ ] Integration with MXCP as a native command
- [ ] Real-time regeneration on dbt model changes
- [ ] AI-powered query optimization
- [ ] Multi-database dialect support

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This tool is part of the MXCP ecosystem and follows the same licensing terms. 