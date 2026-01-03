import sys
import os

# Set search path
sys.path.insert(0, os.path.abspath("."))

from src.dna import config
from src.senses.mentor import AgniAccelerator

# Mock Brain class for Agni init
class MockBrain:
    def __init__(self):
        self.memory = None

print("--- Agni Connection Test ---")
print(f"Config loaded.")
print(f"API Key present: {bool(config.GEMINI_API_KEY)}")
if config.GEMINI_API_KEY:
    print(f"API Key preview: {config.GEMINI_API_KEY[:4]}...{config.GEMINI_API_KEY[-4:]}")

print("\nInitializing Agni...")
try:
    brain = MockBrain()
    agni = AgniAccelerator(brain)
    print(f"\nAgni Connected: {agni.connected}")
    
    if agni.connected:
        print("Attempting generation...")
        res = agni.generate_experience("Test")
        print(f"Generation Result: {res}")
    else:
        print("Agni is in Mock Mode.")
        
except Exception as e:
    print(f"FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
