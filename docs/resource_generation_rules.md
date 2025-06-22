# Resource Generation Rules

Resources in MXCP are pre-computed, cached views that provide optimized data access for common queries. The tool generation framework creates resources automatically based on specific patterns in your dbt models.

## Types of Resources Generated

### 1. Active Records Resource (`active_<entity>`)

**Created when:**
- Entity has **status fields** (BUSINESS_STATUS classification) with enum values containing active-like terms
- OR entity has **temporal fields** containing expiry/end dates

**Triggers:**
- Status field with enum values containing: `active`, `valid`, `enabled`, `current` 
- Boolean fields with `is_` or `has_` prefix
- Date fields containing: `expir`, `exp`, `end` in the name (for future date filtering)

**Purpose:**
- Pre-filters to only active/current records
- Refreshes every 6 hours
- Optimizes queries that frequently filter by status

**Example SQL:**
```sql
SELECT *
FROM {{ schema }}.dim_licenses_v1
WHERE bl_status_en IN ('Active', 'Valid') 
  AND bl_exp_date_d > CURRENT_DATE
ORDER BY bl_est_date_d DESC
```

### 2. Summary Resource (`<entity>_metrics_summary`)

**Created when:**
- Entity has **METRIC fields** (numeric aggregatable data)
- AND entity has **categorical fields** with enum values (< 20 distinct values)

**Triggers:**
- METRIC classification fields (revenue, count, amount, etc.)
- CATEGORICAL fields with known distinct values for grouping

**Purpose:**
- Pre-computed aggregations by key dimensions
- Daily refresh schedule
- Optimizes analytical queries

**Example SQL:**
```sql
SELECT 
  emirate_name_en,
  COUNT(*) as record_count,
  SUM(license_fee) as total_license_fee,
  AVG(license_fee) as avg_license_fee,
  COUNT(DISTINCT CASE WHEN license_fee > 0 THEN license_pk END) as count_with_license_fee
FROM {{ schema }}.dim_licenses_v1
GROUP BY emirate_name_en
ORDER BY COUNT(*) DESC
```

### 3. Overview Resource (`business_entities_overview`)

**Created when:**
- Multiple business entities exist (> 1)

**Purpose:**
- Cross-entity summary with record counts
- Latest record dates for each entity
- 12-hour refresh schedule

## Current Project Status

For the UAE licenses project, **no resources are currently generated** because:

1. ❌ **Status fields lack enum values**: `bl_status_en` has no defined enum values in dbt schema
2. ❌ **Expiry field naming**: Field is `bl_exp_date` but generator looks for `expir`/`end` 
3. ❌ **No metric fields**: No numeric fields classified as METRIC
4. ❌ **No categorical enums**: Categorical fields have no enum values defined
5. ❌ **Single entity**: Only one business entity (licenses)

## How to Enable Resource Generation

### Option 1: Add Enum Values to Schema
Add `accepted_values` tests to your dbt schema.yml:

```yaml
# models/marts/schema.yml
columns:
  - name: bl_status_en
    tests:
      - accepted_values:
          values: ['Active', 'Expired', 'Suspended', 'Cancelled']
  
  - name: emirate_name_en  
    tests:
      - accepted_values:
          values: ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Fujairah', 'Ras Al Khaimah', 'Umm Al Quwain']
```

### Option 2: Fix Expiry Field Detection
Update the resource generator to recognize `exp` pattern:

```python
# In resource_generator.py
if 'expir' in col.name.lower() or 'end' in col.name.lower() or 'exp' in col.name.lower():
    status_conditions.append(f"{col.name} > CURRENT_DATE")
```

### Option 3: Add Metric Fields  
Classify numeric fields as METRIC in the semantic analyzer:

```python
# Add to CLASSIFICATION_PATTERNS in semantic_analyzer.py
ColumnClassification.METRIC: [
    r'.*_count$', r'.*_amount$', r'.*_fee$', r'.*_total$',
    r'.*_revenue$', r'.*_cost$', r'.*_value$'
]
```

### Option 4: Create Additional Entities
Add more dbt models (e.g., `dim_authorities`, `fact_renewals`) to trigger overview resource.

## Resource Benefits

When resources are generated, they provide:

- ⚡ **Faster queries** - Pre-computed results
- 🔄 **Automatic refresh** - Always up-to-date
- 📊 **Analytics optimization** - Pre-aggregated metrics  
- 🎯 **Common patterns** - Active records, summaries
- 🔍 **Query optimization** - Reduced load on main tables 