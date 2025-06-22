"""
Resource generator for creating MXCP resource definitions
"""

import logging
from typing import Dict, List, Any, Optional
from ..analyzers import BusinessEntity, ColumnClassification

logger = logging.getLogger(__name__)


class ResourceGenerator:
    """
    Generates MXCP resource definitions from business entities
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.version = "1.0.0"
    
    def generate_resources(self, entities: Dict[str, BusinessEntity]) -> List[Dict[str, Any]]:
        """
        Generate resources for all entities
        
        Args:
            entities: Dictionary of business entities
            
        Returns:
            List of MXCP resource definitions
        """
        resources = []
        
        # Generate entity-specific resources
        for entity_name, entity in entities.items():
            # Active records resource
            active_resource = self._generate_active_resource(entity)
            if active_resource:
                resources.append(active_resource)
            
            # Summary resource if entity has metrics
            if self._has_metrics(entity):
                summary_resource = self._generate_summary_resource(entity)
                if summary_resource:
                    resources.append(summary_resource)
        
        # Generate cross-entity resources
        if len(entities) > 1:
            overview_resource = self._generate_overview_resource(entities)
            if overview_resource:
                resources.append(overview_resource)
        
        logger.info(f"Generated {len(resources)} resources")
        return resources
    
    def _generate_active_resource(self, entity: BusinessEntity) -> Optional[Dict[str, Any]]:
        """Generate resource for active/current records"""
        # Find status fields that indicate active records
        status_conditions = []
        
        # Priority 1: Status fields with enum values containing active-like terms
        for col in entity.columns:
            if col.classification == ColumnClassification.BUSINESS_STATUS and col.enum_values:
                col_lower = col.name.lower()
                
                # Common patterns for status fields
                if any(pattern in col_lower for pattern in ['status', 'state', 'active', 'enabled']):
                    active_values = self._get_active_like_values(col.enum_values)
                    if active_values:
                        values_str = ', '.join([f"'{v}'" for v in active_values])
                        status_conditions.append(f"{col.name} IN ({values_str})")
                        
            elif col.classification == ColumnClassification.BUSINESS_STATUS:
                col_lower = col.name.lower()
                
                # Boolean status fields
                if 'bool' in col.data_type.lower():
                    if 'is_' in col_lower or 'has_' in col_lower:
                        status_conditions.append(f"{col.name} = true")
        
        # Priority 2: If no status conditions found, try expiry dates
        if not status_conditions:
            for col in entity.columns:
                if col.classification == ColumnClassification.TEMPORAL:
                    # Only use actual DATE fields, not VARCHAR
                    if col.data_type.upper() == 'DATE' and ('expir' in col.name.lower() or 'end' in col.name.lower() or 'exp' in col.name.lower()):
                        status_conditions.append(f"{col.name} > CURRENT_DATE")
        
        if not status_conditions:
            return None
        
        resource_name = f"active_{entity.name}"
        description = f"Currently active {entity.name} records"
        
        sql = f"""
