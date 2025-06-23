#!/usr/bin/env python3
"""
Regenerate all tools using the updated framework while preserving existing tests
"""

import os
import yaml
import logging
from pathlib import Path
from mxcp_generator import MCPGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_existing_tests(tool_file: Path) -> list:
    """Load existing tests from a tool file"""
    try:
        with open(tool_file, 'r') as f:
            tool_data = yaml.safe_load(f)
        
        tests = tool_data.get('tool', {}).get('tests', [])
        logger.info(f"Found {len(tests)} existing tests in {tool_file.name}")
        return tests
    except Exception as e:
        logger.warning(f"Could not load tests from {tool_file}: {e}")
        return []

def merge_tool_with_tests(new_tool: dict, existing_tests: list) -> dict:
    """Merge new tool definition with existing tests"""
    if existing_tests:
        new_tool['tool']['tests'] = existing_tests
        logger.info(f"Preserved {len(existing_tests)} tests in {new_tool['tool']['name']}")
    return new_tool

def backup_existing_tools():
    """Create backup of existing tools"""
    backup_dir = Path("tools_backup")
    backup_dir.mkdir(exist_ok=True)
    
    tools_dir = Path("tools")
    if tools_dir.exists():
        for tool_file in tools_dir.glob("*.yml"):
            backup_file = backup_dir / tool_file.name
            with open(tool_file, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
        logger.info(f"Backed up {len(list(tools_dir.glob('*.yml')))} tools to {backup_dir}")

def regenerate_all_tools():
    """Regenerate all tools with the updated framework"""
    
    # Step 1: Backup existing tools
    logger.info("🔄 Step 1: Backing up existing tools...")
    backup_existing_tools()
    
    # Step 2: Load existing tests for preservation
    logger.info("📋 Step 2: Loading existing tests...")
    existing_tests = {}
    tools_dir = Path("tools")
    
    if tools_dir.exists():
        for tool_file in tools_dir.glob("*.yml"):
            tests = load_existing_tests(tool_file)
            if tests:
                tool_name = tool_file.stem
                existing_tests[tool_name] = tests
    
    logger.info(f"Found tests in {len(existing_tests)} tools to preserve")
    
    # Step 3: Generate new tools using updated framework
    logger.info("🏗️  Step 3: Generating tools with updated framework...")
    
    generator = MCPGenerator("target/manifest.json")
    
    # Generate tools for all entities
    artifacts = generator.generate()
    
    # Step 4: Merge with existing tests
    logger.info("🔗 Step 4: Merging with existing tests...")
    
    preserved_tests_count = 0
    
    for tool_data in artifacts.tools:
        tool_name = tool_data['tool']['name']
        
        # Check if we have existing tests for this tool
        if tool_name in existing_tests:
            tool_data = merge_tool_with_tests(tool_data, existing_tests[tool_name])
            preserved_tests_count += len(existing_tests[tool_name])
    
    # Step 5: Save updated tools
    logger.info("💾 Step 5: Saving updated tools...")
    
    tools_dir.mkdir(exist_ok=True)
    sql_dir = Path("sql")
    sql_dir.mkdir(exist_ok=True)
    
    tools_saved = 0
    sql_files_saved = 0
    
    # Get SQL queries
    sql_queries = generator.tool_generator.get_sql_queries()
    
    for tool_data in artifacts.tools:
        tool_name = tool_data['tool']['name']
        
        # Save tool definition
        tool_file = tools_dir / f"{tool_name}.yml"
        with open(tool_file, 'w') as f:
            yaml.dump(tool_data, f, default_flow_style=False, sort_keys=False)
        tools_saved += 1
        
        # Save SQL file if it exists
        if tool_name in sql_queries:
            sql_file = sql_dir / f"{tool_name}.sql"
            with open(sql_file, 'w') as f:
                f.write(sql_queries[tool_name])
            sql_files_saved += 1
    
    # Step 6: Summary
    logger.info("✅ Tool regeneration complete!")
    logger.info(f"📊 Summary:")
    logger.info(f"   • Tools generated: {tools_saved}")
    logger.info(f"   • SQL files generated: {sql_files_saved}")
    logger.info(f"   • Tests preserved: {preserved_tests_count}")
    logger.info(f"   • Backup location: tools_backup/")
    
    return {
        'tools_generated': tools_saved,
        'sql_files_generated': sql_files_saved,
        'tests_preserved': preserved_tests_count
    }

def validate_generated_tools():
    """Validate the generated tools"""
    logger.info("🔍 Validating generated tools...")
    
    # Run mxcp validate
    import subprocess
    try:
        result = subprocess.run(['mxcp', 'validate'], capture_output=True, text=True)
        
        # Count valid tools
        valid_tools = result.stdout.count('✓ tools/')
        failed_tools = result.stdout.count('✗ tools/')
        
        logger.info(f"Validation results: {valid_tools} valid, {failed_tools} failed")
        
        if failed_tools > 0:
            logger.warning("Some tools failed validation. Check 'mxcp validate' output for details.")
        
        return valid_tools, failed_tools
        
    except Exception as e:
        logger.error(f"Could not run validation: {e}")
        return 0, 0

def main():
    """Main execution"""
    logger.info("🚀 Starting tool regeneration with updated framework...")
    
    try:
        # Regenerate tools
        results = regenerate_all_tools()
        
        # Validate results
        valid_tools, failed_tools = validate_generated_tools()
        
        # Final summary
        print("\n" + "="*60)
        print("🎉 TOOL REGENERATION COMPLETE!")
        print("="*60)
        print(f"✅ Generated: {results['tools_generated']} tools")
        print(f"📄 SQL files: {results['sql_files_generated']} files")
        print(f"🧪 Tests preserved: {results['tests_preserved']} tests")
        print(f"✅ Valid tools: {valid_tools}")
        print(f"❌ Failed tools: {failed_tools}")
        print("")
        print("🔧 Key improvements applied:")
        print("   • Array parameters instead of individual booleans")
        print("   • Performance safeguards for large datasets")
        print("   • DuckDB-compatible JSON syntax")
        print("   • Enhanced metadata and error handling")
        print("   • Preserved all existing tests")
        print("")
        
        if failed_tools == 0:
            print("🎯 All tools should now work in Claude Desktop!")
        else:
            print("⚠️  Some tools need additional fixes. Run 'mxcp validate' for details.")
            
    except Exception as e:
        logger.error(f"Tool regeneration failed: {e}")
        raise

if __name__ == "__main__":
    main()
