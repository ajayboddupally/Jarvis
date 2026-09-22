from intelligence.models import Message


def build_context(messages: list[Message], new_message: str) -> list[dict[str, str]]:
    context = [
        {"role": message.role, "content": message.content}
        for message in messages
    ]
    context.append({"role": "user", "content": new_message})
    return context
