"""Tool registry for dynamic tool management"""

import importlib
import sys
from pathlib import Path
from typing import Callable

from loguru import logger


class ToolRegistry:
    """Manages dynamically loaded tools"""

    def __init__(self, tools_dir: Path) -> None:
        """Initialize registry"""
        self.tools_dir = tools_dir
        self.tools: dict[str, Callable] = {}

    def register(self, name: str, code: str) -> None:
        """Register and load tool"""
        logger.info(f"Registering tool: {name}")

        file_path = self.tools_dir / f"{name}.py"
        file_path.write_text(code)

        self._reload_tool(name)
        logger.info(f"Tool registered: {name}")

    def _reload_tool(self, name: str) -> None:
        """Reload tool module"""
        module_name = f"src.tools.{name}"

        if module_name in sys.modules:
            del sys.modules[module_name]

        module = importlib.import_module(module_name)

        if hasattr(module, "execute"):
            self.tools[name] = module.execute

    def get_tool(self, name: str) -> Callable | None:
        """Get tool by name"""
        return self.tools.get(name)

    def list_tools(self) -> list[str]:
        """List all available tools"""
        return list(self.tools.keys())
