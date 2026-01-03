import unittest
from unittest.mock import MagicMock
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.cortex.language_center import LanguageCenter
from src.body.hormones import Hormone

class MockBrain:
    def __init__(self):
        self.hormones = {
            Hormone.ADRENALINE: 0,
            Hormone.DOPAMINE: 0,
            Hormone.CORTISOL: 0,
            Hormone.SURPRISE: 0,
            Hormone.SOCIAL: 0
        }
        self.memory = MagicMock()
        self.prediction_engine = MagicMock()
        self.sedimentary_cortex = MagicMock()
        self.sedimentary_cortex.all_fragments = [] # Empty for template testing

class TestChimeraSlots(unittest.TestCase):
    def setUp(self):
        self.brain = MockBrain()
        self.broca = LanguageCenter(self.brain)
        
        # Mock Memory: Setup some concepts
        # format: dictionary of concepts -> [vec] (simplified for test)
        self.brain.memory.concepts = {
            "りんご": [0,0,0,0,0,0], # Dummy
            "食べる": [0,0,0,0,0,0],
            "おいしい": [0,0,0,0,0,0],
            "敵": [0,0,0,0,0,0],
            "倒す": [0,0,0,0,0,0],
            "悪い": [0,0,0,0,0,0]
        }
        
        # Mock Embedding Cache returning vectors
        # Vector logic:
        #  - Thought Vector: [1.0, 0.0]
        #  - "りんご" (Apple) -> matches [1.0, 0.0]
        #  - "敵" (Enemy) -> matches [-1.0, 0.0]
        
        def mock_embedding_get(word):
            if word == "りんご": return np.array([1.0, 0.0])
            if word == "食べる": return np.array([0.9, 0.1])
            if word == "おいしい": return np.array([0.9, 0.0])
            if word == "敵": return np.array([-1.0, 0.0])
            if word == "倒す": return np.array([-0.9, 0.1])
            if word == "悪い": return np.array([-0.9, 0.0])
            return np.array([0.0, 0.0])

        self.brain.prediction_engine.embedding_cache.get.side_effect = mock_embedding_get
        
        # Determine POS for mock
        def mock_check_pos(word, target_pos):
            pos_map = {
                "りんご": "名詞", "敵": "名詞",
                "食べる": "動詞", "倒す": "動詞",
                "おいしい": "形容詞", "悪い": "形容詞"
            }
            return pos_map.get(word, "") == target_pos

        self.broca._check_pos = mock_check_pos

    def test_anger_template(self):
        print("\n🧪 Testing Anger Template...")
        # Adrenaline Spike
        self.brain.hormones[Hormone.ADRENALINE] = 80
        
        # Thought Vector: Negative (Enemy)
        thought = np.array([-1.0, 0.0])
        
        # Force strict template usage
        self.broca._retrieve_shell = MagicMock(return_value=None) 
        
        # Should generate something like "許せない、敵！" or "敵は悪いだ！"
        generated = self.broca.speak(thought, valence_state=-0.8)
        print(f"   Output: {generated}")
        
        # Assertions
        self.assertTrue("敵" in generated or "悪い" in generated or "倒す" in generated)
        self.assertTrue("！" in generated) # Anger templates have !

    def test_curiosity_template(self):
        print("\n🧪 Testing Curiosity Template...")
        # Dopamine & Surprise Spike
        self.brain.hormones[Hormone.DOPAMINE] = 60
        self.brain.hormones[Hormone.SURPRISE] = 0.8
        
        # Thought Vector: Positive (Apple)
        thought = np.array([1.0, 0.0])
        self.broca._retrieve_shell = MagicMock(return_value=None) 
        
        generated = self.broca.speak(thought, valence_state=0.5)
        print(f"   Output: {generated}")
        
        # Assertions
        self.assertTrue("りんご" in generated or "おいしい" in generated)
        self.assertTrue("？" in generated or "かな" in generated or "何" in generated or "みたい" in generated)

    def test_calm_template(self):
        print("\n🧪 Testing Calm Template...")
        # Low hormones
        self.brain.hormones[Hormone.ADRENALINE] = 10
        self.brain.hormones[Hormone.DOPAMINE] = 10
        
        thought = np.array([1.0, 0.0])
        self.broca._retrieve_shell = MagicMock(return_value=None) 
        
        generated = self.broca.speak(thought, valence_state=0.0)
        print(f"   Output: {generated}")
        
        # Assertions
        self.assertTrue("です" in generated or "ます" in generated or "。" in generated)


if __name__ == '__main__':
    unittest.main()
