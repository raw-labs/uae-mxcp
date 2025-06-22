# MXCP Tool Generation Framework

## Overview

This document outlines the strategy for automatically generating high-quality MXCP tools, resources, and prompts from dbt mart models. The framework prioritizes business semantics over technical database operations.

## Implementation Status

### ✅ Completed
- **Generic Framework**: Completely domain-agnostic tool generation
- **Semantic Analysis**: Automatic classification of columns by business purpose
- **Tool Generation**: 5 types of tools automatically generated
- **Resource Generation**: Active records and summary resources
- **Prompt Generation**: AI guidance prompts for data exploration
- **Validation**: All artifacts validate successfully with MXCP
- **Documentation**: Comprehensive guides and examples

### 🔧 Current State
- **5 Working Tools**: find_licenses, aggregate_licenses, timeseries_licenses, geo_licenses, list_licenses_categories
- **1 Resource**: active_licenses (for records with status='Current')
- **2 Prompts**: analyze_licenses, explore_business_data
- **Full Test Suite**: 10 generated tests
- **Generic Framework**: No hardcoded domain-specific logic

### ⚠️ Known Issues
- Parameter handling: MXCP may still treat some parameters as required despite `required: []`
- Some advanced tools have validation warnings (under investigation)

## Architecture

The framework follows a modular, pipeline-based architecture:

```
dbt manifest → Semantic Analysis → Tool Generation → Validation → Deployment
```

### Core Components

1. **SemanticAnalyzer** (`analyzers/semantic_analyzer.py`)
   - Classifies columns by business purpose (identifier, status, temporal, etc.)
   - Extracts enum values from dbt `accepted_values` tests
   - Creates business entity models

2. **ToolGenerator** (`generators/tool_generator.py`)
   - Generates 5 types of tools based on entity characteristics
   - Creates comprehensive parameter sets with proper typing
   - Builds dynamic SQL with intelligent filtering

3. **ResourceGenerator** (`generators/resource_generator.py`)
   - Creates pre-computed views for frequently accessed data
   - Generates active records, summaries, and overviews
   - Uses proper URI schemes and refresh schedules

4. **PromptGenerator** (`generators/prompt_generator.py`)
   - Creates AI guidance prompts for data exploration
   - Provides context-aware suggestions

## Generated Tools

### 1. Search Tool (`find_{entity}`)
- **Purpose**: Comprehensive search and filtering
- **Parameters**: All entity fields with intelligent typing
- **Features**: 
  - Date range filtering
  - Numeric min/max filtering
  - Exact match for enums
  - Partial match for text
  - Pagination support

### 2. Aggregation Tool (`aggregate_{entity}`)
- **Purpose**: Multi-dimensional aggregation analysis
- **Parameters**: Boolean flags for each groupable dimension
- **Features**:
  - Dynamic GROUP BY based on parameters
  - Count totals and unique records
  - Flexible dimension selection

### 3. Time Series Tool (`timeseries_{entity}`)
- **Purpose**: Temporal analysis and trends
- **Parameters**: Time field selection, granularity, date ranges
- **Features**:
  - Multiple temporal fields support
  - Configurable granularity (day/week/month/year)
  - Automatic date field detection

### 4. Geographic Tool (`geo_{entity}`)
- **Purpose**: Spatial analysis and mapping
- **Parameters**: Geographic field selection, coordinate options
- **Features**:
  - Multiple geographic dimensions
  - Coordinate statistics
  - Bounding box filtering

### 5. Categorical Tool (`list_{entity}_categories`)
- **Purpose**: Distinct value enumeration
- **Parameters**: Field selection, count options
- **Features**:
  - All categorical fields supported
  - Optional count aggregation
  - Sorted by frequency

## Generated Resources

### Active Records Resource
- **Trigger**: Status fields with active-like enum values
- **Logic**: Filters for 'Current', 'Active', 'Enabled', etc.
- **Refresh**: Every 6 hours
- **URI**: `data://active/{entity}`

### Summary Resource  
- **Trigger**: Presence of metric fields
- **Logic**: Pre-computed aggregations and statistics
- **Refresh**: Daily at midnight
- **URI**: `data://summary/{entity}`

## Usage

### Generate All Artifacts
```bash
python generate_mxcp_tools.py
```

### Copy to Project
```bash
cp generated_mxcp/tools/*.yml tools/
cp generated_mxcp/sql/*.sql sql/
cp generated_mxcp/resources/*.yml resources/
cp generated_mxcp/prompts/*.yml prompts/
```

### Validate
```bash
mxcp validate
```

### Test
```bash
mxcp run tool list_licenses_categories --param field=emirate_name_en
```

## Configuration

The framework is highly configurable through `MXCPConfig`:

```python
config = {
    "max_parameters": 50,      # Maximum parameters per tool
    "include_descriptions": True,
    "generate_tests": True,
    "output_directory": "generated_mxcp"
}
```

## Future Enhancements

1. **Dynamic Parameter Requirements**: Investigate MXCP parameter handling
2. **Advanced Analytics**: ML-based insights and predictions
3. **Multi-Entity Tools**: Cross-entity joins and relationships
4. **Custom Tool Types**: Domain-specific tool patterns
5. **Performance Optimization**: Query optimization and caching

## Best Practices

1. **Column Naming**: Use consistent naming conventions
2. **dbt Tests**: Define `accepted_values` tests for enums
3. **Descriptions**: Add column descriptions in dbt models
4. **Data Types**: Use appropriate SQL data types
5. **Versioning**: Use `_v1` suffixes for model versioning

This framework represents a significant advancement in automated data tooling, enabling developers to focus on dbt models while automatically generating sophisticated data access tools. 