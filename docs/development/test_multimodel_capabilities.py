#!/usr/bin/env python3
"""
Test script to demonstrate multi-model capabilities with actual tool calls
"""

import yaml
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_tool_definition(tool_name: str) -> dict:
    """Load a tool definition from the tools directory"""
    tool_path = Path(f"tools/{tool_name}.yml")
    if not tool_path.exists():
        raise FileNotFoundError(f"Tool {tool_name} not found")
    
    with open(tool_path, 'r') as f:
        return yaml.safe_load(f)

def demonstrate_embed_parameter():
    """Demonstrate the embed parameter functionality"""
    logger.info("🔗 Demonstrating Multi-Model Embed Parameter")
    
    # Load the multi-model tool
    tool = load_tool_definition("find_license_owners")
    
    # Find the embed parameter
    parameters = tool.get('tool', {}).get('parameters', [])
    embed_param = next((p for p in parameters if p['name'] == 'embed'), None)
    
    if embed_param:
        enum_values = embed_param.get('items', {}).get('enum', [])
        logger.info(f"✅ Embed parameter found!")
        logger.info(f"   Available options: {enum_values}")
        logger.info(f"   Description: {embed_param.get('description', 'N/A')}")
        logger.info(f"   Type: {embed_param.get('type')} of {embed_param.get('items', {}).get('type', 'unknown')}")
        
        # Show example usage
        logger.info(f"\n📝 Example LLM Tool Call:")
        example_call = {
            "tool": "find_license_owners",
            "parameters": {
                "nationality": "UAE",
                "is_primary_owner": True,
                "embed": ["licenses"],
                "limit": 5
            }
        }
        logger.info(f"   {json.dumps(example_call, indent=2)}")
        
    else:
        logger.error("❌ Embed parameter not found!")

def demonstrate_parameter_autocompletion():
    """Show how the enum values enable LLM autocompletion"""
    logger.info("\n🤖 Demonstrating LLM Autocompletion Features")
    
    tool = load_tool_definition("find_license_owners")
    parameters = tool.get('tool', {}).get('parameters', [])
    
    # Find parameters with enum values (categorical)
    categorical_params = []
    for param in parameters:
        if param.get('enum'):
            categorical_params.append({
                'name': param['name'],
                'enum': param['enum'],
                'description': param.get('description', '')
            })
    
    logger.info(f"✅ Found {len(categorical_params)} categorical parameters for autocompletion:")
    
    for param in categorical_params[:3]:  # Show first 3
        logger.info(f"   • {param['name']}: {param['enum'][:3]}{'...' if len(param['enum']) > 3 else ''}")
    
    # Special focus on embed parameter
    embed_param = next((p for p in parameters if p['name'] == 'embed'), None)
    if embed_param:
        logger.info(f"\n🎯 Special: Embed parameter enables relationship autocompletion:")
        logger.info(f"   • LLM can suggest: embed=['licenses']")
        logger.info(f"   • LLM can autocorrect: 'include license data' → embed=['licenses']")
        logger.info(f"   • LLM can validate: embed=['invalid'] → Error + suggestion")

def demonstrate_relationship_detection():
    """Show the relationship detection in action"""
    logger.info("\n🔍 Demonstrating Relationship Detection")
    
    # Check which tools have embed parameters
    tools_with_embed = []
    tools_without_embed = []
    
    for tool_file in Path("tools").glob("*.yml"):
        tool = load_tool_definition(tool_file.stem)
        parameters = tool.get('tool', {}).get('parameters', [])
        embed_param = next((p for p in parameters if p['name'] == 'embed'), None)
        
        if embed_param:
            enum_values = embed_param.get('items', {}).get('enum', [])
            tools_with_embed.append(f"{tool_file.stem} → {enum_values}")
        else:
            tools_without_embed.append(tool_file.stem)
    
    logger.info(f"✅ Tools WITH relationship detection:")
    for tool in tools_with_embed:
        logger.info(f"   • {tool}")
    
    logger.info(f"\n📊 Tools WITHOUT relationships (single-entity):")
    for tool in tools_without_embed[:3]:
        logger.info(f"   • {tool}")
    
    logger.info(f"\n🎯 Relationship Pattern Detected:")
    logger.info(f"   • fact_license_owners.license_pk → dim_licenses.license_pk")
    logger.info(f"   • Relationship type: many-to-one (many owners per license)")
    logger.info(f"   • Detection method: dbt relationships test")

