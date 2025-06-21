# Automated MXCP Tool Generation from dbt Mart Models

## Executive Summary

This document outlines a comprehensive strategy for automatically generating MXCP tools, resources, and prompts from dbt mart models. The goal is to create a system where developers only need to focus on building high-quality dbt models, and the framework automatically generates pitch-perfect MXCP components that feel hand-crafted by domain experts.

### Key Innovation

The framework introduces a **Semantic Business Entity Framework** that analyzes dbt schemas to understand business meaning, then generates natural language-oriented MCP components that AI systems can intuitively use.

## 1. Core Philosophy & Principles

### 1.1 Business Semantics Over Technical Implementation

The generator prioritizes understanding what data **means** to the business rather than how it's stored:

- Generate tools like `find_business_licenses` instead of `search_dim_licenses`
- Create parameters like `business_name` instead of `bl_name_en`
- Return results with clear business context, not raw database fields

### 1.2 AI-First Design

Every generated component is optimized for AI consumption:

- Natural language descriptions that guide AI reasoning
- Smart parameter inference (AI can omit obvious parameters)
- Rich context in error messages
- Progressive disclosure of complexity

### 1.3 Quality Over Quantity

Rather than generating hundreds of generic CRUD operations:

- Focus on high-value business operations
- Combine related operations into cohesive tools
- Generate only what adds genuine value
- Ensure each tool has a clear business purpose

### 1.4 Zero Configuration, Progressive Enhancement

The system works with zero configuration but rewards metadata:

- Automatically infer semantics from column names and types
- Use dbt descriptions and tags when available
- Support custom metadata for advanced features
- Never require manual configuration for basic functionality

## 2. Semantic Analysis Engine

### 2.1 Column Classification

The engine analyzes each column to determine its semantic role:

```yaml
classifications:
  identifiers:
    patterns: ['*_id', '*_key', '*_code', '*_number']
    examples: ['license_id', 'business_key', 'registration_number']
    
  business_status:
    patterns: ['*_status', '*_state', 'is_*', 'has_*']
    examples: ['license_status', 'is_active', 'has_violations']
    
  temporal:
    patterns: ['*_date', '*_time', '*_at', 'created_*', 'updated_*']
    examples: ['issue_date', 'expiry_date', 'created_at']
    
  geographic:
    patterns: ['*_city', '*_country', '*_location', '*_address']
    examples: ['business_city', 'headquarters_country']
    
  monetary:
    patterns: ['*_amount', '*_price', '*_cost', '*_revenue']
    examples: ['license_fee_amount', 'annual_revenue']
    
  descriptive:
    patterns: ['*_name', '*_description', '*_title']
    examples: ['business_name', 'activity_description']
```

### 2.2 Business Entity Detection

Identify cohesive business entities from table structures:

```python
def detect_business_entities(mart_models):
    entities = {}
    
    # Detect primary entities (tables with business meaning)
    for model in mart_models:
        if model.name.startswith('dim_'):
            entity = extract_entity_name(model)
            entities[entity] = {
                'primary_model': model,
                'related_models': [],
                'operations': []
            }
    
    # Find related facts and bridges
    for entity in entities:
        entities[entity]['related_models'] = find_related_models(
            entity, 
            mart_models
        )
    
    return entities
```

### 2.3 Relationship Mapping

Automatically detect and classify relationships:

- **One-to-Many**: Parent entity with child records
- **Many-to-One**: Child records belonging to parent
- **Many-to-Many**: Bridge tables or junction entities
- **Temporal**: Time-series or historical relationships
- **Hierarchical**: Self-referencing structures

## 3. Tool Generation Patterns

### 3.1 Smart Search Tools

Instead of simple SELECT queries, generate intelligent search tools:

```yaml
# Generated from dim_licenses + fact_violations
mxcp: "1.0.0"
tool:
  name: find_business_licenses
  description: |
    Search for business licenses with intelligent filtering.
    Automatically includes related violation data when relevant.
  parameters:
    - name: business_name
      type: string
      description: "Business name (partial match supported)"
      required: false
    - name: status
      type: string
      enum: ${detected_statuses}
      description: "License status"
      required: false
    - name: include_violations
      type: boolean
      default: false
      description: "Include violation history"
  source:
    code: |
      WITH base_licenses AS (
        SELECT * FROM {{ schema }}.dim_licenses
        WHERE 1=1
        {% if business_name %}
          AND business_name_en ILIKE '%' || $business_name || '%'
        {% endif %}
        {% if status %}
          AND license_status = $status
        {% endif %}
      )
      SELECT 
        l.*,
        {% if include_violations %}
          v.violation_count,
          v.latest_violation_date
        {% endif %}
      FROM base_licenses l
      {% if include_violations %}
        LEFT JOIN {{ schema }}.fact_violations_summary v
          ON l.license_id = v.license_id
      {% endif %}
```

### 3.2 Analytical Tools

Generate tools that provide business insights:

