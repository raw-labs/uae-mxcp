"""
Tool generator for creating MXCP tool definitions from business entities
"""

import logging
from typing import Dict, List, Any, Optional
from ..analyzers import BusinessEntity, ColumnClassification, ColumnInfo

logger = logging.getLogger(__name__)


class ToolGenerator:
    """
    Generates MXCP tool definitions from business entities
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.version = "1.0.0"
        self.sql_queries = {}
    
    def generate_for_entity(self, entity: BusinessEntity) -> List[Dict[str, Any]]:
        """Generate tools for a business entity"""
        tools = []
        
        # Always generate search tool
        search_tool = self._generate_search_tool(entity)
        if search_tool:
            tools.append(search_tool)
        
        # Generate aggregation tool if applicable
        if self._has_categorical_fields(entity):
            agg_tool = self._generate_aggregation_tool(entity)
            if agg_tool:
                tools.append(agg_tool)
        
        # Generate time series tool if temporal fields exist
        if self._has_temporal_fields(entity):
            ts_tool = self._generate_timeseries_tool(entity)
            if ts_tool:
                tools.append(ts_tool)
        
        # Generate geographic tool if geo fields exist
        if self._has_geographic_fields(entity):
            geo_tool = self._generate_geographic_tool(entity)
            if geo_tool:
                tools.append(geo_tool)
        
        # Generate categorical values tool
        cat_tool = self._generate_categorical_tool(entity)
        if cat_tool:
            tools.append(cat_tool)
        
        logger.info(f"Generated {len(tools)} tools for entity {entity.name}")
        return tools
    
    def get_sql_queries(self) -> Dict[str, str]:
        """Get all generated SQL queries"""
        return self.sql_queries
    
    def _has_categorical_fields(self, entity: BusinessEntity) -> bool:
        """Check if entity has categorical fields"""
        return any(
            col.classification in [ColumnClassification.CATEGORICAL, ColumnClassification.BUSINESS_STATUS]
            or col.enum_values
            for col in entity.columns
        )
    
    def _generate_search_tool(self, entity: BusinessEntity) -> Optional[Dict[str, Any]]:
        """Generate comprehensive search tool for an entity"""
        tool_name = f"find_{entity.name}"
        description = f"Search and filter {entity.name} records"
        
        # Generate parameters for all columns
        parameters = []
        where_conditions = []
        
        for col in entity.columns:
            param_name = self._to_business_name(col.name)
            
            if col.classification == ColumnClassification.TEMPORAL or col.data_type.lower() == 'date':
                # Add from/to parameters for dates
                parameters.extend([
                    {
                        "name": f"{param_name}From",
                        "type": "string",
                        "format": "date",
                        "description": f"Filter {col.name} from date (YYYY-MM-DD)",
                        "default": None
                    },
                    {
                        "name": f"{param_name}To",
                        "type": "string",
                        "format": "date",
                        "description": f"Filter {col.name} to date (YYYY-MM-DD)",
                        "default": None
                    }
                ])
                
                # Use the _d version for date fields if it exists
                date_field = col.name if col.data_type.lower() == 'date' else f"{col.name}_d"
                where_conditions.extend([
                    f"  AND (${param_name}From IS NULL OR {date_field} >= ${param_name}From::DATE)",
                    f"  AND (${param_name}To IS NULL OR {date_field} <= ${param_name}To::DATE)"
                ])
            
            elif col.data_type.lower() in ['integer', 'bigint', 'numeric', 'decimal', 'float', 'double']:
                # Add min/max for numeric fields
                parameters.extend([
                    {
                        "name": f"{param_name}Min",
                        "type": "number",
                        "description": f"Minimum value for {col.name}",
                        "default": None
                    },
                    {
                        "name": f"{param_name}Max",
                        "type": "number",
                        "description": f"Maximum value for {col.name}",
                        "default": None
                    }
                ])
                where_conditions.extend([
                    f"  AND (${param_name}Min IS NULL OR {col.name} >= ${param_name}Min)",
                    f"  AND (${param_name}Max IS NULL OR {col.name} <= ${param_name}Max)"
                ])
            
            else:
                # Text/categorical fields
                param_def = {
                    "name": param_name,
                    "type": "string",
                    "description": f"Filter by {col.name}"
                }
                
                # Add enum values if available (include null for optional parameters)
                if col.enum_values:
                    param_def["enum"] = col.enum_values + [None]
                
                # Add default null to make parameter optional
                param_def["default"] = None
                
                parameters.append(param_def)
                
                # Use exact match for enums/flags, partial match for text
                if col.enum_values or col.classification in [ColumnClassification.CATEGORICAL, ColumnClassification.BUSINESS_STATUS]:
                    where_conditions.append(f"  AND (${param_name} IS NULL OR {col.name} = ${param_name})")
                else:
                    where_conditions.append(f"  AND (${param_name} IS NULL OR {col.name} ILIKE '%' || ${param_name} || '%')")
        
        # Add multi-model embed parameter
        embed_options = self._get_embed_options(entity)
        if embed_options:
            parameters.append({
                "name": "embed",
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": embed_options
                },
                "description": "Related entities to embed in results (lazy loading)",
                "default": []
            })
        
        # Add pagination parameters
        parameters.extend([
            {
                "name": "limit",
                "type": "integer",
                "description": "Maximum number of records to return",
                "default": 100
            },
            {
                "name": "offset",
                "type": "integer",
                "description": "Number of records to skip",
                "default": 0
            }
        ])
        
        # Build SQL with conditional embedding
        base_sql = f"""
