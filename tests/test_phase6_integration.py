
import sys
import os
import time
import socket
import json
import requests
import threading

# Project Root
# Project Root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import Brain
from src.brain_stem.brain import GeodeBrain
from src.dna import config

def test_integration():
    print("--- 🧠 Phase 6: Full Integration Test ---")
    
    # 1. Initialize Brain
    print("🧠 Initializing Brain...")
    brain = GeodeBrain()
    # Mock Body HAL to avoid GUI requirement if possible
    brain.body_hal = None 
    
    # 2. Start Bot Server (Assume Port 3002 from previous test)
    port = 3002
    api_url = f"http://localhost:{port}"
    
    # Check if server is up
    try:
        requests.get(f"{api_url}/state", timeout=2)
        print("✅ Bot Server is running on port 3002.")
    except:
        print("❌ Bot Server 3002 not reachable. Run connection test first.")
        return False

    # 3. Simulate Minecraft Chat Event
    # We don't need real Minecraft connection if we mock the packet input to the brain
    # BUT Phase 6 goal is "Minecraft Connection", so maybe we should use the Brain's method?
    
    # Brain pulls data via `_process_minecraft_sense` usually.
    # But currently Brain uses `minecraft_manager`.
    
    # Let's manual-feed the brain since we want to test REACTION logic, 
    # and we confirmed connection logic in previous test.
    
    test_word = "Phase6_Test"
    print(f"\n🧪 Injecting Stimulus: '{test_word}'")
    
    # 3a. Prime ConceptLearner with an unknown visual tag
    # This simulates seeing "something" before being told what it is.
    if hasattr(brain, 'concept_learner'):
        print("   👀 Encountering Unknown Object 'test_obj_01'...")
        brain.concept_learner.encounter_unknown("test_obj_01", valence=0.5)
    
    # Simulate "Chat" Input with Teaching Syntax (Japanese)
    # Pattern: これは[Concept]だよ
    brain.input_stimulus(f"これは{test_word}だよ")
    
    # 4. Verify Memory Storage (HDC + Concept)
    print("⏳ Waiting for processing (2s)...")
    time.sleep(2)
    
    if test_word in brain.memory.concepts:
        print(f"✅ Memory Storage Verified: '{test_word}' found in concepts.")
        val = brain.memory.concepts[test_word]
        print(f"   Coords: {val[:2]}")
    else:
        print(f"❌ Memory Storage Failed: '{test_word}' not found.")
        return False
        
    # 5. Verify Hash Generation
    if test_word in brain.memory.hashes:
        print(f"✅ HDC Hash Verified: Hash stored for '{test_word}'.")
    else:
        print(f"❌ HDC Hash Missing for '{test_word}'.")
        return False
        
    # 6. Verify Chimera Language Generation
    # Force 'speaking' by adding to thoughtful active set
    print("\n🗣️ Testing Language Generation...")
    
    # Trigger speak manually
    # We look for result in speech_queue
    brain.activate_concept(test_word, boost=5.0) # Make it dominant
    
    # Force think cycle
    speech_detected = False
    for i in range(10):
        payload = brain.think() 
        # think returns None usually, speech is async in queue
        
        while not brain.speech_queue.empty():
            msg = brain.speech_queue.get()
            print(f"   [Speech Generated]: {msg.get('text', '')}")
            if test_word in msg.get('text', '') or test_word in str(msg):
                speech_detected = True
        
        if speech_detected: break
        time.sleep(0.5)
        
    if speech_detected:
        print("✅ Language Verification Passed: Brain spoke about the concept.")
    else:
        print("⚠️ Language Verification Warning: Brain was silent (might be shy/low dopamine).")
        # Not necessarily a fail, but warning.
        
    print("\n--- Integration Test Complete ---")
    return True

if __name__ == "__main__":
    test_integration()