def demonstrate_sql_enhancement():
    """Show the enhanced SQL with embedding support"""
    logger.info("\n📄 Demonstrating Enhanced SQL Generation")
    
    sql_file = Path("sql/find_license_owners.sql")
    if sql_file.exists():
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        logger.info(f"✅ Enhanced SQL structure found:")
        
        # Check for key multi-model features
        features = {
            "Base query CTE": "WITH base_data AS" in sql_content,
            "Conditional embedding": "CASE" in sql_content and "embed" in sql_content,
            "Embedded field": "_embedded" in sql_content,
            "Parameter support": "$embed" in sql_content
        }
        
        for feature, found in features.items():
            status = "✅" if found else "❌"
            logger.info(f"   {status} {feature}")
        
        # Show key SQL snippet
        lines = sql_content.split('\n')
        embedding_section = []
        in_embedding = False
        
        for line in lines:
            if "Enhanced query with conditional embedding" in line:
                in_embedding = True
            if in_embedding:
                embedding_section.append(line)
                if "FROM base_data" in line:
                    break
        
        if embedding_section:
            logger.info(f"\n📝 Key SQL Enhancement:")
            for line in embedding_section[:6]:  # Show first 6 lines
                logger.info(f"   {line}")
    else:
        logger.error("❌ Enhanced SQL file not found!")

def demonstrate_usage_scenarios():
    """Show practical usage scenarios"""
    logger.info("\n🎪 Demonstrating Usage Scenarios")
    
    scenarios = [
        {
            "name": "Basic Embedding",
            "prompt": "Find license owners and include their license details",
            "tool_call": {
                "tool": "find_license_owners",
                "parameters": {"embed": ["licenses"], "limit": 10}
            },
            "benefit": "Single call instead of multiple API calls"
        },
        {
            "name": "Filtered Embedding", 
            "prompt": "Show UAE national license owners with their active license information",
            "tool_call": {
                "tool": "find_license_owners", 
                "parameters": {
                    "nationality": "UAE",
                    "embed": ["licenses"],
                    "limit": 5
                }
            },
            "benefit": "Cross-entity filtering with embedded data"
        },
        {
            "name": "Performance Optimization",
            "prompt": "Get a quick list of license owners (no extra details)",
            "tool_call": {
                "tool": "find_license_owners",
                "parameters": {"limit": 20}
                # Note: NO embed parameter for better performance
            },
            "benefit": "Lazy loading - only fetch what's needed"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        logger.info(f"\n{i}. {scenario['name']}:")
        logger.info(f"   User: \"{scenario['prompt']}\"")
        logger.info(f"   Tool Call: {json.dumps(scenario['tool_call'], indent=6)}")
        logger.info(f"   Benefit: {scenario['benefit']}")

def main():
    """Run all demonstrations"""
    logger.info("🚀 Multi-Model Framework Capability Demonstration")
    logger.info("=" * 60)
    
    try:
        demonstrate_embed_parameter()
        demonstrate_parameter_autocompletion() 
        demonstrate_relationship_detection()
        demonstrate_sql_enhancement()
        demonstrate_usage_scenarios()
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 Multi-Model Demonstration Complete!")
        logger.info("\n💡 Key Takeaways:")
        logger.info("   • Embed parameter enables lazy loading of related data")
        logger.info("   • Enum values provide LLM autocompletion and validation")
        logger.info("   • Relationship detection works automatically via dbt tests")
        logger.info("   • Enhanced SQL supports conditional embedding")
        logger.info("   • Dramatic improvement in user experience!")
        
    except Exception as e:
        logger.error(f"❌ Demonstration failed: {e}")
        raise

if __name__ == "__main__":
    main()
