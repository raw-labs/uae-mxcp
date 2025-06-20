"""
DBT-related utility functions
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def load_dbt_manifest(manifest_path: Path) -> Dict[str, Any]:
    """
    Load and parse dbt manifest.json file
    
    Args:
        manifest_path: Path to manifest.json file
        
    Returns:
        Parsed manifest dictionary
        
    Raises:
        FileNotFoundError: If manifest file doesn't exist
        json.JSONDecodeError: If manifest is invalid JSON
    """
    if not manifest_path.exists():
        raise FileNotFoundError(f"dbt manifest not found at {manifest_path}")
    
    logger.info(f"Loading dbt manifest from {manifest_path}")
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Validate basic structure
    if 'nodes' not in manifest:
        raise ValueError("Invalid dbt manifest: missing 'nodes' key")
    
    # Count models
    model_count = sum(
        1 for node in manifest['nodes'].values()
        if node.get('resource_type') == 'model'
    )
    
    logger.info(f"Loaded manifest with {model_count} models")
    
    return manifest 