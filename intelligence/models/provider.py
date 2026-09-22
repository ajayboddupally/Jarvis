from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GenerationRequest:
    model: str
    messages: list[dict[str, str]]
    temperature: float = 0.2
    max_tokens: int = 1024


@dataclass(frozen=True)
class GenerationResult:
    text: str
    input_tokens: int
    output_tokens: int
    finish_reason: str = "stop"
    raw: dict[str, Any] | None = None


class ModelProvider:
    name = "base"

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        raise NotImplementedError
