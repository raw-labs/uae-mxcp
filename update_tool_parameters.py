#!/usr/bin/env python3
"""
Update all tools with comprehensive filtering parameters from search_licenses.
This ensures consistent filtering capabilities across all tools.
"""

import yaml
import os
from pathlib import Path

# Standard comprehensive filtering parameters from search_licenses
COMPREHENSIVE_FILTERS = [
    {"name": "emirate_name_en", "type": "string", "description": "Emirate (EN) exact match", "default": None, "examples": ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Ras Al Khaimah', 'Fujairah', 'Umm Al Quwain', 'Umm Al-Quwain']},
    {"name": "emirate_name_en_like", "type": "string", "description": "Emirate (EN) substring match", "default": None, "examples": ["Dub"]},
    {"name": "emirate_name_ar", "type": "string", "description": "Emirate (AR) exact match", "default": None},
    {"name": "emirate_name_ar_like", "type": "string", "description": "Emirate (AR) substring match", "default": None},
    {"name": "issuance_authority_en", "type": "string", "description": "Issuance authority (EN) exact match", "default": None},
    {"name": "issuance_authority_en_like", "type": "string", "description": "Issuing authority (EN) substring match", "default": None},
    {"name": "issuance_authority_ar", "type": "string", "description": "Issuance authority (AR) exact match", "default": None},
    {"name": "issuance_authority_ar_like", "type": "string", "description": "Issuance authority (AR) substring match", "default": None},
    {"name": "issuance_authority_branch_en", "type": "string", "description": "Branch (EN) exact match", "default": None},
    {"name": "issuance_authority_branch_en_like", "type": "string", "description": "Branch (EN) substring match", "default": None},
    {"name": "issuance_authority_branch_ar", "type": "string", "description": "Branch (AR) exact match", "default": None},
    {"name": "issuance_authority_branch_ar_like", "type": "string", "description": "Branch (AR) substring match", "default": None},
    {"name": "bl_num", "type": "string", "description": "License number exact match", "default": None},
    {"name": "bl_num_like", "type": "string", "description": "License number substring match", "default": None},
    {"name": "bl_cbls_num", "type": "string", "description": "CBLS number exact match", "default": None},
    {"name": "bl_cbls_num_like", "type": "string", "description": "CBLS number substring match", "default": None},
    {"name": "bl_name_ar", "type": "string", "description": "Trade name (AR) exact match", "default": None},
    {"name": "bl_name_ar_like", "type": "string", "description": "Trade name (AR) substring match", "default": None},
    {"name": "bl_name_en", "type": "string", "description": "Trade name (EN) exact match", "default": None},
    {"name": "bl_name_en_like", "type": "string", "description": "Trade name (EN) substring match", "default": None},
    {"name": "bl_est_date_from", "type": "string", "format": "date", "description": "Establishment date from (YYYY-MM-DD)", "default": None},
    {"name": "bl_est_date_to", "type": "string", "format": "date", "description": "Establishment date to (YYYY-MM-DD)", "default": None},
    {"name": "bl_exp_date_from", "type": "string", "format": "date", "description": "Expiry date from (YYYY-MM-DD)", "default": None},
    {"name": "bl_exp_date_to", "type": "string", "format": "date", "description": "Expiry date to (YYYY-MM-DD)", "default": None},
    {"name": "bl_status_en", "type": "string", "description": "License status (EN) exact match", "default": None},
    {"name": "bl_status_en_like", "type": "string", "description": "Status (EN) substring match", "default": None},
    {"name": "bl_status_ar", "type": "string", "description": "Status (AR) exact match", "default": None},
    {"name": "bl_status_ar_like", "type": "string", "description": "Status (AR) substring match", "default": None},
    {"name": "bl_legal_type_en", "type": "string", "description": "Legal type (EN) exact match", "default": None},
    {"name": "bl_legal_type_en_like", "type": "string", "description": "Legal type (EN) substring match", "default": None},
    {"name": "bl_legal_type_ar", "type": "string", "description": "Legal type (AR) exact match", "default": None},
    {"name": "bl_legal_type_ar_like", "type": "string", "description": "Legal type (AR) substring match", "default": None},
    {"name": "bl_type_en", "type": "string", "description": "License type (EN) exact match", "default": None, "examples": ['Agrecultural & Animals', 'Business Invest License', 'Commercial', "E'dmad  (Reliance)", 'E-Commerce License', 'Educational License', 'Event   License', 'Handicraft', 'Industrial', 'International Business Companies', 'Media License', 'Preliminary License', 'Professional', 'Service', 'Service License', 'Standard', 'Trade', 'tourism license']},
    {"name": "bl_type_en_like", "type": "string", "description": "License type (EN) substring match", "default": None},
    {"name": "bl_type_ar", "type": "string", "description": "License type (AR) exact match", "default": None},
    {"name": "bl_type_ar_like", "type": "string", "description": "License type (AR) substring match", "default": None},
    {"name": "bl_full_address", "type": "string", "description": "Full address exact match", "default": None},
    {"name": "bl_full_address_like", "type": "string", "description": "Full address substring match", "default": None},
    {"name": "license_latitude_min", "type": "number", "description": "Minimum latitude", "default": None},
    {"name": "license_latitude_max", "type": "number", "description": "Maximum latitude", "default": None},
    {"name": "license_longitude_min", "type": "number", "description": "Minimum longitude", "default": None},
    {"name": "license_longitude_max", "type": "number", "description": "Maximum longitude", "default": None},
    {"name": "license_branch_flag", "type": "string", "description": "Branch flag (Y/N)", "default": None, "examples": ['Y', 'N']},
    {"name": "parent_licence_license_number", "type": "string", "description": "Parent license number exact match", "default": None},
    {"name": "parent_licence_license_number_like", "type": "string", "description": "Parent license number substring match", "default": None},
    {"name": "parent_license_issuance_authority_en", "type": "string", "description": "Parent authority (EN) exact match", "default": None},
    {"name": "parent_license_issuance_authority_en_like", "type": "string", "description": "Parent authority (EN) substring match", "default": None},
    {"name": "parent_license_issuance_authority_ar", "type": "string", "description": "Parent authority (AR) exact match", "default": None},
    {"name": "parent_license_issuance_authority_ar_like", "type": "string", "description": "Parent issuing authority (AR) substring match", "default": None},
    {"name": "relationship_type_en", "type": "string", "description": "Relationship type (EN) exact match", "default": None, "examples": ['Authorized signatory', 'Chairman of the Board of Directors', 'Cheif Executive', 'Designated Member', 'Doctor', 'Founder', 'Leased-Rented', 'Owner', 'Partner', 'Pharmacist', 'Representative of the Board', 'Representative of the Successors ', 'Secretary', 'Service Agent', 'Shareholders of the Company', 'Successors', 'The Board of Directors, Member and CEO/Executive Director']},
    {"name": "relationship_type_en_like", "type": "string", "description": "Relationship type (EN) substring match", "default": None},
    {"name": "relationship_type_ar", "type": "string", "description": "Relationship type (AR) exact match", "default": None},
    {"name": "relationship_type_ar_like", "type": "string", "description": "Relationship type (AR) substring match", "default": None},
    {"name": "owner_nationality_en", "type": "string", "description": "Owner nationality (EN) exact match", "default": None},
    {"name": "owner_nationality_en_like", "type": "string", "description": "Owner nationality (EN) substring match", "default": None},
    {"name": "owner_nationality_ar", "type": "string", "description": "Owner nationality (AR) exact match", "default": None},
    {"name": "owner_nationality_ar_like", "type": "string", "description": "Owner nationality (AR) substring match", "default": None},
    {"name": "owner_gender", "type": "string", "description": "Owner gender exact match", "default": None, "examples": ['Male', 'Female', 'UnKnown']},
    {"name": "business_activity_code", "type": "string", "description": "Business activity code exact match", "default": None},
    {"name": "business_activity_code_like", "type": "string", "description": "Business activity code substring match", "default": None},
    {"name": "business_activity_desc_en", "type": "string", "description": "Business activity description (EN) exact match", "default": None},
    {"name": "business_activity_desc_en_like", "type": "string", "description": "Business activity description (EN) substring match", "default": None},
    {"name": "business_activity_desc_ar", "type": "string", "description": "Business activity description (AR) exact match", "default": None},
    {"name": "business_activity_desc_ar_like", "type": "string", "description": "Business activity description (AR) substring match", "default": None}
]

def update_tool_parameters(tool_file_path):
    """Update a tool's parameters to include comprehensive filters."""
    print(f"Updating {tool_file_path}...")
    
    with open(tool_file_path, 'r') as f:
        tool_data = yaml.safe_load(f)
    
    if not tool_data or 'tool' not in tool_data:
        print(f"  Skipping {tool_file_path} - not a valid tool file")
        return
    
    tool_name = tool_data['tool']['name']
    current_params = tool_data['tool'].get('parameters', [])
    
    # Find existing pagination and tool-specific parameters
    preserved_params = []
    existing_filter_names = set()
    
    for param in current_params:
        param_name = param.get('name', '')
        
        # Always preserve these tool-specific parameters
        if param_name in ['page', 'page_size', 'group_by', 'metrics', 'embed']:
            preserved_params.append(param)
        # Keep track of existing filter parameters
        elif any(filter_param['name'] == param_name for filter_param in COMPREHENSIVE_FILTERS):
            existing_filter_names.add(param_name)
        # Preserve any other unique parameters
        else:
            preserved_params.append(param)
    
    # Add comprehensive filters (skip ones that already exist)
    new_params = preserved_params.copy()
    for filter_param in COMPREHENSIVE_FILTERS:
        if filter_param['name'] not in existing_filter_names:
            new_params.append(filter_param)
    
    # Update the tool
    tool_data['tool']['parameters'] = new_params
    
    # Write back to file
    with open(tool_file_path, 'w') as f:
        yaml.dump(tool_data, f, default_flow_style=False, sort_keys=False, width=120)
    
    print(f"  Updated {tool_name}: {len(preserved_params)} preserved + {len(COMPREHENSIVE_FILTERS) - len(existing_filter_names)} new filters = {len(new_params)} total")

def main():
    """Update all tool files with comprehensive filtering."""
    tools_dir = Path('tools')
    
    if not tools_dir.exists():
        print("Error: tools/ directory not found")
        return
    
    # Find all .yml files in tools directory
    tool_files = list(tools_dir.glob('*.yml'))
    
    if not tool_files:
        print("No .yml files found in tools/ directory")
        return
    
    print(f"Found {len(tool_files)} tool files to update:")
    for tool_file in tool_files:
        print(f"  - {tool_file}")
    
    print("\nUpdating tools...")
    for tool_file in tool_files:
        try:
            update_tool_parameters(tool_file)
        except Exception as e:
            print(f"  Error updating {tool_file}: {e}")
    
    print(f"\nCompleted updating {len(tool_files)} tools!")
    print("\nNext steps:")
    print("1. Run 'mxcp validate' to check for any issues")
    print("2. Test the updated tools")

if __name__ == "__main__":
    main()
