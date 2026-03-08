from jarvis.core.task_graph import STATUS_COMPLETE, STATUS_PENDING, TaskGraph, TaskNode


def test_independent_tasks_are_ready_together():
    graph = TaskGraph()
    graph.add_task(TaskNode(id="task1", intent="open_youtube"))
    graph.add_task(TaskNode(id="task2", intent="set_timer", params={"duration": 300}))

    ready = graph.get_ready_tasks()
    ready_ids = sorted(task.id for task in ready)

    assert ready_ids == ["task1", "task2"]


def test_dependency_blocks_until_parent_complete():
    graph = TaskGraph()
    graph.add_task(TaskNode(id="task1", intent="open_youtube"))
    graph.add_task(TaskNode(id="task2", intent="set_timer", params={"duration": 300}, dependencies=["task1"]))

    first_ready = graph.get_ready_tasks()
    assert [task.id for task in first_ready] == ["task1"]

    graph.mark_complete("task1")
    second_ready = graph.get_ready_tasks()
    assert [task.id for task in second_ready] == ["task2"]


def test_mark_complete_updates_status():
    graph = TaskGraph()
    graph.add_task(TaskNode(id="task1", intent="open_youtube"))

    graph.mark_complete("task1")

    task = graph.get_task("task1")
    assert task.status == STATUS_COMPLETE


def test_new_task_defaults_to_pending():
    task = TaskNode(id="task1", intent="open_youtube")
    assert task.status == STATUS_PENDING
