# Multi-Model Tool Generation Specification

## 1. Executive Summary

This specification extends our MXCP tool generation framework to support sophisticated multi-model scenarios using dbt meta tags. Instead of generating tools for single entities, we enable automatic creation of tools that intelligently combine multiple related models to answer complex business questions.

## 2. Current Limitations & Vision

### Current State
- Single-entity tools: `find_licenses`, `aggregate_licenses`
- Manual relationship handling
- Limited cross-entity analysis capabilities

### Target State
- Multi-model tools: `monitor_license_compliance`, `analyze_business_violations`
- Automatic relationship detection and optimization
- Business-context-aware tool generation

## 3. Meta Tag Architecture

### 3.1 Core Meta Tag Structure

```yaml
# models/marts/schema.yml
models:
  - name: dim_licenses
    meta:
      mxcp:
        entity_type: "primary"
        business_domain: "licensing"
        relationships:
          - target: "fact_violations"
            type: "one-to-many"
            join_key: "license_id"
            business_context: "compliance"
          - target: "dim_businesses" 
            type: "many-to-one"
            join_key: "business_id"
            business_context: "ownership"
        multi_model_scenarios:
          - name: "compliance_monitoring"
            description: "License compliance with violations and business context"
            includes: ["fact_violations", "dim_businesses"]
            tool_patterns: ["monitoring", "compliance"]
            priority: "high"
```

### 3.2 Meta Tag Categories

#### Entity Classification
```yaml
meta:
  mxcp:
    entity_type: "primary" | "fact" | "bridge" | "lookup"
    business_domain: "licensing" | "compliance" | "financial"
    data_freshness: "real-time" | "daily" | "weekly"
```

#### Relationship Definition
```yaml
relationships:
  - target: "target_model_name"
    type: "one-to-many" | "many-to-one" | "many-to-many"
    join_key: "column_name"
    join_type: "inner" | "left" | "right"
    business_context: "violations" | "renewals" | "payments"
    performance_hint: "index_recommended" | "materialized_join"
```

#### Multi-Model Scenarios
```yaml
multi_model_scenarios:
  - name: "scenario_name"
    description: "Business description"
    includes: ["model1", "model2"]
    tool_patterns: ["monitoring", "analytics", "compliance"]
    join_strategy: "performance_optimized" | "data_complete"
    priority: "high" | "medium" | "low"
```

## 4. Tool Generation Patterns

### 4.1 Compliance Monitoring Pattern

**Generated Tool**: `monitor_license_compliance`

```yaml
mxcp: "1.0.0"
tool:
  name: monitor_license_compliance
  description: |
    Monitor license compliance across violations, renewals, and business status.
    Combines license data with violation history and business information.
  parameters:
    - name: license_status
      type: string
      enum: ["Active", "Expired", "Current"]
    - name: has_violations
      type: boolean
    - name: expiry_within_days
      type: integer
      default: 90
    - name: include_violation_details
      type: boolean
      default: false
```

**Generated SQL**:
```sql
WITH compliance_base AS (
  SELECT 
    l.*,
    COUNT(v.violation_id) as violation_count,
    MAX(v.violation_date) as latest_violation,
    b.business_name_en,
    b.owner_nationality_en
  FROM dim_licenses_v1 l
  LEFT JOIN fact_violations_v1 v ON l.license_pk = v.license_pk
  LEFT JOIN dim_businesses_v1 b ON l.business_id = b.business_id
  WHERE 1=1
    AND ($license_status IS NULL OR l.bl_status_en = $license_status)
    AND ($expiry_within_days IS NULL OR 
         l.bl_exp_date_d BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL $expiry_within_days DAY)
  GROUP BY l.license_pk, b.business_id
)
SELECT *
FROM compliance_base
WHERE ($has_violations IS NULL OR 
       ($has_violations = true AND violation_count > 0) OR
       ($has_violations = false AND violation_count = 0))
ORDER BY 
  CASE WHEN violation_count > 0 THEN 1 ELSE 2 END,
  bl_exp_date_d ASC
```

### 4.2 Cross-Entity Analytics Pattern

