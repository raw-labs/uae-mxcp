#!/usr/bin/env python3
"""
Test script for multi-model tool generation
"""

import logging
from pathlib import Path
from mxcp_generator.core import MCPGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test the multi-model tool generation"""
    
    # Paths
    manifest_path = "target/manifest.json"
    output_dir = "generated_multimodel"
    
    logger.info("Starting multi-model tool generation test")
    
    try:
        # Initialize generator
        generator = MCPGenerator(
            dbt_manifest_path=manifest_path,
            output_dir=output_dir
        )
        
        # Generate artifacts
        artifacts = generator.generate()
        
        # Write to disk
        generator.write_artifacts(output_dir)
        
        logger.info(f"Generated {len(artifacts.tools)} tools")
        logger.info(f"Generated {len(artifacts.resources)} resources") 
        logger.info(f"Generated {len(artifacts.prompts)} prompts")
        
        # Print details about generated tools
        for tool in artifacts.tools:
            tool_name = tool['tool']['name']
            parameters = tool['tool'].get('parameters', [])
            embed_param = next((p for p in parameters if p['name'] == 'embed'), None)
            
            logger.info(f"Tool: {tool_name}")
            if embed_param:
                embed_options = embed_param.get('items', {}).get('enum', [])
                logger.info(f"  - Embed options: {embed_options}")
            else:
                logger.info(f"  - No embed parameter")
                
    except Exception as e:
        logger.error(f"Error during generation: {e}")
        raise

if __name__ == "__main__":
    main() 