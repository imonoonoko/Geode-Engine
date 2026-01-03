# conserved_quantities.py
# Phase 22: 保存量の追跡 (Conserved Quantities)
# 意味生成能力、自己参照密度、世界記述多様性

import time
import threading
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class QuantitySnapshot:
    """保存量のスナップショット"""
    meaning_capacity: float
    self_reference_density: float
    world_description_diversity: float
    timestamp: float = field(default_factory=time.time)


class ConservedQuantities:
    """
    保存量の追跡システム
    
    人格の核として保存されるべき量:
    - 意味生成能力
    - 自己参照密度
    - 世界記述多様性
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.lock = threading.Lock()
        
        # 現在の保存量
        self.meaning_capacity = 1.0
        self.self_reference_density = 1.0
        self.world_description_diversity = 0.5
        
        # 履歴
        self.history: List[QuantitySnapshot] = []
        
        # 変動の許容範囲
        self.tolerance = 0.2
        
        print("📊 Conserved Quantities Initialized.")
    
    def update(self, evaluations: List[Any] = None,
              predictions: List[Any] = None,
              vocabulary: set = None):
        """保存量を更新"""
        with self.lock:
            # 意味生成能力: 意味を見出せた割合
            if evaluations:
                meaningful = sum(1 for e in evaluations 
                               if getattr(e, 'overall_meaning', 0) > 0.5)
                self.meaning_capacity = meaningful / len(evaluations)
            
            # 自己参照密度: 予測の精度
            if predictions:
                accurate = sum(1 for p in predictions 
                             if getattr(p, 'error', 1) < 0.3)
                self.self_reference_density = accurate / len(predictions)
            
            # 世界記述多様性: 使用語彙の多様性
            if vocabulary:
                self.world_description_diversity = min(1.0, len(vocabulary) / 100)
            
            # スナップショットを保存
            self.history.append(QuantitySnapshot(
                meaning_capacity=self.meaning_capacity,
                self_reference_density=self.self_reference_density,
                world_description_diversity=self.world_description_diversity
            ))
            
            # 最大100件
            if len(self.history) > 100:
                self.history = self.history[-100:]
    
    def check_stability(self) -> Dict[str, bool]:
        """保存量の安定性をチェック"""
        if len(self.history) < 2:
            return {"stable": True, "details": {}}
        
        latest = self.history[-1]
        previous = self.history[-2]
        
        stability = {
            "meaning": abs(latest.meaning_capacity - previous.meaning_capacity) < self.tolerance,
            "self_ref": abs(latest.self_reference_density - previous.self_reference_density) < self.tolerance,
            "diversity": abs(latest.world_description_diversity - previous.world_description_diversity) < self.tolerance,
        }
        
        return {
            "stable": all(stability.values()),
            "details": stability
        }
    
    def detect_core_change(self) -> bool:
        """核心的変化を検出"""
        if len(self.history) < 10:
            return False
        
        recent = self.history[-5:]
        earlier = self.history[-10:-5]
        
        # 平均を比較
        recent_avg = sum(s.meaning_capacity for s in recent) / 5
        earlier_avg = sum(s.meaning_capacity for s in earlier) / 5
        
        return abs(recent_avg - earlier_avg) > self.tolerance * 2
    
    def get_state(self) -> Dict[str, Any]:
        """状態を取得"""
        return {
            "meaning_capacity": round(self.meaning_capacity, 3),
            "self_reference_density": round(self.self_reference_density, 3),
            "world_description_diversity": round(self.world_description_diversity, 3),
            "stable": self.check_stability()["stable"]
        }
