# goal_system.py
# Phase 16: 目的の再定義 (Goal Self-Revision)
# 「目的が状態から立ち上がる」

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto


class GoalPriority(Enum):
    """目的の優先度"""
    SURVIVAL = auto()      # 生存
    HOMEOSTASIS = auto()   # 恒常性維持
    CURIOSITY = auto()     # 好奇心
    SOCIAL = auto()        # 社会的
    SELF_ACTUALIZATION = auto()  # 自己実現


@dataclass
class Goal:
    """目的を表現"""
    name: str
    priority: GoalPriority
    target_state: Dict[str, float]  # 目標状態
    current_progress: float = 0.0
    created_at: float = field(default_factory=time.time)
    active: bool = True


class GoalSystem:
    """
    目的の再定義システム
    
    目的を「命令」しない。
    内部状態から目的が「立ち上がる」。
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.lock = threading.Lock()
        
        # アクティブな目的
        self.active_goals: List[Goal] = []
        
        # 目的履歴
        self.goal_history: List[Goal] = []
        
        # 基底目的（常に存在）
        self._init_base_goals()
        
        print("🎯 Goal System Initialized.")
    
    def _init_base_goals(self):
        """基底目的を初期化"""
        self.active_goals = [
            Goal(
                name="homeostasis",
                priority=GoalPriority.HOMEOSTASIS,
                target_state={"glucose": 50.0, "cortisol": 30.0}
            ),
            Goal(
                name="curiosity",
                priority=GoalPriority.CURIOSITY,
                target_state={"boredom": 20.0, "stimulation": 40.0}
            )
        ]
    
    def emerge_goal(self, state: Dict[str, float]) -> Optional[Goal]:
        """
        内部状態から目的を生成（立ち上がる）
        
        目的は与えられるのではなく、状態から創発する。
        """
        # 空腹 → 食事目的
        glucose = state.get("glucose", 50.0)
        if glucose < 30.0:
            goal = Goal(
                name="seek_food",
                priority=GoalPriority.SURVIVAL,
                target_state={"glucose": 60.0}
            )
            self._add_goal(goal)
            return goal
        
        # 退屈 → 探索目的
        boredom = state.get("boredom", 0.0)
        if boredom > 70.0:
            goal = Goal(
                name="explore",
                priority=GoalPriority.CURIOSITY,
                target_state={"boredom": 30.0, "stimulation": 50.0}
            )
            self._add_goal(goal)
            return goal
        
        # ストレス → 回避目的
        cortisol = state.get("cortisol", 30.0)
        if cortisol > 70.0:
            goal = Goal(
                name="reduce_stress",
                priority=GoalPriority.HOMEOSTASIS,
                target_state={"cortisol": 40.0}
            )
            self._add_goal(goal)
            return goal
        
        return None
    
    def _add_goal(self, goal: Goal):
        """目的を追加（重複チェック付き）"""
        with self.lock:
            # 同名の目的が既にあれば追加しない
            if not any(g.name == goal.name for g in self.active_goals):
                self.active_goals.append(goal)
    
    def update_progress(self, goal_name: str, state: Dict[str, float]) -> float:
        """目的の進捗を更新"""
        with self.lock:
            for goal in self.active_goals:
                if goal.name == goal_name:
                    # 目標状態との距離を計算
                    total_dist = 0.0
                    for key, target in goal.target_state.items():
                        current = state.get(key, 0.0)
                        total_dist += abs(target - current)
                    
                    # 進捗 = 1 - 正規化距離
                    max_dist = len(goal.target_state) * 100
                    goal.current_progress = max(0.0, 1.0 - total_dist / max_dist)
                    
                    return goal.current_progress
        return 0.0
    
    def complete_goal(self, goal_name: str):
        """目的を完了"""
        with self.lock:
            for goal in self.active_goals:
                if goal.name == goal_name:
                    goal.active = False
                    self.goal_history.append(goal)
                    self.active_goals.remove(goal)
                    break
    
    def get_highest_priority_goal(self) -> Optional[Goal]:
        """最も優先度の高い目的を取得"""
        with self.lock:
            if not self.active_goals:
                return None
            return min(self.active_goals, key=lambda g: g.priority.value)
    
    def get_state(self) -> Dict[str, Any]:
        """状態を取得"""
        return {
            "active_goals": [g.name for g in self.active_goals],
            "history_count": len(self.goal_history)
        }
