import json
from storage.database import DatabaseManager

def create_macro(db: DatabaseManager, name: str, actions: list[str]) -> str:
    name = name.lower().strip()
    if len(name) < 3:
        return "Macro name must be at least 3 characters long."
        
    builtin_commands = [
        "open", "launch", "start", "search", "go to", 
        "set timer", "cancel timer", "check timer", "remind me",
        "add task", "list tasks", "show tasks", "complete task", "finish task", "delete task", "remove task",
        "enter focus mode", "exit focus mode", "start work session", "end work session",
        "create macro", "delete macro", "list macros"
    ]
    
    for builtin in builtin_commands:
        if name.startswith(builtin):
            return f"Macro name '{name}' conflicts with a built-in command."
            
    if not actions:
        return "A macro must have at least one action."
        
    actions_json = json.dumps([a.strip() for a in actions if a.strip()])
    if db.create_macro(name, actions_json):
        return f"Macro '{name}' created with {len(actions)} action(s)."
    return f"Failed to create macro '{name}'."

def delete_macro(db: DatabaseManager, name: str) -> str:
    name = name.lower().strip()
    if db.delete_macro(name):
        return f"Macro '{name}' deleted."
    return f"Macro '{name}' not found."

def list_macros(db: DatabaseManager) -> str:
    macros = db.list_macros()
    if not macros:
        return "No macros found."
        
    res = ["Saved Macros:"]
    for m in macros:
        actions = json.loads(m['actions'])
        res.append(f"- {m['name']}: {', '.join(actions)}")
        
    return "\n".join(res)

def get_macro(db: DatabaseManager, name: str) -> list[str] | None:
    actions_json = db.get_macro(name.lower().strip())
    if actions_json:
        return json.loads(actions_json)
    return None
