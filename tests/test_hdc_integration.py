import sys
import os
import numpy as np
import time

sys.path.append(os.getcwd())

from src.cortex.memory import GeologicalMemory
from src.cortex.language_center import LanguageCenter
from src.cortex.inference import PredictionEngine, EmbeddingCache

# Mock Brain
class MockBrain:
    def __init__(self):
        self.memory = GeologicalMemory(size=128) # Small for test
        self.prediction_engine = PredictionEngine()
        # Ensure Embedding Cache is active
        self.prediction_engine.embedding_cache = EmbeddingCache()
        self.language_center = LanguageCenter(self)

def test_hdc_integration():
    print("🧱 Testing HDC Integration (Memory <-> LanguageCenter)...")
    
    brain = MockBrain()
    
    # 1. Setup Data
    # Concept: "Apple" (Target)
    vec_apple = np.random.randn(768)
    vec_apple /= np.linalg.norm(vec_apple)
    
    # Concept: "Banana" (Similar to Apple -> Fruit)
    vec_banana = 0.9 * vec_apple + 0.1 * np.random.randn(768)
    vec_banana /= np.linalg.norm(vec_banana)
    
    # Concept: "Car" (Different)
    vec_car = np.random.randn(768)
    vec_car /= np.linalg.norm(vec_car)
    
    # 2. Register Concepts & Compute Hashes
    print("  - Registering concepts and generating SimHashes...")
    brain.memory.concepts["Banana"] = [10, 10, time.time(), 1, 0.5, "User"]
    brain.memory.update_hash("Banana", vec_banana)
    
    brain.memory.concepts["Car"] = [50, 50, time.time(), 1, 0.0, "User"]
    brain.memory.update_hash("Car", vec_car)
    
    # 3. Test Retrieval via LanguageCenter
    print("  - Searching for 'Apple' (should find 'Banana')...")
    
    # Mock Tokenizer in LanguageCenter for POS check
    # We need to ensure 'Banana' is considered a Noun (POS N check)
    # Default Janome might recognize "Banana" (katakana or eng) as Noun.
    # "Car" as Noun.
    
    # Execute Search (looking for Noun)
    result = brain.language_center._find_best_word("名詞", vec_apple, "Original")
    
    print(f"  - Result: {result}")
    
    if result == "Banana":
        print("✅ PASS: HDC correctly identified 'Banana' as similar to 'Apple'.")
    else:
        print(f"❌ FAIL: Expected 'Banana', got '{result}'")

if __name__ == "__main__":
    test_hdc_integration()
