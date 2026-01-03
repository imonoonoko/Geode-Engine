import sys
import os
sys.path.append(os.getcwd())

from src.cortex.inference import PredictionEngine

def test_cache():
    print("🧪 Testing Embedding Cache...")
    engine = PredictionEngine()
    
    # First call - Cache Miss
    vec1 = engine._get_embedding("Hello World", 12)
    print(f"1st call: {engine.embedding_cache.get_stats()}")
    
    # Second call - Same text - Should be Cache Hit
    vec2 = engine._get_embedding("Hello World", 12)
    print(f"2nd call: {engine.embedding_cache.get_stats()}")
    
    # Third call - Different text - Cache Miss
    vec3 = engine._get_embedding("Goodbye Moon", 12)
    print(f"3rd call: {engine.embedding_cache.get_stats()}")
    
    # Verify cache hit worked
    if engine.embedding_cache.hits >= 1:
        print("✅ PASS: Cache Hit detected!")
        with open("cache_test_result.txt", "w", encoding="utf-8") as f:
            f.write("PASS\n")
            f.write(engine.embedding_cache.get_stats())
    else:
        print("❌ FAIL: No cache hits")
        with open("cache_test_result.txt", "w", encoding="utf-8") as f:
            f.write("FAIL\n")

if __name__ == "__main__":
    test_cache()
