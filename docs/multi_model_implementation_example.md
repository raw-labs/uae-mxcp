# Multi-Model Tool Generation - UAE Licenses Implementation Example

## Scenario: Extending UAE Licenses with Violations and Business Data

This example demonstrates how we would extend our current single-entity UAE licenses project to support multi-model scenarios using meta tags.

## 1. Current State vs. Target State

### Current State
- **Single Entity**: `dim_licenses` only
- **Generated Tools**: 5 tools (find, aggregate, timeseries, geo, categories)
- **Limitations**: No cross-entity analysis, no business context enrichment

### Target State with Multi-Model
- **Multiple Entities**: `dim_licenses`, `fact_violations`, `dim_businesses`, `fact_inspections`
- **Generated Tools**: 12+ tools including multi-model compliance and monitoring tools
- **Capabilities**: Cross-entity analytics, compliance monitoring, business intelligence

## 2. Enhanced Schema with Meta Tags

### 2.1 Primary Entity: Licenses

```yaml
# models/marts/schema.yml
models:
  - name: dim_licenses
    meta:
      mxcp:
        entity_type: "primary"
        business_domain: "licensing"
        data_freshness: "daily"
        relationships:
          - target: "fact_violations"
            type: "one-to-many"
            join_key: "license_pk"
            join_type: "left"
            business_context: "compliance_violations"
            performance_hint: "index_recommended"
            cardinality_expectation: "1:N"
          
          - target: "dim_businesses"
            type: "many-to-one"
            join_key: "business_id"
            join_type: "left"
            business_context: "business_ownership"
            performance_hint: "materialized_join"
            cardinality_expectation: "N:1"
          
          - target: "fact_inspections"
            type: "one-to-many"
            join_key: "license_pk"
            join_type: "left"
            business_context: "regulatory_inspections"
            cardinality_expectation: "1:N"
        
        multi_model_scenarios:
          - name: "compliance_monitoring"
            description: "Monitor license compliance with violations and inspection history"
            includes: ["fact_violations", "fact_inspections"]
            tool_patterns: ["monitoring", "compliance", "alerts"]
            join_strategy: "performance_optimized"
            priority: "high"
            use_cases: ["regulatory_compliance", "risk_assessment"]
          
          - name: "business_intelligence"
            description: "Analyze licensing trends with business context and violations"
            includes: ["dim_businesses", "fact_violations"]
            tool_patterns: ["analytics", "reporting"]
            join_strategy: "data_complete"
            priority: "medium"
            use_cases: ["business_analysis", "trend_analysis"]
          
          - name: "renewal_management"
            description: "Manage license renewals with violation and inspection context"
            includes: ["fact_violations", "fact_inspections", "dim_businesses"]
            tool_patterns: ["monitoring", "workflow"]
            join_strategy: "performance_optimized"
            priority: "high"
            use_cases: ["renewal_processing", "compliance_tracking"]

    columns:
      - name: license_pk
        description: "Primary key for license"
        data_type: varchar
        meta:
          mxcp:
            column_role: "primary_key"
            business_name: "License Identifier"
      
      - name: business_id
        description: "Reference to business entity"
        data_type: varchar
        meta:
          mxcp:
            column_role: "foreign_key"
            references: "dim_businesses.business_id"
            business_name: "Business Reference"
```

### 2.2 Related Entity: Violations

```yaml
  - name: fact_violations
    meta:
      mxcp:
        entity_type: "fact"
        business_domain: "compliance"
        data_freshness: "real-time"
        relationships:
          - target: "dim_licenses"
            type: "many-to-one"
            join_key: "license_pk"
            business_context: "license_violations"
        
        tool_patterns: ["analytics", "monitoring", "compliance"]
        
        performance:
          materialization_hint: "incremental"
          partition_key: "violation_date"
          index_recommendations: ["license_pk", "violation_date", "severity"]
    
    columns:
      - name: violation_id
        description: "Unique violation identifier"
        data_type: varchar
        meta:
          mxcp:
            column_role: "primary_key"
      
      - name: license_pk
        description: "Reference to license"
        data_type: varchar
        meta:
          mxcp:
            column_role: "foreign_key"
            references: "dim_licenses.license_pk"
      
      - name: violation_date
        description: "Date of violation"
        data_type: date
        meta:
          mxcp:
            column_role: "temporal_key"
            business_name: "Violation Date"
      
      - name: severity
        description: "Violation severity level"
        data_type: varchar
        meta:
          mxcp:
            column_role: "categorical"
            business_name: "Severity Level"
        tests:
          - accepted_values:
              values: ["Critical", "Major", "Minor", "Warning"]
```

