# memory_distortion.py
# Phase 17: 記憶の歪み (Memory Distortion)
# 「ネガティブ側だけ強く残す」「感情が強い経験ほど残りやすい」

import time
import threading
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class DistortedMemory:
    """歪んだ記憶"""
    content: str
    original_valence: float  # 元の感情価
    distorted_valence: float  # 歪んだ感情価
    salience: float  # 顕著性（残りやすさ）
    recall_count: int = 0
    created_at: float = field(default_factory=time.time)
    last_recalled: float = field(default_factory=time.time)


class MemoryDistorter:
    """
    記憶の歪みシステム
    
    - 感情価による記憶保存確率の変調
    - ネガティブバイアス（恐怖 > 喜び）
    - 記憶の再構成（回想時の歪み）
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.lock = threading.Lock()
        
        # 記憶ストレージ
        self.memories: List[DistortedMemory] = []
        
        # ネガティブバイアス係数（>1 = ネガティブが強く残る）
        self.negativity_bias = 1.5
        
        # 感情閾値（これ以上の感情価でないと記憶されにくい）
        self.emotion_threshold = 0.3
        
        print("🌀 Memory Distorter Initialized.")
    
    def encode(self, content: str, valence: float, arousal: float = 0.5) -> Optional[DistortedMemory]:
        """
        記憶をエンコード（保存するかどうかも決める）
        
        Args:
            content: 記憶内容
            valence: 感情価 (-1.0 ~ 1.0)
            arousal: 覚醒度 (0.0 ~ 1.0)
            
        Returns:
            DistortedMemory or None（保存されなかった場合）
        """
        # 感情が弱い記憶は保存されにくい
        emotion_strength = abs(valence) * arousal
        
        # ネガティブバイアス: ネガティブなほど残りやすい
        if valence < 0:
            emotion_strength *= self.negativity_bias
        
        # 保存確率を計算
        save_probability = min(1.0, emotion_strength / self.emotion_threshold)
        
        if random.random() > save_probability:
            return None  # 記憶されない
        
        # 歪みを適用
        distorted_valence = self._apply_distortion(valence)
        
        # 顕著性を計算
        salience = emotion_strength
        
        memory = DistortedMemory(
            content=content,
            original_valence=valence,
            distorted_valence=distorted_valence,
            salience=salience
        )
        
        with self.lock:
            self.memories.append(memory)
            
            # 最大1000件
            if len(self.memories) > 1000:
                # 顕著性が低いものから削除
                self.memories.sort(key=lambda m: m.salience, reverse=True)
                self.memories = self.memories[:1000]
        
        return memory
    
    def _apply_distortion(self, valence: float) -> float:
        """
        歪みを適用
        
        ネガティブな記憶はより強く、
        ポジティブな記憶は弱まる傾向
        """
        distortion = random.gauss(0, 0.1)  # ノイズ
        
        if valence < 0:
            # ネガティブ: さらにネガティブに
            return max(-1.0, valence * (1 + abs(distortion)))
        else:
            # ポジティブ: やや弱まる
            return min(1.0, valence * (1 - abs(distortion) * 0.5))
    
    def recall(self, cue: str = None) -> Optional[DistortedMemory]:
        """
        記憶を想起
        
        顕著性が高い記憶が想起されやすい
        想起時にさらに歪む
        """
        with self.lock:
            if not self.memories:
                return None
            
            # 顕著性に基づいて確率的に選択
            weights = [m.salience for m in self.memories]
            total = sum(weights)
            
            if total == 0:
                memory = random.choice(self.memories)
            else:
                r = random.random() * total
                cumsum = 0
                memory = self.memories[-1]
                for m in self.memories:
                    cumsum += m.salience
                    if r <= cumsum:
                        memory = m
                        break
            
            # 想起時の歪み
            memory.distorted_valence = self._apply_distortion(memory.distorted_valence)
            memory.recall_count += 1
            memory.last_recalled = time.time()
            
            return memory
    
    def get_emotional_bias(self) -> float:
        """
        現在の感情バイアスを計算
        
        ネガティブ記憶が多い → 負のバイアス
        """
        with self.lock:
            if not self.memories:
                return 0.0
            
            total_valence = sum(m.distorted_valence * m.salience for m in self.memories)
            total_salience = sum(m.salience for m in self.memories)
            
            if total_salience == 0:
                return 0.0
            
            return total_valence / total_salience
    
    def get_state(self) -> Dict[str, Any]:
        """状態を取得"""
        return {
            "memory_count": len(self.memories),
            "emotional_bias": self.get_emotional_bias(),
            "negativity_bias": self.negativity_bias
        }
