#!/usr/bin/env python3
"""
MXCP Tool Generator CLI

Automatically generates MXCP tools, resources, and prompts from dbt models.
"""

import argparse
import logging
import sys
from pathlib import Path

from mxcp_generator import MCPGenerator


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate MXCP tools from dbt models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from dbt manifest
  python generate_mxcp_tools.py

  # Generate with custom output directory
  python generate_mxcp_tools.py --output-dir my_tools

  # Generate with verbose logging
  python generate_mxcp_tools.py --verbose
        """
    )
    
    parser.add_argument(
        '--manifest',
        type=str,
        default='target/manifest.json',
        help='Path to dbt manifest.json file (default: target/manifest.json)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='generated_mxcp',
        help='Output directory for generated files (default: generated_mxcp)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate but do not write files'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize generator
        logger.info("Initializing MXCP generator")
        generator = MCPGenerator(
            dbt_manifest_path=args.manifest,
            output_dir=args.output_dir
        )
        
        # Generate artifacts
        logger.info("Generating MXCP artifacts...")
        artifacts = generator.generate()
        
        # Summary
        logger.info(f"Generated {len(artifacts.tools)} tools")
        logger.info(f"Generated {len(artifacts.resources)} resources")
        logger.info(f"Generated {len(artifacts.prompts)} prompts")
        logger.info(f"Generated {len(artifacts.tests)} tests")
        
        # Write files unless dry run
        if not args.dry_run:
            logger.info(f"Writing artifacts to {args.output_dir}")
            generator.write_artifacts(args.output_dir)
            logger.info("Generation complete!")
        else:
            logger.info("Dry run complete - no files written")
        
        # Print summary
        print("\nGeneration Summary:")
        print(f"  Tools:     {len(artifacts.tools)}")
        print(f"  Resources: {len(artifacts.resources)}")
        print(f"  Prompts:   {len(artifacts.prompts)}")
        print(f"  Tests:     {len(artifacts.tests)}")
        
        if not args.dry_run:
            print(f"\nFiles written to: {Path(args.output_dir).absolute()}")
            print("\nNext steps:")
            print("1. Review generated files in the output directory")
            print("2. Copy desired tools to your project's tools/ directory")
            print("3. Run 'mxcp validate' to check the generated definitions")
            print("4. Run 'mxcp test' to execute the generated tests")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"\nError: {e}")
        print("Make sure to run 'dbt docs generate' first to create the manifest.json")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 