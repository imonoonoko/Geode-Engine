import threading
import networkx as nx
from janome.tokenizer import Tokenizer
import collections
import os
import math
import random
import src.dna.config as config

class SynapticStomach:
    def __init__(self, memory_dir, brain_ref=None):
        print("🧠 Initializing Synaptic Stomach (Graph Theory Core)...")
        # 脳内の神経ネットワーク (無向グラフ)
        self.brain_graph = nx.Graph()
        self.tokenizer = Tokenizer()
        
        self.lock = threading.Lock() # Thread Safety (Phase 14)
        self.brain_ref = brain_ref  # Phase 30: 感情→学習接続
        
        # 短期記憶バッファ (日中の会話) - 感情付き
        self.daily_buffer = []  # [{"tokens": [...], "arousal": float}]
        
        # データの保存先
        self.graph_path = os.path.join(memory_dir, "brain_graph.gexf")
        self.load_graph()

    def load_graph(self):
        """ 既存の脳内マップをロード """
        if os.path.exists(self.graph_path):
            try:
                self.brain_graph = nx.read_gexf(self.graph_path)
                print(f"📖 Loaded Brain Graph: {len(self.brain_graph.nodes)} concepts connected.")
            except AttributeError as e:
                # NumPy 2.0 Compatibility Fix
                if "float_" in str(e):
                    # print("⚠️ NumPy 2.0 Patch: Injecting np.float_ alias...")
                    import numpy as np
                    if not hasattr(np, 'float_'):
                        np.float_ = np.float64 # type: ignore
                    try:
                        self.brain_graph = nx.read_gexf(self.graph_path)
                        print(f"📖 Loaded Brain Graph (Patched): {len(self.brain_graph.nodes)} concepts.")
                    except Exception as e2:
                         print(f"⚠️ Failed to load brain graph after patch: {e2}")
                         self.brain_graph = nx.Graph()
                else:
                    print(f"⚠️ Failed to load brain graph: {e}")
                    self.brain_graph = nx.Graph()
            except Exception as e:
                print(f"⚠️ Failed to load brain graph: {e}")
                self.brain_graph = nx.Graph()

    def save_graph(self):
        """ 脳内マップを保存 (Atomic Safe Save) """
        try:
            temp_path = self.graph_path + ".tmp"
            
            with self.lock:
                # NumPy 2.0 互換性: すべての属性を Python ネイティブ型に変換
                # 1. グラフ属性
                for key, value in self.brain_graph.graph.items():
                    if hasattr(value, 'item'):
                        self.brain_graph.graph[key] = value.item()

                # 2. ノード属性
                for node, data in self.brain_graph.nodes(data=True):
                    for key, value in data.items():
                        if hasattr(value, 'item'):  # numpy スカラー
                            data[key] = value.item()
                        elif not isinstance(value, (int, float, str, bool, list, dict)):
                            try:
                                data[key] = float(value)
                            except:
                                data[key] = str(value)

                # 3. エッジ属性
                for u, v, data in self.brain_graph.edges(data=True):
                    for key, value in data.items():
                        if hasattr(value, 'item'):  # numpy スカラー
                            data[key] = value.item()
                        elif isinstance(value, (int, float, str, bool)):
                            pass
                        else:
                            try:
                                data[key] = float(value)
                            except:
                                data[key] = str(value)
                
                try:
                    nx.write_gexf(self.brain_graph, temp_path)
                except AttributeError as e:
                    if "float_" in str(e):
                        # 最終手段: NetworkX が古い場合、float_ エラーが出るためモンキーパッチ
                        import numpy as np
                        if not hasattr(np, 'float_'):
                            np.float_ = np.float64
                        nx.write_gexf(self.brain_graph, temp_path)
                    else:
                        raise e
            
            # Atomic Rename
            if os.path.exists(self.graph_path):
                os.remove(self.graph_path)
            os.rename(temp_path, self.graph_path)
            
        except Exception as e:
            print(f"⚠️ Failed to save brain graph: {e}")
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass

    def eat(self, text, emotion_snapshot=None):
        """ 1. 摂食: 単語に分解してバッファに溜める (感情付き) """
        try:
            # 名詞と形容詞だけ抽出
            tokens = [token.surface for token in self.tokenizer.tokenize(text) 
                      if token.part_of_speech.split(',')[0] in ['名詞', '形容詞']]
            
            # ストップワード除去 (簡易)
            stop_words = ["私", "僕", "俺", "あなた", "君", "これ", "それ", "あれ", "ん", "よう", "こと", "もの"]
            
            import re
            def is_valid_token(t):
                 if t in stop_words: return False
                 if len(t) < 2: return False # 1文字はノイズが多い
                 if re.match(r'^[a-zA-Z0-9_\-:.]+$', t): return False # LOC:3:-7 などのシステムタグを除外
                 return True

            tokens = [t for t in tokens if is_valid_token(t)]

            # Limit token count to prevent O(N^2) explosion in digest
            tokens = tokens[:50] 

            if len(tokens) > 1:
                # Phase 30: 感情スナップショット取得
                arousal = 50.0  # デフォルト（中立）
                if emotion_snapshot:
                    arousal = emotion_snapshot.get('arousal', 50.0)
                elif self.brain_ref:
                    try:
                        from src.body.hormones import Hormone
                        adrenaline = self.brain_ref.hormones.get(Hormone.ADRENALINE)
                        dopamine = self.brain_ref.hormones.get(Hormone.DOPAMINE)
                        arousal = (adrenaline + dopamine) / 2.0
                    except:
                        pass
                
                with self.lock:
                    if len(self.daily_buffer) < 1000: # Safety Cap
                        self.daily_buffer.append({
                            "tokens": tokens,
                            "arousal": arousal
                        })
                # print(f"🥗 Eaten: {tokens} (arousal={arousal:.1f})")
        except Exception as e:
            print(f"Eating Error: {e}")

    def _should_store(self, arousal: float) -> bool:
        """
        Phase 30: 記憶保存確率 P(store) = σ(κ·‖e‖)
        感情が強い経験ほど残りやすい
        """
        kappa = 0.05  # 感受性パラメータ
        probability = 1 / (1 + math.exp(-kappa * (arousal - 50)))
        return random.random() < probability

    def _get_learning_rate(self, arousal: float) -> float:
        """
        Phase 30: 動的学習率 η_t = η_0 · (1 + γ·e_t)
        高覚醒 → 学習が早い
        """
        gamma = 0.01  # 感情感度
        base_rate = 1.0
        rate = base_rate * (1 + gamma * (arousal - 50))
        return max(0.5, min(1.5, rate))  # クランプ [0.5, 1.5]

    def digest(self):
        """ 2. 消化 (睡眠時): ネットワークを構築・強化・剪定する """
        buffer_copy = []
        with self.lock:
            if self.daily_buffer:
                buffer_copy = list(self.daily_buffer)
                self.daily_buffer = [] # Clear immediately for safety

        print("🧠 Synaptic Crystallization (シナプス結合プロセス) 開始...")

        # --- Dream Rehearsal (夢の反芻) ---
        # バッファが空でも、過去の記憶を呼び起こして強化する
        self._rehearse_memories()

        # --- A. 結合 (Networking) ---
        # 今日の会話から、単語間のリンクを作る
        # O(N^2) Warning: Daily buffer shouldn't be too huge per batch
        new_edges_count = 0
        skipped_count = 0
        
        with self.lock:  # Demon Audit Fix: Hold lock during graph mutations
            for entry in buffer_copy:
                # Phase 30: 感情付きバッファ対応 (後方互換)
                if isinstance(entry, dict):
                    tokens = entry.get("tokens", [])
                    arousal = entry.get("arousal", 50.0)
                else:
                    tokens = entry  # 旧形式 (リスト)
                    arousal = 50.0
                
                # Phase 30: 記憶保存確率 - 平坦な体験は消える
                if not self._should_store(arousal):
                    skipped_count += 1
                    continue
                
                # Phase 30: 動的学習率
                learning_rate = self._get_learning_rate(arousal)
                
                # 同じ文の中にある単語同士を「共起」として結ぶ
                for i in range(len(tokens)):
                    for j in range(i + 1, len(tokens)):
                        word_a = tokens[i]
                        word_b = tokens[j]
                        
                        if word_a == word_b: continue

                        # 既に結合があれば太く、なければ新規作成
                        if self.brain_graph.has_edge(word_a, word_b):
                            self.brain_graph[word_a][word_b]['weight'] += learning_rate
                        else:
                            self.brain_graph.add_edge(word_a, word_b, weight=learning_rate)
                        new_edges_count += 1
        
        print(f"🔗 Formed {new_edges_count} synaptic connections (skipped {skipped_count} low-emotion entries).")
        if new_edges_count > 0:
            avg_arousal = sum(e.get('arousal', 50) if isinstance(e, dict) else 50 for e in buffer_copy) / max(1, len(buffer_copy))
            print(f"📈 Average Arousal: {avg_arousal:.1f} → Learning Rate: {self._get_learning_rate(avg_arousal):.2f}")

        # --- B. 忘却 (Pruning) ---
        # 「結合が弱い（weightが低い）」エッジを容赦なく切る
        # これが「どうでもいい雑談を忘れる」プロセス
        threshold = 2 # 閾値（2回以上関連しないと忘れる）
        
        with self.lock:  # Demon Audit Fix: Hold lock during pruning
            edges_to_remove = []
            for u, v, data in self.brain_graph.edges(data=True):
                if data['weight'] < threshold:
                    edges_to_remove.append((u, v))
            
            self.brain_graph.remove_edges_from(edges_to_remove)
            
            # 孤立したノード（誰とも繋がっていない単語）も削除
            isolated_nodes = list(nx.isolates(self.brain_graph))
            self.brain_graph.remove_nodes_from(isolated_nodes)
        
        print(f"🍂 Pruned {len(edges_to_remove)} weak connections and {len(isolated_nodes)} isolated concepts.")

        # --- C. 結晶の抽出 (Extraction) ---
        # 最も強く結びついている「概念の塊（コミュニティ）」を見つける
        
        crystallized_memories = []
        
        with self.lock:  # Hold lock for analysis
            if len(self.brain_graph) > 0:
                # PageRankで重要語を抽出
                try:
                    ranking = nx.pagerank(self.brain_graph, weight='weight')
                    top_concepts = sorted(ranking.items(), key=lambda x: x[1], reverse=True)[:5]
                    
                    # 結果をテキスト化
                    concepts_str = ", ".join([w for w, score in top_concepts])
                    crystallized_memories.append(f"Recent Obsession: {concepts_str}")
                    
                    # 最も強いエッジ (Top 3)
                    sorted_edges = sorted(self.brain_graph.edges(data=True), 
                                          key=lambda x: x[2]['weight'], reverse=True)[:3]
                    for u, v, data in sorted_edges:
                        crystallized_memories.append(f"Strong Bond: {u}⇔{v} (Lv:{data['weight']})")
                        
                except Exception as e:
                    print(f"Crystallization Analysis Error: {e}")

        # Save state
        self.save_graph()

        # Buffer was cleared at start of digest
        
        return crystallized_memories

    def forget_concepts(self, words):
        """ 3. 忘却の同期: 記憶層(Memory)から消えた概念をグラフからも消す """
        if not words: return
        
        with self.lock:
            count = 0
            for w in words:
                if self.brain_graph.has_node(w):
                    self.brain_graph.remove_node(w)
                    count += 1
            
    def _rehearse_memories(self):
        """ 4. 夢の反芻: 既存の記憶をランダムに強化する (Forgot Prevention) """
        import random
        
        rehearsed_count = 0
        rehearsed_pairs = []
        
        with self.lock:
            if self.brain_graph.number_of_edges() == 0:
                print("🧠 Dream: No memories to rehearse yet.")
                return

            # 全エッジからランダムに数個選ぶ (反復演習)
            # エッジ数が多い場合はサンプリング、少なければ全部
            all_edges = list(self.brain_graph.edges(data=True))
            sample_size = min(len(all_edges), 10) # 一晩に10個のエピソードを反芻
            
            selected_edges = random.sample(all_edges, sample_size)
            
            for u, v, data in selected_edges:
                # 既存の結合を強化 (Heppian Learning: Use it or lose it)
                # 強い記憶ほどよく思い出される? あるいはランダム?
                # ここでは「ランダムな再活性化」により、弱い記憶も救済するチャンスを与える
                
                # Weight Increment
                # 既に強い記憶(>10)はあまり強化しなくてもいいかもしれないが、
                # 単純に +1 することで「忘れにくく」する
                self.brain_graph[u][v]['weight'] += 1
                rehearsed_count += 1
                rehearsed_pairs.append(f"{u}⇔{v}")

        if rehearsed_count > 0:
            print(f"🌙 Dream Rehearsal: Reinforced {rehearsed_count} synaptic bonds.")
            print(f"   💭 Dreamed of: {', '.join(rehearsed_pairs[:5])}...")
    def get_strong_links(self, limit=20, threshold=2.0):
        """
        Phase 6: Synaptic-Geological Bridge
        強い結合を持つ単語ペアを抽出する（地図の引力計算用）
        """
        strong_links = []
        with self.lock:
            # 重みでソート
            sorted_edges = sorted(self.brain_graph.edges(data=True), 
                                key=lambda x: x[2]['weight'], reverse=True)
            
            for u, v, data in sorted_edges:
                w = data['weight']
                if w >= threshold:
                    strong_links.append((u, v, w))
                if len(strong_links) >= limit:
                    break
        
        return strong_links