SELECT *
FROM {entity.primary_model.name}_v1
WHERE 1=1
{chr(10).join(where_conditions)}
ORDER BY {self._get_default_order_column(entity)} DESC
LIMIT $limit
OFFSET $offset
        """.strip()
        
        # Generate enhanced SQL with embedding support
        sql = self._generate_embedding_sql(entity, base_sql)
        
        # Store SQL separately
        self.sql_queries[tool_name] = sql
        
        return_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": self._generate_return_properties(entity)
            }
        }
        
        tool_def = {
            "mxcp": self.version,
            "tool": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
                "required": [],  # No required parameters for search
                "return": return_schema,
                "source": {
                    "file": f"../sql/{tool_name}.sql"
                },
                "enabled": True
            }
        }
        
        return tool_def
    
    def _generate_analytics_tool(self, entity: BusinessEntity) -> Optional[Dict[str, Any]]:
        """Generate analytics tool for entities with metrics"""
        metric_fields = [
            col for col in entity.columns
            if col.classification == ColumnClassification.METRIC
        ]
        
        if not metric_fields:
            return None
        
        tool_name = f"analyze_{entity.name}_metrics"
        description = f"Analyze metrics and aggregations for {entity.name}"
        
        # Find grouping dimensions
        dimension_fields = [
            col for col in entity.columns
            if col.classification in [
                ColumnClassification.CATEGORICAL,
                ColumnClassification.GEOGRAPHIC,
                ColumnClassification.TEMPORAL
            ]
        ]
        
        parameters = []
        
        # Add grouping parameter
        if dimension_fields:
            parameters.append({
                "name": "group_by",
                "type": "string",
                "description": "Dimension to group results by",
                "enum": [self._to_business_name(f.name) for f in dimension_fields[:5]],
            })
        
        # Add time period parameter if temporal fields exist
        temporal_fields = [
            col for col in entity.columns
            if col.classification == ColumnClassification.TEMPORAL
        ]
        
        if temporal_fields:
            parameters.append({
                "name": "time_period",
                "type": "string",
                "description": "Time period for analysis",
                "enum": ["day", "week", "month", "quarter", "year"],
                "default": "month",
            })
        
        # Build SQL with aggregations
        metric_aggregations = []
        for field in metric_fields[:5]:  # Limit to 5 metrics
            agg_name = self._to_business_name(field.name)
            metric_aggregations.append(
                f"  SUM({field.name}) as total_{agg_name},\n"
                f"  AVG({field.name}) as avg_{agg_name},\n"
                f"  MAX({field.name}) as max_{agg_name}"
            )
        
        # For now, just generate a simple aggregation query without dynamic grouping
        sql = f"""
