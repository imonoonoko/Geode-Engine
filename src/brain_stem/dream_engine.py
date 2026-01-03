# dream_engine.py
"""
Phase 15.3: Dream Engine Module
睡眠と自律思考の責務を担う。

責務:
- 睡眠中の記憶整理
- 自律思考（衝動・独り言）
- 記憶の圧縮と統合

設計原則:
- 状態を持たない（計算のみ）
- 依存性注入（DI）
"""

import random
import time

from src.body.hormones import Hormone


class DreamEngine:
    """
    夢エンジン: 睡眠中の記憶処理と自律思考を担当。
    """
    
    def __init__(self, hormones, memory, cortex=None, soliloquy=None):
        """
        Args:
            hormones: HormoneManager インスタンス
            memory: GeologicalMemory インスタンス
            cortex: SedimentaryCortex インスタンス (記憶整理用)
            soliloquy: SoliloquyManager インスタンス (独り言生成)
        """
        self.hormones = hormones
        self.memory = memory
        self.cortex = cortex
        self.soliloquy = soliloquy
        
        print("💤 DreamEngine Initialized (Phase 15.3)")
    
    def process_dream(self):
        """
        睡眠中の記憶整理処理。
        記憶の圧縮、統合、忘却を行う。
        """
        try:
            print("💤 [Dream] Memory consolidation starting...")
            
            # 1. 記憶の圧縮 (SedimentaryCortex delegation)
            if self.cortex and hasattr(self.cortex, 'compress_memory'):
                self.cortex.compress_memory()
            
            # 2. 感情リセット（睡眠によるリフレッシュ）
            self.hormones.update(Hormone.CORTISOL, -10.0)
            self.hormones.update(Hormone.BOREDOM, -20.0)
            self.hormones.update(Hormone.SEROTONIN, 5.0)
            
            # 3. 夢の内容をログ（ランダムな概念を選択）
            if hasattr(self.memory, 'concepts') and self.memory.concepts:
                dream_concepts = random.sample(
                    list(self.memory.concepts.keys()),
                    min(3, len(self.memory.concepts))
                )
                print(f"💭 [Dream] Dreaming of: {', '.join(dream_concepts)}")
            
            print("💤 [Dream] Consolidation complete.")
            
        except Exception as e:
            print(f"⚠️ [DreamEngine] Error: {e}")
    
    def process_autonomous_thought(self, heart_rate: float = 60.0) -> dict:
        """
        自律思考（衝動）の処理。
        
        Args:
            heart_rate: 心拍数（活動レベルの指標）
            
        Returns:
            {"impulse": str, "valence": float} または None
        """
        try:
            # 刺激レベルに基づく思考確率
            stim = self.hormones.get(Hormone.STIMULATION)
            boredom = self.hormones.get(Hormone.BOREDOM)
            
            # 退屈度が高いほど思考しやすい
            thought_chance = 0.1 + (boredom / 100.0) * 0.3
            
            if random.random() > thought_chance:
                return None
            
            # 独り言生成
            if self.soliloquy and hasattr(self.soliloquy, 'generate_impulse'):
                impulse = self.soliloquy.generate_impulse()
                if impulse:
                    # 思考で退屈を解消
                    self.hormones.update(Hormone.BOREDOM, -5.0)
                    self.hormones.update(Hormone.STIMULATION, 10.0)
                    return impulse
            
            # Fallback: ランダムな記憶から思考
            if hasattr(self.memory, 'concepts') and self.memory.concepts:
                concept = random.choice(list(self.memory.concepts.keys()))
                valence = random.uniform(-0.3, 0.3)
                return {"impulse": concept, "valence": valence}
            
            return None
            
        except Exception as e:
            print(f"⚠️ [DreamEngine] Thought Error: {e}")
            return None
