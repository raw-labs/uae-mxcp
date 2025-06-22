# MCP Resource Best Practices

## Overview

According to the official Model Context Protocol documentation, **resources** are a core primitive that allow servers to expose data and content that can be read by clients and used as context for LLM interactions. They are fundamentally different from **tools** in their design philosophy and use cases.

## Key Principle: Application-Controlled vs Model-Controlled

The most important distinction is:

- **Resources** are **application-controlled** - The client application decides how and when to use them
- **Tools** are **model-controlled** - The AI model can invoke them autonomously

This fundamental difference drives when you should create each type.

## When to Create MCP Resources

### 1. **Static or Semi-Static Content**
Resources are ideal for data that doesn't change frequently or can be cached:

✅ **Good Resource Examples:**
- Configuration files
- Documentation
- Reference data
- Product catalogs
- User profiles
- Organization hierarchies

❌ **Bad Resource Examples:**
- Real-time stock prices (use tools)
- Dynamic calculations (use tools)
- Data requiring complex parameters (use tools)

### 2. **Pre-computed Views and Summaries**
When you have expensive computations that can be cached:

✅ **Create Resources for:**
- Daily/hourly aggregated metrics
- Pre-computed reports
- Materialized views
- Summary statistics
- Active record subsets

**Example from your project:**
```yaml
# This SHOULD be a resource (pre-computed active licenses)
resource:
  name: active_licenses
  description: Currently active business licenses
```

### 3. **Discoverable Content Libraries**
Resources excel at making content discoverable:

✅ **Good Use Cases:**
- Knowledge base articles
- Template libraries
- Code snippets
- Standard operating procedures
- FAQ collections

### 4. **Context Enhancement**
Resources provide persistent context across conversations:

✅ **Create Resources for:**
- User preferences
- Session history
- Domain-specific knowledge
- Business rules
- Glossaries and definitions

## When NOT to Create Resources (Use Tools Instead)

### 1. **Dynamic Queries**
If the data requires parameters or filtering:

❌ **Use Tools for:**
- Search operations
- Filtered queries
- Date range selections
- Conditional logic

### 2. **Actions and Mutations**
Resources are read-only by design:

❌ **Never Use Resources for:**
- Creating records
- Updating data
- Deleting items
- Triggering workflows

### 3. **Real-time Data**
When freshness is critical:

❌ **Use Tools for:**
- Live metrics
- Current prices
- Real-time status
- Streaming data

## Resource Design Patterns

### Pattern 1: Active Records Resource
```yaml
# Good: Pre-filtered subset of frequently needed data
resource:
  name: active_customers
  uri: "db://customers/active"
  description: "Customers with active subscriptions"
  mimeType: "application/json"
```

### Pattern 2: Summary Statistics Resource
```yaml
# Good: Pre-computed metrics that are expensive to calculate
resource:
  name: license_summary_by_emirate
  uri: "analytics://licenses/by-emirate"
  description: "License counts and metrics grouped by emirate"
  mimeType: "application/json"
```

### Pattern 3: Reference Data Resource
```yaml
# Good: Static reference data used across many queries
resource:
  name: business_types_catalog
  uri: "catalog://business-types"
  description: "Valid business types and their descriptions"
  mimeType: "application/json"
```

## Resource vs Tool Decision Matrix

| Criteria | Resource | Tool |
|----------|----------|------|
| **Data Changes** | Rarely/Scheduled | Frequently/Real-time |
| **Parameters** | None/Few | Many/Complex |
| **Operation** | Read-only | Read/Write |
| **Computation** | Pre-computed | On-demand |
| **Access Pattern** | Browse/Discover | Search/Filter |
| **Context** | Persistent | Transient |
| **Control** | Application | AI Model |

## Implementation Best Practices

### 1. **URI Design**
Use clear, hierarchical URIs:
```
protocol://category/subcategory/identifier

Examples:
- file:///config/app-settings.json
- db://customers/active/premium
- analytics://reports/monthly/2024-01
```

### 2. **Metadata**
Always include:
- Clear descriptions
- MIME types
- Size estimates
- Last updated timestamps

### 3. **Security Considerations**
- Validate all resource URIs
- Implement access controls
- Sanitize file paths
- Consider data masking for sensitive content
- Audit resource access

## Real-World Examples

### Example 1: Customer Service Context
```yaml
# RESOURCE: Customer's order history (static context)
resource:
  name: customer_order_history
  uri: "crm://customer/12345/orders"
  description: "Last 10 orders for customer"
  
# TOOL: Check current order status (dynamic query)
tool:
  name: check_order_status
  description: "Get real-time status of an order"
  parameters:
    - order_id
```

### Example 2: Analytics Dashboard
```yaml
# RESOURCE: Pre-computed daily metrics
resource:
  name: daily_sales_summary
  uri: "analytics://sales/daily/2024-01-15"
  description: "Sales metrics for the day"
  
# TOOL: Custom date range analysis
tool:
  name: analyze_sales
  description: "Analyze sales for custom date range"
  parameters:
    - start_date
    - end_date
    - group_by
```

## Common Pitfalls to Avoid

1. **Creating resources for dynamic queries** - Use tools instead
2. **Over-granular resources** - Combine related data
3. **Missing metadata** - Makes resources hard to discover
4. **Ignoring security** - Resources need access controls too

## Conclusion

Resources in MCP are best suited for:
- ✅ Static or cacheable content
- ✅ Pre-computed views and summaries  
- ✅ Reference data and catalogs
- ✅ Persistent context across sessions

Use tools instead for:
- ❌ Dynamic queries with parameters
- ❌ Real-time data access
- ❌ Actions and mutations
- ❌ Complex business logic

The key is to think about **who controls the access** - if the application should decide when to use the data, make it a resource. If the AI should be able to fetch it on-demand, make it a tool. 