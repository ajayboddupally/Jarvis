from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]


class Tool(ABC):
    definition: ToolDefinition

    @abstractmethod
    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