SELECT
  COUNT(*) as record_count,
{','.join(metric_aggregations)}
FROM {entity.primary_model.name}_v1
        """.strip()
        
        return {
            "mxcp": self.version,
            "tool": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
                "required": [],  # No required parameters for analytics
                "return": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": self._generate_return_properties(entity)  # Properties inside items
                    }
                },
                "source": {
                    "code": sql
                },
                "enabled": True
            }
        }
    
    def _generate_relationship_tool(self, entity: BusinessEntity, rel_info: Any) -> Optional[Dict[str, Any]]:
        """Generate tool for navigating relationships"""
        tool_name = f"get_{entity.name}_with_{rel_info.to_entity}"
        description = f"Get {entity.name} records with related {rel_info.to_entity} data"
        
        # Build join query
        join_conditions = []
        for from_col, to_col in rel_info.join_keys:
            join_conditions.append(f"a.{from_col} = b.{to_col}")
        
        sql = f"""
SELECT 
  a.*,
  b.* EXCLUDE ({', '.join([col for _, col in rel_info.join_keys])})
FROM {entity.primary_model.name}_v1 a
LEFT JOIN dim_{rel_info.to_entity}_v1 b
  ON {' AND '.join(join_conditions)}
WHERE 1=1
  AND ($id IS NULL OR a.{self._get_primary_key(entity)} = $id)
