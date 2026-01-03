# dreaming.py
# Phase 19: 睡眠中の記憶圧縮 (Dreaming)
# 睡眠中に記憶を再構成・統合

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import random


@dataclass
class DreamFragment:
    """夢の断片"""
    content: str
    source_memories: List[str]
    emotional_tone: float
    timestamp: float = field(default_factory=time.time)


class DreamProcessor:
    """
    睡眠中の記憶圧縮システム
    
    - 類似記憶の統合・圧縮
    - 感情的に重要な記憶の強化
    - 不要な記憶の忘却
    - 翌日の状態初期化
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.lock = threading.Lock()
        
        # 夢の履歴
        self.dreams: List[DreamFragment] = []
        
        # 圧縮された記憶
        self.compressed_memories: Dict[str, List[str]] = defaultdict(list)
        
        # 処理パラメータ
        self.compression_ratio = 0.7  # 70%に圧縮
        self.forgetting_threshold = 0.2  # 重要度がこれ以下は忘却
        
        print("💤 Dream Processor Initialized.")
    
    def process_sleep(self, memories: List[Dict[str, Any]], 
                     emotion_state: Dict[str, float]) -> Dict[str, Any]:
        """
        睡眠処理を実行
        
        Args:
            memories: 処理対象の記憶リスト
            emotion_state: 現在の感情状態
            
        Returns:
            処理結果（圧縮数、忘却数、夢の内容）
        """
        results = {
            "compressed": 0,
            "forgotten": 0,
            "dream_generated": False,
            "dream_content": None
        }
        
        if not memories:
            return results
        
        with self.lock:
            # 1. 重要度でソート
            scored_memories = self._score_memories(memories, emotion_state)
            
            # 2. 低重要度の記憶を忘却
            retained = []
            for mem, score in scored_memories:
                if score > self.forgetting_threshold:
                    retained.append((mem, score))
                else:
                    results["forgotten"] += 1
            
            # 3. 類似記憶を圧縮
            compressed = self._compress_similar(retained)
            results["compressed"] = len(retained) - len(compressed)
            
            # 4. 夢を生成
            dream = self._generate_dream(compressed, emotion_state)
            if dream:
                self.dreams.append(dream)
                results["dream_generated"] = True
                results["dream_content"] = dream.content
        
        return results
    
    def _score_memories(self, memories: List[Dict], 
                       emotion: Dict[str, float]) -> List[tuple]:
        """記憶に重要度スコアを付与"""
        scored = []
        
        for mem in memories:
            # 基本スコア
            score = 0.5
            
            # 感情的重要度
            valence = mem.get("valence", 0)
            score += abs(valence) * 0.3
            
            # 新しさ
            age = time.time() - mem.get("timestamp", time.time())
            recency = max(0, 1 - age / 86400)  # 24時間で減衰
            score += recency * 0.2
            
            # 繰り返し
            count = mem.get("access_count", 1)
            score += min(0.3, count * 0.05)
            
            scored.append((mem, min(1.0, score)))
        
        return scored
    
    def _compress_similar(self, memories: List[tuple]) -> List[Dict]:
        """類似記憶を圧縮"""
        if not memories:
            return []
        
        # 簡易的な圧縮（同じキーワードを持つ記憶を統合）
        clusters = defaultdict(list)
        
        for mem, score in memories:
            key = mem.get("category", "general")
            clusters[key].append((mem, score))
        
        compressed = []
        for key, mems in clusters.items():
            if len(mems) <= 2:
                compressed.extend([m for m, s in mems])
            else:
                # 上位のみ保持
                mems.sort(key=lambda x: x[1], reverse=True)
                keep = max(1, int(len(mems) * self.compression_ratio))
                compressed.extend([m for m, s in mems[:keep]])
        
        return compressed
    
    def _generate_dream(self, memories: List[Dict], 
                       emotion: Dict[str, float]) -> Optional[DreamFragment]:
        """夢を生成"""
        if not memories:
            return None
        
        # ランダムに記憶を選択して組み合わせ
        sample_size = min(3, len(memories))
        selected = random.sample(memories, sample_size)
        
        # 内容を抽出
        contents = [m.get("content", str(m))[:50] for m in selected]
        
        # 感情トーンを計算
        avg_valence = sum(m.get("valence", 0) for m in selected) / len(selected)
        
        dream = DreamFragment(
            content="...".join(contents),
            source_memories=[str(m.get("id", ""))[:10] for m in selected],
            emotional_tone=avg_valence
        )
        
        return dream
    
    def get_recent_dreams(self, count: int = 5) -> List[DreamFragment]:
        """最近の夢を取得"""
        with self.lock:
            return list(self.dreams[-count:])
    
    def reset_for_morning(self) -> Dict[str, float]:
        """
        朝の状態初期化
        
        睡眠で回復した状態を返す
        """
        return {
            "cortisol": 30.0,  # ストレス低下
            "serotonin": 60.0,  # 安定
            "glucose": 45.0,  # やや空腹
            "boredom": 20.0,  # 低退屈
        }
    
    def get_state(self) -> Dict[str, Any]:
        """状態を取得"""
        return {
            "dream_count": len(self.dreams),
            "last_dream": self.dreams[-1].content[:30] if self.dreams else None
        }
