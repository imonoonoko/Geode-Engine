
import sys
import os
import time

# Setup Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from src.brain_stem.brain import KanameBrain

def check_speech():
    print("🗣️ Checking Chimera Language Engine output...")
    
    brain = KanameBrain()
    # brain.language_center.load_memory() # Not needed / Not existing
    
    words = ["空", "海", "楽しい", "未来", "家"]
    
    print("\n--- Generating 5 Sentences ---")
    for i, word in enumerate(words):
        # Get Vector from Prediction Engine
        if hasattr(brain, 'prediction_engine'):
             vec = brain.prediction_engine._get_embedding(word, 0) # 0 context
        else:
             print("⚠️ No Prediction Engine")
             vec = None
             
        if vec is not None:
            sentence = brain.language_center.speak(vec, valence_state=0.5, trigger_source="IMPULSE")
            print(f"[{word}] {sentence}")
        else:
            print(f"[{word}] (No Vector)")
        
    # Loop 2 removed (invalid kwargs)

if __name__ == "__main__":
    check_speech()
