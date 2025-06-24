#!/usr/bin/env python3
"""
Fix SQL parameter replacements that were too broad.
"""

import re
from pathlib import Path

def fix_sql_file(sql_file_path):
    """Fix incorrect parameter replacements in a SQL file."""
    print(f"Fixing {sql_file_path}...")
    
    with open(sql_file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix incorrect replacements
    # $bl_num_status_en should be $bl_status_en
    content = re.sub(r'\$bl_num_([a-z_]+)', r'$bl_\1', content)
    
    # But keep $bl_num and $bl_num_like as they are correct
    content = re.sub(r'\$bl_([^_])', r'$bl_num_\1', content)
    content = content.replace('$bl_like', '$bl_num_like')
    content = content.replace('$bl_num_num', '$bl_num')
    
    # Write back if changes were made
    if content != original_content:
        with open(sql_file_path, 'w') as f:
            f.write(content)
        print(f"  Fixed parameter names")
    else:
        print(f"  No fixes needed")

def main():
    """Fix all SQL files with incorrect parameter names."""
    tools_dir = Path('tools')
    
    if not tools_dir.exists():
        print("Error: tools/ directory not found")
        return
    
    # Find all .sql files in tools directory
    sql_files = list(tools_dir.glob('*.sql'))
    
    print(f"Found {len(sql_files)} SQL files to fix:")
    for sql_file in sql_files:
        print(f"  - {sql_file}")
    
    print("\nFixing SQL files...")
    for sql_file in sql_files:
        try:
            fix_sql_file(sql_file)
        except Exception as e:
            print(f"  Error fixing {sql_file}: {e}")
    
    print(f"\nCompleted fixing {len(sql_files)} SQL files!")

if __name__ == "__main__":
    main()
