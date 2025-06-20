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
    
    def generate_for_entity(self, entity: BusinessEntity) -> List[Dict[str, Any]]:
        """
        Generate tools for a business entity
        
        Args:
            entity: Business entity to generate tools for
            
        Returns:
            List of MXCP tool definitions
        """
        tools = []
        
        # Generate search tool
        search_tool = self._generate_search_tool(entity)
        if search_tool:
            tools.append(search_tool)
        
        # Generate analytics tool if entity has metrics
        if self._has_metric_fields(entity):
            analytics_tool = self._generate_analytics_tool(entity)
            if analytics_tool:
                tools.append(analytics_tool)
        
        # Generate aggregation tool
        aggregation_tool = self._generate_aggregation_tool(entity)
        if aggregation_tool:
            tools.append(aggregation_tool)
        
        # Generate time series tool if entity has temporal fields
        if self._has_temporal_fields(entity):
            timeseries_tool = self._generate_timeseries_tool(entity)
            if timeseries_tool:
                tools.append(timeseries_tool)
        
        # Generate geographic tool if entity has geographic fields
        if self._has_geographic_fields(entity):
            geo_tool = self._generate_geographic_tool(entity)
            if geo_tool:
                tools.append(geo_tool)
        
        # Generate relationship navigation tools
        for rel_name, rel_info in entity.relationships.items():
            rel_tool = self._generate_relationship_tool(entity, rel_info)
            if rel_tool:
                tools.append(rel_tool)
        
        logger.info(f"Generated {len(tools)} tools for entity {entity.name}")
        return tools
    
    def _generate_search_tool(self, entity: BusinessEntity) -> Optional[Dict[str, Any]]:
        """Generate a search tool for the entity"""
        # Build tool definition
        tool_name = f"find_{entity.name}"
        description = f"Search for {entity.name} records with comprehensive filtering options"
        
        parameters = []
        where_conditions = []
        
        # Add parameters for ALL fields
        for field in entity.columns:
            param_name = self._to_business_name(field.name)
            param_def = {
                "name": param_name,
                "type": "string",
                "description": f"Filter by {param_name}",
                "default": None
            }
            
            # Add enum values if available
            if field.enum_values:
                param_def["enum"] = field.enum_values
            
            # Determine filter type based on classification and field name
            field_lower = field.name.lower()
            
            # Check if this should use partial match
            use_partial_match = (
                field.classification in [ColumnClassification.DESCRIPTIVE, ColumnClassification.IDENTIFIER] or
                any(pattern in field_lower for pattern in ['name', 'desc', 'address', 'title', 'text'])
            )
            
            if use_partial_match:
                # Partial match for text fields
                parameters.append(param_def)
                where_conditions.append(
                    f"  AND (${param_name} IS NULL OR {field.name} ILIKE '%' || ${param_name} || '%')"
                )
            elif field.classification == ColumnClassification.TEMPORAL:
                # Add date range parameters
                param_from = param_def.copy()
                param_from["name"] = f"{param_name}From"
                param_from["description"] = f"{param_name} from date (YYYY-MM-DD)"
                param_from["format"] = "date"
                parameters.append(param_from)
                
                param_to = param_def.copy()
                param_to["name"] = f"{param_name}To"
                param_to["description"] = f"{param_name} to date (YYYY-MM-DD)"
                param_to["format"] = "date"
                parameters.append(param_to)
                
                where_conditions.append(
                    f"  AND (${param_name}From IS NULL OR {field.name} >= ${param_name}From)"
                )
                where_conditions.append(
                    f"  AND (${param_name}To IS NULL OR {field.name} <= ${param_name}To)"
                )
            elif field.classification == ColumnClassification.METRIC:
                # Add min/max parameters for numeric fields
                param_min = param_def.copy()
                param_min["name"] = f"{param_name}Min"
                param_min["type"] = "number"
                param_min["description"] = f"Minimum {param_name}"
                parameters.append(param_min)
                
                param_max = param_def.copy()
                param_max["name"] = f"{param_name}Max"
                param_max["type"] = "number"
                param_max["description"] = f"Maximum {param_name}"
                parameters.append(param_max)
                
                where_conditions.append(
                    f"  AND (${param_name}Min IS NULL OR {field.name} >= ${param_name}Min)"
                )
                where_conditions.append(
                    f"  AND (${param_name}Max IS NULL OR {field.name} <= ${param_name}Max)"
                )
            else:
                # Exact match for other fields
                parameters.append(param_def)
                where_conditions.append(
                    f"  AND (${param_name} IS NULL OR {field.name} = ${param_name})"
                )
        
        # Add pagination parameters
        parameters.extend([
            {
                "name": "page",
                "type": "integer",
                "description": "Page number (1-based)",
                "default": 1,
                "minimum": 1
            },
            {
                "name": "page_size",
                "type": "integer",
                "description": "Number of records per page",
                "default": 20,
                "minimum": 1,
                "maximum": 1000
            }
        ])
        
        # Build SQL query
        sql = f"""
SELECT *
FROM {entity.primary_model.name}_v1
WHERE 1=1
{chr(10).join(where_conditions)}
ORDER BY {self._get_default_order_column(entity)} DESC
LIMIT $page_size OFFSET (($page - 1) * $page_size)
        """.strip()
        
        # Generate return type with properties at the correct level
        return_properties = self._generate_return_properties(entity)
        
        return {
            "mxcp": self.version,
            "tool": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
                "return": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": return_properties  # Properties inside items
                    }
                },
                "source": {
                    "code": sql
                },
                "enabled": True
            }
        }
    
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
        
        # Remove entity-specific prefixes
        for prefix in ['bl_', 'dim_', 'fact_']:
            if name.startswith(prefix):
                name = name[len(prefix):]
        
        # Remove other common suffixes (but not language ones)
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
        """Get primary key column name"""
        for col in entity.columns:
            if col.is_primary_key:
                return col.name
        
        # Fallback to first identifier
        for col in entity.columns:
            if col.classification == ColumnClassification.IDENTIFIER:
                return col.name
        
        return entity.columns[0].name if entity.columns else "id"
    
    def _generate_common_filter_parameters(self, entity: BusinessEntity, limit: int = 10) -> List[Dict[str, Any]]:
        """Generate common filter parameters that can be added to any tool"""
        parameters = []
        
        # Add filters for key categorical fields
        categorical_fields = [
            col for col in entity.columns
            if col.classification in [ColumnClassification.CATEGORICAL, ColumnClassification.BUSINESS_STATUS]
        ]
        
        for field in categorical_fields[:limit]:
            param_name = f"filter{self._to_business_name(field.name)}"
            param_def = {
                "name": param_name,
                "type": "string",
                "description": f"Filter by {self._to_business_name(field.name)}",
            }
            if field.enum_values:
                param_def["enum"] = field.enum_values
            parameters.append(param_def)
        
        # Add date range filters for temporal fields
        temporal_fields = [
            col for col in entity.columns
            if col.classification == ColumnClassification.TEMPORAL
        ]
        
        for field in temporal_fields[:2]:  # Limit to 2 most important date fields
            param_base = self._to_business_name(field.name)
            parameters.extend([
                {
                    "name": f"{param_base}From",
                    "type": "string",
                    "format": "date",
                    "description": f"Filter {param_base} from date (YYYY-MM-DD)"
                },
                {
                    "name": f"{param_base}To",
                    "type": "string",
                    "format": "date",
                    "description": f"Filter {param_base} to date (YYYY-MM-DD)"
                }
            ])
        
        return parameters
    
    def _generate_common_where_clauses(self, entity: BusinessEntity, limit: int = 10) -> List[str]:
        """Generate WHERE clauses for common filters"""
        where_clauses = []
        
        # Add filters for categorical fields
        categorical_fields = [
            col for col in entity.columns
            if col.classification in [ColumnClassification.CATEGORICAL, ColumnClassification.BUSINESS_STATUS]
        ]
        
        for field in categorical_fields[:limit]:
            param_name = f"filter{self._to_business_name(field.name)}"
            where_clauses.append(
                f"  AND (${param_name} IS NULL OR {field.name} = ${param_name})"
            )
        
        # Add date range filters
        temporal_fields = [
            col for col in entity.columns
            if col.classification == ColumnClassification.TEMPORAL
        ]
        
        for field in temporal_fields[:2]:
            param_base = self._to_business_name(field.name)
            # Handle both string and date fields
            if field.data_type.lower() == 'date':
                where_clauses.extend([
                    f"  AND (${param_base}From IS NULL OR {field.name} >= ${param_base}From::DATE)",
                    f"  AND (${param_base}To IS NULL OR {field.name} <= ${param_base}To::DATE)"
                ])
            else:
                # For string date fields, use the _d version if available
                date_field = field.name.replace('_date', '_date_d')
                where_clauses.extend([
                    f"  AND (${param_base}From IS NULL OR {date_field} >= ${param_base}From::DATE)",
                    f"  AND (${param_base}To IS NULL OR {date_field} <= ${param_base}To::DATE)"
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
        
        # Add common filters
        parameters.extend(self._generate_common_filter_parameters(entity))
        
        # Build dynamic SQL
        select_columns = ["COUNT(*) as total_count", "COUNT(DISTINCT license_pk) as unique_licenses"]
        
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
        
        return {
            "mxcp": self.version,
            "tool": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
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
        
        # Add common filters
        parameters.extend(self._generate_common_filter_parameters(entity))
        
        # Get common where clauses
        where_clauses = self._generate_common_where_clauses(entity)
        
        # Build SQL
        sql = f"""
SELECT
  DATE_TRUNC($granularity, 
    CASE 
      WHEN $timeField = 'bl_est_date_d' THEN bl_est_date_d
      WHEN $timeField = 'bl_exp_date_d' THEN bl_exp_date_d
      ELSE bl_est_date_d
    END
  ) as period,
  COUNT(*) as count,
  COUNT(DISTINCT license_pk) as unique_licenses
FROM {entity.primary_model.name}_v1
WHERE CASE 
    WHEN $timeField = 'bl_est_date_d' THEN bl_est_date_d
    WHEN $timeField = 'bl_exp_date_d' THEN bl_exp_date_d
    ELSE bl_est_date_d
  END IS NOT NULL
  AND ($startDate IS NULL OR 
    CASE 
      WHEN $timeField = 'bl_est_date_d' THEN bl_est_date_d
      WHEN $timeField = 'bl_exp_date_d' THEN bl_exp_date_d
      ELSE bl_est_date_d
    END >= $startDate::DATE)
  AND ($endDate IS NULL OR 
    CASE 
      WHEN $timeField = 'bl_est_date_d' THEN bl_est_date_d
      WHEN $timeField = 'bl_exp_date_d' THEN bl_exp_date_d
      ELSE bl_est_date_d
    END <= $endDate::DATE)
{chr(10).join(where_clauses)}
GROUP BY period
ORDER BY period DESC
        """.strip()
        
        return {
            "mxcp": self.version,
            "tool": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
                "return": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "period": {"type": "string", "format": "date"},
                            "count": {"type": "integer"},
                            "unique_licenses": {"type": "integer"}
                        }
                    }
                },
                "source": {
                    "code": sql
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
        
        # Find coordinate fields
        lat_field = next((col.name for col in entity.columns if 'lat' in col.name.lower() and 'dd' in col.name.lower()), 'lat_dd')
        lon_field = next((col.name for col in entity.columns if 'lon' in col.name.lower() and 'dd' in col.name.lower()), 'lon_dd')
        
        # Find the main geographic field (e.g., emirate)
        main_geo = next((f for f in geo_fields if 'emirate' in f.name.lower()), geo_fields[0])
        
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
        
        sql = f"""
SELECT
  CASE 
    WHEN $groupByField = 'emirate_name_en' THEN emirate_name_en
    WHEN $groupByField = 'emirate_name_ar' THEN emirate_name_ar
    WHEN $groupByField = 'issuance_authority_en' THEN issuance_authority_en
    WHEN $groupByField = 'issuance_authority_ar' THEN issuance_authority_ar
    WHEN $groupByField = 'bl_full_address' THEN bl_full_address
    ELSE emirate_name_en
  END as location,
  COUNT(*) as count,
  COUNT(DISTINCT license_pk) as unique_licenses,
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
    WHEN $groupByField = 'emirate_name_en' THEN emirate_name_en
    WHEN $groupByField = 'emirate_name_ar' THEN emirate_name_ar
    WHEN $groupByField = 'issuance_authority_en' THEN issuance_authority_en
    WHEN $groupByField = 'issuance_authority_ar' THEN issuance_authority_ar
    WHEN $groupByField = 'bl_full_address' THEN bl_full_address
    ELSE emirate_name_en
  END IS NOT NULL
{chr(10).join(where_clauses)}
GROUP BY location
ORDER BY count DESC
        """.strip()
        
        return {
            "mxcp": self.version,
            "tool": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
                "return": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "count": {"type": "integer"},
                            "unique_licenses": {"type": "integer"},
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
                    "code": sql
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