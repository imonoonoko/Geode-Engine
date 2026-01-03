import sys
import os
import numpy as np
from unittest.mock import MagicMock

sys.path.append(os.getcwd())

from src.cortex.simhash_engine import SimHasher

def test_hdc_verification():
    print("🧱 Testing HDC SimHash Engine...")
    
    # Initialize Engine
    hasher = SimHasher(input_dim=768, hash_bits=1024)
    
    # Mock Embeddings (768-dim)
    # Ideally we'd use real embeddings but we don't want to burn API.
    # We will construct synthetic vectors with known cosine similarities.
    
    # Vector A: Baseline
    vec_a = np.random.randn(768)
    vec_a = vec_a / np.linalg.norm(vec_a)
    
    # Vector B: Very Similar to A (Cosine ~0.95)
    # In high dim, simple addition of noise effectively orthogonalizes.
    # Use interpolation: 0.9*A + 0.1*Random
    noise = np.random.randn(768)
    noise = noise / np.linalg.norm(noise)
    vec_b = 0.95 * vec_a + 0.05 * noise
    vec_b = vec_b / np.linalg.norm(vec_b)
    
    # Vector C: Orthogonal to A (Random) -> Cosine ~0.0
    vec_c = np.random.randn(768)
    vec_c = vec_c / np.linalg.norm(vec_c)
    
    # Vector D: Opposite to A (-A) -> Cosine -1.0
    vec_d = -vec_a
    
    # Compute Hashes
    hash_a = hasher.to_hash(vec_a)
    hash_b = hasher.to_hash(vec_b)
    hash_c = hasher.to_hash(vec_c)
    hash_d = hasher.to_hash(vec_d)
    
    # Compute Distances
    dist_ab = hasher.compute_distance(hash_a, hash_b) # Should be low
    dist_ac = hasher.compute_distance(hash_a, hash_c) # Should be ~0.5
    dist_ad = hasher.compute_distance(hash_a, hash_d) # Should be ~1.0
    
    print(f"\n[Validation Data]")
    print(f"Dist(A, B) [Similar]: {dist_ab:.4f} (Expected < 0.2)")
    print(f"Dist(A, C) [Random]:  {dist_ac:.4f} (Expected ~ 0.5)")
    print(f"Dist(A, D) [Opposite]:{dist_ad:.4f} (Expected ~ 1.0)")
    
    # Assertions
    if dist_ab < 0.2 and 0.4 < dist_ac < 0.6 and dist_ad > 0.9:
        print("\n✅ PASS: HDC SimHash preserves cosine similarity topology.")
    else:
        print("\n❌ FAIL: SimHash property violation.")

if __name__ == "__main__":
    test_hdc_verification()
