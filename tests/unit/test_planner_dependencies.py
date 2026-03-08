from jarvis.core.planner import Planner


def test_planner_creates_dependency_for_summarize_after_search():
    planner = Planner()
    graph = planner.create_plan(
        {
            "actions": [
                {"intent": "search_web", "params": {"query": "python asyncio"}},
                {"intent": "summarize_results"},
            ]
        }
    )

    task1 = graph.get_task("task1")
    task2 = graph.get_task("task2")

    assert task1.intent == "search_web"
    assert task1.dependencies == []
    assert task2.intent == "summarize_results"
    assert task2.dependencies == ["task1"]


def test_planner_keeps_independent_tasks_parallel():
    planner = Planner()
    graph = planner.create_plan(
        {
            "actions": [
                {"intent": "open_youtube"},
                {"intent": "set_timer", "params": {"duration": 300}},
            ]
        }
    )

    task1 = graph.get_task("task1")
    task2 = graph.get_task("task2")

    assert task1.dependencies == []
    assert task2.dependencies == []
