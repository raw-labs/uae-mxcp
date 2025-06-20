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
        
        # Generate filter tool if entity has status fields
        if self._has_status_fields(entity):
            filter_tool = self._generate_filter_tool(entity)
            if filter_tool:
                tools.append(filter_tool)
        
        # Generate analytics tool if entity has metrics
        if self._has_metric_fields(entity):
            analytics_tool = self._generate_analytics_tool(entity)
            if analytics_tool:
                tools.append(analytics_tool)
        
        # Generate relationship navigation tools
        for rel_name, rel_info in entity.relationships.items():
            rel_tool = self._generate_relationship_tool(entity, rel_info)
            if rel_tool:
                tools.append(rel_tool)
        
        logger.info(f"Generated {len(tools)} tools for entity {entity.name}")
        return tools
    
    def _generate_search_tool(self, entity: BusinessEntity) -> Optional[Dict[str, Any]]:
        """Generate a search tool for the entity"""
        # Find searchable fields
        searchable_fields = [
            col for col in entity.columns
            if col.classification in [
                ColumnClassification.DESCRIPTIVE,
                ColumnClassification.IDENTIFIER
            ]
        ]
        
        if not searchable_fields:
            return None
        
        # Build tool definition
        tool_name = f"find_{entity.name}"
        description = f"Search for {entity.name} records with intelligent filtering"
        
        parameters = []
        where_conditions = []
        
        # Add search parameters for each searchable field
        for field in searchable_fields[:3]:  # Limit to top 3 fields
            param_name = self._to_business_name(field.name)
            parameters.append({
                "name": param_name,
                "type": "string",
                "description": f"Search by {param_name} (partial match supported)",
                "required": False
            })
            
            where_conditions.append(
                f"{{% if {param_name} %}}\n"
                f"  AND {field.name} ILIKE '%' || ${param_name} || '%'\n"
                f"{{% endif %}}"
            )
        
        # Add status filter if available
        status_fields = [
            col for col in entity.columns
            if col.classification == ColumnClassification.BUSINESS_STATUS
        ]
        
        if status_fields:
            field = status_fields[0]
            param_name = self._to_business_name(field.name)
            
            param_def = {
                "name": param_name,
                "type": "string",
                "description": f"Filter by {param_name}",
                "required": False
            }
            
            # Add enum values if available
            if field.enum_values:
                param_def["enum"] = field.enum_values
            
            parameters.append(param_def)
            where_conditions.append(
                f"{{% if {param_name} %}}\n"
                f"  AND {field.name} = ${param_name}\n"
                f"{{% endif %}}"
            )
        
        # Build SQL query
        sql = f"""
SELECT *
FROM {{{{ schema }}}}.{entity.primary_model.name}
WHERE 1=1
{chr(10).join(where_conditions)}
ORDER BY {self._get_default_order_column(entity)}
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
                        "type": "object",
                        "properties": self._generate_return_properties(entity)
                    }
                },
                "source": {
                    "code": sql
                },
                "enabled": True
            }
        }
    
    def _generate_filter_tool(self, entity: BusinessEntity) -> Optional[Dict[str, Any]]:
        """Generate a filter tool for status-based queries"""
        status_fields = [
            col for col in entity.columns
            if col.classification == ColumnClassification.BUSINESS_STATUS
        ]
        
        if not status_fields:
            return None
        
        tool_name = f"filter_{entity.name}_by_status"
        description = f"Filter {entity.name} records by status fields"
        
        parameters = []
        where_conditions = []
        
        for field in status_fields:
            param_name = self._to_business_name(field.name)
            param_def = {
                "name": param_name,
                "type": "boolean" if field.data_type.lower() in ['boolean', 'bool'] else "string",
                "description": f"Filter by {param_name}",
                "required": False
            }
            
            if field.enum_values:
                param_def["enum"] = field.enum_values
            
            parameters.append(param_def)
            
            where_conditions.append(
                f"{{% if {param_name} is defined %}}\n"
                f"  AND {field.name} = ${param_name}\n"
                f"{{% endif %}}"
            )
        
        sql = f"""
SELECT *
FROM {{{{ schema }}}}.{entity.primary_model.name}
WHERE 1=1
{chr(10).join(where_conditions)}
ORDER BY {self._get_default_order_column(entity)}
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
                        "properties": self._generate_return_properties(entity)
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
                "required": False
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
                "required": False
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
        
        sql = f"""
SELECT
{{% if group_by %}}
  {{{{ group_by }}}},
{{% endif %}}
{','.join(metric_aggregations)}
FROM {{{{ schema }}}}.{entity.primary_model.name}
{{% if group_by %}}
GROUP BY {{{{ group_by }}}}
ORDER BY {{{{ group_by }}}}
{{% endif %}}
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
FROM {{{{ schema }}}}.{entity.primary_model.name} a
LEFT JOIN {{{{ schema }}}}.dim_{rel_info.to_entity} b
  ON {' AND '.join(join_conditions)}
WHERE 1=1
{{% if id %}}
  AND a.{self._get_primary_key(entity)} = $id
{{% endif %}}
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
                    "required": False
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
        
        # Remove entity-specific prefixes
        for prefix in ['bl_', 'dim_', 'fact_']:
            if name.startswith(prefix):
                name = name[len(prefix):]
        
        # Remove common suffixes
        for suffix in ['_en', '_ar', '_id', '_key']:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
        
        # Convert underscores to spaces and capitalize
        return name.replace('_', ' ').title().replace(' ', '')
    
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