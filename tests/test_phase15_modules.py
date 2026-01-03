# test_phase15_modules.py
"""
Phase 15.2-15.4: Unit Tests for Modularized Brain Components
"""

import unittest
from unittest.mock import MagicMock


class MockHormoneManager:
    """Mock HormoneManager"""
    def __init__(self):
        self._values = {"DOPAMINE": 50.0, "CORTISOL": 0.0, "SEROTONIN": 50.0,
                       "BOREDOM": 0.0, "STIMULATION": 50.0, "GLUCOSE": 50.0}
    
    def get(self, hormone):
        name = hormone.name if hasattr(hormone, 'name') else str(hormone)
        return self._values.get(name, 50.0)
    
    def update(self, hormone, delta):
        name = hormone.name if hasattr(hormone, 'name') else str(hormone)
        if name in self._values:
            self._values[name] += delta
    
    def decay_all(self, factor):
        pass


class MockMemory:
    """Mock GeologicalMemory"""
    def __init__(self):
        self.concepts = {"LOC:0:0": [0, 0, 0, 5, 0.5]}
        self.lock = MagicMock()
    
    def get_coords(self, key):
        return [0, 0]
    
    def reinforce(self, key, valence):
        pass


class TestSensoryCortex(unittest.TestCase):
    """Test SensoryCortex initialization and methods"""
    
    def test_init(self):
        from src.brain_stem.sensory_cortex import SensoryCortex
        cortex = SensoryCortex(
            hormones=MockHormoneManager(),
            memory=MockMemory()
        )
        self.assertIsNotNone(cortex)
    
    def test_process_visual_input(self):
        from src.brain_stem.sensory_cortex import SensoryCortex
        cortex = SensoryCortex(
            hormones=MockHormoneManager(),
            memory=MockMemory()
        )
        # Should not raise
        cortex.process_visual_input({"name": "minecraft:stone"})
    
    def test_process_spatial_input(self):
        from src.brain_stem.sensory_cortex import SensoryCortex
        cortex = SensoryCortex(
            hormones=MockHormoneManager(),
            memory=MockMemory()
        )
        cortex.process_spatial_input({"x": 100.0, "y": 64.0, "z": -50.0})


class TestDreamEngine(unittest.TestCase):
    """Test DreamEngine initialization and methods"""
    
    def test_init(self):
        from src.brain_stem.dream_engine import DreamEngine
        engine = DreamEngine(
            hormones=MockHormoneManager(),
            memory=MockMemory()
        )
        self.assertIsNotNone(engine)
    
    def test_process_dream(self):
        from src.brain_stem.dream_engine import DreamEngine
        engine = DreamEngine(
            hormones=MockHormoneManager(),
            memory=MockMemory()
        )
        # Should not raise
        engine.process_dream()
    
    def test_process_autonomous_thought(self):
        from src.brain_stem.dream_engine import DreamEngine
        engine = DreamEngine(
            hormones=MockHormoneManager(),
            memory=MockMemory()
        )
        result = engine.process_autonomous_thought()
        # Can be None or dict
        self.assertTrue(result is None or isinstance(result, dict))


class TestMetabolismManager(unittest.TestCase):
    """Test MetabolismManager initialization and methods"""
    
    def test_init(self):
        from src.body.metabolism import MetabolismManager
        manager = MetabolismManager(
            hormones=MockHormoneManager(),
            memory=MockMemory()
        )
        self.assertIsNotNone(manager)
    
    def test_update(self):
        from src.body.metabolism import MetabolismManager
        manager = MetabolismManager(
            hormones=MockHormoneManager(),
            memory=MockMemory()
        )
        # Should not raise
        manager.update(cpu_percent=30.0, memory_percent=50.0, current_hour=14)
    
    def test_check_sleep_condition(self):
        from src.body.metabolism import MetabolismManager
        manager = MetabolismManager(
            hormones=MockHormoneManager(),
            memory=MockMemory()
        )
        result = manager.check_sleep_condition()
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    unittest.main()
