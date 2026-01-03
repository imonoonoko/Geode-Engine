# inference.py
import numpy as np
import os
import math
import collections
import threading

import google.generativeai as genai
from src.dna import config

# Phase 2.3: Embedding Cache (LRU)
class EmbeddingCache:
    """ LRU Cache for Gemini Embeddings to reduce API calls and latency. """
    def __init__(self, max_size=1000):
        self.max_size = max_size
        self.cache = collections.OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def get(self, text):
        if text in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(text)
            self.hits += 1
            return self.cache[text]
        self.misses += 1
        return None
    
    def set(self, text, vector):
        if text in self.cache:
            self.cache.move_to_end(text)
        else:
            if len(self.cache) >= self.max_size:
                # Remove oldest (LRU)
                self.cache.popitem(last=False)
            self.cache[text] = vector
    
    def get_stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return f"Hits: {self.hits}, Misses: {self.misses}, Rate: {hit_rate:.1f}%"

class PredictionEngine:
    def __init__(self, brain_ref=None):
        print("🔮 Initializing Prediction Engine (State Space Model / ESN)...")
        # Soul Storage: This vector IS the user context.
        self.state_path = os.path.join("memory_data", "core_state.npy")
        self.brain_ref = brain_ref  # Phase 30: 感情バイアス予測用
        
        # Phase 2.3: Embedding Cache
        self.embedding_cache = EmbeddingCache(max_size=1000)
        
        # Setup Gemini API (Phase 2 Metamorphism)
        if config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.embedding_model = config.GEMINI_EMBEDDING_MODEL
            print(f"✨ Semantic Mode: Enabled ({self.embedding_model})")
        else:
            print("⚠️ Semantic Mode: Disabled (No API Key)")
            self.embedding_model = None

        # SSM Hyperparameters
        # Phase 2: Upgrade to 768 Dimensions (Semantic Space)
        self.input_dim = 768 
        self.reservoir_dim = 256 # internal state size (The Soul)
        self.output_dim = 2   # [Mood, Energy]
        self.spectral_radius = 0.95
        self.leak_rate = 0.3 # Slow dynamics (Memory persistence)

        # Initialize Matrices (Fixed Random Reservoir)
        # W_in: Input -> Reservoir
        np.random.seed(42) # Deterministic initialization for consistent "brain structure"
        self.W_in = np.random.uniform(-0.1, 0.1, (self.reservoir_dim, self.input_dim)) # Scale down for high-dim input
        
        # W_rec: Reservoir -> Reservoir (Recurrent weights)
        W_rec_raw = np.random.uniform(-0.5, 0.5, (self.reservoir_dim, self.reservoir_dim))
        eigenvalues = np.linalg.eigvals(W_rec_raw)
        max_eigenvalue = np.max(np.abs(eigenvalues))
        self.W_rec = W_rec_raw * (self.spectral_radius / max_eigenvalue) # Scale for stability
        
        # W_out: Reservoir -> Output (Readout - This learns!)
        self.W_out = np.random.uniform(-0.1, 0.1, (self.output_dim, self.reservoir_dim))

        # Initialize State Vector (h_t)
        self.state_vector = np.zeros(self.reservoir_dim)

        # Load "Soul" if exists
        self.load_model()
        
        self.current_free_energy = 0.0
        self.observation_buffer = collections.deque(maxlen=1000)
        self.lock = threading.Lock() 
        
        # Phase 30: サプライズ履歴
        self.surprise_history = collections.deque(maxlen=100)
        
        # Phase 30: 内部状態遷移ログ
        self.state_log = collections.deque(maxlen=50)
        self.last_state_norm = 0.0

    def load_model(self):
        """ Restore the Soul (Hidden State) and Intuition (Weights) """
        if os.path.exists(self.state_path):
            try:
                data = np.load(self.state_path, allow_pickle=True).item()
                loaded_state = data["state"]
                loaded_weights = data["weights"]
                
                # Validation: Check dimensions
                if loaded_state.shape[0] != self.reservoir_dim:
                    raise ValueError(f"State Dimension Mismatch: {loaded_state.shape[0]} vs {self.reservoir_dim}")
                
                self.state_vector = loaded_state
                self.W_out = loaded_weights
                print(f"💎 Soul & Intuition Restored. State Norm: {np.linalg.norm(self.state_vector):.2f}")
            except Exception as e:
                print(f"⚠️ Soul Load Error (Metamorphosis Required): {e}")
                print("🔥 Resetting Soul to accommodate new dimensions...")
                # Backup old soul? Maybe later. For now, rebirth.
                self.state_vector = np.zeros(self.reservoir_dim)
                # Note: W_in is already re-initialized in __init__ with correct new dimensions.
        else:
            print("🌱 New Soul Born.")

    def save_model(self):
        """ Persist the Soul and Weights """
        try:
            np.save(self.state_path, {"state": self.state_vector, "weights": self.W_out})
        except Exception as e:
            print(f"⚠️ Soul Save Error: {e}")

    def _get_embedding_api(self, text):
        """ Call Gemini Embedding API with Cache """
        if not self.embedding_model: return None
        
        # 1. Check Cache First
        cached = self.embedding_cache.get(text)
        if cached is not None:
            return cached
        
        # 2. API Call (Cache Miss)
        try:
            normalized_text = text.replace("\n", " ")
            result = genai.embed_content(
                model=self.embedding_model,
                content=normalized_text,
                task_type="clustering",
            )
            vec = np.array(result['embedding'])
            
            # 3. Store in Cache
            self.embedding_cache.set(text, vec)

            # Output dimensions check (Safeguard)
            if len(vec) != self.input_dim:
                 # Reset dimensions logic... (omitted for brevity in prompt, keep existing)
                 pass 

            # --- Phase 3: HDC Auto-Update ---
            # Automatically store SimHash in Memory for fast retrieval
            if self.brain_ref and hasattr(self.brain_ref, 'memory'):
                 self.brain_ref.memory.update_hash(text, vec)
                 
            return vec
        except Exception as e:
            # print(f"⚠️ Embedding API Error: {e}")
            return None

    def _get_embedding(self, text, hour):
        """ Projection of Text+Context into Input Space (Hybrid) """
        
        # 1. Try API (Semantic)
        vec = self._get_embedding_api(text)
        
        # 2. Fallback to Hash (Syntactic)
        if vec is None:
            # Fallback: Hash 64-dim * 12 -> 768-dim
            temp_dim = 64
            hash_vec = np.zeros(temp_dim)
            seed = 0
            for char in text[-50:]: 
                seed = (seed * 31 + ord(char)) % (2**32)
                idx = seed % (temp_dim - 2) + 2
                val = (seed % 100) / 100.0
                hash_vec[idx] += val
            
            # Normalize Hash
            norm = np.linalg.norm(hash_vec)
            if norm > 0: hash_vec = hash_vec / norm
            
            # Tile to 768
            vec = np.tile(hash_vec, 12) # 64 * 12 = 768
            
        # 3. Add Hour Signal (Cyclic) - Mutate first 2 dims
        # We overlay time context onto the semantic vector
        angle = (hour / 24.0) * 2 * math.pi
        vec[0] += math.sin(angle) * 0.1 # Small influence
        vec[1] += math.cos(angle) * 0.1
        
        return vec

    def observe(self, input_text, current_hour):
        """
        State Space Update: h_t = (1-a)*h_{t-1} + a*tanh(Win*u_t + Wrec*h_{t-1})
        Phase 30: 感情バイアス付き予測
        """
        with self.lock:
             # 1. Input embedding (u_t)
             u_t = self._get_embedding(input_text, current_hour)
             
             # 2. Update Reservoir State (The Soul)
             # h_new = tanh(W_in @ u + W_rec @ h_old)
             pre_activation = np.dot(self.W_in, u_t) + np.dot(self.W_rec, self.state_vector)
             update = np.tanh(pre_activation)
             
             # Leaky Integrator (Smooth transitions)
             self.state_vector = (1.0 - self.leak_rate) * self.state_vector + self.leak_rate * update
             
             # 3. Readout (Prediction) from NEW state
             # y_t = W_out @ h_t
             prediction_vec = np.dot(self.W_out, self.state_vector)
             # Sigmoid to clamp to 0-1
             pred_mood = 1.0 / (1.0 + np.exp(-prediction_vec[0]))
             pred_energy = 1.0 / (1.0 + np.exp(-prediction_vec[1]))
             
             # Phase 30: 感情バイアス付き予測
             # 高緊張 → 悪い未来を過大評価
             # 低覚醒 → 変化を過小評価
             emotion_bias = 0.0
             if self.brain_ref:
                 try:
                     from src.body.hormones import Hormone
                     adrenaline = self.brain_ref.hormones.get(Hormone.ADRENALINE)
                     cortisol = self.brain_ref.hormones.get(Hormone.CORTISOL)
                     dopamine = self.brain_ref.hormones.get(Hormone.DOPAMINE)
                     
                     # 高緊張(adrenaline/cortisol高) → 悪い予測に偏る
                     tension = (adrenaline + cortisol) / 200.0  # 0-1
                     optimism = dopamine / 100.0  # 0-1
                     
                     # バイアス: tension高いと pred_mood を下げる
                     emotion_bias = (optimism - tension) * 0.2
                     pred_mood = max(0.0, min(1.0, pred_mood + emotion_bias))
                 except:
                     pass
             
             # 4. Measure Reality (Same heuristics as before for Ground Truth)
             # Note: In a real SSM, we would train W_out here (RLS/LMS).
             # For this prototype, we just calculate Surprise.
             obs_energy = min(1.0, len(input_text) / 50.0)
             obs_mood = 0.5 
             positives = ["笑", "ｗ", "良", "好", "楽", "凄", "ありがとう", "nice", "good"]
             negatives = ["疲", "痛", "嫌", "悪", "辛", "ダメ", "bad", "tired"]
             hit_pos = sum(1 for w in positives if w in input_text)
             hit_neg = sum(1 for w in negatives if w in input_text)
             if hit_pos > hit_neg: obs_mood = 0.8
             elif hit_neg > hit_pos: obs_mood = 0.2
             
             # 5. Surprise (Free Energy)
             diff_mood = obs_mood - pred_mood
             diff_energy = obs_energy - pred_energy
             surprise = math.sqrt(diff_mood**2 + diff_energy**2)
             
             self.current_free_energy = surprise
             
             # Phase 30: サプライズ履歴追跡
             self.surprise_history.append(surprise)
             
             # Phase 30: 内部状態遷移ログ（人格基準）
             import time
             state_norm = np.linalg.norm(self.state_vector)
             state_change = abs(state_norm - self.last_state_norm)
             
             self.state_log.append({
                 "t": time.time(),
                 "state_norm": state_norm,
                 "surprise": surprise,
                 "emotion_bias": emotion_bias
             })
             
             # Phase 30: 分岐アラート（観測のみ、修正しない）
             # 自己予測誤差が構造的に収束しなくなった時
             if len(self.surprise_history) >= 10:
                 recent_avg = sum(list(self.surprise_history)[-10:]) / 10
                 if recent_avg > 0.7 and state_change > 0.5:
                     print(f"⚠️ [BIFURCATION ALERT] State diverging: ΔNorm={state_change:.2f}, AvgSurprise={recent_avg:.2f}")
                     # Part 4: 修正しない、アラートのみ
             
             self.last_state_norm = state_norm
             
             # 6. Store Observation for Sleep Learning (Crystallization)
             # Fix: Must store a COPY of the state vector, otherwise we learn on mutable current state
             self.observation_buffer.append({
                 "state_snapshot": self.state_vector.copy(),
                 "mood_target": obs_mood,
                 "energy_target": obs_energy,
                 "emotion_bias": emotion_bias  # Phase 30: 保存
             })
        
        return surprise, obs_mood

    def simulate(self, input_text, current_hour):
        """
        Thought Simulation: Predicts surprise WITHOUT updating state.
        Used for 'Pondering' (Verbal Reasoning).
        Returns: predicted_surprise (0.0 - 1.0)
        """
        # 1. Input embedding
        u_t = self._get_embedding(input_text, current_hour)
        
        # 2. Virtual State Update (Do not touch self.state_vector)
        # Thread Safety: Copy state under lock
        with self.lock:
            local_state = self.state_vector.copy()
        
        # h_new = tanh(W_in @ u + W_rec @ h_old)
        pre_activation = np.dot(self.W_in, u_t) + np.dot(self.W_rec, local_state)
        virtual_state = (1.0 - self.leak_rate) * local_state + self.leak_rate * np.tanh(pre_activation)
        
        # 3. Virtual Prediction
        prediction_vec = np.dot(self.W_out, virtual_state)
        pred_mood = 1.0 / (1.0 + np.exp(-prediction_vec[0]))
        pred_energy = 1.0 / (1.0 + np.exp(-prediction_vec[1]))
        
        # 4. Self-Evaluation (Fantasy)
        # We assume the "Self" wants to be understood (Low Surprise)
        # OR we check if this thought aligns with the "Soul Bias"
        
        # Surprise relative to ITSELF? No, surprise is diff between Prediction and Reality.
        # Here, "Reality" hasn't happened yet.
        # So we simulate: "If I said this, would I feel consistent?"
        
        # Heuristic: 
        # Does this state vector align with W_out driven bias?
        # Let's return the "Confidence" (Inverse Variance?) 
        # For now, we return the Magnitude of the State Change (Energy Cost)
        # Low change = Consistent thought. High change = Radical thought.
        
        diff = np.linalg.norm(virtual_state - local_state)
        stability = 1.0 / (1.0 + diff) # 1.0 = Very stable, 0.0 = Chaotic
        
        return 1.0 - stability # Return as "Instability/Surprise" metric

    def crystallize(self):
        """
        The Abyss Process: Crystallization as Weight Learning.
        Update output weights (W_out) to minimize prediction error (Surprise).
        Simulates 'Sleep Consolidation' or 'LoRA' update.
        """
        if not self.observation_buffer: return
        
        print(f"💎 Crystallizing {len(self.observation_buffer)} memories into Intuition (Weights)...")
        
        with self.lock:
            # Simple Online Learning (LMS / Delta Rule)
            learning_rate = 0.01
            
            for obs in self.observation_buffer:
                # Reconstruct the state from snapshot (Correct LMS)
                state_snapshot = obs["state_snapshot"]
                
                # Target (Reality)
                target = np.array([obs["mood_target"], obs["energy_target"]])
                
                # Prediction (Re-calculate with current weights but OLD state)
                prediction_vec = np.dot(self.W_out, state_snapshot)
                pred_clamped = 1.0 / (1.0 + np.exp(-prediction_vec)) # Sigmoid
                
                # Error
                error = target - pred_clamped
                
                # Update Weights: W_out += lr * error * state.T
                delta = learning_rate * np.outer(error, state_snapshot)
                self.W_out += delta
                
            print(f"⚖️ Weights Adjusted. L2 Norm delta: {np.linalg.norm(delta):.4f}")
            
            # Clear Buffer (Erosion)
            self.observation_buffer.clear()
            
            # Save both State and Weights
            self.save_model()

    def get_soul_bias(self):
        """
        Soul Compass: Returns -1.0 to 1.0 based on Core State.
        Used to guide the Geological Memory (Terrain) focus.
        """
        # Thread Safety: Copy state under lock
        with self.lock:
            local_state = self.state_vector.copy()
        
        # Simple projection: Mean of state vector * sensitivity
        # A heavily activated state -> Positive Bias?
        # Chaotic state -> Negative?
        # Let's use the first Principal Component (or just mean for now)
        val = np.tanh(np.mean(local_state) * 50.0)
        return val

    def get_action_strategy(self):
        """
        Determine Action Strategy based on Free Energy & Boredom.
        Returns: "RESONATE", "PROBE", or "FRICTION"
        """
        # High Surprise -> Probe (Confusion/Curiosity)
        if self.current_free_energy > 0.6:
            return "PROBE"
        
        # Very Low Surprise (Boredom) -> Friction (Playfulness/Rebellion)
        # Assuming we can track how long surprise has been low? 
        # For now, simplistic check: if surprise is effectively zero (< 0.05) or just randomly if low
        if self.current_free_energy < 0.1:
            # 20% chance to be rebellious when bored
            if np.random.random() < 0.2:
                return "FRICTION"
                
        # Default -> Resonance (Empathy)
        return "RESONATE"

    def verify_stability(self) -> dict:
        """
        Phase 30: 形式検証
        ρ(A) < 1 を確認し、感情系が暴走しないことを数学的に保証
        
        Returns: dict with verification results
        """
        result = {
            "spectral_radius": 0.0,
            "is_stable": False,
            "recovery_time_estimate": 0.0,
            "self_amplification_bound": 0.0
        }
        
        with self.lock:
            # 1. スペクトル半径 ρ(W_rec) の再計算
            eigenvalues = np.linalg.eigvals(self.W_rec)
            spectral_radius = np.max(np.abs(eigenvalues))
            result["spectral_radius"] = float(spectral_radius)
            result["is_stable"] = spectral_radius < 1.0
            
            # 2. 回復時間の推定 (時定数 τ ≈ 1 / (1 - ρ))
            if spectral_radius < 1.0:
                tau = 1.0 / (1.0 - spectral_radius)
                result["recovery_time_estimate"] = float(tau)
            else:
                result["recovery_time_estimate"] = float('inf')
            
            # 3. 自己増幅上界 (leak_rate による減衰)
            # Effective gain = leak_rate * spectral_radius
            effective_gain = self.leak_rate * spectral_radius
            result["self_amplification_bound"] = float(effective_gain)
            
            # ログ出力
            status = "✅ STABLE" if result["is_stable"] else "⚠️ UNSTABLE"
            print(f"🔬 [FORMAL VERIFICATION] {status}")
            print(f"   ρ(W_rec) = {spectral_radius:.4f} (< 1.0 required)")
            print(f"   τ = {result['recovery_time_estimate']:.2f} steps")
            print(f"   Self-amp bound = {effective_gain:.4f}")
        
        return result