LIMIT 100
        """.strip()
        
        return {
            "mxcp": self.version,
            "tool": {
                "name": tool_name,
                "description": description,
                "parameters": [{
                    "name": "id",
                    "type": "string",
                    "description": f"{entity.name} identifier",
                }],
                "return": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    }
                },
                "source": {
                    "code": sql
                },
                "enabled": True
            }
        }
    
    def _has_status_fields(self, entity: BusinessEntity) -> bool:
        """Check if entity has status fields"""
        return any(
            col.classification == ColumnClassification.BUSINESS_STATUS
            for col in entity.columns
        )
    
    def _has_metric_fields(self, entity: BusinessEntity) -> bool:
        """Check if entity has metric fields"""
        return any(
            col.classification == ColumnClassification.METRIC
            for col in entity.columns
        )
    
    def _to_business_name(self, technical_name: str) -> str:
        """Convert technical column name to business-friendly name"""
        # Remove common prefixes/suffixes
        name = technical_name.lower()
        
        # Check if this has a language suffix we should preserve
        lang_suffix = ""
        if name.endswith('_en'):
            lang_suffix = "En"
            name = name[:-3]
        elif name.endswith('_ar'):
            lang_suffix = "Ar"
            name = name[:-3]
        
        # Remove common entity prefixes (generic patterns)
        for prefix in ['dim_', 'fact_', 'bridge_']:
            if name.startswith(prefix):
                name = name[len(prefix):]
        
        # Remove common suffixes (but not language ones)
        for suffix in ['_id', '_key']:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
        
        # Convert underscores to spaces and capitalize
        result = name.replace('_', ' ').title().replace(' ', '')
        
        # Add back language suffix if present
        return result + lang_suffix
    
    def _get_default_order_column(self, entity: BusinessEntity) -> str:
        """Get default column for ordering results"""
        # Try to find a creation date
        for col in entity.columns:
            if col.classification == ColumnClassification.TEMPORAL:
                if any(keyword in col.name.lower() for keyword in ['created', 'issue']):
                    return col.name
        
        # Fall back to primary key
        return self._get_primary_key(entity)
    
    def _get_primary_key(self, entity: BusinessEntity) -> str:
        """Find the primary key field for the entity"""
        # Look for common primary key patterns
        for col in entity.columns:
            col_lower = col.name.lower()
            
            # Common PK patterns
            if col_lower in ['id', 'pk', 'key']:
                return col.name
            
            # Entity-specific patterns like table_pk, table_id
            entity_lower = entity.name.lower()
            if col_lower in [f"{entity_lower}_pk", f"{entity_lower}_id", f"{entity_lower}_key"]:
                return col.name
            
            # Generic patterns
            if col_lower.endswith('_pk') or col_lower.endswith('_id') or col_lower.endswith('_key'):
                return col.name
        
        # Fallback to first identifier field
        for col in entity.columns:
            if col.classification == ColumnClassification.IDENTIFIER:
                return col.name
        
        # Last resort - use first column
        return entity.columns[0].name if entity.columns else 'id'
    
    def _generate_common_filter_parameters(self, entity: BusinessEntity, limit: int = 10) -> List[Dict[str, Any]]:
        """Generate common filter parameters for tools"""
        parameters = []
        
        # Add parameters for all columns (up to limit), making them all optional
        for col in entity.columns[:limit]:
            param_name = self._to_business_name(col.name)
            
            param_def = {
                "name": param_name,
                "type": self._get_parameter_type(col),
                "description": f"Filter by {col.name}"
            }
            
            # Add enum values if available (include null for optional parameters)
            if col.enum_values:
                param_def["enum"] = col.enum_values + [None]
            
            # Add format for date strings
            if col.data_type.lower() in ['varchar', 'text'] and 'date' in col.name.lower():
                param_def["format"] = "date"
                
            parameters.append(param_def)
        
        # Add range parameters for numeric/date fields
        for col in entity.columns:
            if col.classification in [ColumnClassification.TEMPORAL, ColumnClassification.METRIC]:
                param_name = self._to_business_name(col.name)
                
                if col.data_type.upper() == 'DATE':
                    parameters.extend([
                        {
                            "name": f"{param_name}From",
                            "type": "string",
                            "format": "date",
                            "description": f"Filter {col.name} from date (YYYY-MM-DD)"
                        },
                        {
                            "name": f"{param_name}To", 
                            "type": "string",
                            "format": "date",
                            "description": f"Filter {col.name} to date (YYYY-MM-DD)"
                        }
                    ])
                elif col.data_type.upper() in ['INTEGER', 'BIGINT', 'DOUBLE', 'FLOAT', 'DECIMAL']:
                    parameters.extend([
                        {
                            "name": f"{param_name}Min",
                            "type": "number",
                            "description": f"Minimum value for {col.name}"
                        },
                        {
                            "name": f"{param_name}Max",
                            "type": "number", 
                            "description": f"Maximum value for {col.name}"
                        }
                    ])
        
        return parameters
    
    def _generate_common_where_clauses(self, entity: BusinessEntity, limit: int = 10) -> List[str]:
        """Generate WHERE clauses for common filters"""
        where_clauses = []
        
        # Add filters for categorical fields using same naming as search tool
        categorical_fields = [
            col for col in entity.columns
            if col.classification in [ColumnClassification.CATEGORICAL, ColumnClassification.BUSINESS_STATUS]
        ]
        
        for field in categorical_fields[:limit]:
            param_name = self._to_business_name(field.name)  # Same as search tool
            where_clauses.append(
                f"  AND (${param_name} IS NULL OR {field.name} = ${param_name})"
            )
        
        # Add date range filters using same naming as search tool
        temporal_fields = [
            col for col in entity.columns
            if col.classification == ColumnClassification.TEMPORAL
        ]
        
        for field in temporal_fields[:2]:
            # Use the actual field name for parameter generation (including _d suffix if present)
            if field.data_type.lower() == 'date':
                param_base = self._to_business_name(field.name)
                where_clauses.extend([
                    f"  AND (${param_base}From IS NULL OR {field.name} >= ${param_base}From::DATE)",
                    f"  AND (${param_base}To IS NULL OR {field.name} <= ${param_base}To::DATE)"
                ])
            else:
                # For string date fields, check if _d version exists and use it
                date_field = f"{field.name}_d"
                if any(col.name == date_field for col in entity.columns):
                    param_base = self._to_business_name(date_field)  # Use _d version for param name
                    where_clauses.extend([
                        f"  AND (${param_base}From IS NULL OR {date_field} >= ${param_base}From::DATE)",
                        f"  AND (${param_base}To IS NULL OR {date_field} <= ${param_base}To::DATE)"
                    ])
                else:
                    # Fallback to original field
                    param_base = self._to_business_name(field.name)
                    where_clauses.extend([
                        f"  AND (${param_base}From IS NULL OR {field.name} >= ${param_base}From::DATE)",
                        f"  AND (${param_base}To IS NULL OR {field.name} <= ${param_base}To::DATE)"
                    ])
        
        return where_clauses
    
    def _generate_return_properties(self, entity: BusinessEntity) -> Dict[str, Any]:
        """Generate return type properties for the entity"""
        properties = {}
        
        for col in entity.columns[:20]:  # Limit to 20 properties
            prop_type = self._map_sql_type_to_json(col.data_type)
            properties[col.name] = {
                "type": prop_type,
                "description": col.description or f"{col.name} field"
            }
        
        return properties
    
    def _map_sql_type_to_json(self, sql_type: str) -> str:
        """Map SQL data type to JSON schema type"""
        sql_type_lower = sql_type.lower()
        
        if any(t in sql_type_lower for t in ['int', 'serial', 'bigint', 'smallint']):
            return "integer"
        elif any(t in sql_type_lower for t in ['decimal', 'numeric', 'real', 'double', 'float']):
            return "number"
        elif any(t in sql_type_lower for t in ['bool', 'boolean']):
            return "boolean"
        elif any(t in sql_type_lower for t in ['array', 'json']):
            return "array"
        elif any(t in sql_type_lower for t in ['date', 'time', 'timestamp']):
            return "string"  # ISO format
        else:
            return "string"
    
    def _generate_aggregation_tool(self, entity: BusinessEntity) -> Optional[Dict[str, Any]]:
        """Generate aggregation tool for complex queries"""
        # Find aggregatable fields - include both CATEGORICAL and BUSINESS_STATUS
        categorical_fields = [
            col for col in entity.columns
            if col.classification in [ColumnClassification.CATEGORICAL, ColumnClassification.BUSINESS_STATUS]
        ]
        
        # Also include other string fields that could be used for grouping
        string_fields = [
            col for col in entity.columns
            if col.data_type.lower() in ['varchar', 'string', 'text', 'char'] 
            and col.classification not in [ColumnClassification.DESCRIPTIVE]
            and col not in categorical_fields
        ]
        
        all_groupable_fields = categorical_fields + string_fields
        
        metric_fields = [
            col for col in entity.columns
            if col.classification == ColumnClassification.METRIC
        ]
        
        if not all_groupable_fields:
            return None
        
        tool_name = f"aggregate_{entity.name}"
        description = f"Aggregate {entity.name} data by various dimensions"
        
        parameters = []
        
        # Add group by parameters for ALL categorical/string fields
        for field in all_groupable_fields:
            param_name = f"groupBy{self._to_business_name(field.name)}"
            parameters.append({
                "name": param_name,
                "type": "boolean",
                "description": f"Group by {self._to_business_name(field.name)}",
                "default": False
            })
        
        # Add common filters using same method as search tool
        parameters.extend(self._generate_common_filter_parameters(entity, limit=10))
        
        # Build dynamic SQL
        select_columns = ["COUNT(*) as total_count", f"COUNT(DISTINCT {self._get_primary_key(entity)}) as unique_records"]
        
        # Add dynamic group by columns based on parameters
        for i, field in enumerate(all_groupable_fields):
            param_name = f"groupBy{self._to_business_name(field.name)}"
            select_columns.insert(i, f"CASE WHEN ${param_name} THEN {field.name} ELSE 'All' END as {field.name}")
        
        # Get common where clauses
        where_clauses = self._generate_common_where_clauses(entity)
        
        # Build the final SQL
        sql = f"""
