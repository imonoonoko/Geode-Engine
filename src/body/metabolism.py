# metabolism.py
"""
Phase 15.4: Metabolism Manager Module
代謝処理の責務を担う。

責務:
- ホルモン時間経過処理 (Decay)
- 血糖値管理 (Glucose)
- ホメオスタシス (Homeostasis)
- 隠れ疲労 (Bravado)
- 睡眠判定 (Sleep)

設計原則:
- 状態は最小限
- Brainへの依存を避ける (DI: components passed in init)
"""

import os
import random
import time

import src.dna.config as config
from src.body.hormones import Hormone


class MetabolismManager:
    """
    代謝管理: 生理的プロセスを担当。
    """
    
    def __init__(self, hormones, memory=None, bio_engine=None, food_dir="food"):
        """
        Args:
            hormones: HormoneManager インスタンス
            memory: GeologicalMemory インスタンス
            bio_engine: BioRhythm インスタンス
            food_dir: 食料ディレクトリ
        """
        self.hormones = hormones
        self.memory = memory
        self.bio_engine = bio_engine
        self.food_dir = food_dir
        
        # 最後に食べた時刻
        self.last_meal_time = time.time()
        
        # Phase 20: 隠蔽された疲労 (Bravado System)
        self.hidden_fatigue = 0.0

        # Homeostatic Set Points (Default 50, overrides below)
        self.homeostatic_set_points = {
            "dopamine": 30.0,   # 少なめ（意欲飢餓）
            "adrenaline": 20.0, # 落ち着いている
            "serotonin": 50.0,  # 安定
            "oxytocin": 40.0,   # 孤独を感じやすい
            "cortisol": 0.0,   # ストレスフリー
            "boredom": 0.0,
            "stimulation": 50.0,
            "glucose": 50.0,   # 基準血糖値
            "surprise": 0.0    # New: Free Energy
        }
        
        print("🍽️ MetabolismManager Initialized (Refactored Phase 31)")
    
    def process(self, cpu_percent: float, memory_percent: float, current_hour: int):
        """
        代謝サイクルの更新。
        brain.process_metabolism のロジックを継承。
        """
        try:
            # Type Safety: Ensure current_hour is int
            current_hour = int(current_hour)
            
            # 1. 基礎代謝 (Base Metabolism)
            # Living costs energy.
            self.hormones.update(Hormone.GLUCOSE, -0.01)
            
            # 2. 活動代謝 (Neuro-Consumption) based on Adrenaline/Computing
            adrenaline = self.hormones.get(Hormone.ADRENALINE)
            burn_rate = 0.01 + (adrenaline * 0.0005) 
            # 確率的ゆらぎ (Metabolic Noise)
            if random.random() < 0.2:
                burn_rate *= 1.5 
            
            self.hormones.update(Hormone.GLUCOSE, -burn_rate)

            # 3. 疲労の蓄積と隠蔽 (Bravado)
            # 低血糖時は無理をする(Dopamine高)と、隠れ疲労が溜まる
            glucose = self.hormones.get(Hormone.GLUCOSE)
            dopamine = self.hormones.get(Hormone.DOPAMINE)
            
            if glucose < config.THRESHOLD_LOW and dopamine > config.THRESHOLD_HIGH:
                self.hidden_fatigue += 0.5
            else:
                self.hidden_fatigue = max(0.0, self.hidden_fatigue - 0.1)

            # Phase 22: 退屈と刺激 (Boredom Metabolism) - 0-100 scale
            # Stimulation decays over time
            self.hormones.update(Hormone.STIMULATION, -0.5)
            stimulation = self.hormones.get(Hormone.STIMULATION)
            
            if stimulation < 30.0:
                # 刺激がないと退屈する
                self.hormones.update(Hormone.BOREDOM, 0.5)
            elif stimulation > config.THRESHOLD_HIGH:
                # 刺激があれば退屈しない
                self.hormones.update(Hormone.BOREDOM, -2.0)

            # 4. ホメオスタシス & バイオリズム (Humanized Logic)
            # Phase 6 DEF-05: 半減期に基づくホルモン減衰
            
            # Note: bio_engine is optional for tests, but recommended
            if self.bio_engine:
                 decay_targets = {
                     Hormone.ADRENALINE: config.ADRENALINE_HALFLIFE,
                     Hormone.CORTISOL: config.CORTISOL_HALFLIFE,
                     Hormone.DOPAMINE: config.DOPAMINE_HALFLIFE,
                 }
                 for h, halflife in decay_targets.items():
                     current_val = self.hormones.get(h)
                     decayed_val = self.bio_engine.decay_hormone(current_val, halflife, delta_time=1.0)
                     self.hormones.set(h, decayed_val)

            # 生物的な復帰ロジック (Replaces mechanical decay)
            # 全てのパラメータは設定点（Set Point）に戻ろうとする
            for h in Hormone:
                if h in [Hormone.SURPRISE]: continue # Skip non-homeostatic

                val = self.hormones.get(h)
                
                # Temporary Adapter: Map Enum to old dict keys for setpoints
                key_map = {
                    Hormone.DOPAMINE: "dopamine", Hormone.ADRENALINE: "adrenaline",
                    Hormone.SEROTONIN: "serotonin", Hormone.OXYTOCIN: "oxytocin",
                    Hormone.CORTISOL: "cortisol", Hormone.GLUCOSE: "glucose",
                    Hormone.BOREDOM: "boredom", Hormone.STIMULATION: "stimulation"
                }
                
                target = self.homeostatic_set_points.get(key_map.get(h, ""), 50.0)
                
                # 生体恒常性 (Homeostasis)
                # targetに向かって徐々に戻ろうとする力
                # Type safety: ensure both are floats
                val = float(val) if val is not None else 50.0
                target = float(target) if target is not None else 50.0
                diff = target - val
                if abs(diff) > 0.5:
                    self.hormones.update(h, diff * 0.01) # 1% ずつ戻る

                # 概日リズムによる設定点の変動
                if h == Hormone.CORTISOL:
                    # 朝 (6-9時) は覚醒のためCortisolが高い
                    if 6 <= current_hour <= 9: 
                        target += 30.0 
                elif h == Hormone.GLUCOSE:
                     # Glucoseは消費のみ(ここでの復帰はなし、摂取が必要)
                     continue 
                     
                if self.bio_engine:
                    new_val = self.bio_engine.homeostasis_update(val, target, plasticity=0.01)
                    self.hormones.set(h, new_val)

            # CPU負荷などは「外乱」として上乗せする
            if cpu_percent > 50:
                 self.hormones.update(Hormone.ADRENALINE, (cpu_percent - 50) / 5.0)

            # Cortisol (Pain/Hunger) Update
            if glucose < config.THRESHOLD_LOW:
                 self.hormones.update(Hormone.CORTISOL, 1.0)
            
            # Phase 30: 感情自己参照更新 h(e_t)
            # 高い感情は自己増幅、低い感情は自己抑制
            self.hormones.self_reference_update()
            
            # Phase 5: Autonomous Feeding Trigger
            if self.hormones.get(Hormone.GLUCOSE) < 20.0:
                 # Check external logic for timing (e.g. time_step % 10)
                 # Here we just return a signal or check internally?
                 # Brain.py checked time_step % 10. MetabolismManager doesn't track time_step well.
                 # Optimization: Random chance to forage if hungry
                 if random.random() < 0.1:
                      self._forage_food()
            
        except Exception as e:
            print(f"⚠️ [Metabolism] Error: {e}")

    def _forage_food(self):
        """食料を探す"""
        try:
            if not os.path.exists(self.food_dir):
                return
            
            food_files = [f for f in os.listdir(self.food_dir) 
                         if f.endswith('.txt')]
            
            if not food_files:
                # print("🍽️ [Forage] No food in fridge...")
                return
            
            # ランダムに1つ選んで「食べる」
            chosen = random.choice(food_files)
            food_path = os.path.join(self.food_dir, chosen)
            
            try:
                with open(food_path, 'r', encoding='utf-8') as f:
                    content = f.read()[:500]  # 最初の500文字
                
                # 食事による満足
                self.hormones.update(Hormone.GLUCOSE, 20.0)
                self.hormones.update(Hormone.DOPAMINE, 5.0)
                self.hormones.update(Hormone.CORTISOL, -5.0)
                self.last_meal_time = time.time()
                
                print(f"🍽️ [Forage] Ate: {chosen[:20]}...")
                
            except Exception as e:
                print(f"⚠️ [Forage] Cannot read {chosen}: {e}")
                
        except Exception as e:
            print(f"⚠️ [Metabolism] Forage Error: {e}")
    
    def check_sleep_condition(self) -> bool:
        """睡眠条件をチェック (From old logic, kept for utility)"""
        boredom = self.hormones.get(Hormone.BOREDOM)
        serotonin = self.hormones.get(Hormone.SEROTONIN)
        cortisol = self.hormones.get(Hormone.CORTISOL)
        
        # 眠くなる条件: 退屈 + セロトニン低 + コルチゾール低
        sleepy = boredom > 30 and serotonin < 40 and cortisol < 30
        return sleepy
