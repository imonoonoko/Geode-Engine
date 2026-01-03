# world_model.py
# Phase 14: 世界モデル (World Model)
# 「行動したらどうなるかを内部シミュレーション」

import time
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import deque


@dataclass
class StatePrediction:
    """状態予測の記録"""
    state_before: Dict[str, float]
    action: str
    predicted_state: Dict[str, float]
    actual_state: Optional[Dict[str, float]] = None
    error: float = 0.0
    timestamp: float = field(default_factory=time.time)


class WorldModel:
    """
    世界モデル: 行動の結果を予測
    
    p(s_{t+1} | s_t, a_t) を近似し、
    予測誤差を学習信号として活用。
    
    Active Inference の核心部分。
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.lock = threading.Lock()
        
        # 状態遷移モデル: (action, state_key) -> expected_delta
        self.transition_model: Dict[Tuple[str, str], float] = {}
        
        # 予測履歴
        self.prediction_history: deque = deque(maxlen=100)
        
        # 予測誤差の履歴
        self.error_history: deque = deque(maxlen=100)
        
        # 学習率
        self.learning_rate = 0.1
        
        print("🌍 World Model Initialized.")
    
    def predict(self, state: Dict[str, float], action: str) -> Dict[str, float]:
        """
        次の状態を予測: p(s_{t+1} | s_t, a_t)
        
        Args:
            state: 現在の状態（ホルモンレベル等）
            action: 予定している行動
            
        Returns:
            予測される次の状態
        """
        predicted = {}
        
        with self.lock:
            for key, value in state.items():
                # 遷移モデルから予測変化量を取得
                delta = self.transition_model.get((action, key), 0.0)
                predicted[key] = value + delta
        
        # 予測を記録
        prediction = StatePrediction(
            state_before=state.copy(),
            action=action,
            predicted_state=predicted
        )
        
        with self.lock:
            self.prediction_history.append(prediction)
        
        return predicted
    
    def update(self, predicted: Dict[str, float], actual: Dict[str, float], action: str) -> float:
        """
        予測誤差から学習
        
        Args:
            predicted: 予測した状態
            actual: 実際の状態
            action: 行った行動
            
        Returns:
            予測誤差
        """
        total_error = 0.0
        
        with self.lock:
            for key in predicted:
                if key not in actual:
                    continue
                
                error = actual[key] - predicted[key]
                total_error += abs(error)
                
                # 遷移モデルを更新
                current_delta = self.transition_model.get((action, key), 0.0)
                new_delta = current_delta + self.learning_rate * error
                self.transition_model[(action, key)] = new_delta
            
            # 誤差を記録
            self.error_history.append(total_error)
            
            # 最後の予測を更新
            if self.prediction_history:
                last = self.prediction_history[-1]
                last.actual_state = actual.copy()
                last.error = total_error
        
        return total_error
    
    def get_prediction_error(self) -> float:
        """
        直近の予測誤差を取得
        
        Returns:
            平均予測誤差
        """
        with self.lock:
            if not self.error_history:
                return 0.0
            
            recent = list(self.error_history)[-10:]
            return sum(recent) / len(recent)
    
    def simulate(self, state: Dict[str, float], actions: List[str]) -> List[Dict[str, float]]:
        """
        複数ステップの内部シミュレーション
        
        Args:
            state: 初期状態
            actions: 行動列
            
        Returns:
            予測される状態列
        """
        trajectory = [state.copy()]
        current = state.copy()
        
        for action in actions:
            predicted = self.predict(current, action)
            trajectory.append(predicted)
            current = predicted
        
        return trajectory
    
    def get_best_action(self, state: Dict[str, float], candidates: List[str], 
                        goal_key: str, maximize: bool = True) -> str:
        """
        目標に最適な行動を選択
        
        Args:
            state: 現在の状態
            candidates: 行動候補
            goal_key: 最適化対象の状態キー
            maximize: True=最大化, False=最小化
            
        Returns:
            最適な行動
        """
        best_action = candidates[0] if candidates else ""
        best_value = float('-inf') if maximize else float('inf')
        
        for action in candidates:
            predicted = self.predict(state, action)
            value = predicted.get(goal_key, 0.0)
            
            if maximize and value > best_value:
                best_value = value
                best_action = action
            elif not maximize and value < best_value:
                best_value = value
                best_action = action
        
        return best_action
    
    def get_state(self) -> Dict[str, Any]:
        """現在の状態を取得（デバッグ用）"""
        with self.lock:
            return {
                "transition_model_size": len(self.transition_model),
                "prediction_count": len(self.prediction_history),
                "avg_error": self.get_prediction_error()
            }
