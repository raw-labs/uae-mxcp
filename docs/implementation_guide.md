# MXCP Tool Generation Framework - Implementation Guide

## Overview

The MXCP Tool Generation Framework automatically creates high-quality MXCP tools, resources, and prompts from dbt mart models using semantic analysis and intelligent pattern recognition.

## Quick Start

### Prerequisites
- dbt project with mart models
- Python 3.8+ environment
- MXCP installed and configured

### Basic Usage

1. **Generate dbt manifest**:
   ```bash
   dbt docs generate
   ```

2. **Run tool generation**:
   ```bash
   python generate_mxcp_tools.py
   ```

3. **Validate generated tools**:
   ```bash
   mxcp validate
   ```

### Safe Regeneration (Preserves Manual Tests)

```bash
# Write directly to current directory to preserve existing tests
python generate_mxcp_tools.py --output-dir .
```

## What Gets Generated

### 1. Tools
- **Search Tool**: `find_{entity}` - Comprehensive search with all fields as optional parameters
- **Aggregation Tool**: `aggregate_{entity}` - Group by categorical fields with counts
- **Time Series Tool**: `timeseries_{entity}` - Trend analysis over time fields
- **Geographic Tool**: `geo_{entity}` - Location-based analysis
- **Categorical Tool**: `list_{entity}_categories` - List distinct values for categorical fields

### 2. Resources
- **Active Records**: Pre-filtered subsets based on status fields
- **Summary Views**: Pre-computed metrics and aggregations

### 3. Prompts
- **Analysis Prompts**: Guide AI in data exploration
- **Business Context**: Provide domain-specific guidance

## Key Features

### Semantic Business Entity Framework
- Automatically analyzes dbt schemas to understand business meaning
- Generates natural language-oriented parameters
- Creates business-friendly tool names and descriptions

### Test Preservation (Merge Functionality)
- **Problem**: Regenerating tools would wipe out manually written tests
- **Solution**: Automatic merge preserves existing tests during regeneration
- **Usage**: Use `--output-dir .` to write directly to current directory

### Parameter Handling
- All parameters have `default: null` to make them optional
- Enum values include `null` for filter parameters
- Date ranges and numeric ranges supported
- Smart parameter naming (e.g., `EmirateNameEn` instead of `emirate_name_en`)

## Architecture

### Core Components

1. **Semantic Analyzer** (`mxcp_generator/analyzers/`)
   - Extracts business entities from dbt manifest
   - Classifies columns by semantic meaning
   - Detects enum values from dbt tests

2. **Tool Generator** (`mxcp_generator/generators/tool_generator.py`)
   - Creates MXCP tool definitions
   - Generates corresponding SQL queries
   - Implements merge functionality for test preservation

3. **Resource Generator** (`mxcp_generator/generators/resource_generator.py`)
   - Creates pre-computed views
   - Generates summary resources

4. **Prompt Generator** (`mxcp_generator/generators/prompt_generator.py`)
   - Creates AI guidance prompts
   - Provides business context

### Column Classification

The framework automatically classifies columns:
- **IDENTIFIER**: Primary keys, unique identifiers
- **CATEGORICAL**: Enum fields, status fields
- **TEMPORAL**: Date fields, timestamps
- **GEOGRAPHIC**: Location fields, coordinates
- **METRIC**: Numeric measurements
- **DESCRIPTIVE**: Text descriptions

## Advanced Usage

### Custom Configuration

Create configuration files to override default behavior:

```python
config = {
    "entity_patterns": {
        "primary_key_patterns": ["_pk", "_id", "_key"],
        "status_patterns": ["status", "state"],
        "date_patterns": ["date", "time", "created", "updated"]
    },
    "tool_generation": {
        "max_parameters": 50,
        "include_all_fields": True
    }
}
```

### Validation and Testing

```bash
# Validate all MXCP endpoints
mxcp validate

# Test specific tools
mxcp test tool find_licenses

# Run all tests
mxcp test
```

## Development Workflow

1. **Model Development**: Focus on creating high-quality dbt mart models
2. **Initial Generation**: Run tool generator to create base tools
3. **Customization**: Add manual tests and customizations to tools
4. **Safe Iteration**: Use merge functionality to regenerate without losing customizations
5. **Validation**: Ensure all tools validate and tests pass

## Troubleshooting

### Common Issues

1. **Parameter Requirement Errors**
   - **Cause**: MXCP treats all SQL parameters as required
   - **Solution**: All parameters now have `default: null`

2. **Test Preservation Not Working**
   - **Cause**: Using separate output directory
   - **Solution**: Use `--output-dir .` to write directly to current directory

3. **No Tools Generated**
   - **Cause**: No mart models found or manifest not generated
   - **Solution**: Ensure `dbt docs generate` ran successfully

4. **SQL Errors in Generated Queries**
   - **Cause**: Field name mismatches or missing columns
   - **Solution**: Check dbt model schema and regenerate

## Production Deployment

### AICP Compliance
- All changes follow AI Change Protocol
- Comprehensive testing before deployment
- Documentation updated with implementation details

### Performance Considerations
- Generated SQL uses efficient patterns
- Proper indexing on frequently queried fields
- Resource caching for optimal performance

### Monitoring
- Track tool usage patterns
- Monitor query performance
- Validate data freshness

## Future Enhancements

- Support for more complex relationships
- Advanced aggregation patterns
- Custom tool templates
- Integration with data lineage tools
- Automated performance optimization 