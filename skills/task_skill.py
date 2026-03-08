def handle_task(command: str, db) -> str:
    lower = command.lower()

    if lower.startswith("add task "):
        text = command[9:].strip()
        if not text:
            return "No task specified."
        if not db.add_task(text):
            return "Task already exists."
        return "Task added: " + text

    if "list task" in lower:
        tasks = db.list_tasks()
        if not tasks:
            return "No pending tasks."
        lines = ["Pending tasks:"]
        for t in tasks:
            lines.append(str(t["id"]) + ". " + t["task"])
        return "\n".join(lines)

    if "complete task" in lower or "finish task" in lower:
        parts = lower.replace("complete task ", "").replace("finish task ", "").strip()
        try:
            task_id = int(parts)
        except ValueError:
            return "Invalid task ID."
        db.mark_task_done(task_id)
        return "Task " + str(task_id) + " marked as done."

    if "delete task" in lower or "remove task" in lower:
        parts = lower.replace("delete task ", "").replace("remove task ", "").strip()
        try:
            task_id = int(parts)
        except ValueError:
            return "Invalid task ID."
        db.delete_task(task_id)
        return "Task " + str(task_id) + " deleted."

    if "what was i doing" in lower or "last task" in lower:
        task = db.get_last_pending_task()
        if not task:
            return "No pending tasks found."
        return "Your last task: " + task["task"]

    return "Unknown task command."