SELECT
  {',\n  '.join(select_columns)}
FROM {entity.primary_model.name}_v1
WHERE 1=1
{chr(10).join(where_clauses)}
GROUP BY {', '.join([f"{i+1}" for i in range(len(all_groupable_fields))])}
ORDER BY total_count DESC
LIMIT 100
        """.strip()
        
        # Store SQL separately
        self.sql_queries[tool_name] = sql
        
        return {
            "mxcp": self.version,
            "tool": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
                "required": [],  # No required parameters for aggregation
                "return": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    }
                },
                "source": {
                    "file": f"../sql/{tool_name}.sql"
                },
                "enabled": True
            }
        }
    
    def _generate_timeseries_tool(self, entity: BusinessEntity) -> Optional[Dict[str, Any]]:
        """Generate time series analysis tool"""
        temporal_fields = [
            col for col in entity.columns
            if col.classification == ColumnClassification.TEMPORAL
        ]
        
        if not temporal_fields:
            return None
        
        tool_name = f"timeseries_{entity.name}"
        description = f"Analyze {entity.name} trends over time"
        
        parameters = [
            {
                "name": "timeField",
                "type": "string",
                "description": "Date field to analyze",
                "enum": [f.name for f in temporal_fields],
                "default": temporal_fields[0].name if temporal_fields else None
            },
            {
                "name": "granularity",
                "type": "string",
                "description": "Time granularity",
                "enum": ["day", "week", "month", "quarter", "year"],
                "default": "month"
            },
            {
                "name": "startDate",
                "type": "string",
                "format": "date",
                "description": "Start date (YYYY-MM-DD)",
                "default": None
            },
            {
                "name": "endDate",
                "type": "string",
                "format": "date",
                "description": "End date (YYYY-MM-DD)",
                "default": None
            }
        ]
        
        # Add common filters using same method as search tool
        parameters.extend(self._generate_common_filter_parameters(entity, limit=10))
        
        # Get common where clauses
        where_clauses = self._generate_common_where_clauses(entity)
        
        # Build SQL - use dynamic field selection
        primary_key = self._get_primary_key(entity)
        
        # Create dynamic CASE statement for all temporal fields
        temporal_field_cases = []
        for field in temporal_fields:
            # Use the proper date field (prefer _d version if available)
            actual_field = field.name
            if field.data_type.lower() != 'date':
                # Check if there's a _d version
                date_version = f"{field.name}_d"
                if any(col.name == date_version for col in entity.columns):
                    actual_field = date_version
            temporal_field_cases.append(f"    WHEN $timeField = '{field.name}' THEN {actual_field}")
        
        # Fallback to first temporal field
        default_field = temporal_fields[0].name
        if temporal_fields[0].data_type.lower() != 'date':
            date_version = f"{temporal_fields[0].name}_d"
            if any(col.name == date_version for col in entity.columns):
                default_field = date_version
        
        sql = f"""
