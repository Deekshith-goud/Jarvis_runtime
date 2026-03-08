class ReportGenerator:
    @staticmethod
    def generate_report(analytics_tracker) -> str:
        today_commands = analytics_tracker.get_today_command_count()
        most_used = analytics_tracker.get_most_used_command()
        ai_total, ai_success, ai_failure = analytics_tracker.get_ai_stats()
        tasks_done = analytics_tracker.get_task_completion_count()
        reminders_fired = analytics_tracker.get_reminder_trigger_count()
        work_minutes = analytics_tracker.get_work_session_stats()
        focus_minutes = analytics_tracker.get_focus_minutes_today()

        total_seconds = int(round(work_minutes * 60))
        if total_seconds < 60:
            duration_str = f"{total_seconds} seconds"
        else:
            m = total_seconds // 60
            s = total_seconds % 60
            duration_str = f"{m} minutes {s} seconds"
            
        focus_seconds = int(round(focus_minutes * 60))
        if focus_seconds < 60:
            focus_str = f"{focus_seconds} seconds"
        else:
            fm = focus_seconds // 60
            fs = focus_seconds % 60
            focus_str = f"{fm} minutes {fs} seconds"

        report = "--- Productivity Analytics Report ---\n"
        report += f"Commands Issued Today: {today_commands}\n"
        report += f"Most Used Command: {most_used if most_used else 'N/A'}\n"
        
        if ai_total == 0:
            ai_str = "No AI usage today"
        else:
            success_rate = (ai_success / ai_total) * 100
            ai_str = f"{ai_total} calls ({success_rate:.1f}% success rate)"
            
        report += f"AI Calls Today: {ai_str}\n"
        report += f"Tasks Completed Today: {tasks_done}\n"
        report += f"Reminders Triggered Today: {reminders_fired}\n"
        report += f"Time Worked Today: {duration_str}\n"
        report += f"Time in Focus Mode Today: {focus_str}\n"
        report += "--------------------------------------"
        
        return report