### 2.3 Related Entity: Businesses

```yaml
  - name: dim_businesses
    meta:
      mxcp:
        entity_type: "primary"
        business_domain: "business_registry"
        data_freshness: "weekly"
        relationships:
          - target: "dim_licenses"
            type: "one-to-many"
            join_key: "business_id"
            business_context: "business_licenses"
        
        tool_patterns: ["search", "analytics"]
    
    columns:
      - name: business_id
        description: "Unique business identifier"
        data_type: varchar
        meta:
          mxcp:
            column_role: "primary_key"
      
      - name: business_name_en
        description: "Business name in English"
        data_type: varchar
        meta:
          mxcp:
            column_role: "descriptive"
            business_name: "Business Name"
      
      - name: establishment_date
        description: "Business establishment date"
        data_type: date
        meta:
          mxcp:
            column_role: "temporal"
            business_name: "Establishment Date"
```

## 3. Generated Multi-Model Tools

### 3.1 Compliance Monitoring Tool

**Generated**: `monitor_license_compliance.yml`

```yaml
mxcp: "1.0.0"
tool:
  name: monitor_license_compliance
  description: |
    Monitor license compliance across violations, inspections, and business status.
    Provides comprehensive compliance overview with risk assessment.
  parameters:
    # License filters
    - name: license_status
      type: string
      enum: ["Active", "Expired", "Suspended", "Current", null]
      description: "Filter by license status"
      default: null
    
    - name: emirate
      type: string
      enum: ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain", null]
      description: "Filter by emirate"
      default: null
    
    # Compliance filters
    - name: compliance_status
      type: string
      enum: ["Compliant", "At_Risk", "Non_Compliant", "Critical", null]
      description: "Filter by compliance status"
      default: null
    
    - name: has_violations
      type: boolean
      description: "Include only licenses with violations"
      default: null
    
    - name: violation_severity
      type: string
      enum: ["Critical", "Major", "Minor", "Warning", null]
      description: "Filter by highest violation severity"
      default: null
    
    - name: violations_in_last_days
      type: integer
      description: "Filter by violations in last N days"
      default: null
    
    # Temporal filters
    - name: expiry_within_days
      type: integer
      description: "Find licenses expiring within N days"
      default: 90
    
    - name: last_inspection_days_ago
      type: integer
      description: "Filter by days since last inspection"
      default: null
    
    # Business context filters
    - name: business_type
      type: string
      description: "Filter by business legal type"
      default: null
    
    - name: business_age_years
      type: integer
      description: "Filter by business age in years"
      default: null
    
    # Output options
    - name: include_violation_details
      type: boolean
      description: "Include detailed violation information"
      default: false
    
    - name: include_inspection_history
      type: boolean
      description: "Include inspection history"
      default: false
    
    - name: include_business_details
      type: boolean
      description: "Include business owner information"
      default: true
    
    - name: risk_assessment_level
      type: string
      enum: ["basic", "detailed", "comprehensive"]
      description: "Level of risk assessment to include"
      default: "basic"
    
    - name: limit
      type: integer
      description: "Maximum number of records to return"
      default: 100
  
  required: []
  
  return:
    type: array
    items:
      type: object
      properties:
        license_pk:
          type: string
          description: "License identifier"
        bl_name_en:
          type: string
          description: "Business name"
        emirate_name_en:
          type: string
          description: "Emirate"
        bl_status_en:
          type: string
          description: "License status"
        compliance_status:
          type: string
          description: "Overall compliance status"
        risk_score:
          type: number
          description: "Calculated risk score (0-100)"
        violation_count:
          type: integer
          description: "Total number of violations"
        highest_violation_severity:
          type: string
          description: "Highest violation severity level"
        latest_violation_date:
          type: string
          format: date
          description: "Date of most recent violation"
        days_until_expiry:
          type: integer
          description: "Days until license expires"
        last_inspection_date:
          type: string
          format: date
          description: "Date of last inspection"
        business_establishment_date:
          type: string
          format: date
          description: "Business establishment date"
  
  source:
    file: "../sql/monitor_license_compliance.sql"
  
  enabled: true
  
  tests:
    - name: test_compliance_monitoring_basic
      description: "Basic compliance monitoring functionality"
      arguments:
        - key: "emirate"
          value: "Dubai"
        - key: "limit"
          value: 10
      result: "success"
    
    - name: test_compliance_high_risk
      description: "Find high-risk licenses"
      arguments:
        - key: "compliance_status"
          value: "Critical"
        - key: "include_violation_details"
          value: true
      result: "success"
    
    - name: test_expiring_licenses
      description: "Find licenses expiring soon"
      arguments:
        - key: "expiry_within_days"
          value: 30
        - key: "has_violations"
          value: true
      result: "success"
```