**Generated Tool**: `analyze_licensing_trends`

```yaml
mxcp: "1.0.0"
tool:
  name: analyze_licensing_trends
  description: |
    Analyze licensing trends across violations, renewals, and business characteristics.
  parameters:
    - name: analysis_type
      type: string
      enum: ["renewal_patterns", "violation_trends", "compliance_rates"]
    - name: time_granularity
      type: string
      enum: ["monthly", "quarterly", "yearly"]
      default: "monthly"
    - name: breakdown_dimension
      type: string
      enum: ["emirate", "business_type", "license_type"]
```

### 4.3 Enriched Search Pattern

**Generated Tool**: `find_businesses_with_context`

```yaml
mxcp: "1.0.0"
tool:
  name: find_businesses_with_context
  description: |
    Search businesses with enriched context including license status,
    violation history, and compliance metrics.
  parameters:
    - name: business_name
      type: string
    - name: include_license_details
      type: boolean
      default: true
    - name: include_violation_summary
      type: boolean
      default: false
```

## 5. Implementation Architecture

### 5.1 Extended Data Structures

```python
@dataclass
class MultiModelScenario:
    """Represents a multi-model tool generation scenario"""
    name: str
    description: str
    primary_entity: BusinessEntity
    related_entities: List[BusinessEntity]
    tool_patterns: List[str]
    join_strategy: str
    priority: str
    business_context: str

@dataclass
class EnhancedRelationshipInfo:
    """Extended relationship information with meta tag support"""
    from_entity: str
    to_entity: str
    relationship_type: str
    join_keys: List[Tuple[str, str]]
    join_type: str = "left"
    business_context: str = ""
    performance_hint: str = ""
    cardinality_expectation: str = ""
```

### 5.2 Multi-Model Tool Generator

```python
class MultiModelToolGenerator:
    """Generates tools that span multiple related entities"""
    
    def generate_multi_model_tools(
        self, 
        entities: Dict[str, BusinessEntity]
    ) -> List[Dict[str, Any]]:
        """Generate tools based on multi-model scenarios"""
        tools = []
        scenarios = self._extract_scenarios_from_meta_tags(entities)
        
        for scenario in scenarios:
            if "compliance" in scenario.tool_patterns:
                tools.append(self._generate_compliance_tool(scenario))
            if "monitoring" in scenario.tool_patterns:
                tools.append(self._generate_monitoring_tool(scenario))
            if "analytics" in scenario.tool_patterns:
                tools.append(self._generate_analytics_tool(scenario))
        
        return tools
    
    def _generate_compliance_tool(self, scenario: MultiModelScenario) -> Dict:
        """Generate compliance monitoring tool"""
        return {
            "mxcp": "1.0.0",
            "tool": {
                "name": f"monitor_{scenario.primary_entity.name}_compliance",
                "description": scenario.description,
                "parameters": self._generate_compliance_parameters(scenario),
                "source": {
                    "file": f"../sql/monitor_{scenario.primary_entity.name}_compliance.sql"
                }
            }
        }
```

### 5.3 Advanced SQL Generation

```python
class MultiModelSQLGenerator:
    """Generates optimized SQL for multi-model tools"""
    
    def generate_compliance_sql(self, scenario: MultiModelScenario) -> str:
        """Generate SQL for compliance monitoring"""
        joins = self._build_optimized_joins(scenario)
        filters = self._build_conditional_filters(scenario)
        aggregations = self._build_business_aggregations(scenario)
        
        return f"""
WITH base_query AS (
  SELECT l.* FROM {scenario.primary_entity.primary_model.name}_v1 l
  {joins}
  WHERE 1=1 {filters}
),
enriched_data AS (
  SELECT 
    *,
    {aggregations}
  FROM base_query
  GROUP BY {self._get_grouping_columns(scenario)}
)
SELECT * FROM enriched_data
ORDER BY {self._get_business_priority_order(scenario)}
        """
```

## 6. Performance Optimization Strategies

### 6.1 Join Strategy Selection

