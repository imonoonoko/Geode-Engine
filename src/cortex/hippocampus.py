import os
import json
import time
import threading
import numpy as np
import warnings

# Suppress warnings from torch/transformers if they exist
warnings.filterwarnings("ignore", category=FutureWarning)

class Hippocampus:
    def __init__(self, save_dir="memory_data"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
        
        self.index_path = os.path.join(self.save_dir, "hippocampus_index.json")
        self.vectors_path = os.path.join(self.save_dir, "hippocampus_vectors.npy")
        
        # Thread safety
        self.lock = threading.Lock()
        
        # In-Memory Storage
        self.metadata = [] 
        self.vectors_list = [] # List of 1D arrays
        
        # Model Status
        self.model = None
        self.is_ready = False
        
        # Async initialization to not block startup
        threading.Thread(target=self._load_model, daemon=True).start()
        
        # Load existing data
        self._load_data()

    def _load_model(self):
        """ Load Sentence-Transformer Model (Async) """
        try:
            print("🧠 Hippocampus: Loading Embedding Model (all-MiniLM-L6-v2)...")
            from sentence_transformers import SentenceTransformer
            # Use a lightweight model suitable for CPU
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.is_ready = True
            print("🧠 Hippocampus: Model Loaded. Deep Memory Active.")
        except ImportError:
            print("⚠️ Hippocampus: 'sentence-transformers' not found. Vector Memory disabled.")
            print("   Please install: pip install sentence-transformers")
        except Exception as e:
            print(f"⚠️ Hippocampus: Model Load Error: {e}")

    def _load_data(self):
        """ Load index and vectors from disk """
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.vectors_path):
                with open(self.index_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                
                vectors_np = np.load(self.vectors_path)
                # Convert back to list of 1D arrays
                self.vectors_list = [row for row in vectors_np]
                
                print(f"📖 Hippocampus: Loaded {len(self.metadata)} memories.")
            else:
                self.vectors_list = []
        except Exception as e:
            print(f"⚠️ Hippocampus: Data Load Error: {e}")
            self.vectors_list = []

    def memorize(self, text, importance=0.5, emotion="NEUTRAL"):
        """ Store a memory (Async) """
        if not self.is_ready or not text: return
        
        def _job():
            try:
                # Encode (Heavy CPU op)
                vector = self.model.encode([text])[0]
                
                # Create 1D array
                vector_np = np.array(vector, dtype=np.float32)
                
                with self.lock:
                    # Append Metadata (ONCE only - Demon Audit Fix)
                    entry = {
                        "text": text,
                        "timestamp": time.time(),
                        "importance": importance,
                        "emotion": emotion
                    }
                    self.metadata.append(entry)
                    
                    # Append Vector to LIST (O(1)) instead of vstack (O(N))
                    if self.vectors_list is None: self.vectors_list = []
                    self.vectors_list.append(vector_np)
                        
                    # Auto-save every 10 memories
                    if len(self.metadata) % 10 == 0:
                        self._save()
                        
            except Exception as e:
                print(f"⚠️ Hippocampus: Memorization Error: {e}")

        threading.Thread(target=_job, daemon=True).start()

    def recall(self, query_text, limit=3, min_score=0.3):
        """ Retrieve similar memories """
        if not self.is_ready or not self.vectors_list:
            return []
            
        try:
            # Encode Query
            query_vec = self.model.encode([query_text])[0]
            
            with self.lock:
                # Convert list to matrix for calculation (On Demand)
                # This is O(N) but only happens on recall, which is rarer than memorize
                # Optimization: Cache the matrix if read-heavy? 
                # For now, just stack.
                matrix = np.stack(self.vectors_list)
                
                # Manual Cosine Sim (Numpy)
                norm_q = np.linalg.norm(query_vec)
                norm_v = np.linalg.norm(matrix, axis=1)
                
                # Check zero division
                valid_mask = norm_v > 0
                if not np.any(valid_mask): return []
                
                dot = np.dot(matrix[valid_mask], query_vec)
                sims = dot / (norm_v[valid_mask] * norm_q)
                
                # Get indices of top scores
                indices = np.argsort(sims)[-limit:]
                
                results = []
                for idx in reversed(indices):
                    score = sims[idx]
                    real_idx = np.where(valid_mask)[0][idx] # Map back if filtered
                    
                    if score >= min_score:
                        mem = self.metadata[real_idx].copy()
                        mem["similarity"] = float(score)
                        results.append(mem)
                        
                return results
                
        except Exception as e:
            print(f"⚠️ Hippocampus: Recall Error: {e}")
            return []

    def get_similarity(self, text_a, text_b):
        """ Calculate Semantic Similarity between two texts (0.0 - 1.0) """
        if not self.is_ready: return 0.0
        try:
            # Encode
            embs = self.model.encode([text_a, text_b])
            vec_a = embs[0]
            vec_b = embs[1]
            
            # Cosine Logic
            norm_a = np.linalg.norm(vec_a)
            norm_b = np.linalg.norm(vec_b)
            if norm_a == 0 or norm_b == 0: return 0.0
            
            score = np.dot(vec_a, vec_b) / (norm_a * norm_b)
            return float(score)
        except:
            return 0.0

    def _save(self):
        """ Save to disk """
        try:
            with open(self.index_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False)
            
            if self.vectors_list:
                vectors_np = np.stack(self.vectors_list)
                np.save(self.vectors_path, vectors_np)
            else:
                # Save empty array
                np.save(self.vectors_path, np.empty((0, 384), dtype=np.float32))
                
        except Exception as e:
            print(f"⚠️ Hippocampus: Save Error: {e}")
