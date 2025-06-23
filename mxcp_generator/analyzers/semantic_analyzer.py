"""
Semantic analyzer for extracting business meaning from dbt models
"""

import re
import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ColumnClassification(Enum):
    """Semantic classification of database columns"""
    IDENTIFIER = "identifier"
    BUSINESS_STATUS = "business_status"
    TEMPORAL = "temporal"
    GEOGRAPHIC = "geographic"
    MONETARY = "monetary"
    DESCRIPTIVE = "descriptive"
    METRIC = "metric"
    CATEGORICAL = "categorical"
    UNKNOWN = "unknown"


@dataclass
class ColumnInfo:
    """Information about a database column"""
    name: str
    data_type: str
    classification: ColumnClassification
    description: Optional[str] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    referenced_table: Optional[str] = None
    referenced_column: Optional[str] = None
    enum_values: List[str] = field(default_factory=list)
    relationships: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class BusinessEntity:
    """Represents a business entity extracted from dbt models"""
    name: str
    primary_model: 'DbtModel'
    columns: List[ColumnInfo]
    related_models: List['DbtModel'] = field(default_factory=list)
    relationships: Dict[str, 'RelationshipInfo'] = field(default_factory=dict)
    business_description: Optional[str] = None


@dataclass
class RelationshipInfo:
    """Information about relationships between entities"""
    from_entity: str
    to_entity: str
    relationship_type: str  # one-to-many, many-to-one, many-to-many
    join_keys: List[Tuple[str, str]]  # List of (from_column, to_column) pairs


@dataclass
class DbtModel:
    """Simplified representation of a dbt model"""
    name: str
    table_name: str  # Actual table name/alias in database
    schema: str
    description: Optional[str]
    columns: Dict[str, Dict]
    tags: List[str] = field(default_factory=list)
    meta: Dict = field(default_factory=dict)