SELECT
  DATE_TRUNC($granularity, 
    CASE 
{chr(10).join(temporal_field_cases)}
      ELSE {default_field}
    END
  ) as period,
  COUNT(*) as count,
  COUNT(DISTINCT {primary_key}) as unique_records
FROM {entity.primary_model.name}_v1
WHERE CASE 
{chr(10).join(temporal_field_cases)}
      ELSE {default_field}
  END IS NOT NULL
  AND ($startDate IS NULL OR 
    CASE 
{chr(10).join(temporal_field_cases)}
      ELSE {default_field}
    END >= $startDate::DATE)
  AND ($endDate IS NULL OR 
    CASE 
{chr(10).join(temporal_field_cases)}
      ELSE {default_field}
    END <= $endDate::DATE)
{chr(10).join(where_clauses)}
GROUP BY period
ORDER BY period DESC
        """.strip()
        
        # Store SQL separately
        self.sql_queries[tool_name] = sql
        
        return {
            "mxcp": self.version,
            "tool": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
                "required": [],  # No required parameters for time series
                "return": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "period": {"type": "string", "format": "date"},
                            "count": {"type": "integer"},
                            "unique_records": {"type": "integer"}
                        }
                    }
                },
                "source": {
                    "file": f"../sql/{tool_name}.sql"
                },
                "enabled": True
            }
        }
    
    def _generate_geographic_tool(self, entity: BusinessEntity) -> Optional[Dict[str, Any]]:
        """Generate geographic analysis tool"""
        geo_fields = [
            col for col in entity.columns
            if col.classification == ColumnClassification.GEOGRAPHIC
        ]
        
        if not geo_fields:
            return None
        
        tool_name = f"geo_{entity.name}"
        description = f"Analyze {entity.name} by geographic location"
        
        # Find coordinate fields using generic patterns
        lat_field = None
        lon_field = None
        
        for col in entity.columns:
            col_lower = col.name.lower()
            if not lat_field and any(pattern in col_lower for pattern in ['lat', 'latitude']):
                lat_field = col.name
            if not lon_field and any(pattern in col_lower for pattern in ['lon', 'lng', 'longitude']):
                lon_field = col.name
        
        # Fallback to common names
        if not lat_field:
            lat_field = 'latitude'
        if not lon_field:
            lon_field = 'longitude'
        
        # Find the main geographic field (first geographic field)
        main_geo = geo_fields[0]
        
        parameters = [
            {
                "name": "groupByField",
                "type": "string",
                "description": "Geographic field to group by",
                "enum": [f.name for f in geo_fields],
                "default": main_geo.name
            },
            {
                "name": "includeCoordinates",
                "type": "boolean",
                "description": "Include lat/lon statistics",
                "default": False
            },
            {
                "name": "boundingBox",
                "type": "object",
                "description": "Filter by bounding box coordinates",
                "properties": {
                    "minLat": {"type": "number"},
                    "maxLat": {"type": "number"},
                    "minLon": {"type": "number"},
                    "maxLon": {"type": "number"}
                }
            }
        ]
        
        # Add common filters
        parameters.extend(self._generate_common_filter_parameters(entity))
        
        # Get common where clauses
        where_clauses = self._generate_common_where_clauses(entity)
        
        # Add bounding box filter
        where_clauses.extend([
            f"  AND ($boundingBox.minLat IS NULL OR {lat_field} >= $boundingBox.minLat)",
            f"  AND ($boundingBox.maxLat IS NULL OR {lat_field} <= $boundingBox.maxLat)",
            f"  AND ($boundingBox.minLon IS NULL OR {lon_field} >= $boundingBox.minLon)",
            f"  AND ($boundingBox.maxLon IS NULL OR {lon_field} <= $boundingBox.maxLon)"
        ])
        
        # Create dynamic CASE statement for geographic fields
        geo_field_cases = []
        for field in geo_fields:
            geo_field_cases.append(f"    WHEN $groupByField = '{field.name}' THEN {field.name}")
        
        primary_key = self._get_primary_key(entity)
        
        sql = f"""
