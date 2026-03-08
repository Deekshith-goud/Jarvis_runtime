import asyncio

from jarvis.agents.browser_agent import BrowserAgent
from jarvis.agents.code_agent import CodeAgent
from jarvis.agents.productivity_agent import ProductivityAgent
from jarvis.agents.research_agent import ResearchAgent
from jarvis.agents.system_agent import SystemAgent


def test_system_agent_contract():
    agent = SystemAgent()
    assert agent.capabilities == ["open_app", "open_website"]
    assert agent.can_handle("open_app") is True
    assert agent.can_handle("search_web") is False

    result = asyncio.run(agent.execute({"intent": "open_app", "params": {"app": "notepad"}}, {"source": "test"}))
    assert result["agent"] == "system_agent"
    assert result["status"] == "completed"


def test_productivity_agent_contract():
    agent = ProductivityAgent()
    assert agent.capabilities == ["set_timer", "check_timer", "cancel_timer", "create_task", "set_reminder"]
    assert agent.can_handle("set_timer") is True
    assert agent.can_handle("open_website") is False

    result = asyncio.run(
        agent.execute({"intent": "set_timer", "params": {"duration": 300}}, {"source": "test"})
    )
    assert result["agent"] == "productivity_agent"
    assert result["status"] == "completed"


def test_browser_agent_contract():
    agent = BrowserAgent()
    assert agent.capabilities == ["search_web", "open_youtube", "open_website"]
    assert agent.can_handle("search_web") is True
    assert agent.can_handle("set_timer") is False

    result = asyncio.run(
        agent.execute({"intent": "open_youtube", "params": {"query": "music"}}, {"source": "test"})
    )
    assert result["agent"] == "browser_agent"
    assert result["status"] == "completed"


def test_research_agent_contract_and_small_reasoning_route():
    agent = ResearchAgent()
    assert agent.capabilities == ["research_topic", "summarize_text", "answer_question"]
    assert agent.can_handle("research_topic") is True
    assert agent.can_handle("open_youtube") is False

    result = asyncio.run(
        agent.execute({"intent": "research_topic", "params": {"topic": "quantum computing"}}, {"source": "test"})
    )
    assert result["agent"] == "research_agent"
    assert result["provider"] == "groq"
    assert isinstance(result["response"], str)


def test_research_agent_routes_large_reasoning_to_gemini():
    agent = ResearchAgent()
    long_question = " ".join(["explain"] * 30)

    result = asyncio.run(
        agent.execute({"intent": "answer_question", "params": {"question": long_question}}, {"source": "test"})
    )

    assert result["provider"] == "gemini"


class SpyCodexClient:
    def __init__(self) -> None:
        self.calls = []

    async def generate(self, prompt: str, metadata: dict):
        self.calls.append({"prompt": prompt, "metadata": metadata})
        return "print('hello from codex')"


def test_code_agent_uses_codex_for_generation_tasks():
    client = SpyCodexClient()
    agent = CodeAgent(codex_client=client)

    task = {
        "id": "task1",
        "intent": "generate_code",
        "params": {"language": "python", "task": "write a web scraper"},
    }
    result = asyncio.run(agent.execute(task, {"source": "test"}))

    assert agent.can_handle("generate_code") is True
    assert agent.can_handle("open_youtube") is False
    assert result["provider"] == "codex"
    assert result["status"] == "accepted"
    assert result["response"] == "print('hello from codex')"
    assert len(client.calls) == 1
    assert "Generate python: write a web scraper" in client.calls[0]["prompt"]
