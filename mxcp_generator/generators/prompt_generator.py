"""
Prompt generator for creating MXCP prompt definitions
"""

import logging
from typing import Dict, List, Any, Optional
from ..analyzers import BusinessEntity, ColumnClassification

logger = logging.getLogger(__name__)


class PromptGenerator:
    """
    Generates MXCP prompt definitions to guide AI interactions
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.version = "1.0.0"
    
    def generate_prompts(
        self, 
        entities: Dict[str, BusinessEntity], 
        tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate prompts for guiding AI interactions with the data
        
        Args:
            entities: Dictionary of business entities
            tools: List of generated tools
            
        Returns:
            List of MXCP prompt definitions
        """
        prompts = []
        
        # Generate exploration prompt
        exploration_prompt = self._generate_exploration_prompt(entities, tools)
        if exploration_prompt:
            prompts.append(exploration_prompt)
        
        # Generate entity-specific prompts
        for entity_name, entity in entities.items():
            entity_prompt = self._generate_entity_prompt(entity, tools)
            if entity_prompt:
                prompts.append(entity_prompt)
        
        # Generate analysis prompt if there are metrics
        if self._has_analytics_tools(tools):
            analysis_prompt = self._generate_analysis_prompt(entities, tools)
            if analysis_prompt:
                prompts.append(analysis_prompt)
        
        logger.info(f"Generated {len(prompts)} prompts")
        return prompts
    
    def _generate_exploration_prompt(
        self, 
        entities: Dict[str, BusinessEntity],
        tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a general exploration prompt"""
        prompt_name = "explore_business_data"
        description = "Guide AI to effectively explore and understand the business data"
        
        # Extract tool names and descriptions
        tool_list = []
        for tool in tools[:10]:  # Limit to prevent prompt from being too long
            tool_info = tool['tool']
            tool_list.append(f"- `{tool_info['name']}`: {tool_info['description']}")
        
        # Build entity descriptions
        entity_descriptions = []
        for entity_name, entity in entities.items():
            desc = f"**{entity_name.replace('_', ' ').title()}**"
            if entity.business_description:
                desc += f": {entity.business_description}"
            else:
                # Auto-generate description based on columns
                key_columns = [
                    col.name for col in entity.columns[:5]
                    if col.classification in [
                        ColumnClassification.DESCRIPTIVE,
                        ColumnClassification.IDENTIFIER,
                        ColumnClassification.BUSINESS_STATUS
                    ]
                ]
                if key_columns:
                    desc += f" (key fields: {', '.join(key_columns)})"
            entity_descriptions.append(desc)
        
        system_prompt = f"""You have access to business data with the following entities:

{chr(10).join(entity_descriptions)}

## Available Operations

{chr(10).join(tool_list)}

## Common Questions You Can Answer

- Search for specific records by name or identifier
- Filter records by status or other criteria
- Analyze trends and patterns over time
- Compare metrics across different dimensions
- Identify relationships between entities

## Tips for Effective Queries

1. Start with search tools to find specific records
2. Use filter tools to narrow down results
3. Apply analytics tools for aggregated insights
4. Combine multiple tools for comprehensive analysis

## Example Queries

- "Find all active businesses in Dubai"
- "Show me license expiration trends"
- "What are the top revenue-generating activities?"
- "Identify businesses with compliance issues"

Remember to be specific in your queries and use the appropriate tools for each task."""
        
        return {
            "mxcp": self.version,
            "prompt": {
                "name": prompt_name,
                "description": description,
                "parameters": [],
                "messages": [
                    {
                        "role": "system",
                        "type": "text",
                        "prompt": system_prompt
                    },
                    {
                        "role": "user",
                        "type": "text",
                        "prompt": "Welcome! I can help you explore and analyze business data. What would you like to know?"
                    }
                ],
                "enabled": True
            }
        }
    
    def _generate_entity_prompt(
        self, 
        entity: BusinessEntity,
        tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate entity-specific prompt"""
        prompt_name = f"analyze_{entity.name}"
        description = f"Guide AI to effectively analyze {entity.name} data"
        
        # Find tools related to this entity
        entity_tools = [
            tool for tool in tools
            if entity.name in tool['tool']['name']
        ]
        
        # Identify key fields by classification
        key_fields = {
            "identifiers": [],
            "descriptive": [],
            "status": [],
            "temporal": [],
            "metrics": []
        }
        
        for col in entity.columns:
            if col.classification == ColumnClassification.IDENTIFIER:
                key_fields["identifiers"].append(col.name)
            elif col.classification == ColumnClassification.DESCRIPTIVE:
                key_fields["descriptive"].append(col.name)
            elif col.classification == ColumnClassification.BUSINESS_STATUS:
                status_info = f"{col.name}"
                if col.enum_values:
                    status_info += f" (values: {', '.join(col.enum_values[:5])})"
                key_fields["status"].append(status_info)
            elif col.classification == ColumnClassification.TEMPORAL:
                key_fields["temporal"].append(col.name)
            elif col.classification == ColumnClassification.METRIC:
                key_fields["metrics"].append(col.name)
        
        # Build system prompt
        system_prompt = f"""## {entity.name.replace('_', ' ').title()} Analysis Guide

{entity.business_description or f'This entity contains data about {entity.name}.'}

### Key Fields

**Identifiers**: {', '.join(key_fields['identifiers'][:3]) or 'None'}
**Descriptive Fields**: {', '.join(key_fields['descriptive'][:3]) or 'None'}
**Status Fields**: {', '.join(key_fields['status'][:3]) or 'None'}
**Date Fields**: {', '.join(key_fields['temporal'][:3]) or 'None'}
**Metrics**: {', '.join(key_fields['metrics'][:3]) or 'None'}

### Available Tools for {entity.name}

{chr(10).join([f"- `{t['tool']['name']}`: {t['tool']['description']}" for t in entity_tools[:5]])}

### Common Analysis Patterns

1. **Find Specific Records**: Use search tools with descriptive fields
2. **Status Analysis**: Filter by status fields to understand current state
3. **Temporal Analysis**: Use date fields to analyze trends over time
4. **Metric Analysis**: Aggregate and compare metric fields

### Example Queries

- "Find {entity.name} by name"
- "Show all active {entity.name}"
- "Analyze {entity.name} trends over the last year"
- "Compare {entity.name} metrics by category"
"""
        
        return {
            "mxcp": self.version,
            "prompt": {
                "name": prompt_name,
                "description": description,
                "parameters": [],
                "messages": [
                    {
                        "role": "system",
                        "type": "text",
                        "prompt": system_prompt
                    },
                    {
                        "role": "user",
                        "type": "text",
                        "prompt": f"I'm ready to help you analyze {entity.name} data. What would you like to know?"
                    }
                ],
                "enabled": True
            }
        }
    
    def _generate_analysis_prompt(
        self,
        entities: Dict[str, BusinessEntity],
        tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate prompt for analytical queries"""
        prompt_name = "perform_business_analysis"
        description = "Guide AI to perform complex business analysis"
        
        # Find analytics tools
        analytics_tools = [
            tool for tool in tools
            if 'analyz' in tool['tool']['name'] or 'metric' in tool['tool']['name']
        ]
        
        # Find entities with metrics
        entities_with_metrics = [
            entity_name for entity_name, entity in entities.items()
            if any(col.classification == ColumnClassification.METRIC for col in entity.columns)
        ]
        
        system_prompt = f"""## Business Analysis Guide

You have access to analytical tools for performing complex business analysis.

### Entities with Metrics

{', '.join(entities_with_metrics)}

### Analytics Tools

{chr(10).join([f"- `{t['tool']['name']}`: {t['tool']['description']}" for t in analytics_tools[:7]])}

### Analysis Strategies

1. **Trend Analysis**
   - Use temporal grouping to identify patterns over time
   - Compare metrics across different time periods
   - Look for seasonal variations

2. **Comparative Analysis**
   - Group by categorical dimensions
   - Compare metrics across segments
   - Identify outliers and anomalies

3. **Performance Analysis**
   - Calculate aggregated metrics
   - Identify top and bottom performers
   - Analyze distribution patterns

4. **Relationship Analysis**
   - Explore connections between entities
   - Analyze correlated metrics
   - Identify cause-and-effect patterns

### Best Practices

- Start with high-level summaries before drilling down
- Use appropriate time periods for your analysis
- Consider multiple dimensions for comprehensive insights
- Validate findings by cross-referencing different tools

### Example Analysis Queries

- "What are the revenue trends over the last quarter?"
- "Compare performance metrics across different regions"
- "Identify the top 10 performers by key metrics"
- "Analyze the relationship between different business factors"
"""
        
        return {
            "mxcp": self.version,
            "prompt": {
                "name": prompt_name,
                "description": description,
                "parameters": [],
                "messages": [
                    {
                        "role": "system",
                        "type": "text",
                        "prompt": system_prompt
                    },
                    {
                        "role": "user",
                        "type": "text",
                        "prompt": "I'm ready to help you perform business analysis. What insights are you looking for?"
                    }
                ],
                "enabled": True
            }
        }
    
    def _has_analytics_tools(self, tools: List[Dict[str, Any]]) -> bool:
        """Check if analytics tools were generated"""
        return any(
            'analyz' in tool['tool']['name'] or 'metric' in tool['tool']['name']
            for tool in tools
        ) 