SELECT
  CASE 
{chr(10).join(geo_field_cases)}
    ELSE {main_geo.name}
  END as location,
  COUNT(*) as count,
  COUNT(DISTINCT {primary_key}) as unique_records,
  CASE 
    WHEN $includeCoordinates THEN AVG({lat_field})
    ELSE NULL
  END as avg_latitude,
  CASE 
    WHEN $includeCoordinates THEN AVG({lon_field})
    ELSE NULL
  END as avg_longitude,
  CASE 
    WHEN $includeCoordinates THEN MIN({lat_field})
    ELSE NULL
  END as min_latitude,
  CASE 
    WHEN $includeCoordinates THEN MAX({lat_field})
    ELSE NULL
  END as max_latitude,
  CASE 
    WHEN $includeCoordinates THEN MIN({lon_field})
    ELSE NULL
  END as min_longitude,
  CASE 
    WHEN $includeCoordinates THEN MAX({lon_field})
    ELSE NULL
  END as max_longitude
FROM {entity.primary_model.name}_v1
WHERE CASE 
{chr(10).join(geo_field_cases)}
    ELSE {main_geo.name}
  END IS NOT NULL
{chr(10).join(where_clauses)}
GROUP BY location
ORDER BY count DESC
        """.strip()
        
        # Store SQL separately
        self.sql_queries[tool_name] = sql
        
        return {
            "mxcp": self.version,
            "tool": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
                "required": [],  # No required parameters for geographic analysis
                "return": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "count": {"type": "integer"},
                            "unique_records": {"type": "integer"},
                            "avg_latitude": {"type": "number"},
                            "avg_longitude": {"type": "number"},
                            "min_latitude": {"type": "number"},
                            "max_latitude": {"type": "number"},
                            "min_longitude": {"type": "number"},
                            "max_longitude": {"type": "number"}
                        }
                    }
                },
                "source": {
                    "file": f"../sql/{tool_name}.sql"
                },
                "enabled": True
            }
        }
    
    def _has_temporal_fields(self, entity: BusinessEntity) -> bool:
        """Check if entity has temporal fields"""
        return any(
            col.classification == ColumnClassification.TEMPORAL
            for col in entity.columns
        )
    
    def _has_geographic_fields(self, entity: BusinessEntity) -> bool:
        """Check if entity has geographic fields"""
        return any(
            col.classification == ColumnClassification.GEOGRAPHIC
            for col in entity.columns
        )
    
    def _generate_categorical_tool(self, entity: BusinessEntity) -> Optional[Dict[str, Any]]:
        """Generate tool to list categorical values"""
        categorical_fields = [
            col for col in entity.columns
            if col.classification in [ColumnClassification.CATEGORICAL, ColumnClassification.BUSINESS_STATUS]
            or col.enum_values
        ]
        
        if not categorical_fields:
            return None
        
        tool_name = f"list_{entity.name}_categories"
        description = f"List distinct values for categorical fields in {entity.name}"
        
        parameters = [
            {
                "name": "field",
                "type": "string",
                "description": "The categorical field to get values for",
                "enum": [col.name for col in categorical_fields]
            },
            {
                "name": "includeCount",
                "type": "boolean",
                "description": "Include count of records for each value",
                "default": True
            }
        ]
        
        # Build SQL with dynamic field selection
        sql = f"""
