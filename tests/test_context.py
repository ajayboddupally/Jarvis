from types import SimpleNamespace

from intelligence.context import build_context


def test_build_context():
    messages = [
        SimpleNamespace(role="user", content="Hello"),
        SimpleNamespace(role="assistant", content="Hi"),
    ]

    context = build_context(messages, "How are you?")

    assert context == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"},
        {"role": "user", "content": "How are you?"},
    ]
