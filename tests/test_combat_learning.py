import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.games.minecraft.game_brain import MinecraftBrain
from src.body.hormones import Hormone, HormoneManager

class TestCombatLearning(unittest.TestCase):
    def setUp(self):
        # Mock Brain & Memory
        self.mock_brain = MagicMock()
        self.mock_brain.hormones = HormoneManager()
        self.mock_brain.memory = MagicMock()
        
        # Default Memory Behavior (Unknown Mob)
        self.mock_brain.memory.get_combat_win_rate.return_value = 0.5
        
        self.game_brain = MinecraftBrain(self.mock_brain)

    def test_encounter_pain_response(self):
        """Test reaction to pain (high Cortisol)"""
        # Scenario: High Pain (Cortisol 80), Nearby Enemy
        state = {
            "nearestMob": {"name": "zombie", "isEnemy": True, "distance": 2.0},
            "isDigging": False
        }
        self.mock_brain.hormones.update(Hormone.CORTISOL, 80.0) # High Stress
        
        # Decision
        intent = self.game_brain.decide_intent(state)
        
        # 距離が近い & 痛みがある -> ATTACK or FLEE (Action Bias High)
        # 初期WinRate 0.5 なので ATTACK/FLEE 半々だが、距離2.0だとパニックでどちらかが出るはず
        print(f"Panic Intent: {intent}")
        self.assertIn(intent, ["ATTACK", "MOVE_FORWARD"]) # MOVE_FORWARD is FLEE here

    def test_reinforcement_learning_win(self):
        """Test behavior change after Winning"""
        # 1. Simulate Win Experience -> High Win Rate
        self.mock_brain.memory.get_combat_win_rate.return_value = 0.9 # Confident
        
        state = {
            "nearestMob": {"name": "zombie", "isEnemy": True, "distance": 5.0},
        }
        self.mock_brain.hormones.update(Hormone.CORTISOL, 50.0) # Moderate Threat
        
        intents = [self.game_brain.decide_intent(state) for _ in range(20)]
        attack_count = intents.count("ATTACK")
        flee_count = intents.count("MOVE_FORWARD")
        
        print(f"Win Biased Intents: Attack={attack_count}, Flee={flee_count}")
        self.assertGreater(attack_count, flee_count, "Should prefer ATTACK after winning")

    def test_reinforcement_learning_loss(self):
        """Test behavior change after Losing"""
        # 1. Simulate Loss Experience -> Low Win Rate
        self.mock_brain.memory.get_combat_win_rate.return_value = 0.1 # Fearful
        
        state = {
            "nearestMob": {"name": "zombie", "isEnemy": True, "distance": 5.0},
        }
        self.mock_brain.hormones.update(Hormone.CORTISOL, 50.0)
        
        intents = [self.game_brain.decide_intent(state) for _ in range(20)]
        attack_count = intents.count("ATTACK")
        flee_count = intents.count("MOVE_FORWARD")
        
        print(f"Loss Biased Intents: Attack={attack_count}, Flee={flee_count}")
        self.assertGreater(flee_count, attack_count, "Should prefer FLEE after losing")

if __name__ == '__main__':
    unittest.main()
