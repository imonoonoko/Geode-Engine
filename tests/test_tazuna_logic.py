
import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cortex.tazuna import Tazuna, TazunaSignal
from src.body.hormones import Hormone, HormoneManager

class TestTazuna(unittest.TestCase):
    def setUp(self):
        self.tazuna = Tazuna()
        self.hormones = HormoneManager()

    def test_normal_state(self):
        # Default state
        signal = self.tazuna.modulate(self.hormones)
        self.assertEqual(signal.mode, "NORMAL")
        self.assertEqual(signal.temperature, 1.0) # Serotonin 50 (default) -> 1.0

    def test_boredom_divergence(self):
        # Inject Boredom
        self.hormones.update(Hormone.BOREDOM, 100.0) # Add 100 to make it high
        # Check current value
        print(f"Boredom: {self.hormones.get(Hormone.BOREDOM)}")
        
        signal = self.tazuna.modulate(self.hormones)
        self.assertEqual(signal.mode, "DIVERGE")
        self.assertGreater(signal.temperature, 1.5)
        self.assertGreater(signal.radius_mod, 1.0)
        self.assertEqual(signal.vector_strategy, "ORTHOGONAL") # Check Strategy

    def test_serotonin_convergence(self):
        # Inject Serotonin
        self.hormones.update(Hormone.SEROTONIN, 100.0)
        
        signal = self.tazuna.modulate(self.hormones)
        self.assertEqual(signal.mode, "CONVERGE")
        self.assertLess(signal.temperature, 0.5)
        self.assertLess(signal.radius_mod, 1.0)

    def test_panic_state(self):
        # Inject Surprise
        self.hormones.update(Hormone.SURPRISE, 100.0)
        
        signal = self.tazuna.modulate(self.hormones)
        self.assertEqual(signal.mode, "PANIC")
        self.assertEqual(signal.temperature, 0.1)
        self.assertEqual(signal.radius_mod, 0.1)

if __name__ == '__main__':
    unittest.main()
