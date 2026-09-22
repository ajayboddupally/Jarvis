from intelligence.reasoning import classify_request


def test_tool_request():
    plan = classify_request("Please search for the latest weather.")
    assert plan.requires_tools is True
    assert plan.intent == "information_or_tool_request"


def test_general_request():
    plan = classify_request("Help me write a short email.")
    assert plan.requires_tools is False
    assert plan.intent == "general_assistance"
