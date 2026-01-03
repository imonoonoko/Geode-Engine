import random
import json
import os
import math
import time
import threading
import sqlite3  # Phase 6: SQLite移行
from datetime import datetime
from src.cortex.memory import GeologicalMemory
import src.dna.config as config
from src.body.maya_synapse import SynapticStomach

class SedimentaryCortex:
    def __init__(self, memory_system, max_sediments=config.SEDIMENT_MAX):
        self.memory = memory_system
        self.max_sediments = max_sediments
        self.grid_size = 50 
        self.lock = threading.Lock()
        
        # 空間インデックス (メモリキャッシュ用)
        self.spatial_index = {} 
        self.all_fragments = []  # 後方互換性のため維持
        
        # New: Synaptic Stomach (Phase 13)
        self.stomach = SynapticStomach(self.memory.save_dir)
        
        # Phase 6: SQLiteデータベース
        self.db_path = os.path.join(self.memory.save_dir, "brain_sediments.db")
        self.json_path = os.path.join(self.memory.save_dir, "brain_sediments.json")  # 移行元
        self._init_db()
        self.load()

    def _init_db(self):
        """ Phase 6: SQLiteテーブルの初期化 """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sediments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                timestamp REAL NOT NULL
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_xy ON sediments (x, y)')
        conn.commit()
        conn.close()
        print("🗄️ SQLite DB Initialized.")

    def load(self):
        """ 記憶の復元 (SQLite + JSON移行) """
        # 1. 既存JSONからの移行 (初回のみ)
        if os.path.exists(self.json_path):
            self._migrate_from_json()
        
        # 2. SQLiteから読み込み (メモリキャッシュ構築)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT text, x, y, timestamp FROM sediments')
            rows = cursor.fetchall()
            conn.close()
            
            self.all_fragments = []
            self.spatial_index = {}
            for row in rows:
                frag = {'text': row[0], 'x': row[1], 'y': row[2], 'timestamp': row[3]}
                self.all_fragments.append(frag)
                key = self._get_grid_key(frag['x'], frag['y'])
                if key not in self.spatial_index: self.spatial_index[key] = []
                self.spatial_index[key].append(frag)
            
            print(f"📚 {len(self.all_fragments)} words excavated from SQLite.")
        except Exception as e:
            print(f"Sediment Load Error: {e}")

    def _migrate_from_json(self):
        """ Phase 6: JSONからSQLiteへのデータ移行 """
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for frag in old_data:
                cursor.execute(
                    'INSERT INTO sediments (text, x, y, timestamp) VALUES (?, ?, ?, ?)',
                    (frag.get('text', ''), frag.get('x', 0), frag.get('y', 0), frag.get('timestamp', time.time()))
                )
            
            conn.commit()
            conn.close()
            
            # 移行完了後、JSONをバックアップして削除
            backup_path = self.json_path + ".migrated"
            os.rename(self.json_path, backup_path)
            print(f"✅ Migrated {len(old_data)} records from JSON to SQLite.")
        except Exception as e:
            print(f"⚠️ JSON Migration Error: {e}")

    def _get_grid_key(self, x, y):
        return (int(x // self.grid_size), int(y // self.grid_size))

    def save(self, async_mode=True):
        """ 
        Phase 6: SQLiteは即時コミットのため、このメソッドは主にメモリキャッシュの同期用
        """
        if not async_mode:
            print("💾 Cortex (SQLite) is always synced.")

    def learn(self, text, trigger_word, surprise=0.0):
        """ 言葉を大地に埋める (Active Inference Plasticity) """
        # A. 胃袋への情報提供 (Synaptic Networking)
        self.stomach.eat(text)
        
        # B. 大地への埋め込み (Geo-Embedding)
        cx, cy = self.memory.get_coords(trigger_word)
        
        # 簡易分かち書き
        fragments = self._shatter_text(text)
        
        # Plasticity Modulation:
        # High surprise = High variance (Scatter/Trauma)
        # Low surprise = Low variance (Focus/Routine)
        base_spread = 15
        if surprise > 0.6: base_spread = 40 # Excited/Confused
        if surprise > 0.8: base_spread = 80 # Panic/Chaos
        
        for frag in fragments:
            # 中心からばらけさせる
            off_x = int(random.gauss(0, base_spread))
            off_y = int(random.gauss(0, base_spread))
            x, y = max(0, min(self.memory.size, cx + off_x)), max(0, min(self.memory.size, cy + off_y))
            
            new_sediment = {
                "text": frag,
                "x": x,
                "y": y,
                "timestamp": time.time()
            }
            
            # Phase 6: SQLite INSERT
            self._insert_sediment(new_sediment)

        # Phase 2.2: Metamorphic Pressure (80% Trigger)
        if len(self.all_fragments) > self.max_sediments * 0.8:
            # 80%超えたら圧縮を試みる (スロットル: 毎回やると重いので、ランダムか時間制御が必要)
            # ここではシンプルに毎回チェックするが、compress_memory内でsample_size制限しているのでOK
            if len(self.all_fragments) % 50 == 0: # 少し間引く
                print(f"🧱 Metamorphic Pressure rising ({len(self.all_fragments)} sediments). Attempting compression...")
                self.compress_memory()

        # 風化（容量オーバーしたら古いのを消す）
        if len(self.all_fragments) > self.max_sediments:
            self._erode()

    def deposit(self, memory_entry):
        """ 構造化された記憶（視覚イベント等）を堆積させる (Gemini Proposal) """
        # コンテンツから座標を決定
        content = memory_entry.get("content", "")
        # "saw_object: cat" -> trigger="cat"
        trigger = content.split(":")[-1].strip() if ":" in content else "unknown"
        
        cx, cy = self.memory.get_coords(trigger)
        
        # 配列範囲
        spread = 20
        off_x = int(random.gauss(0, spread))
        off_y = int(random.gauss(0, spread))
        x, y = max(0, min(self.memory.size, cx + off_x)), max(0, min(self.memory.size, cy + off_y))
        
        # 必須フィールドの補完 (for compatibility with excavate/speak)
        # textフィールドがないとspeakで落ちるため、contentをtextとして扱う
        if "text" not in memory_entry:
            memory_entry["text"] = content
        
        memory_entry["x"] = x
        memory_entry["y"] = y
        if "timestamp" not in memory_entry:
            memory_entry["timestamp"] = time.time()
            
        # Phase 6: SQLite INSERT
        self._insert_sediment(memory_entry)
            
        # 風化
        if len(self.all_fragments) > self.max_sediments:
            self._erode()

    def _insert_sediment(self, sediment):
        """ Phase 6: SQLiteへの即時INSERT + メモリキャッシュ更新 """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO sediments (text, x, y, timestamp) VALUES (?, ?, ?, ?)',
                (sediment.get('text', ''), sediment.get('x', 0), sediment.get('y', 0), sediment.get('timestamp', time.time()))
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ SQLite Insert Error: {e}")
        
        # メモリキャッシュも更新
        with self.lock:
            self.all_fragments.append(sediment)
            g_key = self._get_grid_key(sediment['x'], sediment['y'])
            if g_key not in self.spatial_index:
                self.spatial_index[g_key] = []
            self.spatial_index[g_key].append(sediment)

    def speak(self, trigger_word, strategy="RESONATE"):
        """ 発掘作業 """
        if trigger_word not in self.memory.concepts:
            return None # 知らない言葉は黙る

        cx, cy = self.memory.get_coords(trigger_word)
        
        # === Phase 28: Goal-Directed Recall (Joy Seeking Pivot) ===
        # If we need joy, but the current topic is sad, look for a happy neighbor.
        if strategy == "JOY_SEEKING":
             current_valence = self.memory.get_valence(trigger_word)
             if current_valence < 0.1: # Neutral or Sad
                 # 近くにある「楽しい記憶」を探す (Pivot)
                 # Scan nearby area for concept with high valence
                 print(f"🔦 Seeking JOY... '{trigger_word}' is too sad ({current_valence:.2f}). Scanning neighbors...")
                 best_concept = None
                 best_val = -1.0
                 
                 # Randomly sample 20 neighbors to find a better topic
                 # (Full scan is too heavy, random sampling is sufficient)
                 # Use existing memory reference
                 with self.memory.lock:
                     # Copy keys to avoid iteration error if mutated elsewhere
                     keys = list(self.memory.concepts.keys())
                 
                 random.shuffle(keys)
                 
                 for w in keys[:50]: # Check 50 random concepts (Global Search for now)
                     c_val = self.memory.get_valence(w)
                     if c_val > 0.3:
                         best_concept = w
                         best_val = c_val
                         break # Found one!
                 
                 if best_concept:
                     print(f"✨ Pivot: Switching topic from '{trigger_word}' to '{best_concept}' (Val: {best_val:.2f})")
                     trigger_word = best_concept
                     cx, cy = self.memory.get_coords(trigger_word)
                     # Update active thoughts in Brain? No, implicitly updating focus here.

        search_radius = 40 # 探索半径
        
        # 探索範囲のグリッドだけをチェック（高速化）
        start_gx = int((cx - search_radius) // self.grid_size)
        end_gx = int((cx + search_radius) // self.grid_size)
        start_gy = int((cy - search_radius) // self.grid_size)
        end_gy = int((cy + search_radius) // self.grid_size)
        
        candidates = []
        
        with self.lock:
            for gx in range(start_gx, end_gx + 1):
                for gy in range(start_gy, end_gy + 1):
                    key = (gx, gy)
                    if key in self.spatial_index:
                        for frag in self.spatial_index[key]:
                            # 精密な距離チェック
                            dist = math.sqrt((frag['x'] - cx)**2 + (frag['y'] - cy)**2)
                            if dist <= search_radius:
                                # 距離が近いほど採用確率アップ
                                weight = 1.0 - (dist / search_radius)
                                if random.random() < weight + 0.2: # 0.2はベース確率
                                    candidates.append(frag)

        if not candidates:
            # Phase 21: De-scripting (Silence)
            # 知らない言葉は無理に喋らない。本能(Hot/Cold)はResonanceの音だけで表現する。
            return None

        # Filter by Strategy (Active Inference / Homeostasis)
        filtered_candidates = []
        if strategy == "JOY_SEEKING":
             # 楽しい記憶 (Valence > 0.2) を優先
             # 候補の中からポジティブなものだけ抽出
             # しかし候補が位置ベースなので、偶然そこにポジティブなものがなければ見つからない。
             # -> 本当は「全検索」すべきだが、コストが高いので「候補内のフィルタリング」に留める。
             # もし候補内に良いものがなければ、範囲を広げるか？ -> 今は簡易実装。
             
             # Check Memory Valence for each candidate's concept (need triggers)
             # Sediments are fragments. We need to check the concept they belong to? 
             # No, fragments are raw text. We rely on the *trigger_word* valence.
             
             # Actually, simpler: If strategy is JOY, we only return if the *Trigger Word* is positive?
             # No, we want to find *associated* positive memories even if the trigger is neutral.
             
             # Alternative: In JOY_SEEKING, we ignore the input trigger and search the "North" (Intellect/Joy?)
             # No, stay contextual.
             
             # Let's iterate candidates and check if their content looks happy? 
             # Impossible with raw text. 
             
             # Fallback: Just return candidates, but tell Translator to bias output?
             # No. Let's trust the trigger valence.
             pass 
             
        elif strategy == "REJECT":
             return None # Don't speak

        # Default: Random Sample
        filtered_candidates = candidates
        
        # 気分によって混ぜ方を変える（ランダムシャッフル）
        count = min(len(filtered_candidates), random.randint(3, 6))
        chosen = random.sample(filtered_candidates, count)
        
        # うわ言生成
        # うわ言生成 (IR出力)
        # Phase 5: Translator Integration
        # 文字列結合ではなく、データを返す
        valence = self.memory.get_valence(trigger_word) # Phase 6
        
        ir_data = {
            "type": "sediment_recall",
            "concept": trigger_word,
            "fragments": [c['text'] for c in chosen],
            "count": len(chosen),
            "valence": valence, # -1.0 to 1.0
            "strategy": strategy # RESONATE, PROBE, FRICTION
        }
        return ir_data

    def digest_memories(self):
        """ 睡眠時の消化プロセス (Synapse Crystallization) """
        crystallized = self.stomach.digest()
        for crystal in crystallized:
            print(f"💎 Memory Crystal: {crystal}")
        return crystallized

    def _erode(self):
        """ 
        風化作用：古い記憶を消す 
        Phase 6 修正: SQLiteからもDELETEする
        """
        with self.lock:
            if not self.all_fragments:
                return  # 防御: 空なら何もしない
            
            # 最も古い10%を削除
            remove_count = max(1, int(self.max_sediments * 0.1))  # 最低1件
            to_remove = self.all_fragments[:remove_count]
            self.all_fragments = self.all_fragments[remove_count:]
            
            # Phase 6: SQLiteからもDELETE
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                # timestampが最も古いものをDELETE
                cursor.execute('''
                    DELETE FROM sediments 
                    WHERE id IN (
                        SELECT id FROM sediments 
                        ORDER BY timestamp ASC 
                        LIMIT ?
                    )
                ''', (remove_count,))
                deleted = cursor.rowcount
                conn.commit()
                conn.close()
                print(f"🍃 Erosion: Removed {deleted} records from SQLite.")
            except sqlite3.Error as e:
                print(f"⚠️ SQLite Erode Error: {e}")
            
            # インデックス再構築
            self.spatial_index = {}
            for frag in self.all_fragments:
                key = self._get_grid_key(frag['x'], frag['y'])
                if key not in self.spatial_index: 
                    self.spatial_index[key] = []
                self.spatial_index[key].append(frag)
        
        print("🍃 Erosion process completed. Old memories faded.")

    def compress_memory(self, brain_ref=None):
        """ 
        Phase 2.2: Metamorphic Compression (変成作用)
        意味的に類似した記憶をクラスタリングし、代表以外を削除する。
        
        Args:
            brain_ref: KanameBrain instance (for PredictionEngine access)
        """
    def compress_memory(self, brain_ref=None):
        """ 
        Phase 2.2: Metamorphic Compression (変成作用)
        意味的に類似した記憶をクラスタリングし、代表以外を削除する。
        """
        # 1. Resolve Engine
        engine = None
        if hasattr(self, 'prediction_engine') and self.prediction_engine:
            engine = self.prediction_engine
        elif brain_ref and hasattr(brain_ref, 'prediction_engine'):
            engine = brain_ref.prediction_engine
        
        if not engine:
            print("⚠️ Compression skipped: No Prediction Engine found.")
            return
        
        print(f"⛏️ Metamorphic Compression starting... ({len(self.all_fragments)} fragments)")
        
        # 1. Sample fragments for compression (limit to 500 for performance)
        sample_size = min(500, len(self.all_fragments))
        if sample_size < 10:
            print("   Not enough fragments to compress.")
            return
        
        with self.lock:
            # Random sample from all fragments
            sample_indices = random.sample(range(len(self.all_fragments)), sample_size)
            samples = [self.all_fragments[i] for i in sample_indices]
        
        # 2. Get embeddings for samples
        embeddings = []
        valid_samples = []
        for frag in samples:
            text = frag.get('text', '')
            if len(text) < 2:
                continue
            vec = engine._get_embedding_api(text)
            if vec is not None:
                embeddings.append(vec)
                valid_samples.append(frag)
        
        if len(valid_samples) < 10:
            print("   Not enough valid embeddings.")
            return
        
        import numpy as np
        embeddings = np.array(embeddings)
        
        # 3. Leader Algorithm Clustering (1-pass, lightweight)
        # Threshold: cosine similarity > 0.8 = same cluster
        similarity_threshold = 0.8
        valence_threshold = 0.5  # Valence Safeguard
        
        clusters = []  # List of (leader_idx, [member_indices])
        assigned = set()
        
        for i in range(len(valid_samples)):
            if i in assigned:
                continue
            
            # Create new cluster with i as leader
            cluster_members = [i]
            leader_vec = embeddings[i]
            leader_valence = self._get_fragment_valence(valid_samples[i])
            
            for j in range(i + 1, len(valid_samples)):
                if j in assigned:
                    continue
                
                # Cosine Similarity
                dot = np.dot(leader_vec, embeddings[j])
                norm = np.linalg.norm(leader_vec) * np.linalg.norm(embeddings[j])
                sim = dot / norm if norm > 0 else 0
                
                if sim > similarity_threshold:
                    # Valence Safeguard: Don't merge if emotions are opposite
                    member_valence = self._get_fragment_valence(valid_samples[j])
                    if abs(leader_valence - member_valence) < valence_threshold:
                        cluster_members.append(j)
                        assigned.add(j)
            
            assigned.add(i)
            if len(cluster_members) > 1:
                clusters.append((i, cluster_members))
        
        # 4. Compress: Keep leader, remove others
        to_remove_texts = []
        merged_count = 0
        for leader_idx, members in clusters:
            # Keep leader, remove others
            for m_idx in members:
                if m_idx != leader_idx:
                    to_remove_texts.append(valid_samples[m_idx].get('text', ''))
                    merged_count += 1
        
        # 5. Remove from memory and DB
        if to_remove_texts:
            self._remove_sediments_by_text(to_remove_texts)
            print(f"🔮 Metamorphism complete: {len(clusters)} clusters formed, {merged_count} fragments merged.")
        else:
            print("   No similar memories found to compress.")
    
    def _get_fragment_valence(self, fragment):
        """ Get emotional valence for a fragment """
        try:
            text = fragment.get('text', '')
            # Use GeologicalMemory to get valence of the concept
            # Note: Fragments might be just parts of words, but get_valence handles partials?
            # GeologicalMemory.get_valence expects a 'concept' key.
            # If text is not a known concept, it might return 0.0.
            # But it's better than hardcoded 0.0.
            return self.memory.get_valence(text)
        except:
            return 0.0
    
    def _remove_sediments_by_text(self, texts_to_remove):
        """ Remove specific sediments from memory and DB """
        texts_set = set(texts_to_remove)
        
        with self.lock:
            # Remove from memory cache
            self.all_fragments = [f for f in self.all_fragments if f.get('text', '') not in texts_set]
            
            # Rebuild spatial index
            self.spatial_index = {}
            for frag in self.all_fragments:
                key = self._get_grid_key(frag['x'], frag['y'])
                if key not in self.spatial_index:
                    self.spatial_index[key] = []
                self.spatial_index[key].append(frag)
        
        # Remove from SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Delete by text (batch)
            placeholders = ','.join('?' * len(texts_to_remove))
            cursor.execute(f'DELETE FROM sediments WHERE text IN ({placeholders})', list(texts_to_remove))
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            print(f"   Removed {deleted} records from SQLite.")
        except sqlite3.Error as e:
            print(f"⚠️ SQLite Delete Error: {e}")

    def _shatter_text(self, text):
        """ テキスト断片化ロジック """
        frags = []
        i = 0
        while i < len(text):
            length = random.randint(2, 5)
            frags.append(text[i:i+length])
            i += length
        return frags

    def excavate(self, x, y, radius=50):
        """ 発掘: 指定座標周辺の堆積物を掘り起こす (Gravity-Aware Retrieval) """
        start_gx = int((x - radius) // self.grid_size)
        end_gx = int((x + radius) // self.grid_size)
        start_gy = int((y - radius) // self.grid_size)
        end_gy = int((y + radius) // self.grid_size)
        
        found_fossils = set()
        
        with self.lock:
            for gx in range(start_gx, end_gx + 1):
                for gy in range(start_gy, end_gy + 1):
                    key = (gx, gy)
                    if key in self.spatial_index:
                        for sediment in self.spatial_index[key]:
                             # Check precise distance
                             d = math.sqrt((sediment['x'] - x)**2 + (sediment['y'] - y)**2)
                             if d < radius:
                                 found_fossils.add(sediment['text'])
        
        return list(found_fossils)

    def get_emotional_gradient(self, x, y, radius=100):
        """
        Calculate the 'Emotional Gradient' at (x, y).
        Returns a vector (dx, dy) that points towards Positive Valence
        and away from Negative Valence.
        """
        gx_start = int((x - radius) // self.grid_size)
        gx_end = int((x + radius) // self.grid_size)
        gy_start = int((y - radius) // self.grid_size)
        gy_end = int((y + radius) // self.grid_size)
        
        force_x = 0.0
        force_y = 0.0
        
        # We limit the number of samples to avoid lag
        samples = 0
        limit = 50 
        
        with self.lock:
            for gx in range(gx_start, gx_end + 1):
                for gy in range(gy_start, gy_end + 1):
                    key = (gx, gy)
                    if key in self.spatial_index:
                        # Shuffle to get random samples if dense
                        candidates = list(self.spatial_index[key]) # Copy to avoid shuffle mutation of original list? No, shuffle mutates. copy it.
                        random.shuffle(candidates)
                        
                        if len(candidates) > 10:
                            candidates = candidates[:10]
                            
                        for frag in candidates:
                            dx = frag['x'] - x
                            dy = frag['y'] - y
                            dist = math.sqrt(dx*dx + dy*dy)
                            
                            if 1.0 < dist <= radius:
                                # Get Valence
                                text = frag.get('text', '')
                                valence = self.memory.get_valence(text)
                                
                                if abs(valence) > 0.1:
                                    # Force = Valence / Distance^2 (Gravity-like)
                                    # Positive -> Pull (Attraction)
                                    # Negative -> Push (Repulsion)
                                    # We uses 1/dist for stability instead of 1/dist^2
                                    force = valence / dist
                                    
                                    force_x += (dx / dist) * force
                                    force_y += (dy / dist) * force
                                    samples += 1
                                    
                            if samples >= limit: break
                if samples >= limit: break
                
        # Normalize magnitude if too strong
        mag = math.sqrt(force_x**2 + force_y**2)
        if mag > 1.0:
            force_x /= mag
            force_y /= mag
            
        return force_x, force_y




