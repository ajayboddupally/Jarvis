from dataclasses import dataclass


@dataclass(frozen=True)
class ReasoningPlan:
    intent: str
    requires_tools: bool
    complexity: str


def classify_request(message: str) -> ReasoningPlan:
    text = message.lower()

    tool_words = (
        "search",
        "look up",
        "calculate",
        "weather",
        "latest",
        "current",
        "find",
        "open",
    )

    if any(word in text for word in tool_words):
        return ReasoningPlan(
            intent="information_or_tool_request",
            requires_tools=True,
            complexity="medium",
        )

    if len(message) > 1200:
        return ReasoningPlan(
            intent="long_form_reasoning",
            requires_tools=False,
            complexity="high",
        )

    return ReasoningPlan(
        intent="general_assistance",
        requires_tools=False,
        complexity="low",
    )
