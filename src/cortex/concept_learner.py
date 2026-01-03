# concept_learner.py
"""
Phase 6: Concept Learner (ハイブリッド学習システム)

学習フロー:
1. 未知の物体を発見 → 感情状態と共に一時記憶
2. ユーザーが名前を教える → 永続記憶に昇格
3. 次回からはその名前で認識

責任:
- 未知物体の一時記憶管理
- ユーザー教示の受付
- 学習済み概念の永続化
"""

import time
import json
import os
import threading


class ConceptLearner:
    """
    ハイブリッド学習: 感情記銘 + ユーザー教示
    """
    
    def __init__(self, brain, data_dir="memory"):
        """
        Args:
            brain: KanameBrain インスタンス
            data_dir: 学習データの保存先
        """
        self.brain = brain
        self.data_dir = data_dir
        self.lock = threading.Lock()
        
        # 一時記憶: 未知物体 (まだ名前を教わっていない)
        # {yolo_tag: {"first_seen": timestamp, "valence": float, "count": int}}
        self.unknown_concepts = {}
        
        # 学習済み辞書: ユーザーが教えた名前
        # {yolo_tag: {"name": str, "learned_at": timestamp, "valence": float}}
        self.learned_concepts = {}
        
        # 辞書ファイルパス
        self.dict_path = os.path.join(data_dir, "learned_concepts.json")
        
        # 読み込み
        self._load()
        
        print(f"📚 Concept Learner Initialized. Learned: {len(self.learned_concepts)} concepts.")
    
    def _load(self):
        """学習済み概念を読み込み"""
        if os.path.exists(self.dict_path):
            try:
                with open(self.dict_path, 'r', encoding='utf-8') as f:
                    self.learned_concepts = json.load(f)
            except Exception as e:
                print(f"⚠️ Concept Learner Load Error: {e}")
    
    def _save(self):
        """学習済み概念を保存"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.dict_path, 'w', encoding='utf-8') as f:
                json.dump(self.learned_concepts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Concept Learner Save Error: {e}")
    
    def translate(self, yolo_tag: str) -> tuple:
        """
        YOLOタグ → 表示名に変換
        
        Returns:
            (display_name, is_known)
            is_known: 辞書or学習済みかどうか
        """
        # 1. 元の辞書にある？
        if hasattr(self.brain, 'visual_bridge'):
            builtin_name = self.brain.visual_bridge.YOLO_TO_JP.get(yolo_tag)
            if builtin_name:
                return (builtin_name, True)
        
        # 2. 学習済み？
        with self.lock:
            if yolo_tag in self.learned_concepts:
                return (self.learned_concepts[yolo_tag]["name"], True)
        
        # 3. 未知
        return (None, False)
    
    def encounter_unknown(self, yolo_tag: str, valence: float = 0.0):
        """
        未知の物体に遭遇した時に呼ばれる
        
        Args:
            yolo_tag: YOLOが検出したタグ (英語)
            valence: 現在の感情価 (-1.0 ~ 1.0)
        """
        with self.lock:
            if yolo_tag not in self.unknown_concepts:
                self.unknown_concepts[yolo_tag] = {
                    "first_seen": time.time(),
                    "valence": valence,
                    "count": 1
                }
                print(f"❓ 新しい何かを見つけた... ({yolo_tag})")
            else:
                # 既に見たことがある未知物体
                self.unknown_concepts[yolo_tag]["count"] += 1
                # 感情価を更新 (平均化)
                old_valence = self.unknown_concepts[yolo_tag]["valence"]
                self.unknown_concepts[yolo_tag]["valence"] = (old_valence + valence) / 2
    
    def teach(self, name: str) -> bool:
        """
        ユーザーが「これは〇〇だよ」と教えた時に呼ばれる
        最後に見た未知物体に名前を付ける
        
        Args:
            name: ユーザーが教えた名前 (日本語)
            
        Returns:
            成功したかどうか
        """
        with self.lock:
            if not self.unknown_concepts:
                # 未知物体がない状態で教示された (無視)
                return False
            
            # 最後に見た (最新の) 未知物体を取得
            latest_tag = max(
                self.unknown_concepts.keys(),
                key=lambda t: self.unknown_concepts[t]["first_seen"]
            )
            
            unknown_data = self.unknown_concepts.pop(latest_tag)
            
            # 学習済みに昇格
            self.learned_concepts[latest_tag] = {
                "name": name,
                "learned_at": time.time(),
                "valence": unknown_data["valence"],
                "exposure_count": unknown_data["count"]
            }
            
            # 記憶にも追加
            if hasattr(self.brain, 'memory'):
                self.brain.memory.touch(name)  # 座標を割り当て
                self.brain.memory.reinforce(name, unknown_data["valence"])  # 感情を引き継ぎ
                
                # Phase 6: Vectorize the new concept (Generate Hash)
                if hasattr(self.brain, 'prediction_engine'):
                     # Trigger API embedding to auto-calculate hash
                     # We use _get_embedding_api directly to ensure Semantic Vector
                     try:
                         self.brain.prediction_engine._get_embedding_api(name)
                     except Exception as e:
                         print(f"⚠️ Concept Vectorization Failed: {e}")
            
            print(f"📝 学習完了: {latest_tag} → 「{name}」 (感情価: {unknown_data['valence']:.2f})")
            
            # 保存
            self._save()
            return True
    
    def get_recent_unknown(self) -> str | None:
        """
        直近で見た未知物体のタグを取得 (UI用)
        """
        with self.lock:
            if not self.unknown_concepts:
                return None
            return max(
                self.unknown_concepts.keys(),
                key=lambda t: self.unknown_concepts[t]["first_seen"]
            )
    
    def get_display_name(self, yolo_tag: str) -> str:
        """
        表示用の名前を取得 (ログ用)
        
        未知の場合: "❓ 何か"
        学習済みの場合: その名前
        """
        name, is_known = self.translate(yolo_tag)
        
        if is_known:
            return f"{name} ({yolo_tag})"
        else:
            return f"❓ 何か ({yolo_tag})"
