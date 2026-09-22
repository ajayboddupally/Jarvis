from dataclasses import dataclass
from typing import Any

from intelligence.reasoning import ReasoningPlan, classify_request
from intelligence.tools.registry import ToolRegistry


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class AgentDecision:
    plan: ReasoningPlan
    tool_call: ToolCall | None


class AgentRuntime:
    """Small deterministic agent loop.

    The runtime decides whether a request needs a registered tool.
    Model-driven tool selection will replace/extend this policy later.
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def decide(self, message: str) -> AgentDecision:
        plan = classify_request(message)

        if not plan.requires_tools:
            return AgentDecision(plan=plan, tool_call=None)

        expression = self._extract_calculation(message)

        if expression is not None and self.registry.get("calculator"):
            return AgentDecision(
                plan=plan,
                tool_call=ToolCall(
                    name="calculator",
                    arguments={"expression": expression},
                ),
            )

        return AgentDecision(plan=plan, tool_call=None)

    async def execute(self, decision: AgentDecision) -> dict[str, Any] | None:
        if decision.tool_call is None:
            return None

        call = decision.tool_call

        try:
            result = await self.registry.execute(
                call.name,
                call.arguments,
            )
            return {
                "tool": call.name,
                "success": True,
                "arguments": call.arguments,
                "result": result,
            }
        except Exception as exc:
            return {
                "tool": call.name,
                "success": False,
                "arguments": call.arguments,
                "error": str(exc),
            }

    @staticmethod
    def _extract_calculation(message: str) -> str | None:
        lower = message.lower()

        triggers = (
            "calculate ",
            "what is ",
            "compute ",
        )

        if not any(trigger in lower for trigger in triggers):
            return None

        candidate = message

        for separator in ("calculate", "Calculate", "compute", "Compute"):
            if separator in candidate:
                candidate = candidate.split(separator, 1)[1].strip()
                break

        if "what is " in candidate.lower():
            candidate = candidate.lower().split("what is ", 1)[1].strip()

        allowed = set("0123456789+-*/().% ")
        cleaned = "".join(char for char in candidate if char in allowed).strip()

        return cleaned if cleaned else None
