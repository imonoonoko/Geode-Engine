# meaning_generator.py
# Phase 21: 意味の生成 (Meaning Generation)
# 「これは自分にとって意味があるか？」

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class MeaningEvaluation:
    """意味評価結果"""
    content: str
    significance: float  # 重要度 (0-1)
    relevance: float  # 関連性 (0-1)
    emotional_resonance: float  # 感情的共鳴 (0-1)
    overall_meaning: float  # 総合的意味 (0-1)
    timestamp: float = field(default_factory=time.time)


class MeaningGenerator:
    """
    意味の生成システム
    
    「これは自分にとって意味があるか？」を判定。
    意味 = 内部整合性から導出。
    
    重要なもの / どうでもいいもの を区別する。
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.lock = threading.Lock()
        
        # 意味評価履歴
        self.evaluations: List[MeaningEvaluation] = []
        
        # 自分にとって重要なテーマ（学習される）
        self.important_themes: Dict[str, float] = {}
        
        # 閾値
        self.significance_threshold = 0.5
        
        print("✨ Meaning Generator Initialized.")
    
    def evaluate(self, content: str, state: Dict[str, float],
                emotion: float, memories: List[str] = None) -> MeaningEvaluation:
        """
        内容の意味を評価
        
        Args:
            content: 評価対象
            state: 現在の内部状態
            emotion: 感情価
            memories: 関連記憶
        """
        # 1. 重要度: 過去に重要だったテーマとの関連
        significance = self._calc_significance(content)
        
        # 2. 関連性: 現在の状態との整合性
        relevance = self._calc_relevance(content, state)
        
        # 3. 感情的共鳴: 感情を動かすか
        emotional_resonance = abs(emotion)
        
        # 4. 総合的意味
        overall = (
            significance * 0.4 +
            relevance * 0.3 +
            emotional_resonance * 0.3
        )
        
        evaluation = MeaningEvaluation(
            content=content[:100],
            significance=significance,
            relevance=relevance,
            emotional_resonance=emotional_resonance,
            overall_meaning=overall
        )
        
        with self.lock:
            self.evaluations.append(evaluation)
            
            # 意味があれば、テーマとして記録
            if overall > self.significance_threshold:
                self._learn_theme(content, overall)
            
            # 最大500件
            if len(self.evaluations) > 500:
                self.evaluations = self.evaluations[-500:]
        
        return evaluation
    
    def _calc_significance(self, content: str) -> float:
        """重要度を計算（過去のテーマとの関連）"""
        if not self.important_themes:
            return 0.5  # デフォルト
        
        # 単語ベースのマッチング
        words = set(content.lower().split())
        
        max_match = 0.0
        for theme, importance in self.important_themes.items():
            theme_words = set(theme.lower().split())
            overlap = len(words & theme_words)
            if overlap > 0:
                match = overlap / max(len(words), len(theme_words)) * importance
                max_match = max(max_match, match)
        
        return min(1.0, max_match + 0.3)  # ベースライン0.3
    
    def _calc_relevance(self, content: str, state: Dict[str, float]) -> float:
        """関連性を計算（現在の状態との整合性）"""
        # 状態が活発なほど、新しい情報に関連性を感じる
        avg_activation = sum(state.values()) / len(state) if state else 50
        
        # 活性度が高い → 関連性を感じやすい
        return min(1.0, avg_activation / 100 + 0.3)
    
    def _learn_theme(self, content: str, importance: float):
        """重要テーマを学習"""
        # 簡易的にキーワードを抽出
        words = content.split()[:3]  # 最初の3単語
        theme = " ".join(words)
        
        if theme in self.important_themes:
            # 既存テーマは強化
            self.important_themes[theme] = min(1.0, 
                self.important_themes[theme] * 0.7 + importance * 0.3)
        else:
            self.important_themes[theme] = importance * 0.5
        
        # 最大50テーマ
        if len(self.important_themes) > 50:
            # 重要度が低いものを削除
            sorted_themes = sorted(
                self.important_themes.items(),
                key=lambda x: x[1], reverse=True
            )
            self.important_themes = dict(sorted_themes[:50])
    
    def is_meaningful(self, content: str, state: Dict[str, float],
                     emotion: float) -> bool:
        """意味があるかどうかを判定"""
        eval = self.evaluate(content, state, emotion)
        return eval.overall_meaning > self.significance_threshold
    
    def get_important_themes(self, top_k: int = 10) -> List[tuple]:
        """重要テーマを取得"""
        sorted_themes = sorted(
            self.important_themes.items(),
            key=lambda x: x[1], reverse=True
        )
        return sorted_themes[:top_k]
    
    def get_state(self) -> Dict[str, Any]:
        """状態を取得"""
        return {
            "evaluation_count": len(self.evaluations),
            "theme_count": len(self.important_themes),
            "top_themes": self.get_important_themes(3)
        }
