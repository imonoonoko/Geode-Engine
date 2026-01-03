# word_binding.py
# Phase 18: 言葉↔状態の三項結合
# word → (state, emotion, memory) マッピング

import time
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class WordBinding:
    """言葉と内部状態の結合"""
    word: str
    state: Dict[str, float]  # ホルモン状態
    emotion: float  # 感情価
    memory_fragments: List[str]  # 関連記憶
    usage_count: int = 0
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)


class WordStateBindingSystem:
    """
    言葉↔状態の三項結合システム
    
    言語化したときの内部状態を保存し、
    次にその言葉を使うとき同じ状態が再活性化する。
    
    これにより「口癖」「思考パターン」が自然発生する。
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.lock = threading.Lock()
        
        # word → [WordBinding, ...] (同じ言葉、異なる状態)
        self.bindings: Dict[str, List[WordBinding]] = defaultdict(list)
        
        # 再活性化の強度
        self.reactivation_strength = 0.3
        
        print("🔗 Word-State Binding Initialized.")
    
    def bind(self, word: str, state: Dict[str, float], emotion: float, 
             memory_fragments: List[str] = None) -> WordBinding:
        """
        言葉と状態を結合
        
        Args:
            word: 使用した言葉
            state: そのときの内部状態
            emotion: 感情価
            memory_fragments: 関連する記憶断片
        """
        binding = WordBinding(
            word=word,
            state=state.copy(),
            emotion=emotion,
            memory_fragments=memory_fragments or []
        )
        
        with self.lock:
            self.bindings[word].append(binding)
            
            # 最大10結合/語
            if len(self.bindings[word]) > 10:
                # 使用頻度が低いものを削除
                self.bindings[word].sort(key=lambda b: b.usage_count, reverse=True)
                self.bindings[word] = self.bindings[word][:10]
        
        return binding
    
    def reactivate(self, word: str) -> Optional[Dict[str, float]]:
        """
        言葉から状態を再活性化
        
        過去にその言葉を使ったときの状態を呼び起こす
        
        Returns:
            再活性化された状態差分（加算用）
        """
        with self.lock:
            if word not in self.bindings or not self.bindings[word]:
                return None
            
            # 最も使用頻度が高い結合を選択
            bindings = self.bindings[word]
            best = max(bindings, key=lambda b: b.usage_count)
            
            # 使用カウント更新
            best.usage_count += 1
            best.last_used = time.time()
            
            # 状態差分を計算（完全な状態ではなく、変化量として返す）
            delta = {}
            for key, value in best.state.items():
                # 現在の基準値(50)からの差分を再活性化
                delta[key] = (value - 50.0) * self.reactivation_strength
            
            return delta
    
    def get_associated_words(self, state: Dict[str, float], top_k: int = 5) -> List[str]:
        """
        現在の状態に近い言葉を取得
        
        「この気分のとき、よく使う言葉」を返す
        """
        word_scores = []
        
        with self.lock:
            for word, bindings in self.bindings.items():
                for binding in bindings:
                    # 状態の類似度を計算
                    similarity = self._state_similarity(state, binding.state)
                    word_scores.append((word, similarity, binding.usage_count))
        
        # 類似度 × 使用頻度でソート
        word_scores.sort(key=lambda x: x[1] * (1 + x[2] * 0.1), reverse=True)
        
        return [w for w, _, _ in word_scores[:top_k]]
    
    def _state_similarity(self, s1: Dict[str, float], s2: Dict[str, float]) -> float:
        """状態間の類似度（コサイン類似度っぽいもの）"""
        common_keys = set(s1.keys()) & set(s2.keys())
        if not common_keys:
            return 0.0
        
        dot = sum(s1[k] * s2[k] for k in common_keys)
        norm1 = sum(s1[k] ** 2 for k in common_keys) ** 0.5
        norm2 = sum(s2[k] ** 2 for k in common_keys) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot / (norm1 * norm2)
    
    def get_habit_words(self, min_usage: int = 3) -> List[Tuple[str, int]]:
        """
        口癖を取得
        
        頻繁に使われる言葉のリスト
        """
        habits = []
        
        with self.lock:
            for word, bindings in self.bindings.items():
                total_usage = sum(b.usage_count for b in bindings)
                if total_usage >= min_usage:
                    habits.append((word, total_usage))
        
        habits.sort(key=lambda x: x[1], reverse=True)
        return habits
    
    def get_state(self) -> Dict[str, Any]:
        """状態を取得"""
        with self.lock:
            return {
                "total_words": len(self.bindings),
                "total_bindings": sum(len(b) for b in self.bindings.values()),
                "habit_words": self.get_habit_words()[:5]
            }