SELECT DISTINCT
  CASE 
{chr(10).join([f"    WHEN $field = '{col.name}' THEN {col.name}" for col in categorical_fields])}
  END as value,
  CASE 
    WHEN $includeCount THEN COUNT(*)
    ELSE NULL
  END as count
FROM {entity.primary_model.name}_v1
WHERE CASE 
{chr(10).join([f"    WHEN $field = '{col.name}' THEN {col.name}" for col in categorical_fields])}
  END IS NOT NULL
GROUP BY value
ORDER BY count DESC NULLS LAST, value
        """.strip()
        
        # Store SQL separately
        self.sql_queries[tool_name] = sql
        
        return {
            "mxcp": self.version,
            "tool": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
                "required": [],  # No required parameters for categorical listing
                "return": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string"},
                            "count": {"type": "integer"}
                        }
                    }
                },
                "source": {
                    "file": f"../sql/{tool_name}.sql"
                },
                "enabled": True
            }
        }
    
    def _get_parameter_type(self, col: ColumnInfo) -> str:
        """Map database column type to parameter type"""
        data_type = col.data_type.upper()
        
        if data_type in ['INTEGER', 'BIGINT', 'SMALLINT']:
            return 'integer'
        elif data_type in ['DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL']:
            return 'number'
        elif data_type in ['BOOLEAN', 'BOOL']:
            return 'boolean'
        elif data_type in ['DATE', 'DATETIME', 'TIMESTAMP']:
            return 'string'  # Dates as strings with format
        else:
            return 'string'
    
    def _get_embed_options(self, entity: BusinessEntity) -> List[str]:
        """Get available embed options for an entity based on relationships"""
        embed_options = []
        
        # Look for foreign key relationships in the entity's columns
        for col in entity.columns:
            col_info = getattr(col, 'relationships', None)
            if col_info:
                for rel_info in col_info:
                    target_model = rel_info.get('target_model', '')
                    if target_model and target_model.startswith('dim_'):
                        # Convert dim_licenses -> licenses
                        entity_name = target_model[4:]  # Remove 'dim_' prefix
                        embed_options.append(entity_name)
        
        # Also check if there are related models that reference this entity
        # This would require analyzing all entities, but for now we'll use the direct relationships
        
        return list(set(embed_options))  # Remove duplicates
    
    def _generate_embedding_sql(self, entity: BusinessEntity, base_sql: str) -> str:
        """Generate SQL with conditional embedding support"""
        # For now, generate a simple version that can be enhanced
        # In a full implementation, this would use CASE statements and JSON aggregation
        
        embedding_template = f"""
-- Base query
WITH base_data AS (
{base_sql}
)

-- Enhanced query with conditional embedding
SELECT 
  bd.*,
  CASE 
    WHEN $embed IS NULL OR ARRAY_LENGTH($embed) = 0 THEN NULL
    ELSE JSON_OBJECT()  -- Placeholder for embedded data
  END as _embedded
FROM base_data bd
        """.strip()
        
        return embedding_template
    
    def _detect_relationships_from_columns(self, entity: BusinessEntity) -> Dict[str, Any]:
        """Detect relationships from column metadata"""
        relationships = {}
        
        for col in entity.columns:
            # Check if column has relationship metadata from dbt tests
            if hasattr(col, 'relationships') and col.relationships:
                for rel_info in col.relationships:
                    target_model = rel_info.get('target_model', '')
                    target_field = rel_info.get('target_field', '')
                    
                    if target_model and target_field:
                        # Determine relationship type (for now assume many-to-one)
                        rel_type = "many-to-one"
                        
                        relationships[target_model] = {
                            'type': rel_type,
                            'source_field': col.name,
                            'target_field': target_field,
                            'target_model': target_model
                        }
        
        return relationships 