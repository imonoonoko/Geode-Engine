# personality_field.py
# Phase 6: 人格系 (Personality Field)
# Ψ = { P₁, P₂, ..., Pn }

import numpy as np
import time
import json
import os
from typing import Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class PersonalitySnapshot:
    """人格のスナップショット"""
    id: str
    timestamp: float
    state_vector: np.ndarray  # ESN状態ベクトル
    hormone_levels: Dict[str, float]
    surprise_mean: float
    surprise_variance: float
    
    # 保存量
    meaning_generation: float  # 意味生成能力
    self_reference_density: float  # 自己参照密度
    world_description_diversity: float  # 世界記述多様性


class PersonalityField:
    """
    Phase 6: 人格系の管理
    
    人格は粒子
    相互作用する
    融合も分裂もする
    """
    
    def __init__(self, save_dir: str = "memory_data"):
        self.personalities: Dict[str, PersonalitySnapshot] = {}
        self.interaction_log = []
        self.save_dir = save_dir
        self.log_path = os.path.join(save_dir, "personality_field.json")
        
        os.makedirs(save_dir, exist_ok=True)
        self._load()
        
        print("🧬 Personality Field Initialized.")
    
    def _load(self):
        """保存された人格系を読み込み"""
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.interaction_log = data.get("interaction_log", [])
                    # PersonalitySnapshot は numpy を含むため別途ロード
            except Exception as e:
                print(f"⚠️ Personality Field Load Error: {e}")
    
    def _save(self):
        """人格系を保存"""
        try:
            data = {
                "interaction_log": self.interaction_log[-100:],  # 最新100件
                "personality_count": len(self.personalities)
            }
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Personality Field Save Error: {e}")
    
    def snapshot_personality(self, brain) -> str:
        """
        現在の人格をスナップショット
        
        Returns: 人格ID
        """
        p_id = f"P_{time.time():.6f}"
        
        try:
            # ESN状態ベクトル
            state_vector = brain.prediction_engine.state_vector.copy()
            
            # ホルモンレベル
            hormone_levels = brain.hormones.as_dict()
            
            # サプライズ統計
            surprise_history = list(brain.prediction_engine.surprise_history)
            surprise_mean = np.mean(surprise_history) if surprise_history else 0.0
            surprise_variance = np.var(surprise_history) if surprise_history else 0.0
            
            # 保存量の計算
            meaning_gen = self._calc_meaning_generation(brain)
            self_ref = self._calc_self_reference_density(brain)
            world_div = self._calc_world_description_diversity(brain)
            
            snapshot = PersonalitySnapshot(
                id=p_id,
                timestamp=time.time(),
                state_vector=state_vector,
                hormone_levels=hormone_levels,
                surprise_mean=float(surprise_mean),
                surprise_variance=float(surprise_variance),
                meaning_generation=meaning_gen,
                self_reference_density=self_ref,
                world_description_diversity=world_div
            )
            
            self.personalities[p_id] = snapshot
            
            # ログ記録
            self.interaction_log.append({
                "type": "snapshot",
                "id": p_id,
                "timestamp": time.time(),
                "conserved": {
                    "meaning": meaning_gen,
                    "self_ref": self_ref,
                    "diversity": world_div
                }
            })
            
            self._save()
            
            print(f"📸 Personality Snapshot: {p_id}")
            print(f"   Meaning={meaning_gen:.3f}, SelfRef={self_ref:.3f}, Diversity={world_div:.3f}")
            
            return p_id
            
        except Exception as e:
            print(f"⚠️ Snapshot Error: {e}")
            return ""
    
    def _calc_meaning_generation(self, brain) -> float:
        """意味生成能力を計算"""
        try:
            # brain_graph のエッジ数 × 平均重み
            graph = brain.cortex.stomach.brain_graph
            if not graph.edges():
                return 0.0
            
            edge_count = len(graph.edges())
            avg_weight = np.mean([d.get('weight', 1.0) for _, _, d in graph.edges(data=True)])
            
            # 正規化（0-1）
            return min(1.0, (edge_count * avg_weight) / 1000.0)
        except:
            return 0.0
    
    def _calc_self_reference_density(self, brain) -> float:
        """自己参照密度を計算"""
        try:
            # ESN状態ベクトルの自己相関
            state = brain.prediction_engine.state_vector
            norm = np.linalg.norm(state)
            if norm == 0:
                return 0.0
            
            # 状態ベクトルの非ゼロ要素の割合
            non_zero = np.count_nonzero(state) / len(state)
            
            return float(non_zero)
        except:
            return 0.0
    
    def _calc_world_description_diversity(self, brain) -> float:
        """世界記述多様性を計算"""
        try:
            # 概念の多様性（ユニークな概念数）
            concepts = brain.memory.get_all_concepts()
            unique_count = len(concepts)
            
            # 正規化（0-1）
            return min(1.0, unique_count / 100.0)
        except:
            return 0.0
    
    def detect_bifurcation(self, p1_id: str, p2_id: str) -> dict:
        """
        2つの人格間の距離を計算
        分岐検出に使用
        """
        if p1_id not in self.personalities or p2_id not in self.personalities:
            return {"error": "Personality not found"}
        
        p1 = self.personalities[p1_id]
        p2 = self.personalities[p2_id]
        
        # 1. 状態ベクトル距離
        state_dist = np.linalg.norm(p1.state_vector - p2.state_vector)
        
        # 2. ホルモン距離
        hormone_dist = 0.0
        for key in p1.hormone_levels:
            h1 = p1.hormone_levels.get(key, 50.0)
            h2 = p2.hormone_levels.get(key, 50.0)
            hormone_dist += (h1 - h2) ** 2
        hormone_dist = np.sqrt(hormone_dist)
        
        # 3. 保存量の差
        meaning_diff = abs(p1.meaning_generation - p2.meaning_generation)
        self_ref_diff = abs(p1.self_reference_density - p2.self_reference_density)
        diversity_diff = abs(p1.world_description_diversity - p2.world_description_diversity)
        
        # 4. 総合距離
        total_dist = state_dist * 0.5 + hormone_dist * 0.01 + \
                     (meaning_diff + self_ref_diff + diversity_diff) * 100
        
        # 5. 分岐判定
        is_bifurcated = total_dist > 10.0  # 閾値
        
        result = {
            "p1": p1_id,
            "p2": p2_id,
            "state_distance": float(state_dist),
            "hormone_distance": float(hormone_dist),
            "conserved_diff": {
                "meaning": meaning_diff,
                "self_ref": self_ref_diff,
                "diversity": diversity_diff
            },
            "total_distance": float(total_dist),
            "is_bifurcated": is_bifurcated
        }
        
        if is_bifurcated:
            print(f"⚠️ [BIFURCATION DETECTED] {p1_id} ↔ {p2_id}")
            print(f"   Total Distance: {total_dist:.2f}")
        
        return result
    
    def get_conserved_quantities(self, p_id: str) -> dict:
        """保存量を取得"""
        if p_id not in self.personalities:
            return {"error": "Personality not found"}
        
        p = self.personalities[p_id]
        return {
            "id": p.id,
            "meaning_generation": p.meaning_generation,
            "self_reference_density": p.self_reference_density,
            "world_description_diversity": p.world_description_diversity
        }