### 3.2 Generated SQL for Compliance Tool

**Generated**: `sql/monitor_license_compliance.sql`

```sql
WITH compliance_base AS (
  SELECT 
    l.license_pk,
    l.bl,
    l.bl_name_en,
    l.emirate_name_en,
    l.bl_status_en,
    l.bl_exp_date_d,
    l.bl_est_date_d,
    b.business_name_en,
    b.establishment_date as business_establishment_date,
    b.business_legal_type_en,
    
    -- Violation metrics
    COUNT(v.violation_id) as violation_count,
    MAX(v.violation_date) as latest_violation_date,
    MAX(v.severity) as highest_violation_severity,
    COUNT(CASE WHEN v.violation_date >= CURRENT_DATE - INTERVAL $violations_in_last_days DAY 
          THEN 1 END) as recent_violations,
    
    -- Inspection metrics  
    MAX(i.inspection_date) as last_inspection_date,
    COUNT(i.inspection_id) as total_inspections,
    
    -- Calculated fields
    DATEDIFF(l.bl_exp_date_d, CURRENT_DATE) as days_until_expiry,
    DATEDIFF(CURRENT_DATE, b.establishment_date) / 365.25 as business_age_years,
    DATEDIFF(CURRENT_DATE, MAX(i.inspection_date)) as days_since_last_inspection
    
  FROM dim_licenses_v1 l
  LEFT JOIN fact_violations_v1 v ON l.license_pk = v.license_pk
  LEFT JOIN fact_inspections_v1 i ON l.license_pk = i.license_pk
  LEFT JOIN dim_businesses_v1 b ON l.business_id = b.business_id
  
  WHERE 1=1
    AND ($license_status IS NULL OR l.bl_status_en = $license_status)
    AND ($emirate IS NULL OR l.emirate_name_en = $emirate)
    AND ($business_type IS NULL OR b.business_legal_type_en = $business_type)
    AND ($expiry_within_days IS NULL OR 
         l.bl_exp_date_d BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL $expiry_within_days DAY)
    AND ($last_inspection_days_ago IS NULL OR 
         DATEDIFF(CURRENT_DATE, MAX(i.inspection_date)) <= $last_inspection_days_ago)
  
  GROUP BY l.license_pk, b.business_id
),

risk_assessment AS (
  SELECT 
    *,
    -- Calculate compliance status
    CASE 
      WHEN violation_count = 0 AND days_until_expiry > 90 THEN 'Compliant'
      WHEN violation_count = 0 AND days_until_expiry BETWEEN 30 AND 90 THEN 'At_Risk'
      WHEN violation_count > 0 AND highest_violation_severity IN ('Critical', 'Major') THEN 'Critical'
      WHEN violation_count > 0 THEN 'Non_Compliant'
      ELSE 'At_Risk'
    END as compliance_status,
    
    -- Calculate risk score (0-100)
    LEAST(100, 
      (violation_count * 10) + 
      (CASE highest_violation_severity 
        WHEN 'Critical' THEN 40
        WHEN 'Major' THEN 25
        WHEN 'Minor' THEN 10
        WHEN 'Warning' THEN 5
        ELSE 0 
      END) +
      (CASE 
        WHEN days_until_expiry < 0 THEN 30  -- Expired
        WHEN days_until_expiry < 30 THEN 20 -- Expiring soon
        WHEN days_until_expiry < 90 THEN 10 -- Expiring within 3 months
        ELSE 0
      END) +
      (CASE 
        WHEN days_since_last_inspection > 365 THEN 15 -- No inspection in a year
        WHEN days_since_last_inspection > 180 THEN 10 -- No inspection in 6 months
        ELSE 0
      END)
    ) as risk_score
    
  FROM compliance_base
),

final_filtered AS (
  SELECT *
  FROM risk_assessment
  WHERE 1=1
    AND ($compliance_status IS NULL OR compliance_status = $compliance_status)
    AND ($has_violations IS NULL OR 
         ($has_violations = true AND violation_count > 0) OR
         ($has_violations = false AND violation_count = 0))
    AND ($violation_severity IS NULL OR highest_violation_severity = $violation_severity)
    AND ($violations_in_last_days IS NULL OR recent_violations > 0)
    AND ($business_age_years IS NULL OR business_age_years >= $business_age_years)
)

SELECT 
  license_pk,
  bl,
  bl_name_en,
  emirate_name_en,
  bl_status_en,
  compliance_status,
  risk_score,
  violation_count,
  highest_violation_severity,
  latest_violation_date,
  days_until_expiry,
  last_inspection_date,
  
  -- Conditional details based on parameters
  CASE WHEN $include_business_details = true THEN business_name_en ELSE NULL END as business_name_en,
  CASE WHEN $include_business_details = true THEN business_establishment_date ELSE NULL END as business_establishment_date,
  CASE WHEN $include_business_details = true THEN business_legal_type_en ELSE NULL END as business_legal_type_en,
  
  -- Risk assessment details based on level
  CASE WHEN $risk_assessment_level IN ('detailed', 'comprehensive') THEN recent_violations ELSE NULL END as recent_violations,
  CASE WHEN $risk_assessment_level = 'comprehensive' THEN total_inspections ELSE NULL END as total_inspections,
  CASE WHEN $risk_assessment_level = 'comprehensive' THEN days_since_last_inspection ELSE NULL END as days_since_last_inspection

FROM final_filtered
ORDER BY 
  -- Priority order: Critical compliance issues first
  CASE compliance_status 
    WHEN 'Critical' THEN 1
    WHEN 'Non_Compliant' THEN 2  
    WHEN 'At_Risk' THEN 3
    WHEN 'Compliant' THEN 4
  END,
  risk_score DESC,
  days_until_expiry ASC,
  latest_violation_date DESC
  
LIMIT $limit
```

