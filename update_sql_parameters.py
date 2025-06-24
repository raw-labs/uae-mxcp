#!/usr/bin/env python3
"""
Update SQL files to use standardized parameter names from search_licenses.
"""

import re
from pathlib import Path

# Mapping from old parameter names to new standardized names
PARAMETER_MAPPINGS = {
    # License number mappings
    'bl': 'bl_num',
    'bl_like': 'bl_num_like',
    
    # Date field mappings (remove _d suffix)
    'bl_est_date_d_from': 'bl_est_date_from',
    'bl_est_date_d_to': 'bl_est_date_to', 
    'bl_exp_date_d_from': 'bl_exp_date_from',
    'bl_exp_date_d_to': 'bl_exp_date_to',
    
    # Add any other mappings as needed
}

def update_sql_file(sql_file_path):
    """Update parameter references in a SQL file."""
    print(f"Updating {sql_file_path}...")
    
    with open(sql_file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    # Replace parameter references
    for old_param, new_param in PARAMETER_MAPPINGS.items():
        # Replace $parameter_name references
        old_pattern = f'${old_param}'
        new_pattern = f'${new_param}'
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            changes_made += content.count(new_pattern) - original_content.count(new_pattern)
            print(f"  Replaced ${old_param} -> ${new_param}")
    
    # Write back if changes were made
    if content != original_content:
        with open(sql_file_path, 'w') as f:
            f.write(content)
        print(f"  Made {changes_made} parameter updates")
    else:
        print(f"  No changes needed")

def main():
    """Update all SQL files with standardized parameter names."""
    tools_dir = Path('tools')
    
    if not tools_dir.exists():
        print("Error: tools/ directory not found")
        return
    
    # Find all .sql files in tools directory
    sql_files = list(tools_dir.glob('*.sql'))
    
    if not sql_files:
        print("No .sql files found in tools/ directory")
        return
    
    print(f"Found {len(sql_files)} SQL files to update:")
    for sql_file in sql_files:
        print(f"  - {sql_file}")
    
    print("\nUpdating SQL files...")
    for sql_file in sql_files:
        try:
            update_sql_file(sql_file)
        except Exception as e:
            print(f"  Error updating {sql_file}: {e}")
    
    print(f"\nCompleted updating {len(sql_files)} SQL files!")
    print("\nNext steps:")
    print("1. Run 'mxcp validate' to check for remaining issues")
    print("2. Test the updated tools")

if __name__ == "__main__":
    main()
