from datetime import datetime, timedelta

class MorningBriefing:
    @staticmethod
    def generate(database_manager, focus_manager) -> str:
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%A, %B %d, %Y")
        
        # Pending tasks
        tasks = database_manager.list_tasks()
        pending_count = len(tasks)
        
        # Suggested task
        suggested = "None"
        if tasks:
            suggested = tasks[0]["task"]
            
        # Upcoming reminders (next 24 hours)
        current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        limit_time = now + timedelta(days=1)
        limit_time_str = limit_time.strftime("%Y-%m-%d %H:%M:%S")
        
        reminders = database_manager.get_upcoming_reminders(current_time_str, limit_time_str)
        reminder_count = len(reminders)
        
        # Focus state
        focus_state = "Active" if focus_manager.is_active() else "Inactive"
        
        briefing = f"Good morning! It is {time_str} on {date_str}.\n"
        briefing += f"Focus Mode: {focus_state}\n"
        briefing += f"You have {pending_count} pending tasks.\n"
        briefing += f"Suggested task to start with: {suggested}\n"
        briefing += f"You have {reminder_count} upcoming reminders in the next 24 hours."
        
        return briefing
