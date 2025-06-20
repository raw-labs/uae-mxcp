"""
Core MXCP Generator functionality
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

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
        
    def generate(self) -> GeneratedArtifacts:
        """
        Generate all MXCP artifacts from dbt models.
        
        Returns:
            GeneratedArtifacts containing all generated components
        """
        logger.info(f"Starting MXCP generation from {self.manifest_path}")
        
        # 1. Analyze dbt models to extract business entities
        entities = self.semantic_analyzer.extract_entities(self.manifest)
        logger.info(f"Detected {len(entities)} business entities")
        
        # 2. Generate tools for each entity
        tools = []
        for entity in entities.values():
            entity_tools = self.tool_generator.generate_for_entity(entity)
            tools.extend(entity_tools)
        logger.info(f"Generated {len(tools)} tools")
        
        # 3. Generate resources
        resources = self.resource_generator.generate_resources(entities)
        logger.info(f"Generated {len(resources)} resources")
        
        # 4. Generate prompts
        prompts = self.prompt_generator.generate_prompts(entities, tools)
        logger.info(f"Generated {len(prompts)} prompts")
        
        # 5. Generate tests for all components
        tests = self._generate_tests(tools, resources)
        logger.info(f"Generated {len(tests)} tests")
        
        # 6. Create metadata
        metadata = self._create_metadata(entities, tools, resources, prompts)
        
        return GeneratedArtifacts(
            tools=tools,
            resources=resources,
            prompts=prompts,
            tests=tests,
            metadata=metadata
        )
    
    def write_artifacts(self, artifacts: GeneratedArtifacts):
        """
        Write generated artifacts to the file system.
        
        Args:
            artifacts: Generated artifacts to write
        """
        # Create output directories
        (self.output_dir / "tools").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "resources").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "prompts").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "tests").mkdir(parents=True, exist_ok=True)
        
        # Write tools
        for tool in artifacts.tools:
            tool_path = self.output_dir / "tools" / f"{tool['tool']['name']}.yml"
            self._write_yaml(tool_path, tool)
        
        # Write resources
        for resource in artifacts.resources:
            resource_path = self.output_dir / "resources" / f"{resource['resource']['name']}.yml"
            self._write_yaml(resource_path, resource)
        
        # Write prompts
        for prompt in artifacts.prompts:
            prompt_path = self.output_dir / "prompts" / f"{prompt['prompt']['name']}.yml"
            self._write_yaml(prompt_path, prompt)
        
        # Write test configuration
        test_config = {
            "mxcp": "1.0.0",
            "tests": artifacts.tests
        }
        self._write_yaml(self.output_dir / "tests" / "generated_tests.yml", test_config)
        
        # Write metadata
        self._write_json(self.output_dir / "generation_metadata.json", artifacts.metadata)
        
        logger.info(f"Artifacts written to {self.output_dir}")
    
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
        from datetime import datetime
        
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
        import yaml
        
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def _write_json(self, path: Path, data: Dict):
        """Write data as JSON file."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2) 