class SemanticAnalyzer:
    """
    Analyzes dbt models to extract semantic meaning and business entities
    """
    
    # Pattern mappings for column classification
    CLASSIFICATION_PATTERNS = {
        ColumnClassification.IDENTIFIER: [
            r'.*_id$', r'.*_key$', r'.*_code$', r'.*_number$', r'.*_no$',
            r'^id$', r'^key$', r'^code$'
        ],
        ColumnClassification.BUSINESS_STATUS: [
            r'.*_status$', r'.*_state$', r'^is_.*', r'^has_.*',
            r'.*_flag$', r'^active$', r'^enabled$'
        ],
        ColumnClassification.TEMPORAL: [
            r'.*_date$', r'.*_time$', r'.*_at$', r'^created_.*', r'^updated_.*',
            r'^deleted_.*', r'.*_timestamp$', r'^date$', r'^time$'
        ],
        ColumnClassification.GEOGRAPHIC: [
            r'.*_city$', r'.*_country$', r'.*_location$', r'.*_address$',
            r'.*_region$', r'.*_state$', r'.*_zip$', r'.*_postal.*',
            r'^latitude$', r'^longitude$', r'^lat$', r'^lon$', r'^lng$'
        ],
        ColumnClassification.MONETARY: [
            r'.*_amount$', r'.*_price$', r'.*_cost$', r'.*_revenue$',
            r'.*_fee$', r'.*_payment$', r'.*_balance$', r'^amount$', r'^price$'
        ],
        ColumnClassification.DESCRIPTIVE: [
            r'.*_name$', r'.*_description$', r'.*_title$', r'.*_text$',
            r'^name$', r'^description$', r'^title$', r'.*_comment$'
        ],
        ColumnClassification.METRIC: [
            r'.*_count$', r'.*_total$', r'.*_sum$', r'.*_avg$',
            r'.*_min$', r'.*_max$', r'.*_percentage$', r'.*_ratio$'
        ]
    }
    
    def __init__(self):
        self.compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[ColumnClassification, List[re.Pattern]]:
        """Compile regex patterns for efficiency"""
        compiled = {}
        for classification, patterns in self.CLASSIFICATION_PATTERNS.items():
            compiled[classification] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
        return compiled
    
    def extract_entities(self, manifest: Dict) -> Dict[str, BusinessEntity]:
        """
        Extract business entities from dbt manifest
        
        Args:
            manifest: Parsed dbt manifest.json
            
        Returns:
            Dictionary of entity name to BusinessEntity
        """
        entities = {}
        dbt_models = self._parse_dbt_models(manifest)
        
        # First pass: identify primary entities (usually dim_ tables)
        for model_name, model in dbt_models.items():
            if self._is_primary_entity(model):
                entity_name = self._extract_entity_name(model.name)
                entity = self._create_business_entity(model)
                entities[entity_name] = entity
        
        # Second pass: find related models and relationships
        for entity_name, entity in entities.items():
            self._find_related_models(entity, dbt_models)
            self._detect_relationships(entity, entities, dbt_models)
        
        logger.info(f"Extracted {len(entities)} business entities")
        return entities
    
    def _parse_dbt_models(self, manifest: Dict) -> Dict[str, DbtModel]:
        """Parse dbt models from manifest"""
        models = {}
        
        # First, extract test information
        column_tests = {}  # model_name -> column_name -> tests
        relationship_tests = {}  # model_name -> column_name -> relationship_info
        
        for node_id, node in manifest.get('nodes', {}).items():
            if node.get('resource_type') == 'test':
                test_metadata = node.get('test_metadata', {})
                test_name = test_metadata.get('name')
                
                if test_name == 'accepted_values':
                    # Extract model and column info for enum values
                    attached_node = node.get('attached_node', '')
                    column_name = node.get('column_name', '')
                    values = test_metadata.get('kwargs', {}).get('values', [])
                    
                    # Extract model name from attached_node (e.g., "model.project.dim_licenses.v1")
                    if attached_node and column_name and values:
                        parts = attached_node.split('.')
                        if len(parts) >= 3:
                            model_name = parts[2]  # Get the model name
                            if model_name not in column_tests:
                                column_tests[model_name] = {}
                            if column_name not in column_tests[model_name]:
                                column_tests[model_name][column_name] = []
                            column_tests[model_name][column_name].extend(values)
                
                elif test_name == 'relationships':
                    # Extract relationship information
                    attached_node = node.get('attached_node', '')
                    column_name = node.get('column_name', '')
                    kwargs = test_metadata.get('kwargs', {})
                    to_ref = kwargs.get('to', '')
                    field = kwargs.get('field', '')
                    
                    if attached_node and column_name and to_ref and field:
                        parts = attached_node.split('.')
                        if len(parts) >= 3:
                            model_name = parts[2]  # Get the model name
                            
                            # Extract target model from ref() function
                            # e.g., "ref('dim_licenses')" -> "dim_licenses"
                            ref_match = re.search(r"ref\('([^']+)'\)", to_ref)
                            if ref_match:
                                target_model = ref_match.group(1)
                                
                                if model_name not in relationship_tests:
                                    relationship_tests[model_name] = {}
                                if column_name not in relationship_tests[model_name]:
                                    relationship_tests[model_name][column_name] = []
                                
                                relationship_tests[model_name][column_name].append({
                                    'target_model': target_model,
                                    'target_field': field,
                                    'source_field': column_name
                                })
        
        # Now parse models and enrich with test data
        for node_id, node in manifest.get('nodes', {}).items():
            if node.get('resource_type') == 'model':
                # Only process mart models
                if 'marts' in node.get('path', ''):
                    model_name = node['name']
                    columns = node.get('columns', {})
                    
                    # Enrich columns with enum values from tests
                    if model_name in column_tests:
                        for col_name, col_info in columns.items():
                            if col_name in column_tests[model_name]:
                                # Add enum values to column info
                                if 'enum_values' not in col_info:
                                    col_info['enum_values'] = []
                                col_info['enum_values'] = column_tests[model_name][col_name]
                    
                    # Enrich columns with relationship information
                    if model_name in relationship_tests:
                        for col_name, col_info in columns.items():
                            if col_name in relationship_tests[model_name]:
                                col_info['relationships'] = relationship_tests[model_name][col_name]
                    
                    model = DbtModel(
                        name=model_name,
                        table_name=node.get('alias', model_name),  # Use alias if available, fallback to model name
                        schema=node.get('schema', 'public'),
                        description=node.get('description'),
                        columns=columns,
                        tags=node.get('tags', []),
                        meta=node.get('meta', {})
                    )
                    models[model.name] = model
        
        return models
    
    def _is_primary_entity(self, model: DbtModel) -> bool:
        """Determine if a model represents a primary business entity"""
        # Both dimension and fact tables are primary entities
        return model.name.startswith('dim_') or model.name.startswith('fact_')
    
    def _extract_entity_name(self, model_name: str) -> str:
        """Extract clean entity name from model name"""
        # Remove prefixes like dim_, fact_
        for prefix in ['dim_', 'fact_', 'bridge_']:
            if model_name.startswith(prefix):
                return model_name[len(prefix):]
        return model_name
    
    def _create_business_entity(self, model: DbtModel) -> BusinessEntity:
        """Create a business entity from a dbt model"""
        columns = []
        
        for col_name, col_info in model.columns.items():
            column = ColumnInfo(
                name=col_name,
                data_type=col_info.get('data_type', 'unknown'),
                classification=self._classify_column(col_name, col_info),
                description=col_info.get('description'),
                is_primary_key=col_info.get('is_primary_key', False)
            )
            
            # Extract enum values from tests
            enum_values = self._extract_enum_values(col_info)
            if enum_values:
                column.enum_values = enum_values
            
            # Extract relationship metadata from tests
            relationships = col_info.get('relationships', [])
            if relationships:
                column.relationships = relationships
            
            columns.append(column)
        
        return BusinessEntity(
            name=self._extract_entity_name(model.name),
            primary_model=model,
            columns=columns,
            business_description=model.description
        )
    
    def _classify_column(self, col_name: str, col_info: Dict) -> ColumnClassification:
        """Classify a column based on its name and metadata"""
        # Check metadata hints first
        if 'classification' in col_info.get('meta', {}):
            try:
                return ColumnClassification(col_info['meta']['classification'])
            except ValueError:
                pass
        
        # If column has accepted_values test, it's likely categorical
        if self._has_enum_values(col_info):
            return ColumnClassification.CATEGORICAL
        
        # Use pattern matching
        for classification, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.match(col_name):
                    return classification
        
        # Check data type hints
        data_type = col_info.get('data_type', '').lower()
        if 'bool' in data_type:
            return ColumnClassification.BUSINESS_STATUS
        elif any(t in data_type for t in ['date', 'time']):
            return ColumnClassification.TEMPORAL
        elif any(t in data_type for t in ['decimal', 'numeric', 'money']):
            return ColumnClassification.MONETARY
        
        # Default to CATEGORICAL for string types that don't match other patterns
        if data_type in ['varchar', 'string', 'text', 'char']:
            return ColumnClassification.CATEGORICAL
        
        return ColumnClassification.UNKNOWN
    
    def _has_enum_values(self, col_info: Dict) -> bool:
        """Check if column has enum values from tests"""
        # Check if enum_values were added from manifest parsing
        if col_info.get('enum_values'):
            return True
            
        # Legacy check for tests in column definition
        for test in col_info.get('tests', []):
            if isinstance(test, dict) and 'accepted_values' in test:
                return True
        return False
    
    def _extract_enum_values(self, col_info: Dict) -> List[str]:
        """Extract enum values from column tests"""
        enum_values = []
        
        # First check if enum_values were added from manifest parsing
        if 'enum_values' in col_info:
            return col_info['enum_values']
        
        # Legacy: Look for accepted_values test in column definition
        for test in col_info.get('tests', []):
            if isinstance(test, dict) and 'accepted_values' in test:
                values = test['accepted_values'].get('values', [])
                enum_values.extend(values)
        
        return enum_values
    
    def _find_related_models(self, entity: BusinessEntity, all_models: Dict[str, DbtModel]):
        """Find models related to this entity"""
        entity_keywords = [entity.name, entity.primary_model.name]
        
        for model_name, model in all_models.items():
            if model == entity.primary_model:
                continue
            
            # Check if model name contains entity name
            if any(keyword in model_name for keyword in entity_keywords):
                entity.related_models.append(model)
                continue
            
            # Check for foreign key references
            for col_name, col_info in model.columns.items():
                if self._is_foreign_key_to(col_name, entity):
                    entity.related_models.append(model)
                    break
    
    def _is_foreign_key_to(self, column_name: str, entity: BusinessEntity) -> bool:
        """Check if a column is likely a foreign key to an entity"""
        # Simple heuristic: column name contains entity name and ends with _id or _key
        entity_name = entity.name.lower()
        col_lower = column_name.lower()
        
        return (entity_name in col_lower and 
                any(col_lower.endswith(suffix) for suffix in ['_id', '_key']))
    
    def _detect_relationships(
        self, 
        entity: BusinessEntity, 
        all_entities: Dict[str, BusinessEntity],
        all_models: Dict[str, DbtModel]
    ):
        """Detect relationships between entities"""
        # Look for foreign keys in the entity's columns
        for column in entity.columns:
            if column.classification == ColumnClassification.IDENTIFIER:
                # Check if this references another entity
                for other_name, other_entity in all_entities.items():
                    if other_name != entity.name and other_name in column.name:
                        # Found potential relationship
                        rel_info = RelationshipInfo(
                            from_entity=entity.name,
                            to_entity=other_name,
                            relationship_type="many-to-one",
                            join_keys=[(column.name, self._find_primary_key(other_entity))]
                        )
                        entity.relationships[f"{entity.name}_to_{other_name}"] = rel_info
    
    def _find_primary_key(self, entity: BusinessEntity) -> str:
        """Find the primary key column of an entity"""
        for column in entity.columns:
            if column.is_primary_key:
                return column.name
        
        # Fallback: look for common PK patterns
        for column in entity.columns:
            if column.classification == ColumnClassification.IDENTIFIER:
                if column.name in ['id', f'{entity.name}_id', f'{entity.name}_key']:
                    return column.name
        
        # Last resort: first identifier column
        for column in entity.columns:
            if column.classification == ColumnClassification.IDENTIFIER:
                return column.name
        
        return 'id'  # Default 