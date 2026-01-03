# test_motor_cortex.py
"""
Phase 15.1: MotorCortex Unit Tests
Mock-based testing for isolated verification.
"""

import unittest
from unittest.mock import MagicMock, PropertyMock


class MockHormoneManager:
    """Mock HormoneManager for isolated testing"""
    def __init__(self):
        self._values = {
            "DOPAMINE": 50.0,
            "ADRENALINE": 20.0,
            "BOREDOM": 0.0,
        }
    
    def get(self, hormone):
        # hormone is an Enum, get its name
        name = hormone.name if hasattr(hormone, 'name') else str(hormone)
        return self._values.get(name, 50.0)


class MockMemory:
    """Mock GeologicalMemory"""
    def get_spatial_gradient(self, gx, gz):
        # Return direction scores
        return {"North": 0.5, "South": 0.8, "East": 0.3, "West": 0.4}


class TestMotorCortexInitialization(unittest.TestCase):
    """Test MotorCortex initialization with DI"""
    
    def test_init_with_minimal_deps(self):
        """MotorCortex should initialize with just hormones and memory"""
        from src.brain_stem.motor_cortex import MotorCortex
        
        mock_hormones = MockHormoneManager()
        mock_memory = MockMemory()
        
        cortex = MotorCortex(
            hormones=mock_hormones,
            memory=mock_memory
        )
        
        self.assertIsNotNone(cortex)
        self.assertEqual(cortex.hormones, mock_hormones)
        self.assertEqual(cortex.memory, mock_memory)


class TestMotorCortexGradientAction(unittest.TestCase):
    """Test gradient-based movement decisions"""
    
    def test_calculate_gradient_action(self):
        """Should return a valid movement action"""
        from src.brain_stem.motor_cortex import MotorCortex
        
        mock_hormones = MockHormoneManager()
        mock_memory = MockMemory()
        
        cortex = MotorCortex(
            hormones=mock_hormones,
            memory=mock_memory
        )
        
        pos = {"x": 100.0, "z": -50.0, "yaw": 0.0}
        action = cortex.calculate_gradient_action(pos)
        
        self.assertIn(action, ["MOVE_FORWARD", "TURN_LEFT", "TURN_RIGHT"])


class TestMotorCortexUpdate(unittest.TestCase):
    """Test update() method"""
    
    def test_update_returns_tuple(self):
        """update() should return (fx, fy) tuple"""
        from src.brain_stem.motor_cortex import MotorCortex
        
        mock_hormones = MockHormoneManager()
        mock_memory = MockMemory()
        
        # No visual_bridge = should return (0, 0) safely
        cortex = MotorCortex(
            hormones=mock_hormones,
            memory=mock_memory,
            visual_bridge=None
        )
        
        result = cortex.update()
        self.assertEqual(result, (0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
