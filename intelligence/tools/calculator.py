import ast
import math
import operator
from typing import Any

from intelligence.tools.base import Tool, ToolDefinition


class SafeCalculator(Tool):
    definition = ToolDefinition(
        name="calculator",
        description="Safely evaluate basic arithmetic expressions.",
        input_schema={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Arithmetic expression such as (125 * 4) / 2.",
                }
            },
            "required": ["expression"],
        },
    )

    _binary_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    _unary_ops = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    _functions = {
        "abs": abs,
        "round": round,
        "sqrt": math.sqrt,
    }

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        expression = str(arguments.get("expression", "")).strip()

        if not expression or len(expression) > 500:
            raise ValueError("Expression must contain 1-500 characters")

        tree = ast.parse(expression, mode="eval")
        result = self._evaluate(tree.body)

        if isinstance(result, complex):
            raise ValueError("Complex results are not supported")

        return {
            "expression": expression,
            "result": result,
        }

    def _evaluate(self, node: ast.AST) -> float | int:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            if isinstance(node.value, bool):
                raise ValueError("Boolean values are not allowed")
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in self._binary_ops:
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Exponent is too large")

            return self._binary_ops[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in self._unary_ops:
            return self._unary_ops[type(node.op)](self._evaluate(node.operand))

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            function = self._functions.get(node.func.id)
            if function is None or node.keywords:
                raise ValueError("Unsupported function")
            if len(node.args) > 2:
                raise ValueError("Too many arguments")
            return function(*(self._evaluate(arg) for arg in node.args))

        raise ValueError("Unsupported expression")