```yaml
mxcp: "1.0.0"
tool:
  name: analyze_license_trends
  description: |
    Analyze licensing trends over time with breakdown options.
    Useful for identifying patterns and anomalies.
  parameters:
    - name: time_period
      type: string
      enum: ['day', 'week', 'month', 'quarter', 'year']
      default: 'month'
    - name: breakdown_by
      type: string
      enum: ${detected_dimensions}
      description: "Dimension to break down results"
```

### 3.3 Monitoring Tools

Generate tools for tracking changes and alerts:

```yaml
mxcp: "1.0.0"
tool:
  name: monitor_license_changes
  description: |
    Monitor licenses for status changes or upcoming expirations.
    Returns actionable alerts for business users.
```

## 4. Resource Generation

### 4.1 Semantic Resource Views

Generate resources that represent business concepts:

```yaml
mxcp: "1.0.0"
resource:
  name: active_businesses
  description: "All currently active businesses with valid licenses"
  source:
    code: |
      SELECT * FROM {{ schema }}.dim_licenses
      WHERE license_status = 'Active'
        AND expiry_date > CURRENT_DATE
```

### 4.2 Performance-Optimized Resources

Pre-compute complex aggregations:

```yaml
mxcp: "1.0.0"
resource:
  name: business_metrics_summary
  description: "Pre-computed business metrics for fast access"
  refresh_schedule: "0 */6 * * *"  # Every 6 hours
```

## 5. Prompt Generation

Generate contextual prompts that guide AI interactions:

```yaml
mxcp: "1.0.0"
prompt:
  name: explore_business_data
  description: "Guide AI to effectively explore business licensing data"
  template: |
    You have access to business licensing data for ${region}.
    
    Available operations:
    ${available_tools}
    
    Common questions you can answer:
    - Find businesses by name or activity
    - Check license validity and expiration
    - Analyze trends and patterns
    - Identify compliance issues
    
    Context: ${business_context}
```

## 6. MXCP Integration Points

### 6.1 Leveraging MXCP Features

MXCP already provides several enterprise features that our generator should integrate with:

#### Built-in Features (Provided by MXCP):
- **Authentication**: OAuth, API keys (no need to generate)
- **Audit Logging**: Automatic query tracking via `mxcp log`
- **Testing Framework**: `mxcp test` for endpoint validation
- **Transport Layer**: SSE/stdio/HTTP handling
- **CLI Operations**: `serve`, `validate`, `test` commands

#### What Our Generator Provides:
- **Semantic Tool Definitions**: Business-oriented YAML files
- **Optimized SQL Queries**: dbt-aware query generation
- **Smart Parameter Mapping**: Column to parameter conversion
- **Test Case Generation**: Meaningful test scenarios
- **Documentation**: Business-friendly descriptions

### 6.2 Configuration Integration

Our generator creates MXCP-compatible configurations:

```yaml
# Generated mxcp-site.yml additions
mxcp: 1.0.0
project: ${project_name}
dbt:
  enabled: true
  target: ${dbt_target}
profiles:
  prod:
    audit:
      enabled: true  # Leverage MXCP's audit
```

## 7. Implementation Architecture

### 7.1 Generator Pipeline

```python
class MCPGenerator:
    def __init__(self, dbt_manifest_path: str):
        self.manifest = load_dbt_manifest(dbt_manifest_path)
        self.semantic_analyzer = SemanticAnalyzer()
        self.pattern_matcher = PatternMatcher()
    
    def generate(self):
        # 1. Analyze dbt models
        entities = self.semantic_analyzer.extract_entities(
            self.manifest
        )
        
        # 2. Generate tools
        tools = self.generate_tools(entities)
        
        # 3. Generate resources
        resources = self.generate_resources(entities)
        
        # 4. Generate prompts
        prompts = self.generate_prompts(entities, tools)
        
        # 5. Generate tests (for mxcp test)
        tests = self.generate_tests(tools, resources)
        
        return GeneratedArtifacts(
            tools=tools,
            resources=resources,
            prompts=prompts,
            tests=tests
        )
```

### 7.2 Pattern Library

Reusable patterns for common scenarios:

```python
PATTERNS = {
    'search': SearchPattern(
        when=lambda e: e.has_descriptive_fields,
        generate=generate_search_tool
    ),
    'filter_by_status': StatusFilterPattern(
        when=lambda e: e.has_status_field,
        generate=generate_status_filter
    ),
    'temporal_analysis': TemporalPattern(
        when=lambda e: e.has_date_fields,
        generate=generate_temporal_tool
    ),
    'relationship_navigation': RelationshipPattern(
        when=lambda e: e.has_foreign_keys,
        generate=generate_relationship_tool
    )
}
```

## 8. Advanced Features

### 8.1 Multi-Model Operations

Generate tools that intelligently combine multiple dbt models:

```python
def generate_multi_model_tool(entities, relationships):
    """
    Generate tools that span multiple related entities
    Example: find_businesses_with_violations
    """
    # Detect meaningful combinations
    combinations = find_business_combinations(entities)
    
    for combo in combinations:
        yield generate_combined_tool(
            primary=combo.primary_entity,
            related=combo.related_entities,
            join_strategy=combo.optimal_join_strategy
        )
```

### 8.2 Performance Optimization

