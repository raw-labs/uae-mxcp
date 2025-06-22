#!/usr/bin/env python3
"""
Test script to verify multi-model tool execution
"""

import duckdb
import json
from pathlib import Path

def test_license_owners_tool():
    """Test the find_license_owners tool with embedding"""
    
    # Connect to the database
    conn = duckdb.connect('db-prod.duckdb')
    
    print("Testing find_license_owners tool...")
    
    # Test 1: Basic query without embedding
    print("\n1. Basic query without embedding:")
    sql = """
    SELECT *
    FROM fact_license_owners
    WHERE 1=1
    LIMIT 3
    """
    
    result = conn.execute(sql).fetchall()
    print(f"Found {len(result)} records")
    if result:
        print(f"Sample record: {result[0][:5]}...")  # First 5 columns
    
    # Test 2: Query with embed parameter (simulated)
    print("\n2. Query with embed parameter simulation:")
    embed_param = ['licenses']  # This would come from the API call
    
    # Simulate the embedding logic
    sql_with_embed = f"""
    -- Base query
    WITH base_data AS (
        SELECT *
        FROM fact_license_owners
        WHERE 1=1
        LIMIT 3
    )
    
    -- Enhanced query with conditional embedding
    SELECT 
      bd.*,
      CASE 
        WHEN {len(embed_param)} = 0 THEN NULL
        ELSE JSON_OBJECT('embed_requested', '{",".join(embed_param)}')
      END as _embedded
    FROM base_data bd
    """
    
    result = conn.execute(sql_with_embed).fetchall()
    print(f"Found {len(result)} records with embedding simulation")
    if result:
        print(f"Sample record with _embedded: {result[0][-1]}")  # Last column (_embedded)
    
    # Test 3: Check relationship data exists
    print("\n3. Checking relationship data:")
    sql_relationship = """
    SELECT 
        o.owner_pk,
        o.license_pk,
        o.owner_name,
        l.bl_name_en,
        l.bl_status_en
    FROM fact_license_owners o
    LEFT JOIN dim_licenses_v1 l ON o.license_pk = l.license_pk
    LIMIT 3
    """
    
    result = conn.execute(sql_relationship).fetchall()
    print(f"Found {len(result)} owner-license relationships")
    for row in result:
        print(f"  Owner: {row[2]} -> License: {row[3]} ({row[4]})")
    
    conn.close()
    print("\nMulti-model tool test completed successfully!")

if __name__ == "__main__":
    test_license_owners_tool() 