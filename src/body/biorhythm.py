# biorhythm.py
import math
import time
import random

class BioRhythm:
    def __init__(self):
        print("🧬 Initializing BioRhythm Engine (Circadian & Homeostasis)...")
        # 1/fゆらぎ用の内部状態
        self.noise_history = [0.0] * 10 
        
        # 概日リズムの基準時（起動時ではなく、現在の時刻に基づく）
        self.start_time = time.time()

    def get_circadian_factor(self, current_hour):
        """ 
        24時間周期のリズム係数を返す (Phase 6: 0.0 - 100.0 スケール)
        Energy curve:
        - 03:00 -> Lowest (Deep Sleep)
        - 10:00 -> Peak 1 (High Alertness)
        - 14:00 -> Dip (Post-Lunch Dip)
        - 19:00 -> Peak 2 (Evening Alertness)
        """
        import src.dna.config as config
        
        t = (current_hour / 24.0) * 2 * math.pi
        
        # Base wave (Wake/Sleep)
        base = -math.cos(t + 0.5)
        # Secondary wave (Afternoon dip & Evening peak)
        sec = 0.5 * math.sin(2 * t) 
        
        # Combine
        val = base + sec
        
        # Normalize to 0.0 - 100.0 range (Phase 6)
        # base+sec range is approx -1.5 to +1.5
        norm_val = (val + 1.5) / 3.0
        return max(10.0, min(config.HORMONE_MAX, norm_val * config.HORMONE_MAX))

    def decay_hormone(self, current_val, half_life, delta_time=1.0):
        """
        Phase 6: 半減期に基づくホルモン減衰
        current_val: 現在値
        half_life: 半減期 (秒)
        delta_time: 経過時間 (秒), デフォルト 1秒
        戻り値: 減衰後の値
        """
        if half_life <= 0:
            return current_val
        # 指数関数的減衰: N(t) = N0 * (0.5)^(t/half_life)
        decay_factor = math.pow(0.5, delta_time / half_life)
        return current_val * decay_factor

    def homeostasis_update(self, current_val, set_point, plasticity=0.05):
        """
        恒常性維持: 現在地を設定点に近づける
        current_val: 現在のパラメータ値
        set_point: 目標値（基準値）
        plasticity: 復元力（可塑性）。高いほど早く戻る。
        """
        diff = set_point - current_val
        # バネの動き (指数関数的減衰)
        new_val = current_val + (diff * plasticity)
        return new_val

    def generate_1f_noise(self):
        """
        1/fゆらぎ (Pink Noise) の生成
        簡易的な実装: 複数のホワイトノイズの合成
        間欠カオス法などが有名だが、ここでは処理負荷の軽いメタ法を採用
        """
        active_layers = random.randint(1, len(self.noise_history))
        
        # 一部の層だけ更新することで長い相関を作る
        for i in range(active_layers):
            idx = random.randint(0, len(self.noise_history)-1)
            self.noise_history[idx] = random.uniform(-1.0, 1.0)
            
        noise = sum(self.noise_history) / len(self.noise_history)
        return noise

    def calculate_heart_rate(self, base_bpm, stress_load, excitement):
        """
        生物的な心拍数の計算
        base_bpm: 安静時心拍数 (60)
        stress_load: 負荷 (Adrenaline + Cortisol + CPU)
        excitement: 興奮 (Dopamine)
        """
        # ゆらぎの追加
        fluctuation = self.generate_1f_noise() * 5.0 # +/- 5 bpm variation
        
        target_bpm = base_bpm + (stress_load * 40.0) + (excitement * 20.0)
        final_bpm = int(target_bpm + fluctuation)
        
        return max(40, min(180, final_bpm))
