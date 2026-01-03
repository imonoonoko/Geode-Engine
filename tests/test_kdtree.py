import sys
import os
import time
import random

# Add project root to path
sys.path.insert(0, os.path.abspath("."))

from src.cortex.memory import GeologicalMemory

def test_kdtree_performance():
    print("--- 🌳 KD-Tree Spatial Index Test ---")
    
    # 1. Setup Brain with 1000 concepts
    memory = GeologicalMemory(size=1024)
    
    print("Populating 1000 random concepts...")
    for i in range(1000):
        word = f"concept_{i}"
        memory.get_coords(word) # Creates random coords
    
    print(f"Memory Size: {len(memory.concepts)}")
    
    # 2. Force Rebuild Index
    start_time = time.time()
    memory._rebuild_index()
    build_time = time.time() - start_time
    print(f"Index Build Time: {build_time*1000:.2f} ms")
    
    # 3. Query Spatial Neighborhood (Center)
    center_x = 512
    center_y = 512
    radius = 100.0
    
    start_time = time.time()
    neighbors = memory.find_spatial_neighbors(center_x, center_y, radius=radius, limit=100)
    query_time = time.time() - start_time
    print(f"Query Time (r={radius}): {query_time*1000:.2f} ms")
    print(f"Found Neighbors: {len(neighbors)}")
    
    # 4. Correctness Check
    print("\nVerifying Distances...")
    error_count = 0
    for w, dist, val in neighbors:
        actual_dist = ((val[0]-center_x)**2 + (val[1]-center_y)**2)**0.5
        if abs(dist - actual_dist) > 0.1:
            print(f"❌ Mismatch: {w} TreeDist={dist:.2f}, AutoDist={actual_dist:.2f}")
            error_count += 1
        else:
            if dist > radius:
                 print(f"❌ Out of bounds: {w} Dist={dist:.2f} > Radius={radius}")
                 error_count += 1
            # else:
            #     print(f"✅ {w}: {dist:.2f}")
    
    if error_count == 0:
        print("✅ Correctness Verified: All results within radius.")
    else:
        print(f"❌ Failed: {error_count} errors.")
        
    
    # 5. Density Check (Gradient)
    print("\nGradient Density Check...")
    # Inject a cluster at (100, 100)
    for i in range(10):
        memory.concepts[f"cluster_{i}"] = [100 + i, 100 + i, 0, 1, 0.0]
    
    memory.tree_dirty = True
    scores = memory.get_spatial_gradient(100, 100)
    print(f"Scores near cluster: {scores}")
    
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_kdtree_performance()
