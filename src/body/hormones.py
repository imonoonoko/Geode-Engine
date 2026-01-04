
import threading
from enum import Enum, auto
from typing import Dict, Tuple
import src.dna.config as config

class Hormone(Enum):
    """
    Biological Hormones & Neurotransmitters
    """
    DOPAMINE = "dopamine"       # 意欲、快楽
    SEROTONIN = "serotonin"     # 安定、抑制
    ADRENALINE = "adrenaline"   # 興奮、恐怖
    OXYTOCIN = "oxytocin"       # 愛着、信頼
    CORTISOL = "cortisol"       # ストレス、痛み
    GLUCOSE = "glucose"         # エネルギー (血糖値)
    BOREDOM = "boredom"         # 退屈 (Accumulated State)
    STIMULATION = "stimulation" # 刺激 (Input Rate)
    SURPRISE = "surprise"       # 驚き (Active Inference)
    SOCIAL = "social"           # 社会性 (Politeness/DesuMasu)

class HormoneManager:
    """
    Thread-safe manager for hormone levels.
    Enforces 0.0 - 100.0 scale limits.
    """
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self._data: Dict[Hormone, float] = {}
        self._initialize()

    def _initialize(self) -> None:
        """ Set initial values based on Config """
        with self.lock:
            # 0-100 Scale Initialization
            self._data[Hormone.DOPAMINE] = config.DOPAMINE_BASE
            self._data[Hormone.SEROTONIN] = config.SEROTONIN_BASE
            self._data[Hormone.ADRENALINE] = config.ADRENALINE_BASE
            self._data[Hormone.OXYTOCIN] = config.OXYTOCIN_BASE
            self._data[Hormone.CORTISOL] = config.CORTISOL_BASE
            
            # Others
            self._data[Hormone.GLUCOSE] = 50.0
            self._data[Hormone.BOREDOM] = 0.0
            self._data[Hormone.STIMULATION] = 0.0
            self._data[Hormone.STIMULATION] = 0.0
            self._data[Hormone.SURPRISE] = 0.0
            self._data[Hormone.SOCIAL] = 50.0 # Default Neutral

    def get(self, hormone: Hormone) -> float:
        """ Thread-safe Getter """
        with self.lock:
            val = self._data.get(hormone, 0.0)
            # Type safety: ensure always returns float
            return float(val) if val is not None else 0.0

    def update(self, hormone: Hormone, delta: float) -> None:
        """ 
        Add/Subtract value with Clamping (0 - HORMONE_MAX).
        Thread-safe.
        """
        if not isinstance(hormone, Hormone):
            print(f"⚠️ Usage Warning: HormoneManager.update expects Enum, got {type(hormone)}")
            return

        with self.lock:
            current = self._data.get(hormone, 0.0)
            new_val = current + delta
            
            # Clamp
            new_val = max(0.0, min(config.HORMONE_MAX, new_val))
            
            self._data[hormone] = new_val
            
            # Debug log for large shifts
            if abs(delta) > 5.0:
               pass # print(f"🧪 {hormone.value}: {current:.1f} -> {new_val:.1f} (Δ{delta:+.1f})")

    def set(self, hormone: Hormone, value: float) -> None:
        """ Absolute set with Clamping """
        with self.lock:
            val = max(0.0, min(config.HORMONE_MAX, value))
            self._data[hormone] = val

    def decay(self, hormone: Hormone, factor: float) -> None:
        """ Multiply by factor (e.g. 0.99) """
        with self.lock:
            current = self._data.get(hormone, 0.0)
            self._data[hormone] = current * factor

    def as_dict(self) -> Dict[str, float]:
        """ Return string-key dict for backward compatibility (UI/Logs) """
        with self.lock:
            return {h.value: v for h, v in self._data.items()}

    def get_max_hormone(self) -> Tuple[Hormone, float]:
        """ Return (Hormone, value) of the highest active hormone (excluding Glucose) """
        with self.lock:
            candidates = {k: v for k, v in self._data.items() 
                          if k not in [Hormone.GLUCOSE, Hormone.SURPRISE]}
            if not candidates:
                return (Hormone.SEROTONIN, 0.0)
            
            best_h = max(candidates, key=candidates.get)
            return (best_h, candidates[best_h])

    def self_reference_update(self) -> None:
        """
        Phase 12: 感情自己参照 h(e_t)
        e_t+1 = α·e_t + β·Δ_t + γ·h(e_t)
        
        h(e_t) = tanh(κ * (value - midpoint))
        
        高い感情(>60): 自己増幅 → 落ち込み長期化、高揚連鎖
        低い感情(<40): 自己抑制 → 基準への回帰
        
        Lyapunov安定性保証:
        - γ < 0.1 (発散防止)
        - tanh は |h(e)| ≤ 1 を保証
        
        これにより個体差が固定される。
        """
        import math
        
        gamma = 0.05  # 自己参照強度 (γ < 0.1 for stability)
        kappa = 0.03  # tanh の傾き係数
        baseline = 50.0
        
        with self.lock:
            # 感情系ホルモンのみ対象 (Glucose, Stimulation は除外)
            emotional_hormones = [
                Hormone.DOPAMINE,
                Hormone.SEROTONIN,
                Hormone.ADRENALINE,
                Hormone.OXYTOCIN,
                Hormone.CORTISOL,
                Hormone.BOREDOM
            ]
            
            for h in emotional_hormones:
                current = self._data.get(h, baseline)
                deviation = current - baseline
                
                # Phase 12: Homeostatic Restoring Force (Negative Feedback)
                # 平衡点 (Baseline) に引き戻す力。
                # h_term = -gamma * deviation にすることで、常に中心に戻ろうとする。
                # 非線形性 (tanh) を入れて、乖離が大きいほど強く戻るが、ある程度で飽和させる。
                
                # deviation > 0 (High): -term -> Reduce
                # deviation < 0 (Low): -(-term) -> Increase
                
                restore_force = gamma * deviation 
                
                # Apply Restore Force (Negative Feedback)
                new_val = current - restore_force
                
                # Debug Log for Self-Ref (User Verification)
                if config.DEBUG_MODE and abs(restore_force) > 0.01:
                    print(f"⚖️ [Self-Ref] Restoring {h.name}: {current:.2f} -> {new_val:.2f} (Force: -{restore_force:.3f})")

                # クランプ
                new_val = max(0.0, min(config.HORMONE_MAX, new_val))
                self._data[h] = new_val
    
    def get_self_reference_coefficient(self) -> float:
        """
        現在の自己参照強度を返す（デバッグ/監視用）
        """
        return 0.05  # gamma

