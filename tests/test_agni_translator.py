# test_agni_translator.py
"""
Phase 16: AgniTranslator Unit Tests
"""

import unittest
from unittest.mock import MagicMock, PropertyMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockHormoneManager:
    def __init__(self):
        self._values = {
            "DOPAMINE": 60.0,
            "ADRENALINE": 20.0,
            "CORTISOL": 10.0,
            "SEROTONIN": 50.0,
            "BOREDOM": 15.0,
        }
    
    def get(self, hormone):
        name = hormone.name if hasattr(hormone, 'name') else str(hormone)
        return self._values.get(name, 50.0)


class MockMemory:
    def __init__(self):
        self.concepts = {
            "リンゴ": [0, 0],
            "空": [1, 1],
            "水": [2, 2],
        }


class MockAgni:
    def __init__(self):
        self.client = None  # No real API
        self.limiter = MagicMock()
        self.limiter.consume = MagicMock(return_value=False)


class MockBrain:
    def __init__(self):
        self.hormones = MockHormoneManager()
        self.memory = MockMemory()
        self.mentor = MockAgni()


class TestAgniTranslatorInit(unittest.TestCase):
    """Test initialization"""
    
    def test_init(self):
        from src.cortex.agni_translator import AgniTranslator
        
        brain = MockBrain()
        translator = AgniTranslator(brain=brain)
        
        self.assertIsNotNone(translator)
        self.assertEqual(translator.total_requests, 0)


class TestAgniTranslatorTranslate(unittest.TestCase):
    """Test translate method"""
    
    def test_translate_without_agni(self):
        from src.cortex.agni_translator import AgniTranslator
        
        brain = MockBrain()
        translator = AgniTranslator(brain=brain)
        
        # Without Agni and without samples, should return None or simple string
        result = translator.translate(use_agni=False)
        # May be None if no samples exist
        self.assertTrue(result is None or isinstance(result, str))
    
    def test_capture_internal_state(self):
        from src.cortex.agni_translator import AgniTranslator
        
        brain = MockBrain()
        translator = AgniTranslator(brain=brain)
        
        state = translator._capture_internal_state()
        
        self.assertIn("hormones", state)
        self.assertIn("mood", state)
        self.assertIn("concepts", state)


class TestAgniTranslatorStats(unittest.TestCase):
    """Test statistics"""
    
    def test_get_stats(self):
        from src.cortex.agni_translator import AgniTranslator
        
        brain = MockBrain()
        translator = AgniTranslator(brain=brain)
        
        stats = translator.get_stats()
        
        self.assertIn("total_requests", stats)
        self.assertIn("agni_dependency", stats)
        self.assertIn("graduation_ready", stats)
    
    def test_check_graduation(self):
        from src.cortex.agni_translator import AgniTranslator
        
        brain = MockBrain()
        translator = AgniTranslator(brain=brain)
        
        # Not enough requests
        result = translator.check_graduation()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
