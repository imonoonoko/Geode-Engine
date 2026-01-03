import numpy as np
import json
import os
import time
import random
import math

import threading
from scipy.spatial import KDTree  # Phase 4: KD-Tree

class GeologicalMemory:
    def __init__(self, size=1024):
        self.size = size
        # Lock for Thread Safety (Round 5 Fix)
        self.lock = threading.Lock()
        # Windows環境でのパス問題を回避するため、実行ディレクトリ直下のフォルダを使用
        self.save_dir = "memory_data"
        os.makedirs(self.save_dir, exist_ok=True)
        
        self.terrain_path = os.path.join(self.save_dir, "brain_terrain.npy")
        self.concepts_path = os.path.join(self.save_dir, "brain_concepts.json")
        self.combat_path = os.path.join(self.save_dir, "brain_combat.json") # Phase 11.3
        self.hashes_path = os.path.join(self.save_dir, "brain_hashes.pkl")  # Phase 3: HDC Hashes
        
        # デフォルト地形（平原: 0.5）
        self.terrain = np.ones((size, size), dtype=np.float32) * 0.5
        self.concepts = {} # {"word": [x, y, t, c, v, source, hash]}
        self.combat_history = {} # Phase 11.3: {"zombie": {"wins": 0, "losses": 0}}
        self.last_active = time.time()
        
        # Phase 3: HDC Engine
        from src.cortex.simhash_engine import SimHasher
        self.simhasher = SimHasher()
        self.hashes = {} # {"word": bitarray}

        # Phase 4: Spatial Index (KD-Tree)
        self.tree = None
        self.tree_words = [] # Index mapping: index -> word
        self.tree_dirty = True # Flag to rebuild tree
        
    def load(self):
        """ 記憶の復元と『睡眠中の変化』の計算 """
        report = "New Brain Created."
        
        # Load Hashes (Phase 3)
        if os.path.exists(self.hashes_path):
            import pickle
            try:
                with open(self.hashes_path, "rb") as f:
                    self.hashes = pickle.load(f)
            except Exception as e:
                print(f"⚠️ HDC Hash Load Error: {e}")
        
        if os.path.exists(self.terrain_path) and os.path.exists(self.concepts_path):
            try:
                print("🧠 Loading Mega-Brain Terrain...")
                self.terrain = np.load(self.terrain_path)
                with open(self.concepts_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.concepts = data["concepts"]
                    self.last_active = data.get("last_active", time.time())
                
                # Phase 11.3: Combat History Load
                if os.path.exists(self.combat_path):
                    with open(self.combat_path, "r", encoding="utf-8") as f:
                        self.combat_history = json.load(f)
                
                # 睡眠シミュレーション
                report = self._process_sleep()
                
                # --- Migration: Normalize Data Format ---
                now = time.time()
                import src.dna.config as config
                
                migrated_count = 0
                for w, val in self.concepts.items():
                    # Format: [x, y, timestamp, count, valence, source]
                    # Pad to 5 elements (Valence)
                    if len(val) == 2: val.extend([now, 1, 0.0])
                    elif len(val) == 3: val.extend([1, 0.0])
                    elif len(val) == 4: val.append(0.0)
                    
                    # Pad to 6 elements (Source) - Phase 15.5
                    if len(val) == 5:
                        val.append(config.SOURCE_USER) 
                        migrated_count += 1
                        
                if migrated_count > 0:
                    print(f"🧬 Migrated {migrated_count} memories to Source-Aware Schema.") 
                    
            except Exception as e:
                print(f"Memory Load Error: {e}")
                report = "Memory Corrupted. Resetting."
        
        # Ensure 'Kaname' exists at the center (Self-Concept)
        center = self.size // 2
        # Japanese Name "カナメ"
             # Japanese Name "カナメ"
        if "カナメ" not in self.concepts:
             import src.dna.config as config
             self.concepts["カナメ"] = [center, center, time.time(), 9999, 1.0, config.SOURCE_USER]
        else:
             # Force recenter just in case
             self.concepts["カナメ"][0] = center
             self.concepts["カナメ"][1] = center
             # Ensure format for Kaname too
             while len(self.concepts["カナメ"]) < 6:
                 import src.dna.config as config
                 if len(self.concepts["カナメ"]) < 5: self.concepts["カナメ"].append(0.0)
                 else: self.concepts["カナメ"].append(config.SOURCE_USER)
             
        return report

    def save(self):
        """ 記憶の永続化 """
        # print("💾 Saving Mega-Brain sector map...") 
        
        # Thread Safety: Copy terrain under lock, then save asynchronously safe copy
        with self.lock:
            terrain_copy = self.terrain.copy()
            
        np.save(self.terrain_path, terrain_copy)
        
        # Atomic Save for Concepts
        tmp_path = self.concepts_path + ".tmp"
        for _ in range(3):
            try:
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "concepts": self.concepts,
                        "last_active": time.time()
                    }, f, ensure_ascii=False)
                if os.path.exists(self.concepts_path):
                    os.remove(self.concepts_path)
                os.rename(tmp_path, self.concepts_path)
                break
            except Exception as e:
                time.sleep(0.05)
            print(f"⚠️ Memory Save Error: {e}")
            
        # Phase 11.3: Save Combat History
        try:
            with open(self.combat_path, "w", encoding="utf-8") as f:
                json.dump(self.combat_history, f)
        except Exception as e:
            print(f"⚠️ Combat Memory Save Error: {e}")

        # Phase 3: HDC Hash Save
        try:
            import pickle
            with open(self.hashes_path, "wb") as f:
                pickle.dump(self.hashes, f)
        except Exception as e:
            print(f"⚠️ HDC Hash Save Error: {e}")

    # def export_visualization_data(self):
    #     """ [REMOVED] 3D Visualizer Export """
    #     pass

    def update_hash(self, word, vector):
        """ 
        Phase 3: HDC Hash Update.
        Convert vector -> hash and store.
        """
        if self.simhasher:
            h = self.simhasher.to_hash(vector)
            if h is not None:
                    self.hashes[word] = h
                    # print(f"Stored Hash for {word}")

    def _rebuild_index(self):
        """ Phase 4: Rebuild KD-Tree (O(N log N)) """
        if not self.concepts:
            self.tree = None
            self.tree_words = []
            return

        points = []
        words = []
        # Create list of (x, y)
        for w, val in self.concepts.items():
            points.append([val[0], val[1]]) # val=[x, y, t, c, v, source]
            words.append(w)
        
        self.tree = KDTree(points)
        self.tree_words = words
        self.tree_dirty = False
        # print(f"🌳 Spatial Index Built: {len(words)} nodes.")

    def find_spatial_neighbors(self, x, y, radius=50.0, limit=20):
        """ 
        Phase 4: Fast Spatial Search (O(log N)) 
        Returns: list of (word, distance, concept_data)
        """
        if self.tree_dirty or self.tree is None:
            self._rebuild_index()
            
        if self.tree is None: return []

        # query_ball_point returns indices
        indices = self.tree.query_ball_point([x, y], r=radius)
        
        results = []
        for idx in indices:
            w = self.tree_words[idx]
            val = self.concepts[w]
            dist = math.sqrt((val[0]-x)**2 + (val[1]-y)**2)
            results.append((w, dist, val))
            
        # Sort by distance
        results.sort(key=lambda x: x[1])
        return results[:limit]

    def find_similar_by_hash(self, target_vector, limit=10, min_sim=0.3):
        """
        Phase 3: Fast HDC Search (Hamming Distance)
        Returns: list of (word, similarity)
        """
        if not self.simhasher or not self.hashes:
            return []
            
        target_hash = self.simhasher.to_hash(target_vector)
        if target_hash is None: return []
        
        candidates = []
        
        # O(N) Scan but extremely fast bitwise ops
        # In C++ this is milliseconds for millions. In Python, overhead exists but still faster than dot product.
        # Check SimHasher for batch method? Not implemented yet.
        
        with self.lock:
            items = list(self.hashes.items())
            
        # Release lock during computation
        for word, h in items:
            sim = self.simhasher.compute_similarity(target_hash, h)
            if sim >= min_sim:
                candidates.append((word, sim))
                
        # Sort desc
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:limit]

    def _process_sleep(self):
        """ 睡眠中の地形変化（風化作用） """
        sleep_duration = time.time() - self.last_active
        # テスト用に短く設定: 1分(60秒)で1サイクル
        cycles = int(sleep_duration / 60) 
        if cycles > 0:
            erosion_rate = 0.005 * cycles
            erosion_rate = min(0.3, erosion_rate) # 最大30%戻る
            
            # 地形全体を 0.5 に近づける（風化）
            self.terrain = self.terrain * (1 - erosion_rate) + 0.5 * erosion_rate
            
            return f"Sleep Analysis: {cycles} cycles processed. Erosion Rate: {erosion_rate:.3f}"
        return "Wake up (Short nap)."

    def fossilize(self, age_limit=3600):
        """ 化石化: 古い/感情価の低い記憶をインデックスから削除する (Minimal JSON) """
        now = time.time()
        to_fossilize = []
        
        with self.lock:
            for word, val in self.concepts.items():
                # Data Layout: [x, y, timestamp, count, valence, source]
                last_active = val[2]
                valence = val[4] if len(val) >= 5 else 0.0
                source = val[5] if len(val) >= 6 else "User"
                
                # Rule: Old AND Neutral (Not Loved, Not Hated)
                if (now - last_active > age_limit) and (abs(valence) < 0.3):
                    to_fossilize.append(word)
            
            for word in to_fossilize:
                del self.concepts[word]
                
        if to_fossilize:
            print(f"🦴 Fossilized {len(to_fossilize)} memories (Removed from RAM Index).")
        return to_fossilize

    def get_coords(self, word, source=None):
        """ 言葉の座標を取得（なければ新規割り当て）+ 活性化（タイムスタンプ更新） """
        now = time.time()
        import src.dna.config as config
        if source is None: source = config.SOURCE_USER

        with self.lock:
            if word in self.concepts:
                val = self.concepts[word]
                # Migration: [x,y] -> [x,y,t] -> [...,v] -> [...,source]
                now = time.time()
                
                # Dynamic Migration on Access
                while len(val) < 6:
                    if len(val) < 5: val.append(0.0)
                    else: val.append(config.SOURCE_USER)
                
                # Check source conflict? No, we allow overwriting source? 
                # For now, keep original source unless explicitly overwritten?
                # Actually, if Agni uses a user concept, it stays User. 
                # If User uses an Agni concept, it stays Agni? 
                # Let's say: Source is "Origin". It doesn't change easily.
                
                # Normal update
                val[2] = now # Update last active
                val[3] += 1  # Increment count
                
                # Phase 21: Memory Distortion (Use Frequency Logic)
                # 頻度が低い(count < 5)と、座標がズレる（勘違いする）
                if val[3] < 10 and random.random() < 0.1:
                    self._distort_memory(val)

                self.concepts[word] = val
                self.tree_dirty = True # Mark index dirty on update
                return val[:2]
            
            # ランダム配置（1024x1024の広大な世界）
            x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
            # Init: [x, y, timestamp, count, valence, source]
            self.concepts[word] = [x, y, time.time(), 1, 0.0, source] 
            self.tree_dirty = True # Mark index dirty on new insert
            return [x, y]

    def touch(self, word):
        """ Phase 6: Ensure concept exists and update timestamp """
        self.get_coords(word)

    def reinforce(self, word, delta):
        """ Phase 6: Epigenetic Reinforcement (快/不快の刻印) """
        with self.lock:
            if word in self.concepts:
                val = self.concepts[word]
                # Ensure migration before access
                if len(val) < 6: 
                    # Helper to migrate without full get_coords logic if needed, 
                    import src.dna.config as config
                    while len(val) < 5: val.append(0.0)
                    while len(val) < 6: val.append(config.SOURCE_USER)
                
                # Apply delta (Clamped -1.0 to 1.0)
                current_valence = val[4]
                new_valence = max(-1.0, min(1.0, current_valence + delta))
                val[4] = new_valence
                
                self.concepts[word] = val
                if abs(delta) > 0.1:
                    print(f"🧬 Epigenetics: '{word}' valence shifted to {new_valence:.2f} (Delta: {delta})")

    def get_valence(self, word):
        """ 感情価の取得 (Safe) """
        with self.lock:
            if word in self.concepts:
                val = self.concepts[word]
                if len(val) >= 5:
                    return val[4]
        return 0.0

    def get_source(self, word):
        """ 記憶の発生源を取得 (User or Agni) """
        with self.lock:
            if word in self.concepts:
                val = self.concepts[word]
                if len(val) >= 6:
                    return val[5]
        return "User" # Default

    def _distort_memory(self, val):
        """ 記憶の歪み (Entropy) """
        # 微妙に座標がズレる
        drift_x = random.randint(-5, 5)
        drift_y = random.randint(-5, 5)
        val[0] = max(0, min(self.size, val[0] + drift_x))
        val[1] = max(0, min(self.size, val[1] + drift_y))
        # print(f"🌀 Memory Distorted... ({drift_x}, {drift_y})")

    def modify_terrain(self, word, emotion_value):
        """ 経験による地形操作 """
        # this uses get_coords which locks, but terrain update should also be locked
        cx, cy = self.get_coords(word) # thread-safe call
        
        with self.lock:
            # Mega-Brain なので影響範囲を広く (Radius 15)
            radius = 15
            power = emotion_value * 0.2 
            
            # 簡易的な範囲制限
            x_min = int(max(0, cx - radius))
            x_max = int(min(self.size, cx + radius + 1))
            y_min = int(max(0, cy - radius))
            y_max = int(min(self.size, cy + radius + 1))
            
            # NumPyのスライシングで高速更新
            y_grid, x_grid = np.ogrid[y_min:y_max, x_min:x_max]
            dist_sq = (x_grid - cx)**2 + (y_grid - cy)**2
            mask = dist_sq <= radius**2
            
            # 距離に応じた減衰 (中心が強く、縁は弱い)
            effect_map = power * (1 - np.sqrt(dist_sq[mask]) / (radius + 1))
            
            self.terrain[y_min:y_max, x_min:x_max][mask] += effect_map
            
            # クリップ (0.0 ~ 1.0)
            np.clip(self.terrain[y_min:y_max, x_min:x_max], 0.0, 1.0, out=self.terrain[y_min:y_max, x_min:x_max])

    def forget_forgotten_concepts(self):
        """ 
        廃品回収 (Garbage Collection): 長期間アクセスされない概念を削除
        Phase 6: 感情永続性 (Emotional Persistence) - 感情が強い記憶ほど消えにくい
        公式: effective_threshold = tau * (1 + |valence| * factor)
        """
        import src.dna.config as config  # 定数参照
        
        now = time.time()
        tau = config.MEMORY_TAU_BASE        # 基本半減期 (3600秒 = 1時間)
        factor = config.MEMORY_VALENCE_FACTOR  # 感情係数 (5)
        
        with self.lock:
            to_forget = []
            composted_valence = 0.0  # 堆肥化された感情の蓄積
            
            for word, val in self.concepts.items():
                # Migration check: if old format [x, y], skip
                if len(val) == 2: 
                    continue 

                elif len(val) >= 3:
                    last_seen = val[2]
                    valence = val[4] if len(val) >= 5 else 0.0
                    
                    # 🧬 感情永続性 (Emotional Persistence)
                    # 感情が強い (|valence| が大きい) ほど threshold が大きくなる
                    effective_threshold = tau * (1 + abs(valence) * factor)
                    
                    if now - last_seen > effective_threshold:
                        to_forget.append(word)
                        # 🍂 堆肥化: 消える記憶の感情価を蓄積 (性格への転化)
                        composted_valence += valence
            
            for w in to_forget:
                del self.concepts[w]
            
            if to_forget:
                print(f"🧹 Brain GC: Removed {len(to_forget)} concepts. Composted Valence: {composted_valence:.2f}")
                
            # DEF-06 修正: composted_valence も返す (性格への転化用)
            return to_forget, composted_valence

    def get_context(self, word):
        """ その言葉の『精神座標』情報を返す (Thread Safe) """
        with self.lock:
            if word not in self.concepts:
                return None
                
            val = self.concepts[word]
            cx, cy = val[0], val[1]
            
            altitude = self.terrain[int(cy), int(cx)] # y, x 順
            
            # 方角判定
            sector = ""
            if cy < self.size / 3: sector += "North"
            elif cy > self.size * 2 / 3: sector += "South"
            else: sector += "Central"
            
            if cx < self.size / 3: sector += "-West"
            elif cx > self.size * 2 / 3: sector += "-East"
            
            # 標高判定
            terrain_type = "Plains"
            if altitude > 0.7: terrain_type = "High Peak (Joy)"
            elif altitude > 0.55: terrain_type = "Hills"
            elif altitude < 0.3: terrain_type = "Deep Abyss (Trauma)"
            elif altitude < 0.45: terrain_type = "Valley"
            
            return f"Sector: {sector} / Type: {terrain_type} (Alt: {altitude:.2f})"

    def get_random_concept(self, refresh=False):
        """ Return a random concept safely. If refresh=True, update timestamp (Extension of life). """
        with self.lock:
            if not self.concepts: return None
            word = random.choice(list(self.concepts.keys()))
            
            if refresh:
                # Update timestamp to NOW
                if len(self.concepts[word]) == 2:
                    self.concepts[word].append(time.time())
                else:
                    self.concepts[word][2] = time.time()
                    
            return word

    def get_concepts_in_range(self, y_min, y_max, limit=10):
        """ Return random concepts within Y range (Thread Safe) """
        candidates = []
        with self.lock:
            keys = list(self.concepts.keys())
            # Optimization: Try random sampling instead of full scan if large
            attempts = 0
            while len(candidates) < limit and attempts < 20:
                attempts += 1
                if not keys: break
                w = random.choice(keys)
                cy = self.concepts[w][1]
                if y_min <= cy <= y_max:
                    candidates.append(w)
        return candidates

    def apply_gravity(self, subject, attractor, similarity):
        """ Phase 22: Semantic Gravity (Plate Tectonics) """
        with self.lock:
            if subject not in self.concepts or attractor not in self.concepts:
                return None

            s_val = self.concepts[subject]
            a_val = self.concepts[attractor]

            sx, sy = s_val[0], s_val[1]
            ax, ay = a_val[0], a_val[1]

            # Physics: Calculate vector to attractor
            dx = ax - sx
            dy = ay - sy
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < 10.0: return None # Too close (Stability zone)
            
            # Attraction Force
            # Move closer based on similarity (0.0 to 1.0)
            # Max step needs to be small to avoid chaos
            move_step = 20.0 * (similarity ** 2) # Quadratic for strong pull on high sim
            
            if move_step > dist: move_step = dist * 0.5 # Don't overshoot
            
            ratio = move_step / dist
            
            # Apply Movement
            new_x = sx + (dx * ratio)
            new_y = sy + (dy * ratio)
            
            # Boundary Check
            new_x = max(0, min(self.size-1, new_x))
            new_y = max(0, min(self.size-1, new_y))
            
            self.concepts[subject][0] = new_x
            self.concepts[subject][1] = new_y
            self.tree_dirty = True
            
            return f"🌌 G-Force: {subject} -> {attractor} (Sim: {similarity:.2f}, Moved: {move_step:.1f}px)"

    def get_spatial_gradient(self, grid_x, grid_z):
        """
        Phase 9.3: 空間勾配の計算
        現在地周辺の4方向を評価し、最も魅力的な方向を返す。
        スコア = 感情価 * 1.0 + 新規性(1/count) * 2.0
        """
        directions = {
            "North": (0, -1), # Z decrease
            "South": (0, 1),  # Z increase
            "East": (1, 0),   # X increase
            "West": (-1, 0)   # X decrease
        }
        
        scores = {}
        with self.lock:
            for dirname, (dx, dz) in directions.items():
                target_key = f"LOC:{grid_x + dx}:{grid_z + dz}"
                
                # デフォルトスコア (未知の場所は魅力的)
                score = 0.5 
                
                if target_key in self.concepts:
                    val = self.concepts[target_key]
                    # val: [x, y, timestamp, count, valence]
                    count = val[3] if len(val) >= 4 else 1
                    valence = val[4] if len(val) >= 5 else 0.0
                    
                    # 新規性ボーナス (あまり行ってない場所へ行きたい)
                    novelty = 1.0 / (count + 0.1)
                    
                    score = valence + (novelty * 2.0)
                else:
                    # 全くの未知 (Unknown)
                    # Phase 4: KD-Tree Density Check
                    # 未知の場所でも「近くに何もない」なら少しスコアを下げる (寂しい)
                    # 「近くに何かある」ならスコアを上げる (賑やか)
                    if self.tree and not self.tree_dirty:
                        # Near check (Radius 5)
                        neighbors = self.tree.query_ball_point([grid_x + dx, grid_z + dz], r=5.0)
                        if len(neighbors) > 0:
                            score = 0.8 # 未知だが賑やか
                        else:
                            score = 1.0 # 未知の荒野
                    else:
                        score = 1.0
                
                scores[dirname] = score
        
        return scores

    def update_combat_experience(self, mob_name, result):
        """
        Phase 11.3: 戦闘経験の記録 (Reinforcement Learning Signal)
        mob_name: "zombie", "skeleton" etc.
        result: "WIN" (倒した), "LOSS" (死んだ/逃げた), "DRAW"
        """
        with self.lock:
            if mob_name not in self.combat_history:
                self.combat_history[mob_name] = {"wins": 0, "losses": 0, "last_encounter": 0}
            
            record = self.combat_history[mob_name]
            record["last_encounter"] = time.time()
            
            if result == "WIN":
                record["wins"] += 1
            elif result == "LOSS":
                record["losses"] += 1
            
            self.combat_history[mob_name] = record
            print(f"⚔️ Experience Updated [{mob_name}]: W:{record['wins']} L:{record['losses']}")

    def get_combat_win_rate(self, mob_name):
        """
        Phase 11.3: 勝率の取得 (Prior Belief)
        0.0 (絶対負ける) ~ 1.0 (絶対勝てる)
        データがない場合は 0.5 (不確実)
        """
        with self.lock:
            if mob_name not in self.combat_history:
                return 0.5
            
            record = self.combat_history[mob_name]
            wins = record["wins"]
            losses = record["losses"]
            total = wins + losses
            
            if total == 0: return 0.5
            
            return wins / total


