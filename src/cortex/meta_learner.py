# meta_learner.py
# Phase 13: メタ学習 (Meta-Learning)
# 「自分で学び方を変えられる」

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import deque


@dataclass
class LearningOutcome:
    """学習結果を記録"""
    action: str
    prediction: float
    actual: float
    error: float
    timestamp: float = field(default_factory=time.time)


class MetaLearner:
    """
    メタ学習: 学習戦略を動的に調整
    
    - 予測誤差が高い → 探索強化（学習率↑）
    - 予測誤差が低い → 活用強化（学習率↓）
    - 成功パターンを記録し、類似状況で活用
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.lock = threading.Lock()
        
        # 学習率パラメータ
        self.learning_rate = 0.1  # 現在の学習率
        self.lr_min = 0.01  # 最小学習率
        self.lr_max = 0.5  # 最大学習率
        self.lr_adaptation_speed = 0.05  # 適応速度
        
        # 予測誤差履歴
        self.error_history: deque = deque(maxlen=100)
        
        # 成功/失敗パターン
        self.success_patterns: Dict[str, List[LearningOutcome]] = {}
        self.failure_patterns: Dict[str, List[LearningOutcome]] = {}
        
        # 探索 vs 活用バランス
        self.exploration_rate = 0.3  # ε-greedy の ε
        self.exploration_min = 0.1
        self.exploration_max = 0.5
        
        print("🧠 Meta Learner Initialized.")
    
    def record_outcome(self, action: str, prediction: float, actual: float) -> None:
        """
        行動結果を記録
        
        Args:
            action: 行動の識別子
            prediction: 予測値
            actual: 実際の結果
        """
        error = abs(prediction - actual)
        outcome = LearningOutcome(
            action=action,
            prediction=prediction,
            actual=actual,
            error=error
        )
        
        with self.lock:
            self.error_history.append(error)
            
            # 成功/失敗の判定（予測との乖離が小さいか）
            if error < 0.3:
                if action not in self.success_patterns:
                    self.success_patterns[action] = []
                self.success_patterns[action].append(outcome)
                # 最大50件
                if len(self.success_patterns[action]) > 50:
                    self.success_patterns[action] = self.success_patterns[action][-50:]
            else:
                if action not in self.failure_patterns:
                    self.failure_patterns[action] = []
                self.failure_patterns[action].append(outcome)
                if len(self.failure_patterns[action]) > 50:
                    self.failure_patterns[action] = self.failure_patterns[action][-50:]
    
    def adapt_learning_rate(self) -> float:
        """
        予測誤差に基づいて学習率を調整
        
        高誤差 → 学習率↑（環境が変化した、もっと学ぶ必要がある）
        低誤差 → 学習率↓（うまくいっている、安定を維持）
        
        Returns:
            更新後の学習率
        """
        with self.lock:
            if len(self.error_history) < 5:
                return self.learning_rate
            
            # 直近の平均誤差
            recent_errors = list(self.error_history)[-10:]
            avg_error = sum(recent_errors) / len(recent_errors)
            
            # 誤差が高い → 学習率を上げる
            if avg_error > 0.5:
                self.learning_rate *= (1 + self.lr_adaptation_speed)
            # 誤差が低い → 学習率を下げる
            elif avg_error < 0.2:
                self.learning_rate *= (1 - self.lr_adaptation_speed)
            
            # クリップ
            self.learning_rate = max(self.lr_min, min(self.lr_max, self.learning_rate))
            
            return self.learning_rate
    
    def adapt_exploration_rate(self) -> float:
        """
        探索率を調整
        
        成功が続く → 探索を減らす（活用）
        失敗が続く → 探索を増やす（新しい戦略を試す）
        
        Returns:
            更新後の探索率
        """
        with self.lock:
            if len(self.error_history) < 5:
                return self.exploration_rate
            
            recent_errors = list(self.error_history)[-10:]
            success_rate = sum(1 for e in recent_errors if e < 0.3) / len(recent_errors)
            
            # 成功率が高い → 探索を減らす
            if success_rate > 0.7:
                self.exploration_rate *= 0.95
            # 成功率が低い → 探索を増やす
            elif success_rate < 0.3:
                self.exploration_rate *= 1.05
            
            # クリップ
            self.exploration_rate = max(self.exploration_min, min(self.exploration_max, self.exploration_rate))
            
            return self.exploration_rate
    
    def should_explore(self) -> bool:
        """
        探索すべきかどうかを判定
        
        Returns:
            True: 探索モード（新しい行動を試す）
            False: 活用モード（既知の成功パターンを使う）
        """
        import random
        return random.random() < self.exploration_rate
    
    def get_success_rate(self, action: str) -> float:
        """
        特定の行動の成功率を取得
        
        Args:
            action: 行動の識別子
            
        Returns:
            成功率 (0.0 - 1.0)
        """
        with self.lock:
            successes = len(self.success_patterns.get(action, []))
            failures = len(self.failure_patterns.get(action, []))
            total = successes + failures
            
            if total == 0:
                return 0.5  # 未知の行動は中立
            
            return successes / total
    
    def get_state(self) -> Dict[str, Any]:
        """
        現在の状態を取得（デバッグ用）
        """
        with self.lock:
            return {
                "learning_rate": self.learning_rate,
                "exploration_rate": self.exploration_rate,
                "error_history_len": len(self.error_history),
                "success_patterns_count": sum(len(v) for v in self.success_patterns.values()),
                "failure_patterns_count": sum(len(v) for v in self.failure_patterns.values())
            }
    
    def update(self) -> None:
        """
        定期的に呼ばれる更新処理
        学習率と探索率を適応
        """
        self.adapt_learning_rate()
        self.adapt_exploration_rate()
