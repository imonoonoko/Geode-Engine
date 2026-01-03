import unittest
import sys
import os
import threading
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.senses.mentor import AgniAccelerator, LeakyBucket
from src.cortex.memory import GeologicalMemory
from src.dna import config

class MockBrain:
    def __init__(self):
        self.memory = GeologicalMemory(size=100)
        self.memory.save_dir = "test_memory" # Redirect save
        if not os.path.exists("test_memory"):
            os.makedirs("test_memory")
            
        # Mock SedimentaryCortex
        self.sedimentary_cortex = MockSedimentary()

class MockSedimentary:
    def __init__(self):
        self.learned_texts = []
        
    def learn(self, text, trigger, surprise=0.0):
        self.learned_texts.append((text, trigger, surprise))

class TestAgniAccelerator(unittest.TestCase):
    def setUp(self):
        self.brain = MockBrain()
        self.mentor = AgniAccelerator(self.brain)
        # Force offline mock mode for safe testing without API Key
        self.mentor.connected = False 

    def test_mock_injection(self):
        """ Verify logic of injection using mock data """
        print("\n🔥 Testing Mock Injection...")
        result = self.mentor.inject_knowledge("Apple")
        
        self.assertTrue(result)
        
        # Check Memory
        self.assertIn("Apple", self.brain.memory.concepts)
        val = self.brain.memory.concepts["Apple"]
        # Format: [x,y,t,c,v,source]
        self.assertTrue(len(val) >= 6)
        self.assertEqual(val[5], "Agni_Teacher") # Default persona
        
        # Check Sedimentary
        self.assertTrue(len(self.brain.sedimentary_cortex.learned_texts) > 0)
        print("✅ Mock Injection Passed.")

    def test_leaky_bucket(self):
        """ Verify Rate Limiter Logic """
        print("\n⏳ Testing Rate Limiter...")
        # 60 RPM = 1 token / sec
        bucket = LeakyBucket(60) 
        
        # Should consume successfully
        self.assertTrue(bucket.consume(1.0))
        
        # Drain bucket manually
        bucket.tokens = 0.5
        
        # Should fail non-blocking
        self.assertFalse(bucket.consume(1.0, block=False))
        print("✅ Rate Limiter Passed.")

    def test_persona_switch(self):
        """ Verify Persona Switching """
        self.mentor.set_persona("Rival")
        self.assertEqual(self.mentor.current_persona, "Rival")
        
        # Inject
        self.mentor.inject_knowledge("Linux")
        val = self.brain.memory.concepts["Linux"]
        self.assertEqual(val[5], "Agni_Rival")
        print("✅ Persona Switch Passed.")

if __name__ == '__main__':
    unittest.main()
