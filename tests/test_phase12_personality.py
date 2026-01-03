import unittest
import time
import threading
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock
from src.body.hormones import Hormone, HormoneManager
import src.dna.config as config

class TestPhase12Personality(unittest.TestCase):
    def setUp(self):
        self.hormones = HormoneManager()
        # Mock config if needed, but defaults are fine
        
    def test_homeostasis_convergence(self):
        """
        Verify that hormones return to baseline (50.0) over time
        via self_reference_update logic.
        """
        # 1. Set extreme value (Anger)
        self.hormones.set(Hormone.ADRENALINE, 100.0)
        
        # 2. Update loop simulation
        # Expected: Decays towards baseline (50.0)
        # Assuming gamma=0.05, kappa=0.03, tanh logic
        prev_val = 100.0
        for _ in range(10):
            self.hormones.self_reference_update()
            current_val = self.hormones.get(Hormone.ADRENALINE)
            # print(f"Adrenaline: {current_val:.2f}")
            
            # Should decrease (return to homeostasis)
            self.assertLess(current_val, prev_val)
            prev_val = current_val
            
        # 3. Check significant decay after 50 steps
        for _ in range(40):
            self.hormones.self_reference_update()
            
        final_val = self.hormones.get(Hormone.ADRENALINE)
        # Should be closer to 50 than 100
        self.assertLess(final_val, 80.0)
        
    def test_homeostasis_upward(self):
        """
        Verify that low values also return to baseline
        """
        self.hormones.set(Hormone.DOPAMINE, 0.0)
        prev_val = 0.0
        
        for _ in range(10):
            self.hormones.self_reference_update()
            current_val = self.hormones.get(Hormone.DOPAMINE)
            self.assertGreater(current_val, prev_val)
            prev_val = current_val

    def test_personality_deviation_logic(self):
        """
        Verify deviation calculation logic used in LanguageCenter
        """
        baseline = 50.0
        self.hormones.set(Hormone.ADRENALINE, 80.0)
        
        dev = self.hormones.get(Hormone.ADRENALINE) - baseline
        self.assertAlmostEqual(dev, 30.0)
        
        # Threshold check
        is_angry = dev > 20.0
        self.assertTrue(is_angry)

if __name__ == '__main__':
    unittest.main()
