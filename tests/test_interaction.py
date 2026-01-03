import unittest
import sys
import os
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.games.minecraft.game_brain import MinecraftBrain
from src.body.hormones import Hormone

class TestInteraction(unittest.TestCase):
    def setUp(self):
        # Mock GeodeBrain
        self.mock_core_brain = MagicMock()
        self.mock_core_brain.hormones = MagicMock()
        self.mock_core_brain.hormones.get.side_effect = lambda h: 0.0 # Default
        
        # Instantiate MinecraftBrain with mocked core
        self.mc_brain = MinecraftBrain(self.mock_core_brain)

    def test_digging_trigger_boredom(self):
        """退屈な時、目の前に土があれば掘ろうとするか (GameBrain)"""
        # 条件設定
        self.mock_core_brain.hormones.get.side_effect = lambda h: 25.0 if h == Hormone.BOREDOM else 0.0
        
        state = {
            "cursor": {"name": "minecraft:dirt"},
            "isDigging": False
        }
        
        dig_count = 0
        trials = 100
        for _ in range(trials):
            intent = self.mc_brain.decide_intent(state)
            if intent == "DIG":
                dig_count += 1
                
        print(f"Digging Frequency (Boredom): {dig_count}/{trials}")
        self.assertGreater(dig_count, 10, "Should dig reasonably often when bored and looking at dirt")

    def test_digging_avoid_hard_blocks(self):
        """硬いブロック（岩盤）は掘らないか"""
        self.mock_core_brain.hormones.get.side_effect = lambda h: 50.0 if h == Hormone.BOREDOM else 0.0
        
        state = {
            "cursor": {"name": "minecraft:bedrock"},
            "isDigging": False
        }
        
        dig_count = 0
        for _ in range(50):
            intent = self.mc_brain.decide_intent(state)
            if intent == "DIG":
                dig_count += 1
                
        self.assertEqual(dig_count, 0, "Should NEVER dig bedrock even if bored")

    def test_wait_while_digging(self):
        """掘削中は WAIT を返すか"""
        state = {"isDigging": True}
        intent = self.mc_brain.decide_intent(state)
        self.assertEqual(intent, "WAIT", "Should wait if already digging")

    def test_placing_creative_drive(self):
        """創造的衝動 (Dopamine High + Boredom) -> PLACE"""
        # Boredom > 15, Dopamine > 40
        self.mock_core_brain.hormones.get.side_effect = lambda h: 25.0 if h == Hormone.BOREDOM else (50.0 if h == Hormone.DOPAMINE else 0.0)
        
        state = {
            "cursor": {"name": "minecraft:dirt"}, # Something to place on
            "isDigging": False
        }
        
        place_count = 0
        trials = 100
        for _ in range(trials):
            intent = self.mc_brain.decide_intent(state)
            if intent == "PLACE":
                place_count += 1
                
        # action_weights["PLACE"] += (25-15)*0.1 = 1.0
        # action_weights["PLACE"] += 0.6 (Looking at block) = 1.6
        # action_weights["WAIT"] += 0.2
        # Base: Move=1.0, Turn=1.0, Wait=0.3... Total ~4.0
        # Prob(PLACE) ~ 1.6 / 4.0 = 40%
        
        print(f"Placing Frequency (Creative): {place_count}/{trials}")
        self.assertGreater(place_count, 15, "Should PLACE often when creative and bored")

    def test_digging_destructive_drive(self):
        """破壊的衝動 (Dopamine Low + Boredom) -> DIG"""
        # Boredom > 15, Dopamine < 40
        self.mock_core_brain.hormones.get.side_effect = lambda h: 25.0 if h == Hormone.BOREDOM else (10.0 if h == Hormone.DOPAMINE else 0.0)
        
        state = {
            "cursor": {"name": "minecraft:dirt"},
            "isDigging": False
        }
        
        dig_count = 0
        trials = 100
        for _ in range(trials):
            intent = self.mc_brain.decide_intent(state)
            if intent == "DIG":
                dig_count += 1
                
        print(f"Digging Frequency (Destructive): {dig_count}/{trials}")
        self.assertGreater(dig_count, 15, "Should DIG often when destructive and bored")

if __name__ == '__main__':
    unittest.main()
