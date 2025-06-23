#!/usr/bin/env python3
"""
Verification script to check that multi-model integration worked correctly
"""

import yaml
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_integration():
    """Verify that the integration was successful"""
    logger.info("🔍 Verifying multi-model tools integration...")
    
    tools_dir = Path("tools")
    sql_dir = Path("sql")
    
    # Expected tools
    expected_tools = [
        "find_licenses.yml",
        "aggregate_licenses.yml", 
        "timeseries_licenses.yml",
        "geo_licenses.yml",
        "list_licenses_categories.yml",
        "find_license_owners.yml",  # New multi-model tool
        "aggregate_license_owners.yml",
        "timeseries_license_owners.yml", 
        "list_license_owners_categories.yml"
    ]
    
    # Check tools exist
    missing_tools = []
    tools_with_tests = []
    multimodel_tools = []
    
    for tool_name in expected_tools:
        tool_path = tools_dir / tool_name
        if not tool_path.exists():
            missing_tools.append(tool_name)
            continue
            
        # Load and check tool
        with open(tool_path, 'r') as f:
            tool_data = yaml.safe_load(f)
        
        # Check for preserved tests
        if tool_data.get('tool', {}).get('tests'):
            tests = tool_data['tool']['tests']
            tools_with_tests.append(f"{tool_name} ({len(tests)} tests)")
        
        # Check for embed parameter (multi-model)
        parameters = tool_data.get('tool', {}).get('parameters', [])
        embed_param = next((p for p in parameters if p['name'] == 'embed'), None)
        if embed_param:
            enum_values = embed_param.get('items', {}).get('enum', [])
            multimodel_tools.append(f"{tool_name} (embed: {enum_values})")
        
        # Check corresponding SQL exists
        sql_name = tool_name.replace('.yml', '.sql')
        sql_path = sql_dir / sql_name
        if not sql_path.exists():
            logger.warning(f"⚠️  Missing SQL file: {sql_name}")
    
    # Report results
    logger.info(f"📊 Integration Verification Results:")
    logger.info(f"   ✅ Tools found: {len(expected_tools) - len(missing_tools)}/{len(expected_tools)}")
    
    if missing_tools:
        logger.error(f"   ❌ Missing tools: {', '.join(missing_tools)}")
    
    if tools_with_tests:
        logger.info(f"   🧪 Tools with preserved tests: {len(tools_with_tests)}")
        for tool in tools_with_tests:
            logger.info(f"      • {tool}")
    
    if multimodel_tools:
        logger.info(f"   🔗 Multi-model tools: {len(multimodel_tools)}")
        for tool in multimodel_tools:
            logger.info(f"      • {tool}")
    else:
        logger.warning(f"   ⚠️  No multi-model tools found!")
    
    # Check other artifacts
    other_dirs = ["resources", "prompts", "tests"]
    for dir_name in other_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            file_count = len(list(dir_path.glob("*.yml")))
            logger.info(f"   📁 {dir_name}/: {file_count} files")
    
    # Overall status
    if not missing_tools and multimodel_tools:
        logger.info(f"   🎉 Integration verification: SUCCESS!")
        return True
    else:
        logger.error(f"   ❌ Integration verification: FAILED!")
        return False

if __name__ == "__main__":
    success = verify_integration()
    exit(0 if success else 1) 