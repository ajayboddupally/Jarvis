import json
from typing import Any


def append_tool_result(
    messages: list[dict[str, str]],
    tool_output: dict[str, Any] | None,
) -> list[dict[str, str]]:
    if not tool_output:
        return messages

    enriched = list(messages)
    enriched.append(
        {
            "role": "system",
            "content": (
                "Tool execution result. Use this result when answering the user.\n"
                + json.dumps(tool_output, ensure_ascii=False)
            ),
        }
    )
    return enriched
