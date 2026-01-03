# personality_system.py
# Phase 20: 人格系 (Personality System)
# Ψ = {P₁, P₂, ...} 複数人格の共存・競合

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto


class PersonalityMode(Enum):
    """人格モード"""
    CALM = auto()      # 穏やか
    CURIOUS = auto()   # 好奇心旺盛
    ANXIOUS = auto()   # 不安
    PLAYFUL = auto()   # 遊び心
    FOCUSED = auto()   # 集中


@dataclass
class Personality:
    """個別人格"""
    mode: PersonalityMode
    activation: float  # 活性度 (0-1)
    traits: Dict[str, float]  # 特性
    last_active: float = field(default_factory=time.time)


class PersonalitySystem:
    """
    人格系システム
    
    Ψ = {P₁, P₂, ...}
    人格を個体ではなく粒子として扱う。
    状況によって異なる「自分」が表出する。
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.lock = threading.Lock()
        
        # 人格の集合
        self.personalities: Dict[PersonalityMode, Personality] = {}
        self._init_personalities()
        
        # 現在の優勢人格
        self.dominant: PersonalityMode = PersonalityMode.CALM
        
        # 人格切り替えの慣性
        self.switch_threshold = 0.3
        
        print("👥 Personality System Initialized.")
    
    def _init_personalities(self):
        """人格を初期化"""
        self.personalities = {
            PersonalityMode.CALM: Personality(
                mode=PersonalityMode.CALM,
                activation=0.5,
                traits={"serotonin_affinity": 0.8, "risk_tolerance": 0.3}
            ),
            PersonalityMode.CURIOUS: Personality(
                mode=PersonalityMode.CURIOUS,
                activation=0.3,
                traits={"dopamine_affinity": 0.7, "exploration_drive": 0.9}
            ),
            PersonalityMode.ANXIOUS: Personality(
                mode=PersonalityMode.ANXIOUS,
                activation=0.2,
                traits={"cortisol_sensitivity": 0.9, "caution": 0.8}
            ),
            PersonalityMode.PLAYFUL: Personality(
                mode=PersonalityMode.PLAYFUL,
                activation=0.2,
                traits={"dopamine_affinity": 0.9, "spontaneity": 0.8}
            ),
            PersonalityMode.FOCUSED: Personality(
                mode=PersonalityMode.FOCUSED,
                activation=0.2,
                traits={"attention_span": 0.9, "distraction_resist": 0.7}
            ),
        }
    
    def update(self, hormones: Dict[str, float]) -> PersonalityMode:
        """
        ホルモン状態に基づいて人格活性度を更新
        
        Returns:
            現在の優勢人格
        """
        with self.lock:
            # 各人格の活性度を更新
            dopamine = hormones.get("dopamine", 50)
            serotonin = hormones.get("serotonin", 50)
            cortisol = hormones.get("cortisol", 30)
            adrenaline = hormones.get("adrenaline", 20)
            
            # CALM: セロトニン高、ストレス低
            self.personalities[PersonalityMode.CALM].activation = (
                serotonin / 100 * 0.6 + (100 - cortisol) / 100 * 0.4
            )
            
            # CURIOUS: ドーパミン中〜高
            self.personalities[PersonalityMode.CURIOUS].activation = (
                dopamine / 100 * 0.7 + (100 - cortisol) / 100 * 0.3
            )
            
            # ANXIOUS: コルチゾール高
            self.personalities[PersonalityMode.ANXIOUS].activation = (
                cortisol / 100 * 0.8 + adrenaline / 100 * 0.2
            )
            
            # PLAYFUL: ドーパミン高、ストレス低
            self.personalities[PersonalityMode.PLAYFUL].activation = (
                dopamine / 100 * 0.5 + (100 - cortisol) / 100 * 0.5
            )
            
            # FOCUSED: セロトニン中、刺激低
            stimulation = hormones.get("stimulation", 30)
            self.personalities[PersonalityMode.FOCUSED].activation = (
                serotonin / 100 * 0.4 + (100 - stimulation) / 100 * 0.6
            )
            
            # 優勢人格を決定
            new_dominant = max(
                self.personalities.values(),
                key=lambda p: p.activation
            ).mode
            
            # 切り替え閾値を超えた場合のみ変更
            current_activation = self.personalities[self.dominant].activation
            new_activation = self.personalities[new_dominant].activation
            
            if new_activation - current_activation > self.switch_threshold:
                self.dominant = new_dominant
                self.personalities[new_dominant].last_active = time.time()
            
            return self.dominant
    
    def get_dominant(self) -> Personality:
        """優勢人格を取得"""
        return self.personalities[self.dominant]
    
    def get_behavior_modifier(self) -> Dict[str, float]:
        """
        現在の人格による行動修正係数を取得
        """
        p = self.get_dominant()
        return {
            "exploration_bonus": p.traits.get("exploration_drive", 0.5),
            "caution_bonus": p.traits.get("caution", 0.3),
            "spontaneity": p.traits.get("spontaneity", 0.3),
        }
    
    def get_state(self) -> Dict[str, Any]:
        """状態を取得"""
        return {
            "dominant": self.dominant.name,
            "activations": {
                p.mode.name: round(p.activation, 2)
                for p in self.personalities.values()
            }
        }