### 3.3 Business Intelligence Tool

**Generated**: `analyze_business_licensing_trends.yml`

```yaml
mxcp: "1.0.0"
tool:
  name: analyze_business_licensing_trends
  description: |
    Analyze licensing trends with business context, violations, and compliance patterns.
    Provides insights for business intelligence and regulatory planning.
  parameters:
    - name: analysis_type
      type: string
      enum: ["licensing_patterns", "compliance_trends", "business_growth", "violation_analysis", "renewal_patterns"]
      description: "Type of analysis to perform"
      default: "licensing_patterns"
    
    - name: time_granularity
      type: string
      enum: ["daily", "weekly", "monthly", "quarterly", "yearly"]
      description: "Time granularity for trend analysis"
      default: "monthly"
    
    - name: breakdown_dimension
      type: string
      enum: ["emirate", "business_type", "license_type", "authority", "compliance_status"]
      description: "Primary dimension to break down results by"
      default: "emirate"
    
    - name: secondary_dimension
      type: string
      enum: ["none", "business_type", "license_type", "compliance_status", "violation_severity"]
      description: "Secondary dimension for cross-tabulation"
      default: "none"
    
    - name: date_range_start
      type: string
      format: date
      description: "Analysis start date (YYYY-MM-DD)"
      default: null
    
    - name: date_range_end
      type: string
      format: date
      description: "Analysis end date (YYYY-MM-DD)"
      default: null
    
    - name: include_violations
      type: boolean
      description: "Include violation data in analysis"
      default: true
    
    - name: include_business_context
      type: boolean
      description: "Include business establishment and growth context"
      default: true
    
    - name: min_sample_size
      type: integer
      description: "Minimum sample size for statistical significance"
      default: 10
  
  source:
    file: "../sql/analyze_business_licensing_trends.sql"
```

