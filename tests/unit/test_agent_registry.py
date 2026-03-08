from jarvis.core.agent_registry import AgentRegistry


class BrowserAgent:
    capabilities = ["open_website", "search_web"]


class ProductivityAgent:
    capabilities = ["set_timer"]

    def can_handle(self, intent: str) -> bool:
        return intent == "set_timer"


def test_register_and_get_all_agents():
    registry = AgentRegistry()
    browser = BrowserAgent()
    productivity = ProductivityAgent()

    registry.register(browser)
    registry.register(productivity)

    assert registry.get_all_agents() == [browser, productivity]


def test_find_agent_by_intent_using_capabilities():
    registry = AgentRegistry()
    browser = BrowserAgent()
    registry.register(browser)

    matched = registry.find_agent_by_intent("search_web")

    assert matched is browser


def test_find_agent_by_intent_using_can_handle():
    registry = AgentRegistry()
    productivity = ProductivityAgent()
    registry.register(productivity)

    matched = registry.find_agent_by_intent("set_timer")

    assert matched is productivity


def test_find_agent_by_intent_returns_none_if_no_agent():
    registry = AgentRegistry()
    registry.register(BrowserAgent())

    matched = registry.find_agent_by_intent("unknown_intent")

    assert matched is None
