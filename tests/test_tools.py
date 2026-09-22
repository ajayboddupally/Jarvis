import pytest

from intelligence.agent import AgentRuntime
from intelligence.tools.calculator import SafeCalculator
from intelligence.tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_calculator_tool():
    tool = SafeCalculator()
    result = await tool.execute({"expression": "(10 + 5) * 2"})
    assert result["result"] == 30


@pytest.mark.asyncio
async def test_unsafe_calculator_expression_is_rejected():
    tool = SafeCalculator()
    with pytest.raises(ValueError):
        await tool.execute({"expression": "__import__('os').system('whoami')"})


def test_agent_detects_calculation():
    registry = ToolRegistry([SafeCalculator()])
    agent = AgentRuntime(registry)

    decision = agent.decide("Calculate 25 * 4")

    assert decision.tool_call is not None
    assert decision.tool_call.name == "calculator"
    assert decision.tool_call.arguments["expression"] == "25 * 4"


def test_agent_does_not_force_tool_use():
    registry = ToolRegistry([SafeCalculator()])
    agent = AgentRuntime(registry)

    decision = agent.decide("Write a short email")
    assert decision.tool_call is None
