import sys
import os
import shutil
import math

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from memory import GeologicalMemory

TEMP_DIR = "test_gravity_data"

def test_gravity():
    print("🧪 Gravity Physics Test")
    
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)

    # 1. Initialize Memory
    mem = GeologicalMemory(size=100)
    mem.save_dir = TEMP_DIR
    
    # 2. Setup Concepts
    # Subject: (10, 10)
    # Target: (50, 50)
    # Distance: sqrt(40^2 + 40^2) = 56.56
    mem.concepts["Love"] = [10.0, 10.0, 0, 0, 0.5]
    mem.concepts["Like"] = [50.0, 50.0, 0, 0, 0.5] 
    
    print(f"📍 Start: Love={mem.concepts['Love'][:2]}, Like={mem.concepts['Like'][:2]}")
    
    # 3. Apply Strong Gravity (Sim = 0.9)
    # Formula: step = 20 * (0.9^2) = 16.2 px
    sim = 0.9
    res = mem.apply_gravity("Love", "Like", sim)
    print(f"🚀 Action: {res}")
    
    # 4. Verify
    new_x, new_y = mem.concepts["Love"][:2]
    
    # Expected: 
    # Ratio = 16.2 / 56.56 = 0.286
    # dx = 40 * 0.286 = 11.45
    # New X = 10 + 11.45 = 21.45
    
    print(f"📍 End:   Love=[{new_x:.2f}, {new_y:.2f}]")
    
    if 20.0 < new_x < 23.0:
        print("✅ Test Passed: Physics is accurate.")
    else:
        print("❌ Test Failed: Movement out of expected range.")

    # Cleanup
    try:
        shutil.rmtree(TEMP_DIR)
    except: pass

if __name__ == "__main__":
    test_gravity()
