"""
Core MXCP Generator functionality
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .analyzers import SemanticAnalyzer, BusinessEntity
from .generators import ToolGenerator, ResourceGenerator, PromptGenerator
from .utils.dbt_utils import load_dbt_manifest

logger = logging.getLogger(__name__)


@dataclass
class GeneratedArtifacts:
    """Container for all generated MXCP artifacts"""
    tools: List[Dict[str, Any]]
    resources: List[Dict[str, Any]]
    prompts: List[Dict[str, Any]]
    tests: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class MCPGenerator:
    """
    Main generator class that orchestrates the creation of MXCP artifacts
    from dbt models.
    """
    
    def __init__(
        self, 
        dbt_manifest_path: str,
        output_dir: str = "generated",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the MCP Generator.
        
        Args:
            dbt_manifest_path: Path to dbt manifest.json file
            output_dir: Directory to write generated files
            config: Optional configuration overrides
        """
        self.manifest_path = Path(dbt_manifest_path)
        self.output_dir = Path(output_dir)
        self.config = config or {}
        
        # Initialize components
        self.semantic_analyzer = SemanticAnalyzer()
        self.tool_generator = ToolGenerator()
        self.resource_generator = ResourceGenerator()
        self.prompt_generator = PromptGenerator()
        
        # Load dbt manifest
        self.manifest = load_dbt_manifest(self.manifest_path)
        
        # Initialize artifact storage
        self.entities = {}
        self.tools = []
        self.resources = []
        self.prompts = []
        self.tests = []
        
    def generate(self) -> GeneratedArtifacts:
        """
        Generate all MXCP artifacts from dbt models.
        
        Returns:
            GeneratedArtifacts containing all generated components
        """
        logger.info(f"Starting MXCP generation from {self.manifest_path}")
        
        # 1. Analyze dbt models to extract business entities
        self.entities = self.semantic_analyzer.extract_entities(self.manifest)
        logger.info(f"Detected {len(self.entities)} business entities")
        
        # 2. Generate tools for each entity
        self.tools = []
        for entity in self.entities.values():
            entity_tools = self.tool_generator.generate_for_entity(entity)
            self.tools.extend(entity_tools)
        logger.info(f"Generated {len(self.tools)} tools")
        
        # 3. Generate resources
        self.resources = self.resource_generator.generate_resources(self.entities)
        logger.info(f"Generated {len(self.resources)} resources")
        
        # 4. Generate prompts
        self.prompts = self.prompt_generator.generate_prompts(self.entities, self.tools)
        logger.info(f"Generated {len(self.prompts)} prompts")
        
        # 5. Generate tests for all components
        self.tests = self._generate_tests(self.tools, self.resources)
        logger.info(f"Generated {len(self.tests)} tests")
        
        # 6. Create metadata
        metadata = self._create_metadata(self.entities, self.tools, self.resources, self.prompts)
        
        return GeneratedArtifacts(
            tools=self.tools,
            resources=self.resources,
            prompts=self.prompts,
            tests=self.tests,
            metadata=metadata
        )
    
    def write_artifacts(self, output_dir: str):
        """Write generated artifacts to disk"""
        output_path = Path(output_dir)
        
        # Create directories
        tools_dir = output_path / "tools"
        sql_dir = output_path / "sql"
        resources_dir = output_path / "resources"
        prompts_dir = output_path / "prompts"
        tests_dir = output_path / "tests"
        
        for dir_path in [tools_dir, sql_dir, resources_dir, prompts_dir, tests_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Collect SQL queries from tool generator
        sql_queries = {}
        if hasattr(self.tool_generator, 'get_sql_queries'):
            sql_queries = self.tool_generator.get_sql_queries()
        
        # Write tools (with test preservation)
        for tool in self.tools:
            tool_name = tool['tool']['name']
            file_path = tools_dir / f"{tool_name}.yml"
            
            # Merge existing tests before writing
            merged_tool = self._merge_existing_tests(tool, file_path)
            
            with open(file_path, 'w') as f:
                yaml.dump(merged_tool, f, default_flow_style=False, sort_keys=False)
            
            # Write corresponding SQL file if it exists
            if tool_name in sql_queries:
                sql_path = sql_dir / f"{tool_name}.sql"
                with open(sql_path, 'w') as f:
                    f.write(sql_queries[tool_name])
        
        # Write resources
        for resource in self.resources:
            resource_name = resource['resource']['name']
            file_path = resources_dir / f"{resource_name}.yml"
            with open(file_path, 'w') as f:
                yaml.dump(resource, f, default_flow_style=False, sort_keys=False)
        
        # Write prompts
        for prompt in self.prompts:
            prompt_name = prompt['prompt']['name']
            file_path = prompts_dir / f"{prompt_name}.yml"
            with open(file_path, 'w') as f:
                yaml.dump(prompt, f, default_flow_style=False, sort_keys=False)
        
        # Write tests
        if self.tests:
            tests_file = tests_dir / "generated_tests.yml"
            with open(tests_file, 'w') as f:
                yaml.dump({"tests": self.tests}, f, default_flow_style=False, sort_keys=False)
        
        # Write metadata
        metadata = {
            "version": "0.1.0",
            "generation_timestamp": datetime.now().isoformat(),
            "dbt_manifest": str(self.manifest_path),
            "statistics": {
                "entities_detected": len(self.entities),
                "tools_generated": len(self.tools),
                "resources_generated": len(self.resources),
                "prompts_generated": len(self.prompts),
                "tests_generated": len(self.tests)
            },
            "entities": {
                entity_name: {
                    "primary_model": entity.primary_model.name,
                    "related_models": [m.name for m in entity.related_models],
                    "columns": len(entity.columns)
                }
                for entity_name, entity in self.entities.items()
            }
        }
        
        metadata_file = output_path / "generation_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Artifacts written to {output_path}")
    
    def _generate_tests(self, tools: List[Dict], resources: List[Dict]) -> List[Dict]:
        """Generate test cases for tools and resources."""
        tests = []
        
        # Generate basic tests for each tool
        for tool in tools:
            tool_name = tool['tool']['name']
            
            # Basic functionality test
            tests.append({
                "name": f"test_{tool_name}_basic",
                "tool": tool_name,
                "description": f"Basic functionality test for {tool_name}",
                "params": self._generate_test_params(tool),
                "assertions": [
                    {"type": "status", "value": "success"},
                    {"type": "has_results", "value": True}
                ]
            })
            
            # Invalid parameter test
            if tool['tool'].get('parameters'):
                tests.append({
                    "name": f"test_{tool_name}_invalid_params",
                    "tool": tool_name,
                    "description": f"Invalid parameter test for {tool_name}",
                    "params": {"invalid_param": "test"},
                    "expect_error": True
                })
        
        return tests
    
    def _generate_test_params(self, tool: Dict) -> Dict:
        """Generate test parameters for a tool."""
        params = {}
        
        for param in tool['tool'].get('parameters', []):
            param_name = param['name']
            param_type = param['type']
            
            # Generate sample values based on type
            if param_type == 'string':
                if 'enum' in param:
                    params[param_name] = param['enum'][0]
                else:
                    params[param_name] = "test_value"
            elif param_type == 'integer':
                params[param_name] = 1
            elif param_type == 'boolean':
                params[param_name] = True
            elif param_type == 'array':
                params[param_name] = []
        
        return params
    
    def _create_metadata(
        self, 
        entities: Dict[str, BusinessEntity],
        tools: List[Dict],
        resources: List[Dict],
        prompts: List[Dict]
    ) -> Dict:
        """Create metadata about the generation process."""
        return {
            "version": "0.1.0",
            "generation_timestamp": datetime.now().isoformat(),
            "dbt_manifest": str(self.manifest_path),
            "statistics": {
                "entities_detected": len(entities),
                "tools_generated": len(tools),
                "resources_generated": len(resources),
                "prompts_generated": len(prompts),
                "tests_generated": len(self._generate_tests(tools, resources))
            },
            "entities": {
                name: {
                    "primary_model": entity.primary_model.name,
                    "related_models": [m.name for m in entity.related_models],
                    "columns": len(entity.columns)
                }
                for name, entity in entities.items()
            }
        }
    
    def _write_yaml(self, path: Path, data: Dict):
        """Write data as YAML file."""
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def _write_json(self, path: Path, data: Dict):
        """Write data as JSON file."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def _merge_existing_tests(self, new_tool: Dict[str, Any], existing_file_path: Path) -> Dict[str, Any]:
        """
        Merge existing manually written tests with new tool definition.
        
        Args:
            new_tool: The newly generated tool definition
            existing_file_path: Path to existing tool file
            
        Returns:
            Tool definition with preserved existing tests
        """
        if not existing_file_path.exists():
            logger.debug(f"No existing file found at {existing_file_path}, using new tool as-is")
            return new_tool
        
        try:
            # Load existing tool definition
            with open(existing_file_path, 'r') as f:
                existing_tool = yaml.safe_load(f)
            
            # Check if existing tool has tests
            if (existing_tool and 
                'tool' in existing_tool and 
                'tests' in existing_tool['tool'] and 
                existing_tool['tool']['tests']):
                
                existing_tests = existing_tool['tool']['tests']
                logger.info(f"Preserving {len(existing_tests)} existing tests for {new_tool['tool']['name']}")
                
                # Preserve existing tests in the new tool
                new_tool['tool']['tests'] = existing_tests
                
                # Log which tests are being preserved
                test_names = [test.get('name', 'unnamed') for test in existing_tests]
                logger.debug(f"Preserved tests: {', '.join(test_names)}")
            else:
                logger.debug(f"No existing tests found in {existing_file_path}")
                
        except Exception as e:
            logger.warning(f"Failed to merge existing tests from {existing_file_path}: {e}")
            logger.warning("Using new tool definition without existing tests")
        
        return new_tool 