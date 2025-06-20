"""
MXCP Tool Generator Framework

Automatically generates MXCP tools, resources, and prompts from dbt mart models.
"""

__version__ = "0.1.0"

from .core import MCPGenerator
from .analyzers import SemanticAnalyzer
from .generators import ToolGenerator, ResourceGenerator, PromptGenerator

__all__ = [
    "MCPGenerator",
    "SemanticAnalyzer", 
    "ToolGenerator",
    "ResourceGenerator",
    "PromptGenerator"
] 