SELECT *
FROM {entity.primary_model.name}_v1
WHERE {' AND '.join(status_conditions)}
ORDER BY {self._get_order_column(entity)}
        """.strip()
        
        return {
            "mxcp": self.version,
            "resource": {
                "name": resource_name,
                "description": description,
                "uri": f"data://active/{entity.name}",
                "source": {
                    "code": sql
                },
                "enabled": True
            }
        }
    
    def _get_active_like_values(self, enum_values: List[str]) -> List[str]:
        """Find values that indicate 'active' state - domain agnostic"""
        active_patterns = [
            'active', 'enabled', 'current', 'valid', 'open', 'live',
            'published', 'approved', 'confirmed', 'available', 'running'
        ]
        
        return [
            value for value in enum_values 
            if any(pattern in value.lower() for pattern in active_patterns)
        ]
    
    def _generate_summary_resource(self, entity: BusinessEntity) -> Optional[Dict[str, Any]]:
        """Generate summary resource with pre-computed metrics"""
        metric_fields = [
            col for col in entity.columns
            if col.classification == ColumnClassification.METRIC
        ]
        
        if not metric_fields:
            return None
        
        # Find good grouping dimensions
        grouping_fields = []
        for col in entity.columns:
            if col.classification in [ColumnClassification.CATEGORICAL, ColumnClassification.GEOGRAPHIC]:
                if col.enum_values and len(col.enum_values) < 20:  # Reasonable cardinality
                    grouping_fields.append(col)
        
        if not grouping_fields:
            return None
        
        resource_name = f"{entity.name}_metrics_summary"
        description = f"Pre-computed metrics summary for {entity.name}"
        
        # Build aggregation query
        group_field = grouping_fields[0]
        metrics = []
        
        for metric in metric_fields[:5]:  # Limit metrics
            metrics.extend([
                f"SUM({metric.name}) as total_{metric.name}",
                f"AVG({metric.name}) as avg_{metric.name}",
                f"COUNT(DISTINCT CASE WHEN {metric.name} > 0 THEN {self._get_primary_key(entity)} END) as count_with_{metric.name}"
            ])
        
        sql = f"""
SELECT 
  'Summary' as metric_type,
  COUNT(*) as total_count,
  {', '.join(metrics)}
FROM {entity.primary_model.name}_v1
WHERE {' AND '.join(where_clauses) if where_clauses else '1=1'}
        """.strip()
        
        return {
            "mxcp": self.version,
            "resource": {
                "name": resource_name,
                "description": description,
                "uri": f"data://summary/{entity.name}",
                "source": {
                    "code": sql
                },
                "enabled": True
            }
        }
    
    def _generate_overview_resource(self, entities: Dict[str, BusinessEntity]) -> Optional[Dict[str, Any]]:
        """Generate cross-entity overview resource"""
        resource_name = "business_entities_overview"
        description = "Overview of all business entities with record counts and key metrics"
        
        # Build UNION query for overview
        union_parts = []
        
        for entity_name, entity in entities.items():
            # Find a good count field
            count_field = self._get_primary_key(entity)
            
            # Find a date field for recency
            date_field = None
            for col in entity.columns:
                if col.classification == ColumnClassification.TEMPORAL:
                    if any(word in col.name.lower() for word in ['created', 'updated', 'modified']):
                        date_field = col.name
                        break
            
            query_part = f"""
  SELECT 
    '{entity_name}' as entity_type,
    COUNT(DISTINCT {count_field}) as record_count,
    {f"MAX({date_field})::date" if date_field else "NULL"} as latest_record_date
  FROM {entity.primary_model.name}_v1
            """.strip()
            
            union_parts.append(query_part)
        
        sql = "\nUNION ALL\n".join(union_parts) + "\nORDER BY record_count DESC"
        
        return {
            "mxcp": self.version,
            "resource": {
                "name": resource_name,
                "description": description,
                "uri": f"data://overview/{entity.name}",
                "source": {
                    "code": sql
                },
                "enabled": True
            }
        }
    
    def _has_metrics(self, entity: BusinessEntity) -> bool:
        """Check if entity has metric fields"""
        return any(
            col.classification == ColumnClassification.METRIC
            for col in entity.columns
        )
    
    def _get_primary_key(self, entity: BusinessEntity) -> str:
        """Get primary key column"""
        for col in entity.columns:
            if col.is_primary_key:
                return col.name
        
        # Fallback to first identifier
        for col in entity.columns:
            if col.classification == ColumnClassification.IDENTIFIER:
                return col.name
        
        return entity.columns[0].name if entity.columns else "id"
    
    def _get_order_column(self, entity: BusinessEntity) -> str:
        """Get appropriate ordering column"""
        # Prefer creation date
        for col in entity.columns:
            if col.classification == ColumnClassification.TEMPORAL:
                if 'created' in col.name.lower():
                    return f"{col.name} DESC"
        
        # Fall back to primary key
        return self._get_primary_key(entity) 