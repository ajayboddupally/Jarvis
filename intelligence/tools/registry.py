from typing import Any

from intelligence.tools.base import Tool, ToolDefinition
from intelligence.tools.calculator import SafeCalculator


class ToolRegistry:
    def __init__(self, tools: list[Tool] | None = None):
        self._tools: dict[str, Tool] = {}

        for tool in tools or []:
            self.register(tool)

    def register(self, tool: Tool) -> None:
        name = tool.definition.name

        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")

        self._tools[name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def definitions(self) -> list[ToolDefinition]:
        return [tool.definition for tool in self._tools.values()]

    async def execute(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        tool = self.get(name)

        if tool is None:
            raise ValueError(f"Unknown tool: {name}")

        return await tool.execute(arguments)


def create_default_registry() -> ToolRegistry:
    return ToolRegistry(
        tools=[
            SafeCalculator(),
        ]
    )
