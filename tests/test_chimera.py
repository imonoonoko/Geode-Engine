import sys
import os
import numpy as np
import threading
from unittest.mock import MagicMock

sys.path.append(os.getcwd())

from src.cortex.language_center import LanguageCenter

def test_chimera():
    print("🦁 Testing Chimera Language Engine...")
    
    # 1. Mock Brain & Components
    brain = MagicMock()
    
    # Mock Memory
    brain.memory = MagicMock()
    brain.memory.lock = threading.Lock()
    # Vocabulary: "Apple"(N), "Eat"(V), "Delicious"(Adj), "Sky"(N), "Blue"(Adj)
    brain.memory.concepts = {
        "リンゴ": {}, "食べる": {}, "美味しい": {},
        "空": {}, "青い": {}, "飛ぶ": {}
    }
    
    # Mock Sedimentary Cortex (Past Memories)
    brain.sedimentary_cortex = MagicMock()
    brain.sedimentary_cortex.lock = threading.Lock()
    brain.sedimentary_cortex.all_fragments = [
        {"text": "リンゴは美味しい"}, # Shell: [N]は[Adj]
        {"text": "空を飛ぶ"},       # Shell: [N]を[V]
    ]
    
    # Mock Prediction Engine & Embedding Cache
    brain.prediction_engine = MagicMock()
    cache = MagicMock()
    
    # Mock Vectors (Simple 2D for test)
    # Target Thought: "Sky is Blue" ([0, 1])
    # Words:
    # "リンゴ" [1, 0]
    # "美味しい" [1, 0]
    # "空" [0, 1]
    # "青い" [0, 1]
    # "飛ぶ" [0, 1]
    
    embeddings = {
        "リンゴ": np.array([1.0, 0.0]),
        "美味しい": np.array([1.0, 0.0]),
        "食べる": np.array([1.0, 0.0]),
        "空": np.array([0.0, 1.0]),
        "青い": np.array([0.0, 1.0]),
        "飛ぶ": np.array([0.0, 1.0]),
    }
    
    def get_embedding(text):
        return embeddings.get(text, None)
        
    cache.get.side_effect = get_embedding
    brain.prediction_engine.embedding_cache = cache
    
    # 2. Initialize Language Center
    broca = LanguageCenter(brain)
    
    # 3. Test Morphological Surgery (Extract Shell)
    print("\n[Test 1] Shell Extraction")
    text = "リンゴは美味しい"
    shell = broca._extract_shell(text)
    print(f"Original: {text}")
    print(f"Shell: {shell}")
    
    # Expect: [{'type':'slot', 'pos':'名詞',...}, {'type':'fixed', 'text':'は'}, {'type':'slot', 'pos':'形容詞',...}]
    
    # 4. Test Core Injection (Chimera Synthesis)
    print("\n[Test 2] Chimera Synthesis (Injecting 'Sky/Blue' mood)")
    target_vector = np.array([0.0, 1.0]) # Represents Sky/Blue
    
    # We want "リンゴ" -> "空", "美味しい" -> "青い"
    # Shell: [N]は[Adj] -> "空"は"青い"
    
    # Note: _find_best_word does similarity check.
    # "空" dot target(Sky) = 1.0 -> Match!
    
    generated = broca._inject_core(shell, target_vector)
    print(f"Target Vector: Sky/Blue {target_vector}")
    print(f"Generated: {generated}")
    
    if "空" in generated and "青い" in generated:
        print("✅ PASS: Chimera synthesized correctly!")
    else:
        print("❌ FAIL: Injection failed.")
        
    # 5. Test Full Speak (End-to-End)
    print("\n[Test 3] Speak Method")
    # Force _retrieve_shell to return "リンゴは美味しい" to be deterministic
    broca._retrieve_shell = MagicMock(return_value="リンゴは美味しい")
    
    output = broca.speak(target_vector)
    print(f"Output: {output}")

if __name__ == "__main__":
    test_chimera()
