
import os
import json
import sys

# Setup Project Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

USER_CONFIG = os.path.join(BASE_DIR, "user_config.json")

def cleanup():
    if os.path.exists(USER_CONFIG):
        os.remove(USER_CONFIG)

def verify_persistence():
    print("🧪 Verifying Config Persistence...")
    
    # 1. Create Dummy Config
    data = {
        "DEBUG_MODE": False,
        "WINDOW_WIDTH": 9999
    }
    with open(USER_CONFIG, 'w') as f:
        json.dump(data, f)
    
    print("💾 Dummy config created.")
    
    # 2. Import Config (Should load JSON)
    # Note: We need to reload because it might be cached if run in same process
    if 'src.dna.config' in sys.modules:
        del sys.modules['src.dna.config']
        
    import src.dna.config as config
    
    # 3. Assertions
    print(f"DEBUG_MODE: {config.DEBUG_MODE}")
    print(f"WINDOW_WIDTH: {config.WINDOW_WIDTH}")
    
    assert config.DEBUG_MODE == False, "DEBUG_MODE should be False"
    assert config.WINDOW_WIDTH == 9999, "WINDOW_WIDTH should be 9999"
    
    print("✅ Config loaded successfully from JSON overlay.")
    cleanup()

if __name__ == "__main__":
    try:
        cleanup()
        verify_persistence()
    finally:
        cleanup()
