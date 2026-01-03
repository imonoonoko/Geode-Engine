import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.games.minecraft.action import MinecraftActionModule

class TestMinecraftAction(unittest.TestCase):
    def setUp(self):
        self.action_mod = MinecraftActionModule()
    
    @patch('src.games.minecraft.action.user32')
    @patch('src.games.minecraft.action.pyautogui')
    def test_safety_lock(self, mock_gui, mock_user32):
        """Test that actions are BLOCKED if window is not Minecraft"""
        # 1. Setup Mock User32 to return "Notepad"
        mock_user32.GetForegroundWindow.return_value = 12345
        
        # Mocking ctypes buffer behavior is a bit tricky, assume logic holds if we control return
        # Instead of deep mocking ctypes, let's mock the text retrieval logic or just the is_minecraft_focused method for this specific test
        # But let's try to mock the whole method `is_minecraft_focused` for clarity
        with patch.object(self.action_mod, 'is_minecraft_focused', return_value=False):
            self.action_mod.act("MOVE_FORWARD")
            mock_gui.keyDown.assert_not_called()
            print("✅ Safety Lock Test Passed: Action Blocked when not connected.")

    @patch('src.games.minecraft.action.pyautogui')
    def test_action_execution(self, mock_gui):
        """Test efficient action execution when focused"""
        with patch.object(self.action_mod, 'is_minecraft_focused', return_value=True):
            # Move Forward
            self.action_mod.act("MOVE_FORWARD", duration=0.1)
            mock_gui.keyDown.assert_called_with('w')
            mock_gui.keyUp.assert_called_with('w')
            
            # Reset
            mock_gui.reset_mock()
            
            # Look
            self.action_mod.act("TURN_RIGHT", strength=50)
            mock_gui.moveRel.assert_called()
            print("✅ Action Execution Test Passed (W/Mock Focus).")

if __name__ == "__main__":
    unittest.main()
