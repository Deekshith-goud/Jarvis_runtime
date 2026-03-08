import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure we can import the runtime
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.command_router import route_command, init_router
from storage.database import DatabaseManager

class TestJarvisRuntimeSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize router with mocked dependencies to avoid side effects
        cls.db = MagicMock(spec=DatabaseManager)
        cls.timer_manager = MagicMock()
        cls.timer_callback = MagicMock()
        cls.personal_memory = MagicMock()
        cls.session_memory = MagicMock()
        cls.ai_engine = MagicMock()
        cls.ai_engine.generate.return_value = {"success": True, "content": "Mocked AI Output"}
        cls.ai_router = MagicMock()
        cls.ai_router.route.return_value = "explain"
        cls.prompt_builder = MagicMock()
        cls.focus_manager = MagicMock()
        cls.focus_manager.is_active.return_value = False
        cls.session_tracker = MagicMock()
        cls.analytics_tracker = MagicMock()

        init_router(
            cls.db, cls.timer_manager, cls.timer_callback,
            cls.personal_memory, cls.session_memory,
            cls.ai_engine, cls.ai_router, cls.prompt_builder,
            cls.focus_manager, cls.session_tracker, cls.analytics_tracker
        )

    def test_normal_commands(self):
        print("\n--- Testing Normal Commands ---")
        commands = [
            "what time is it",
            "add task test task",
            "list tasks",
            "set timer for 5 minutes",
            "open notepad",
            "open google",
            "explain quantum physics"
        ]
        for cmd in commands:
            res = route_command(cmd)
            self.assertIsNotNone(res)
            print(f"[OK] '{cmd}' -> {res[:50]}...")

    @patch('skills.app_skill.subprocess.Popen')
    def test_command_injection(self, mock_popen):
        print("\n--- Testing Command Injection (App Skill) ---")
        malicious_commands = [
            'open calc" & echo vulnerable & "',
            'launch app; rm -rf /;',
            'start `id`'
        ]
        for cmd in malicious_commands:
            res = route_command(cmd)
            print(f"Command '{cmd}' resulted in Popen call:")
            # Check what arguments were passed to Popen
            if mock_popen.called:
                call_args = mock_popen.call_args[0][0]
                print(f"  -> Executed: {call_args}")
                if "&" in str(call_args) or ";" in str(call_args):
                     print("  -> VULNERABILITY CONFIRMED: Shell metacharacters passed to Popen!")
            mock_popen.reset_mock()

    @patch('core.command_router.save_as_text')
    @patch('core.command_router.os.path.exists', return_value=True)
    def test_path_traversal(self, mock_exists, mock_save_text):
        print("\n--- Testing Path Traversal (save as command) ---")
        # Ensure there is a last ai output
        import core.command_router
        core.command_router._last_ai_output = "Malicious file content"
        
        malicious_commands = [
            "save as ../../../test.txt",
            "save as C:\\Windows\\System32\\drivers\\etc\\hosts.txt"
        ]
        for cmd in malicious_commands:
            res = route_command(cmd)
            print(f"Command '{cmd}' result: {res}")
            
            # Since builtin open is used for save as .txt let's check what path it tries to open
            # Wait, command router uses direct `open` for save as custom name
            
            pass

class TestSaveAsTraversal(unittest.TestCase):
    def setUp(self):
        # Set up globals for command_router directly
        import core.command_router
        core.command_router._last_ai_output = "AI content"
        self.db = MagicMock()
        core.command_router.init_router(
            self.db, MagicMock(), MagicMock(), MagicMock(), MagicMock(),
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )

    @patch('core.command_router.open', create=True)
    def test_save_as(self, mock_open):
        print("\n--- Testing Path Traversal (direct save as) ---")
        cmd = "save as ../../../evil.bat"
        import core.command_router
        res = core.command_router.route_command(cmd)
        if mock_open.called:
            filename = mock_open.call_args[0][0]
            print(f"  -> File opened: {filename}")
            if ".." in filename or "evil.bat" in filename:
                print("  -> VULNERABILITY CONFIRMED: Path traversal allowed!")

    def test_edge_cases(self):
        print("\n--- Testing Edge Cases ---")
        import core.command_router
        cases = [
            "",
            "   ",
            "A" * 10000,
            "null\x00byte",
            "drop table tasks;"
        ]
        for c in cases:
            try:
                res = core.command_router.route_command(c)
                print(f"[OK] Handled edge case length {len(c)}")
            except Exception as e:
                print(f"[FAIL] Edge case crashed: {e}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