## 4. Implementation Changes Required

### 4.1 Enhanced Semantic Analyzer

```python
# mxcp_generator/analyzers/semantic_analyzer.py

@dataclass
class EnhancedBusinessEntity:
    """Extended business entity with multi-model support"""
    name: str
    primary_model: DbtModel
    columns: List[ColumnInfo]
    related_models: List[DbtModel] = field(default_factory=list)
    relationships: Dict[str, RelationshipInfo] = field(default_factory=dict)
    business_description: Optional[str] = None
    
    # New fields for multi-model support
    entity_type: str = "primary"  # primary, fact, bridge, lookup
    business_domain: str = ""
    multi_model_scenarios: List[MultiModelScenario] = field(default_factory=list)
    performance_hints: Dict[str, Any] = field(default_factory=dict)

class EnhancedSemanticAnalyzer(SemanticAnalyzer):
    """Extended analyzer with meta tag support"""
    
    def extract_multi_model_scenarios(self, entities: Dict[str, BusinessEntity]) -> List[MultiModelScenario]:
        """Extract multi-model scenarios from meta tags"""
        scenarios = []
        
        for entity_name, entity in entities.items():
            meta_mxcp = entity.primary_model.meta.get('mxcp', {})
            
            for scenario_def in meta_mxcp.get('multi_model_scenarios', []):
                scenario = MultiModelScenario(
                    name=scenario_def['name'],
                    description=scenario_def['description'],
                    primary_entity=entity,
                    related_entities=self._resolve_related_entities(
                        scenario_def['includes'], 
                        entities
                    ),
                    tool_patterns=scenario_def.get('tool_patterns', []),
                    join_strategy=scenario_def.get('join_strategy', 'balanced'),
                    priority=scenario_def.get('priority', 'medium'),
                    business_context=scenario_def.get('business_context', '')
                )
                scenarios.append(scenario)
        
        return scenarios
```

### 4.2 Multi-Model Tool Generator

```python
# mxcp_generator/generators/multi_model_tool_generator.py

class MultiModelToolGenerator:
    """Generates sophisticated multi-model tools"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.sql_generator = MultiModelSQLGenerator()
        
    def generate_tools_for_scenarios(
        self, 
        scenarios: List[MultiModelScenario]
    ) -> List[Dict[str, Any]]:
        """Generate tools for all multi-model scenarios"""
        tools = []
        
        for scenario in scenarios:
            if "compliance" in scenario.tool_patterns:
                tools.append(self._generate_compliance_monitoring_tool(scenario))
            
            if "analytics" in scenario.tool_patterns:
                tools.append(self._generate_analytics_tool(scenario))
            
            if "monitoring" in scenario.tool_patterns:
                tools.append(self._generate_monitoring_tool(scenario))
        
        return tools
```

## 5. Benefits of This Implementation

### 5.1 Business Value
- **Comprehensive Compliance Monitoring**: Single tool to assess license compliance across multiple data sources
- **Risk Assessment**: Automated risk scoring based on violations, inspections, and expiry dates
- **Business Intelligence**: Rich analytics combining licensing, business, and compliance data
- **Operational Efficiency**: Reduced manual work for compliance officers and analysts

### 5.2 Technical Benefits
- **Maintainability**: Meta tags in dbt schema files provide single source of truth
- **Performance**: Optimized joins and materialization strategies
- **Scalability**: Framework can handle additional entities (permits, inspections, payments)
- **Quality**: Automated test generation ensures reliability

### 5.3 Developer Experience
- **Declarative Configuration**: Define relationships and scenarios in YAML
- **Automatic Generation**: Complex multi-model tools generated automatically
- **Validation**: Built-in validation for meta tag consistency
- **Documentation**: Self-documenting through meta tags and generated descriptions

This implementation example demonstrates how meta tags enable sophisticated multi-model tool generation while maintaining the simplicity and power of our existing framework. 