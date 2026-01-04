import random
from dataclasses import dataclass
from src.body.hormones import Hormone, HormoneManager

@dataclass
class TazunaSignal:
    """
    Output signal from the Tazuna Engine to the Cortex.
    """
    mode: str          # "DIVERGE", "CONVERGE", "PANIC", "NORMAL"
    temperature: float # 0.0 (Frozen) to 2.0 (Chaos)
    radius_mod: float  # Multiplier for search radius (e.g. 0.5x, 2.0x)
    reason: str        # Explanation for the decision (Meta-Cognition Log)
    vector_strategy: str = "NEAR" # "NEAR", "ORTHOGONAL", "ANTIPODAL"

class Tazuna:
    """
    Meta-Cognition Engine "Tazuna" (The Reins).
    Controls the divergence/convergence of thought streams based on Hormonal State.
    """
    def __init__(self):
        self.last_signal = None
        
        # Phase 2: Q-Learning (Simple Table)
        # State: (Boredom_Level, Serotonin_Level) -> Action: (Mode) -> Value
        # Levels: 0=Low, 1=Med, 2=High
        self.q_table = {} 
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1 # Exploration rate for learning actions

    def _get_state_key(self, boredom, serotonin):
        b_lvl = 0 if boredom < 40 else (1 if boredom < 80 else 2)
        s_lvl = 0 if serotonin < 40 else (1 if serotonin < 80 else 2)
        return (b_lvl, s_lvl)

    def modulate(self, hormones: HormoneManager) -> TazunaSignal:
        """
        Calculate the cognitive control signal based on current hormones.
        Running at O(1) - lightweight rule-based logic.
        """
        # 1. Snapshot critical hormones
        boredom = hormones.get(Hormone.BOREDOM)
        serotonin = hormones.get(Hormone.SEROTONIN)
        surprise = hormones.get(Hormone.SURPRISE)
        
        # 2. Determine Mode & Temperature
        mode = "NORMAL"
        temp = 1.0
        radius_mod = 1.0
        vector_strategy = "NEAR"
        reason = "Balanced state."

        # Priority 1: Panic Defense (High Surprise)
        # 混乱時は新しい情報を遮断し、既知の概念に閉じこもる（保守化）
        if surprise > 80.0:
            mode = "PANIC"
            temp = 0.1 # Almost frozen
            radius_mod = 0.1 # Search only immediate surroundings (strong links)
            reason = f"Too much surprise ({surprise:.1f}%). Reverting to safety."

        # Priority 2: Divergence (High Boredom)
        # 退屈時は探索をそのものを楽しむため、範囲を広げてランダム性を高める
        elif boredom > 80.0:
            mode = "DIVERGE"
            # Boredom 80 -> Temp 1.5, Boredom 100 -> Temp 2.0
            temp = 1.5 + ((boredom - 80) / 20.0) * 0.5
            radius_mod = 2.0 + ((boredom - 80) / 20.0) * 1.0 # 2.0x to 3.0x
            vector_strategy = "ORTHOGONAL" # Jump to related but different topic
            reason = f"Boredom is high ({boredom:.1f}%). Seeking novelty via Orthogonal Jump."

        # Priority 3: Convergence (High Serotonin)
        # 精神が安定している時は、文脈を深掘りする（集中）
        elif serotonin > 80.0:
            mode = "CONVERGE"
            temp = 0.4 # Low randomness
            radius_mod = 0.5 # Focus on local context
            vector_strategy = "NEAR"
            reason = f"Mind is stable ({serotonin:.1f}%). Deepening thought."

        # Normal State (Dynamic Balance)
        else:
            mode = "NORMAL"
            # Base temp fluctuates slightly with Serotonin (Higher Sero -> Lower Temp)
            # Serotonin 50 -> Temp 1.0
            # Serotonin 0 -> Temp 1.5 (Anxious jitter)
            # Serotonin 100 -> Temp 0.5
            base_temp = 1.5 - (serotonin / 100.0)
            temp = max(0.5, min(1.5, base_temp))
            reason = "Fluid cognitive state."

        signal = TazunaSignal(mode, temp, radius_mod, reason, vector_strategy)
        self.last_signal = signal
        return signal

    def learn(self, prev_hormones, action_mode, reward):
        """
        Phase 2: Simple Q-Learning Update
        Updates the value of taking 'action_mode' in 'prev_hormones' state.
        Currently just a stub/foundation for future detailed RL.
        """
        # In this MVP, we just log the learning event if reward is significant
        if abs(reward) > 5.0:
             print(f"🎓 [Tazuna] Learning... Action: {action_mode} -> Reward: {reward:.2f}")
             # Implementation of actual Q-Table update would go here
             # state = self._get_state_key(...)
             # self.q_table[state][action_mode] += ...
