import sys
import os
import time
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.command_router import route_command, init_router
from storage.database import DatabaseManager

def run_comprehensive_tests():
    db = MagicMock(spec=DatabaseManager)
    db.add_task.return_value = True
    db.list_tasks.return_value = [{"id": 1, "task": "finish the report", "status": "pending", "created_at": "2026-02-23 09:00:00"}]
    db.get_last_pending_task.return_value = {"id": 1, "task": "finish the report", "created_at": "2026-02-23 09:00:00"}
    db.get_today_work_minutes.return_value = 120.5
    db.get_command_count_by_date.return_value = 42
    db.get_most_used_command.return_value = "what time is it"
    db.get_ai_call_stats.return_value = (10, 8, 2)
    db.get_task_completion_count.return_value = 5
    db.get_delivered_reminder_count.return_value = 2
    
    from scheduler.timer_manager import TimerManager
    timer_manager = TimerManager()
    
    timer_callback = MagicMock()
    
    personal_memory = MagicMock()
    personal_memory.add_memory.return_value = "I will remember that your favorite color is blue."
    personal_memory.list_memories.return_value = "1: your favorite color is blue"
    personal_memory.delete_memory.return_value = "Memory 1 deleted."
    
    session_memory = MagicMock()
    session_memory.get_last.return_value = {"last_command": "explain quantum mechanics", "last_response": "Mocked explanation"}
    
    ai_engine = MagicMock()
    ai_engine.generate.return_value = {"success": True, "content": "Mocked AI output: Quantum mechanics is a fundamental theory..."}
    
    ai_router = MagicMock()
    ai_router.route.return_value = "explain"
    ai_router.get_format.return_value = ".txt"
    
    prompt_builder = MagicMock()
    prompt_builder.build.return_value = "Mocked prompt"
    
    focus_manager = MagicMock()
    focus_manager.is_active.return_value = False
    focus_manager.enable.return_value = "Focus mode enabled."
    focus_manager.disable.return_value = "Focus mode disabled."
    
    session_tracker = MagicMock()
    session_tracker.start_session.return_value = "Work session started."
    session_tracker.end_session.return_value = "Work session ended."
    session_tracker.get_today_total_minutes.return_value = 120.5
    
    from analytics.analytics_tracker import AnalyticsTracker
    analytics_tracker = MagicMock()
    analytics_tracker.log_command = MagicMock()
    analytics_tracker.log_ai_call = MagicMock()
    analytics_tracker.get_command_counts_today.return_value = {"productivity": 5, "ai": 10}
    analytics_tracker.get_focus_minutes_today.return_value = 45.0
    analytics_tracker.get_ai_stats.return_value = (10, 8, 2)
    
    init_router(
        db, timer_manager, timer_callback,
        personal_memory, session_memory,
        ai_engine, ai_router, prompt_builder,
        focus_manager, session_tracker, analytics_tracker
    )

    commands_to_test = [
        # System & Time
        "time",
        "date",
        "day",
        "year",
        "invalid command syntax xyz",
        
        # Tasks
        "add task finish the report",
        "list tasks",
        "complete task 1",
        "delete task 2",
        "what was i doing",
        
        # Timers & Reminders
        "set timer for 10 minutes",
        "check timer",
        "cancel timer",
        "remind me in 5 minutes to call mom",
        
        # Focus & Productivity
        "good morning",
        "enter focus mode",
        "how long have i worked",
        "start work session",
        "end work session",
        
        # Memory
        "remember that the passcode is 1234",
        "what do you remember",
        "delete memory 1",
        
        # Analytics
        "show analytics",
        
        # Web & App mapping
        "open youtube",
        "search python tutorials",
        "launch notepad",
        
        # Screenshot & Clipboard
        "take screenshot",
        "read clipboard",
        "copy hello world",
        
        # AI Routing
        "explain quantum mechanics",
        "tell me more",
        "save it",
        "save as quantum_notes.txt"
    ]

    print("=== JARVIS COMPREHENSIVE COMMAND TEST OUTPUT ===\n")
    
    # Mocking side effects to prevent opening browsers or calc.exe during tests
    with patch('skills.app_skill.subprocess.Popen') as mock_popen, \
         patch('skills.web_skill.webbrowser.open') as mock_web, \
         patch('skills.screenshot_skill.pyautogui') as mock_pyautogui, \
         patch('skills.clipboard_skill.pyperclip') as mock_pyperclip, \
         patch('core.command_router.save_as_docx') as mock_save_docx, \
         patch('core.command_router.save_as_text') as mock_save_txt:
            
         mock_pyperclip.paste.return_value = "Mocked clipboard content"
            
         for cmd in commands_to_test:
             print(f"> {cmd}")
             if cmd == "check timer":
                 time.sleep(2)
             response = route_command(cmd)
             print(f"JARVIS: {response}\n")

if __name__ == '__main__':
    run_comprehensive_tests()
