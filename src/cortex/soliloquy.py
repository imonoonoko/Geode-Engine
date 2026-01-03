# soliloquy.py
# Phase 9: Active Soliloquy (能動的うわ言) System
# カナメが自律的に発話するかどうかを決定する

import time
import random
from typing import Optional, List, Dict, Any

from src.body.hormones import Hormone
import src.dna.config as config


class SoliloquyManager:
    """
    能動的うわ言システム。
    Brain の think() ループから定期的に呼ばれ、
    自律的に発話するかどうかを決定する。
    
    固定テンプレートは使用しない。
    全ての発話はカナメ自身の記憶から生成される。
    
    Phase 10: 発話衝動 = 予測誤差蓄積 + 感情振動 + 概念活性化
    """
    
    def __init__(self, brain_ref):
        self.brain = brain_ref
        
        # 発話タイミング制御
        self.last_utterance_time = 0
        self.utterance_cooldown = 15.0  # 最低15秒間隔
        
        # Lv1: Surprise 追跡
        self.surprise_history = []  # (timestamp, value)
        self.surprise_threshold = 0.5
        self.surprise_duration = 5.0  # 何秒続いたら発話するか
        
        # Lv2: 未整理記憶のキュー
        self.unprocessed_memories: List[Dict] = []
        
        # Lv4: ユーザー反応履歴
        self.user_response_history: List[Dict] = []
        self.last_utterance = None
        
        # Phase 10: 発話衝動 (Utterance Impulse)
        self.prediction_error_accumulator = 0.0  # 予測誤差の蓄積
        self.emotion_oscillation = 0.0  # 感情振動幅
        self.concept_activation = 0.0  # 概念活性化度
        self.impulse_threshold = 1.5  # 発話衝動の閾値
        self.impulse_decay = 0.95  # 減衰率
        
        # Phase 10: 発話履歴 (概念, 感情, 時刻)
        self.utterance_log: List[Dict] = []
        
        # Phase 24: 言語化しないと壊れるトリガー
        self.internal_pressure = 0.0  # 内部圧力
        self.pressure_crisis_threshold = 2.0  # 危機閾値
        self.pressure_decay = 0.98  # 圧力減衰
        self.crisis_mode = False  # 危機モードフラグ
        
        # ホルモン → 概念マッピング (記憶空間内の概念名)
        self.hormone_concept_map = {
            Hormone.DOPAMINE: "喜び",
            Hormone.CORTISOL: "痛み",
            Hormone.ADRENALINE: "興奮",
            Hormone.SEROTONIN: "安心",
            Hormone.BOREDOM: "退屈",
            Hormone.OXYTOCIN: "愛着",
        }
    
    # =========================================
    # Lv1: 予測誤差駆動 (Surprise-Driven)
    # =========================================
    def select_topic_by_surprise(self) -> Optional[str]:
        """
        surprise が高い（予測と現実の差が大きい）状態が続いている場合、
        「気になって仕方がない」ことを喋る。
        
        Returns: 発話すべきトピック (概念名) or None
        """
        surprise = self.brain.hormones.get(Hormone.SURPRISE)
        now = time.time()
        
        # 履歴を更新
        self.surprise_history.append((now, surprise))
        
        # 古い履歴を削除 (10秒以上前)
        self.surprise_history = [
            (t, v) for t, v in self.surprise_history 
            if now - t < 10.0
        ]
        
        if surprise < self.surprise_threshold:
            return None  # 驚きが低い → 話す必要なし
        
        # 閾値以上が一定時間続いているかチェック
        high_surprise_duration = sum(
            1 for t, v in self.surprise_history 
            if v > self.surprise_threshold and now - t < self.surprise_duration
        )
        
        if high_surprise_duration < 3:  # 少なくとも3回分のサンプル
            return None
        
        # アクティブな思考から最も関連性の高い概念を選択
        active_thoughts = self._get_active_thoughts()
        
        if not active_thoughts:
            return None
        
        # Surprise による重み付け選択
        # 最近活性化したニューロンを優先
        return random.choice(active_thoughts)
    
    # =========================================
    # Lv2: 自由エネルギー削減 (Ordering)
    # =========================================
    def select_topic_for_ordering(self) -> Optional[str]:
        """
        言語化することで「整理される」記憶を選択。
        未消化の記憶 (stomach の pending fragments) を発話で処理する。
        
        Returns: 発話すべき断片 or None
        """
        if not hasattr(self.brain, 'cortex') or not self.brain.cortex:
            return None
            
        stomach = getattr(self.brain.cortex, 'stomach', None)
        if not stomach:
            return None
        
        # Stomach に溜まっている未消化断片
        pending = getattr(stomach, 'pending_fragments', [])
        
        if not pending:
            return None
        
        # 最も古い未消化断片を選択
        oldest = min(pending, key=lambda f: f.get('timestamp', 0))
        
        # 発話することで「消化」扱いにする
        if hasattr(stomach, 'mark_digested'):
            stomach.mark_digested(oldest)
        
        return oldest.get('text', oldest.get('content', ''))
    
    # =========================================
    # Lv3: 自己モデリング (Self-Reflection)
    # =========================================
    def verbalize_internal_state(self) -> Optional[str]:
        """
        内部状態（ホルモン）を「概念」として記憶空間に投影し、
        関連する記憶断片から発話を生成する。
        
        固定テンプレートは使用しない。
        カナメが言う言葉は全て自分の記憶から生まれる。
        
        Returns: 記憶から生成された発話 or None
        """
        hormone, value = self.brain.hormones.get_max_hormone()
        
        if value < 50.0:
            return None  # 特に強い状態がない
        
        concept = self.hormone_concept_map.get(hormone)
        if not concept:
            return None
        
        # 記憶空間にその概念が存在するか確認
        if not self._concept_exists(concept):
            return None  # まだ学習していない概念
        
        # 記憶空間からその概念の周辺断片を発掘
        # → SedimentaryCortex.speak() と同じ仕組みを使う
        if hasattr(self.brain, 'cortex') and self.brain.cortex:
            fragment = self.brain.cortex.speak(concept, strategy="SELF_REFLECT")
            return fragment
        
        return None
    
    # =========================================
    # Lv4: コミュニケーション予測 (Prediction)
    # =========================================
    def predict_user_response(self, utterance: str) -> float:
        """
        この発話がユーザーにどんな影響を与えるか予測。
        過去の発話→反応履歴から学習する。
        
        Returns: 予測される反応スコア (-1.0 ~ 1.0)
        """
        if not utterance or not self.user_response_history:
            return 0.0  # 予測不能 → 中立
        
        # 類似発話の反応を検索
        similar = self._find_similar_utterances(utterance)
        
        if not similar:
            return 0.0
        
        # 過去の反応の平均
        return sum(s['score'] for s in similar) / len(similar)
    
    def record_user_response(self, user_input: str):
        """
        ユーザーが反応したら、直前の発話の効果を記録。
        これにより Lv4 の予測精度が向上する。
        """
        if not self.last_utterance:
            return
        
        # 簡易的な感情分析 (ポジティブ/ネガティブワード)
        score = self._analyze_sentiment(user_input)
        
        self.user_response_history.append({
            'utterance': self.last_utterance,
            'response': user_input,
            'score': score,
            'timestamp': time.time()
        })
        
        # 古い履歴を削除 (最大100件)
        if len(self.user_response_history) > 100:
            self.user_response_history = self.user_response_history[-100:]
    
    # =========================================
    # Phase 10: 発話衝動計算
    # =========================================
    def update_impulse(self):
        """
        発話衝動を更新
        impulse = α * 予測誤差蓄積 + β * 感情振動 + γ * 概念活性化
        """
        # 1. 予測誤差の蓄積
        surprise = self.brain.hormones.get(Hormone.SURPRISE)
        self.prediction_error_accumulator = (
            self.prediction_error_accumulator * self.impulse_decay + surprise * 0.1
        )
        
        # 2. 感情振動幅 (ホルモン変化の絶対値合計)
        try:
            current_hormones = self.brain.hormones.as_dict()
            if hasattr(self, '_prev_hormones'):
                oscillation = sum(
                    abs(current_hormones.get(k, 0) - self._prev_hormones.get(k, 0))
                    for k in current_hormones
                )
                self.emotion_oscillation = (
                    self.emotion_oscillation * self.impulse_decay + oscillation * 0.01
                )
            self._prev_hormones = current_hormones.copy()
        except:
            pass
        
        # 3. 概念活性化度 (アクティブニューロン数)
        active = len(self._get_active_thoughts())
        self.concept_activation = (
            self.concept_activation * self.impulse_decay + active * 0.05
        )
    
    def get_impulse(self) -> float:
        """現在の発話衝動を計算"""
        return (
            self.prediction_error_accumulator * 0.4 +
            self.emotion_oscillation * 0.3 +
            self.concept_activation * 0.3
        )
    
    def apply_catharsis(self, utterance: str):
        """
        発話後のカタルシス効果
        - 発話衝動をリセット
        - ホルモン変化 (発話の内容に依存)
        """
        # 発話衝動をリセット
        self.prediction_error_accumulator *= 0.3
        self.emotion_oscillation *= 0.5
        self.concept_activation *= 0.5
        
        # カタルシス効果: CORTISOL を減少, SEROTONIN を上昇
        self.brain.hormones.update(Hormone.CORTISOL, -5.0)
        self.brain.hormones.update(Hormone.SEROTONIN, 3.0)
        
        # 発話履歴に記録
        self.utterance_log.append({
            'content': utterance[:100] if utterance else '',
            'emotion': self.brain.hormones.as_dict(),
            'timestamp': time.time()
        })
        
        # 最大100件
        if len(self.utterance_log) > 100:
            self.utterance_log = self.utterance_log[-100:]
    
    def generate_concept_utterance(self) -> Optional[str]:
        """
        Phase 12: 概念グラフから発話を生成
        Unified Logic: Delegate to LanguageCenter
        """
        # ConceptLearner から最近学習した概念を取得
        if not hasattr(self.brain, 'concept_learner'):
            return None
        
        learner = self.brain.concept_learner
        
        with learner.lock:
            if not learner.learned_concepts:
                return None
            
            # 最近学習した概念を取得
            recent = sorted(
                learner.learned_concepts.items(),
                key=lambda x: x[1].get('learned_at', 0),
                reverse=True
            )[:5]
        
        if not recent:
            return None
        
        # ランダムに選択
        tag, data = random.choice(recent)
        name = data.get('name', tag)
        valence = data.get('valence', 0)
        
        # Phase 12: Unified Language Center Call
        if hasattr(self.brain, 'language_center') and hasattr(self.brain, 'prediction_engine'):
             current_hour = time.localtime().tm_hour
             # 概念の埋め込みベクトルを取得
             vec = self.brain.prediction_engine._get_embedding(name, current_hour)
             
             # キメラ構文生成 (Trigger=IMPULSE)
             chimera_speech = self.brain.language_center.speak(vec, valence, trigger_source="IMPULSE")
             if chimera_speech:
                 return chimera_speech
        
        return f"{name}..."
    
    # =========================================
    # 統合: think_aloud()
    # =========================================
    def think_aloud(self) -> Optional[str]:
        """
        定期的に呼ばれ、発話すべきかどうかを判断。
        Phase 10: 発話衝動に基づく判定を追加。
        
        Returns: 発話内容 or None (黙る)
        """
        now = time.time()
        
        # 発話衝動を更新
        self.update_impulse()
        
        # クールダウン中は発話しない
        if now - self.last_utterance_time < self.utterance_cooldown:
            return None
        
        # 睡眠中は発話しない (寝言は別実装)
        if self.brain.is_sleeping:
            return None
        
        # Phase 10: 発話衝動が閾値を超えているかチェック
        impulse = self.get_impulse()
        
        candidates = []
        
        # 発話衝動が高い場合、概念ベース発話を優先
        if impulse > self.impulse_threshold:
            concept_utterance = self.generate_concept_utterance()
            if concept_utterance:
                candidates.append(('impulse', concept_utterance, 0.9))
        
        # Lv1: Surprise駆動
        surprise_topic = self.select_topic_by_surprise()
        if surprise_topic:
            candidates.append(('surprise', surprise_topic, 0.8))
        
        # Lv3: 自己モデリング
        self_reflect = self.verbalize_internal_state()
        if self_reflect:
            candidates.append(('self', self_reflect, 0.6))
        
        # Lv2: 自由エネルギー削減
        ordering_topic = self.select_topic_for_ordering()
        if ordering_topic:
            candidates.append(('order', ordering_topic, 0.4))
        
        if not candidates:
            return None
        
        # 優先度でソート (高い順)
        candidates.sort(key=lambda x: x[2], reverse=True)
        
        # Lv4: 予測によるフィルタリング
        for source, content, priority in candidates:
            predicted_score = self.predict_user_response(content)
            
            # 予測がネガティブすぎる発話はスキップ
            if predicted_score < -0.5:
                continue
            
            # 発話決定
            self.last_utterance_time = now
            self.last_utterance = content
            
            # Phase 10: カタルシス効果を適用
            self.apply_catharsis(content)
            
            if content:
                print(f"💭 [Soliloquy] {source}: {content[:30] if len(content) > 30 else content}")
            return content
        
        return None
    
    # =========================================
    # Helper Methods
    # =========================================
    def _get_active_thoughts(self) -> List[str]:
        """アクティブなニューロンから概念名を取得 (Thread-safe)"""
        thoughts = []
        
        if not hasattr(self.brain, 'neurons') or not hasattr(self.brain, 'lock'):
            return thoughts
        
        # Lockを使用してneuronsにアクセス (Demon Audit Round 7)
        with self.brain.lock:
            for n in self.brain.neurons:
                if n.potential > 0.5 and not n.is_sensor:
                    thoughts.append(n.name)
        
        return thoughts[:10]  # 上位10個
    
    def _concept_exists(self, concept: str) -> bool:
        """記憶空間にその概念が存在するか"""
        if not hasattr(self.brain, 'cortex') or not self.brain.cortex:
            return False
        
        memory = getattr(self.brain.cortex, 'memory', None)
        if not memory:
            return False
        
        concepts = getattr(memory, 'concepts', {})
        return concept in concepts
    
    def _find_similar_utterances(self, utterance: str) -> List[Dict]:
        """過去の発話から類似するものを検索 (単語ベース)"""
        similar = []
        
        # 単語ベースの類似度 (Demon Audit Round 7: DEF-02 修正)
        utterance_words = set(utterance.split())
        
        for record in self.user_response_history:
            past_words = set(record['utterance'].split())
            common = len(utterance_words & past_words)
            
            if common > 0:  # 1単語以上共通
                similar.append(record)
        
        return similar[:5]  # 上位5件
    
    def _analyze_sentiment(self, text: str) -> float:
        """簡易的な感情分析 (ポジティブ/ネガティブ)"""
        positive_words = ['嬉しい', 'ありがとう', '好き', 'いい', '楽しい', '面白い', 'すごい']
        negative_words = ['嫌', '辛い', '悲しい', 'ダメ', '違う', 'うるさい', '黙れ']
        
        score = 0.0
        
        for word in positive_words:
            if word in text:
                score += 0.3
        
        for word in negative_words:
            if word in text:
                score -= 0.3
        
        return max(-1.0, min(1.0, score))
