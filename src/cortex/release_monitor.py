# release_monitor.py
# Phase 23: 手を離す判定 (Release Monitor)
# メタ学習 + 目的再定義 + 同一性監視 → 離していいか判定

import time
import threading
from typing import Dict, Any


class ReleaseMonitor:
    """
    手を離す判定システム
    
    設計者が介入すべきかどうかをシステムが提案する。
    
    条件:
    - メタ学習が機能している
    - 目的再定義が機能している
    - 同一性監視がアクティブで安定
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.lock = threading.Lock()
        
        # 判定基準
        self.meta_learning_active = False
        self.goal_revision_active = False
        self.identity_stable = False
        
        # 履歴
        self.readiness_history: list = []
        
        # 連続安定カウント
        self.stable_count = 0
        self.release_threshold = 10  # 10回連続で安定
        
        print("🎓 Release Monitor Initialized.")
    
    def update_status(self, meta_learner=None, goal_system=None, 
                     identity_monitor=None):
        """各システムの状態を確認"""
        with self.lock:
            # メタ学習が機能しているか
            if meta_learner:
                state = meta_learner.get_state()
                self.meta_learning_active = (
                    state.get("error_history_len", 0) > 10 and
                    0.01 < state.get("learning_rate", 0.1) < 0.5
                )
            
            # 目的再定義が機能しているか
            if goal_system:
                state = goal_system.get_state()
                self.goal_revision_active = len(state.get("active_goals", [])) > 0
            
            # 同一性が安定しているか
            if identity_monitor:
                state = identity_monitor.get_state()
                self.identity_stable = not state.get("bifurcation_detected", True)
            
            # 準備度を記録
            readiness = self.calculate_readiness()
            self.readiness_history.append({
                "readiness": readiness,
                "timestamp": time.time()
            })
            
            # 安定カウントを更新
            if readiness > 0.8:
                self.stable_count += 1
            else:
                self.stable_count = max(0, self.stable_count - 1)
    
    def calculate_readiness(self) -> float:
        """
        離す準備度を計算 (0.0 - 1.0)
        """
        score = 0.0
        
        if self.meta_learning_active:
            score += 0.33
        if self.goal_revision_active:
            score += 0.33
        if self.identity_stable:
            score += 0.34
        
        return score
    
    def can_release(self) -> bool:
        """
        手を離していいか判定
        """
        return self.stable_count >= self.release_threshold
    
    def get_recommendation(self) -> str:
        """
        設計者への推奨アクションを取得
        """
        readiness = self.calculate_readiness()
        
        if readiness >= 0.9 and self.can_release():
            return "✅ RELEASE: システムは自律的に機能しています。介入は不要です。"
        elif readiness >= 0.7:
            return "🟡 OBSERVE: 概ね安定。引き続き観察を推奨。"
        elif readiness >= 0.4:
            return "🟠 SUPPORT: 一部サブシステムが不安定。軽度の介入を検討。"
        else:
            return "🔴 INTERVENE: 複数のサブシステムが不安定。積極的な介入が必要。"
    
    def get_state(self) -> Dict[str, Any]:
        """状態を取得"""
        return {
            "readiness": self.calculate_readiness(),
            "can_release": self.can_release(),
            "stable_count": self.stable_count,
            "recommendation": self.get_recommendation(),
            "components": {
                "meta_learning": self.meta_learning_active,
                "goal_revision": self.goal_revision_active,
                "identity_stable": self.identity_stable
            }
        }