Automatic performance enhancements:

- **Materialization hints**: Suggest dbt materializations
- **Index recommendations**: Identify needed indexes
- **Query optimization**: Rewrite for performance
- **Caching strategies**: Implement smart caching

### 8.3 Security Integration

While MXCP handles authentication and audit, our generator can:

- **Generate row-level filters**: Based on dbt model metadata
- **Create data masking rules**: For sensitive columns
- **Define access patterns**: Tool-specific permissions
- **Generate compliance tests**: For data governance

## 9. Testing & Validation

### 9.1 Generated Test Suites

Create comprehensive tests for `mxcp test`:

```yaml
# Generated test file
tests:
  - name: test_find_businesses_basic
    tool: find_business_licenses
    params:
      business_name: "Sample Corp"
    assertions:
      - result_count: ">= 1"
      - contains_field: "license_id"
  
  - name: test_invalid_status
    tool: find_business_licenses  
    params:
      status: "InvalidStatus"
    expect_error: true
```

### 9.2 Continuous Validation

Integration with development workflow:

```bash
# Pre-commit hook
dbt run
python generate_mcp_tools.py
mxcp validate
mxcp test
```

## 10. Monitoring & Observability

### 10.1 Usage Analytics

Track tool usage via MXCP's audit logs:

```python
def analyze_tool_usage():
    """Analyze mxcp audit logs to improve generation"""
    # Query audit logs
    logs = query_mxcp_logs(since="7d")
    
    # Identify patterns
    usage_patterns = analyze_usage_patterns(logs)
    
    # Feedback to generator
    return GeneratorHints(
        popular_tools=usage_patterns.most_used,
        slow_queries=usage_patterns.performance_issues,
        error_patterns=usage_patterns.common_errors
    )
```

### 10.2 Performance Monitoring

Monitor and optimize generated tools:

- Query execution time tracking
- Resource utilization patterns  
- Cache hit rates
- Error frequency analysis

## 11. Maintenance & Evolution

### 11.1 Change Detection

Monitor dbt model changes:

```python
class ChangeDetector:
    def detect_changes(self, old_manifest, new_manifest):
        changes = {
            'added_models': [],
            'removed_models': [],
            'schema_changes': [],
            'relationship_changes': []
        }
        
        # Detailed change analysis
        for model in new_manifest.models:
            if model not in old_manifest:
                changes['added_models'].append(model)
                self.generate_new_tools(model)
            else:
                schema_diff = self.compare_schemas(
                    old_manifest[model],
                    new_manifest[model]
                )
                if schema_diff:
                    changes['schema_changes'].append(schema_diff)
                    self.update_affected_tools(model, schema_diff)
        
        return changes
```

### 11.2 Backward Compatibility

Maintain compatibility while evolving:

- Version generated tools
- Deprecation warnings
- Migration guides
- Compatibility tests

## 12. Future Enhancements

### 12.1 AI-Powered Improvements

- **Query optimization via AI**: Use AI to optimize generated SQL
- **Natural language tool names**: AI-generated business-friendly names
- **Smart test generation**: AI creates meaningful test scenarios
- **Documentation enhancement**: AI improves descriptions

### 12.2 Advanced Integration

- **Real-time schema evolution**: Hot-reload tool definitions
- **Multi-dialect support**: Generate for different SQL dialects
- **GraphQL generation**: Parallel GraphQL schema generation
- **API gateway integration**: Auto-register with API management

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
- [ ] Semantic analyzer for dbt manifest
- [ ] Basic tool generation for single models
- [ ] Integration with MXCP validation

### Phase 2: Intelligence (Weeks 5-8)
- [ ] Multi-model tool generation
- [ ] Relationship detection and navigation
- [ ] Smart parameter inference

### Phase 3: Optimization (Weeks 9-12)
- [ ] Performance optimization
- [ ] Advanced patterns (temporal, geographic)
- [ ] Comprehensive test generation

### Phase 4: Production (Weeks 13-16)
- [ ] Change detection and migration
- [ ] Monitoring integration
- [ ] Documentation generation
- [ ] Production deployment tools

## Success Metrics

1. **Developer Productivity**
   - Time from dbt model to working MXCP tool < 1 minute
   - Zero manual tool creation for 90% of use cases

2. **Quality Metrics**
   - Generated tools pass 100% of validation tests
   - AI successfully uses tools 95%+ of the time
   - Query performance within 10% of hand-optimized

3. **Adoption Metrics**
   - 80% of dbt models have generated tools
   - 90% of generated tools actively used
   - Developer satisfaction score > 4.5/5

## Conclusion

This framework transforms dbt models into intelligent, AI-ready interfaces that feel natural and purposeful. By focusing on business semantics over technical implementation, we create tools that both AI and humans can use effectively. The system scales from simple single-table operations to complex multi-entity analytics, all while maintaining quality, performance, and security.

The key innovation is treating dbt models not just as data transformations, but as rich business entity definitions that can be automatically exposed through intelligent, self-documenting interfaces. This approach dramatically reduces the time and expertise needed to create production-ready AI data interfaces.
