from ai.ai_router import AIRouter


def test_ai_router_route_priority_code_over_explain():
    router = AIRouter()
    command = "Explain recursion and write a python script for factorial"
    assert router.route(command) == "code"


def test_ai_router_detect_language_and_format():
    router = AIRouter()

    assert router.detect_language("write a script in javascript") == ".js"
    assert router.get_format("code", "create program in rust") == ".rs"
    assert router.get_format("notes", "summarize this topic") == ".txt"
    assert router.get_format("research", "research ai trends") == ".docx"
