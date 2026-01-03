# identity_monitor.py
# Phase 15: 自己同一性モニター (Identity Monitor)
# 「自己モデルが自分の将来を予測できなくなった瞬間に分岐が起きる」

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import deque
import math


@dataclass
class IdentitySnapshot:
    """自己状態のスナップショット"""
    state: Dict[str, float]
    predicted_next: Optional[Dict[str, float]] = None
    prediction_error: float = 0.0
    timestamp: float = field(default_factory=time.time)


class IdentityMonitor:
    """
    自己同一性モニター
    
    - 自己状態の予測: P(self(t+Δ) | self(t))
    - 予測不能性の検出（カオス判定）
    - 分岐アラートの発行
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.lock = threading.Lock()
        
        # 自己状態の履歴
        self.state_history: deque = deque(maxlen=100)
        
        # 予測誤差の履歴
        self.error_history: deque = deque(maxlen=50)
        
        # 予測不能性の閾値
        self.unpredictability_threshold = 0.5
        
        # 分岐検出フラグ
        self.bifurcation_detected = False
        self.bifurcation_timestamp = None
        
        # 自己参照密度（自己モデルの精度）
        self.self_reference_density = 1.0
        
        print("🪞 Identity Monitor Initialized.")
    
    def capture_state(self, state: Dict[str, float]) -> IdentitySnapshot:
        """
        現在の自己状態をキャプチャ
        """
        snapshot = IdentitySnapshot(state=state.copy())
        
        with self.lock:
            self.state_history.append(snapshot)
        
        return snapshot
    
    def predict_self(self, current_state: Dict[str, float]) -> Dict[str, float]:
        """
        自己状態の予測: P(self(t+Δ) | self(t))
        
        過去の履歴から傾向を推定し、次の状態を予測
        """
        predicted = {}
        
        with self.lock:
            if len(self.state_history) < 2:
                return current_state.copy()
            
            # 直近2つの状態から変化率を計算
            recent = list(self.state_history)[-2:]
            prev_state = recent[0].state
            
            for key, value in current_state.items():
                if key in prev_state:
                    # 変化率を継続
                    delta = value - prev_state.get(key, value)
                    predicted[key] = value + delta * 0.5  # 慣性を考慮
                else:
                    predicted[key] = value
        
        return predicted
    
    def check_identity_consistency(self) -> bool:
        """
        自己同一性の一貫性をチェック
        
        Returns:
            True: 一貫性あり（同一人格）
            False: 一貫性なし（分岐の可能性）
        """
        unpredictability = self.detect_unpredictability()
        
        if unpredictability > self.unpredictability_threshold:
            self._trigger_bifurcation_alert(unpredictability)
            return False
        
        return True
    
    def detect_unpredictability(self) -> float:
        """
        予測不能性を検出
        
        予測誤差の増加傾向と分散から判定
        
        Returns:
            予測不能性スコア (0.0 - 1.0)
        """
        with self.lock:
            if len(self.error_history) < 5:
                return 0.0
            
            errors = list(self.error_history)
            
            # 平均誤差
            avg_error = sum(errors) / len(errors)
            
            # 分散
            variance = sum((e - avg_error) ** 2 for e in errors) / len(errors)
            
            # 増加傾向
            first_half = errors[:len(errors)//2]
            second_half = errors[len(errors)//2:]
            trend = (sum(second_half)/len(second_half)) - (sum(first_half)/len(first_half))
            
            # 予測不能性スコア
            unpredictability = min(1.0, (avg_error + math.sqrt(variance) + max(0, trend)) / 3)
            
            return unpredictability
    
    def update(self, actual_state: Dict[str, float]) -> float:
        """
        実際の状態で更新し、予測誤差を計算
        
        Returns:
            予測誤差
        """
        with self.lock:
            if len(self.state_history) < 2:
                self.capture_state(actual_state)
                return 0.0
            
            # 最後の予測と比較
            last = self.state_history[-1]
            if last.predicted_next is None:
                last.predicted_next = self.predict_self(last.state)
            
            # 予測誤差を計算
            error = 0.0
            for key in last.predicted_next:
                if key in actual_state:
                    error += abs(last.predicted_next[key] - actual_state[key])
            
            last.prediction_error = error
            self.error_history.append(error)
            
            # 自己参照密度を更新
            self.self_reference_density = max(0.1, 1.0 - error / 100)
        
        # 新しい状態をキャプチャ
        self.capture_state(actual_state)
        
        # 一貫性チェック
        self.check_identity_consistency()
        
        return error
    
    def _trigger_bifurcation_alert(self, unpredictability: float):
        """分岐アラートを発行"""
        if not self.bifurcation_detected:
            self.bifurcation_detected = True
            self.bifurcation_timestamp = time.time()
            print(f"⚠️ [IDENTITY ALERT] Unpredictability={unpredictability:.3f}")
            print("   自己予測不能性が閾値を超過。人格分岐の可能性。")
    
    def reset_bifurcation_flag(self):
        """分岐フラグをリセット"""
        self.bifurcation_detected = False
        self.bifurcation_timestamp = None
    
    def get_state(self) -> Dict[str, Any]:
        """現在の状態を取得（デバッグ用）"""
        return {
            "history_len": len(self.state_history),
            "avg_error": sum(self.error_history) / len(self.error_history) if self.error_history else 0,
            "unpredictability": self.detect_unpredictability(),
            "bifurcation_detected": self.bifurcation_detected,
            "self_reference_density": self.self_reference_density
        }