```python
def select_join_strategy(self, scenario: MultiModelScenario) -> str:
    """Select optimal join strategy based on meta tags and data characteristics"""
    
    if scenario.join_strategy == "performance_optimized":
        return self._generate_materialized_join_strategy(scenario)
    elif scenario.join_strategy == "data_complete":
        return self._generate_complete_data_strategy(scenario)
    else:
        return self._generate_balanced_strategy(scenario)
```

### 6.2 Materialized View Recommendations

```python
def recommend_materializations(self, scenarios: List[MultiModelScenario]) -> List[str]:
    """Recommend materialized views for common multi-model patterns"""
    recommendations = []
    
    # Analyze join frequency and complexity
    join_patterns = self._analyze_join_patterns(scenarios)
    
    for pattern in join_patterns:
        if pattern.frequency > 3 and pattern.complexity > 2:
            recommendations.append(
                f"CREATE MATERIALIZED VIEW {pattern.suggested_name} AS {pattern.optimized_sql}"
            )
    
    return recommendations
```

## 7. Validation & Quality Assurance

### 7.1 Meta Tag Validation

```python
class MetaTagValidator:
    """Validates meta tags for consistency and correctness"""
    
    def validate_multi_model_scenarios(self, entities: Dict[str, BusinessEntity]) -> List[str]:
        """Validate multi-model scenarios for consistency"""
        errors = []
        
        for entity_name, entity in entities.items():
            scenarios = entity.primary_model.meta.get('mxcp', {}).get('multi_model_scenarios', [])
            
            for scenario in scenarios:
                # Validate referenced models exist
                for included_model in scenario.get('includes', []):
                    if included_model not in entities:
                        errors.append(f"Model {included_model} referenced in scenario but not found")
                
                # Validate join keys exist
                # Validate tool patterns are supported
                # Validate business context consistency
        
        return errors
```

### 7.2 Generated Tool Testing

```python
def generate_multi_model_tests(self, tools: List[Dict]) -> List[Dict]:
    """Generate comprehensive tests for multi-model tools"""
    tests = []
    
    for tool in tools:
        tool_name = tool['tool']['name']
        
        # Basic functionality test
        tests.append({
            "name": f"test_{tool_name}_basic",
            "tool": tool_name,
            "description": f"Basic multi-model functionality test",
            "params": self._generate_minimal_params(tool),
            "assertions": [
                {"type": "status", "value": "success"},
                {"type": "has_results", "value": True},
                {"type": "join_integrity", "value": True}
            ]
        })
        
        # Cross-entity consistency test
        tests.append({
            "name": f"test_{tool_name}_consistency",
            "tool": tool_name,
            "description": f"Cross-entity data consistency test",
            "params": self._generate_consistency_params(tool),
            "assertions": [
                {"type": "referential_integrity", "value": True},
                {"type": "business_logic_consistency", "value": True}
            ]
        })
    
    return tests
```

## 8. Migration Strategy

### 8.1 Backward Compatibility

- Existing single-entity tools remain unchanged
- Meta tags are optional - models without meta tags continue to work
- Gradual migration path for adding multi-model capabilities

### 8.2 Implementation Phases

**Phase 1**: Meta tag infrastructure and validation
**Phase 2**: Basic multi-model tool generation
**Phase 3**: Advanced patterns and optimization
**Phase 4**: Performance monitoring and tuning

## 9. Success Metrics

### 9.1 Technical Metrics
- Multi-model tool generation time < 30 seconds
- Generated SQL query performance within 20% of hand-optimized
- 100% meta tag validation pass rate

### 9.2 Business Metrics
- 80% reduction in manual cross-entity query development
- 90% of complex business questions answerable through generated tools
- Developer satisfaction score > 4.5/5 for multi-model capabilities

## 10. Future Enhancements

### 10.1 AI-Powered Optimization
- Automatic join strategy selection based on query patterns
- Intelligent materialization recommendations
- Dynamic performance tuning

### 10.2 Advanced Business Patterns
- Temporal relationship handling
- Hierarchical entity navigation
- Complex business rule enforcement

This specification provides a comprehensive foundation for implementing sophisticated multi-model tool generation while maintaining the simplicity and power of our existing framework. 