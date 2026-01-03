import numpy as np

class SimHasher:
    """
    HDC (Hyperdimensional Computing) Engine
    Uses SimHash (Locality Sensitive Hashing) to compress 768-dim vectors 
    into 1024-bit binary fingerprints.
    """
    def __init__(self, input_dim=768, hash_bits=1024, seed=2026):
        self.input_dim = input_dim
        self.hash_bits = hash_bits
        self.seed = seed
        self.projection_matrix = self._init_projection()
        print(f"🧱 HDC Engine Online: {input_dim}f -> {hash_bits}bit")

    def _init_projection(self):
        """
        Generate a deterministic random projection matrix.
        No need to save to disk; seeds ensure reproducibility.
        """
        rng = np.random.RandomState(self.seed)
        # Random normal distribution (Gaussian)
        # Shape: (768, 1024)
        return rng.randn(self.input_dim, self.hash_bits)

    def to_hash(self, vector):
        """ 
        Convert float vector to boolean array (bits) 
        Args:
            vector (np.array): Shape (768,)
        Returns:
            np.array: Shape (1024,) dtype=bool
        """
        if vector is None: return None
        if len(vector) != self.input_dim:
            # Handle dimension mismatch if needed, or raise err
            return None
            
        # Projection: dot product
        # (N,) @ (N, M) -> (M,)
        projected = np.dot(vector, self.projection_matrix)
        
        # Binarize: > 0 is 1, <= 0 is 0
        return projected > 0

    def compute_distance(self, hash1, hash2):
        """ 
        Calculate Normalized Hamming Distance (0.0 to 1.0) 
        0.0 = Identical
        0.5 = Orthogonal (Unrelated)
        1.0 = Opposite
        """
        if hash1 is None or hash2 is None: return 1.0
        
        # XOR to find different bits
        # Numpy boolean XOR is fast
        xor_result = np.bitwise_xor(hash1, hash2)
        
        # Count set bits (True)
        # np.sum on boolean array counts True
        diff_count = np.sum(xor_result)
        
        return diff_count / self.hash_bits

    def compute_similarity(self, hash1, hash2):
        """ 1.0 - Hamming Distance """
        return 1.0 - self.compute_distance(hash1, hash2)
