#!/usr/bin/env python3
"""
Calculates dbt model test coverage based on the manifest.json file.
"""
import json
from pathlib import Path
import sys

def calculate_coverage(manifest_path: Path):
    """
    Parses the dbt manifest file to calculate test coverage per model and overall.

    Coverage is defined as the percentage of columns that have at least one test.
    """
    if not manifest_path.exists():
        print(f"Error: manifest.json not found at {manifest_path}", file=sys.stderr)
        print("Please run 'dbt docs generate' first.", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = json.load(f)

    # --- Data Extraction from Manifest ---
    
    # Get all models
    models = {
        name: node
        for name, node in manifest["nodes"].items()
        if node["resource_type"] == "model"
    }
    
    # Get all tests and map them to the models and columns they depend on
    model_column_tests = {}  # {model_name: {column_name: [test_names]}}
    model_level_tests = {}   # {model_name: [test_names]}
    for name, node in manifest["nodes"].items():
        if node["resource_type"] == "test":
            for dep_name in node["depends_on"]["nodes"]:
                if dep_name.startswith("model."):
                    # Extract model short name - handle versioned models
                    parts = dep_name.split(".")
                    model_short_name = parts[-2] if parts[-1].startswith("v") and parts[-1][1:].isdigit() else parts[-1]
                    # Check if this is a column-level test
                    test_meta = node.get("test_metadata")
                    if test_meta and "column_name" in test_meta.get("kwargs", {}):
                        col = test_meta["kwargs"]["column_name"]
                        model_column_tests.setdefault(model_short_name, {}).setdefault(col, []).append(node["name"])
                    else:
                        model_level_tests.setdefault(model_short_name, []).append(node["name"])

    print("--- dbt Test Coverage Report ---")

    total_columns = 0
    total_tested_columns = 0
    models_with_tests = 0

    for model_name, model_data in models.items():
        model_short_name = model_data["name"]
        columns = model_data.get("columns", {})
        
        # --- Column-level Coverage ---
        column_count = len(columns)
        tested_column_count = 0
        for col_name in columns:
            if model_column_tests.get(model_short_name, {}).get(col_name):
                tested_column_count += 1
        total_columns += column_count
        total_tested_columns += tested_column_count
        coverage = (tested_column_count / column_count) * 100 if column_count > 0 else 0

        # --- Model-level Coverage (Custom Data Tests) ---
        model_tests = model_level_tests.get(model_short_name, [])
        if model_tests:
            models_with_tests +=1

        # --- Reporting ---
        print(f"\nModel: {model_short_name} ({model_name})")
        if column_count > 0:
            print(f"  - Column Level: {tested_column_count} / {column_count} columns tested ({coverage:.2f}%)")
        else:
            print(f"  - Column Level: No columns defined in schema.yml")
            
        if model_tests:
            print(f"  - Model Level:  {len(model_tests)} custom data test(s) found.")
        else:
            print(f"  - Model Level:  No custom data tests found.")

    # --- Summary ---
    overall_column_coverage = (total_tested_columns / total_columns) * 100 if total_columns > 0 else 0
    overall_model_coverage = (models_with_tests / len(models)) * 100 if models else 0
    
    print("\n" + "="*40)
    print("           OVERALL SUMMARY")
    print("="*40)
    print(f"Column Coverage: {total_tested_columns} / {total_columns} columns have direct tests ({overall_column_coverage:.2f}%)")
    print(f"Model Coverage:  {models_with_tests} / {len(models)} models are covered by at least one custom test ({overall_model_coverage:.2f}%)")
    print("="*40)


def main():
    """
    Main function to run the script.
    Assumes the script is run from the project root.
    """
    project_root = Path.cwd()
    manifest_path = project_root / "target" / "manifest.json"
    calculate_coverage(manifest_path)

if __name__ == "__main__":
    main() 