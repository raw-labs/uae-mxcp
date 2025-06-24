#!/usr/bin/env python3
"""
Fix tool parameters to match what their SQL files actually expect.
"""

import yaml
import re
from pathlib import Path

def extract_sql_parameters(sql_file_path):
    """Extract parameter names from a SQL file."""
    with open(sql_file_path, 'r') as f:
        content = f.read()
    
    # Find all $parameter_name references
    parameters = set()
    for match in re.finditer(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', content):
        param_name = match.group(1)
        parameters.add(param_name)
    
    return sorted(parameters)

def create_parameter_definition(param_name):
    """Create a parameter definition based on the parameter name."""
    base_def = {
        "name": param_name,
        "type": "string",
        "default": None
    }
    
    # Add descriptions based on parameter patterns
    if param_name in ['page', 'page_size']:
        if param_name == 'page':
            base_def.update({
                "type": "integer",
                "description": "Page number (1-based)",
                "default": 1,
                "minimum": 1
            })
        else:
            base_def.update({
                "type": "integer", 
                "description": "Number of records per page",
                "default": 20,
                "minimum": 1,
                "maximum": 1000
            })
    elif param_name in ['group_by', 'metrics']:
        if param_name == 'group_by':
            base_def.update({
                "description": "Comma-separated list of columns to group by (max 2)",
                "examples": ["emirate_name_en,bl_status_en"]
            })
        else:
            base_def.update({
                "description": "Comma-separated list of metrics: count,distinct_count",
                "default": "count",
                "examples": ["count,distinct_count"]
            })
    elif param_name.endswith('_like'):
        base_def["description"] = f"{param_name.replace('_like', '')} substring match"
    elif param_name.endswith('_from'):
        if 'date' in param_name:
            base_def.update({
                "format": "date",
                "description": f"{param_name.replace('_from', '')} from (YYYY-MM-DD)"
            })
        else:
            base_def["description"] = f"Minimum {param_name.replace('_from', '')}"
            base_def["type"] = "number"
    elif param_name.endswith('_to'):
        if 'date' in param_name:
            base_def.update({
                "format": "date", 
                "description": f"{param_name.replace('_to', '')} to (YYYY-MM-DD)"
            })
        else:
            base_def["description"] = f"Maximum {param_name.replace('_to', '')}"
            base_def["type"] = "number"
    elif param_name == 'embed':
        base_def.update({
            "type": "array",
            "description": "Related entities to embed",
            "items": {"type": "string", "enum": ["licenses"]},
            "examples": [["licenses"]]
        })
    else:
        # Generic description based on name
        base_def["description"] = f"{param_name.replace('_', ' ').title()} exact match"
        
        # Add examples for known categorical fields
        if param_name == 'emirate_name_en':
            base_def["examples"] = ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Ras Al Khaimah', 'Fujairah', 'Umm Al Quwain']
        elif param_name == 'owner_gender':
            base_def["examples"] = ['Male', 'Female', 'UnKnown']
        elif param_name == 'license_branch_flag':
            base_def["examples"] = ['Y', 'N']
    
    return base_def

def fix_tool_parameters(tool_file_path):
    """Fix a tool's parameters to match its SQL file."""
    print(f"Fixing {tool_file_path}...")
    
    # Load tool definition
    with open(tool_file_path, 'r') as f:
        tool_data = yaml.safe_load(f)
    
    if not tool_data or 'tool' not in tool_data:
        print(f"  Skipping {tool_file_path} - not a valid tool file")
        return
    
    tool_name = tool_data['tool']['name']
    
    # Find corresponding SQL file
    sql_file_path = tool_file_path.parent / f"{tool_name}.sql"
    if not sql_file_path.exists():
        print(f"  No SQL file found for {tool_name}")
        return
    
    # Extract expected parameters from SQL
    expected_params = extract_sql_parameters(sql_file_path)
    print(f"  SQL expects {len(expected_params)} parameters: {', '.join(expected_params)}")
    
    # Create new parameter definitions
    new_parameters = []
    for param_name in expected_params:
        param_def = create_parameter_definition(param_name)
        new_parameters.append(param_def)
    
    # Update tool definition
    tool_data['tool']['parameters'] = new_parameters
    
    # Write back to file
    with open(tool_file_path, 'w') as f:
        yaml.dump(tool_data, f, default_flow_style=False, sort_keys=False, width=120)
    
    print(f"  Updated {tool_name} with {len(new_parameters)} parameters")

def main():
    """Fix all tool files to match their SQL parameters."""
    tools_dir = Path('tools')
    
    if not tools_dir.exists():
        print("Error: tools/ directory not found")
        return
    
    # Find all .yml files in tools directory
    tool_files = list(tools_dir.glob('*.yml'))
    
    if not tool_files:
        print("No .yml files found in tools/ directory")
        return
    
    print(f"Found {len(tool_files)} tool files to fix:")
    for tool_file in tool_files:
        print(f"  - {tool_file}")
    
    print("\nFixing tool parameters...")
    for tool_file in tool_files:
        try:
            fix_tool_parameters(tool_file)
        except Exception as e:
            print(f"  Error fixing {tool_file}: {e}")
    
    print(f"\nCompleted fixing {len(tool_files)} tools!")
    print("\nNext steps:")
    print("1. Run 'mxcp validate' to check validation")
    print("2. Test the tools")

if __name__ == "__main__":
    main()
