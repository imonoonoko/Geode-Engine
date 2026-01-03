# metabolism.py
"""
Phase 15.4: Metabolism Manager Module
代謝処理の責務を担う。

責務:
- ホルモン時間経過処理
- 血糖値管理
- 食料探索トリガー
- 睡眠判定

設計原則:
- 状態は最小限
- 依存性注入（DI）
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
    
    def __init__(self, hormones, memory=None, food_dir="food"):
        """
        Args:
            hormones: HormoneManager インスタンス
            memory: GeologicalMemory インスタンス (食料リンク用)
            food_dir: 食料ディレクトリ
        """
        self.hormones = hormones
        self.memory = memory
        self.food_dir = food_dir
        
        # 最後に食べた時刻
        self.last_meal_time = time.time()
        
        print("🍽️ MetabolismManager Initialized (Phase 15.4)")
    
    def update(self, cpu_percent: float, memory_percent: float, current_hour: int):
        """
        代謝サイクルの更新。
        
        Args:
            cpu_percent: CPU使用率 (0-100)
            memory_percent: メモリ使用率 (0-100)
            current_hour: 現在の時刻 (0-23)
        """
        try:
            # 1. 血糖値の消費
            activity_cost = cpu_percent * 0.01
            self.hormones.update(Hormone.GLUCOSE, -activity_cost)
            
            # 2. 時間経過による自然減衰
            self.hormones.decay_all(0.98)  # 2% natural decay
            
            # 3. 空腹チェック
            glucose = self.hormones.get(Hormone.GLUCOSE)
            if glucose < config.HUNGER_THRESHOLD:
                self.hormones.update(Hormone.CORTISOL, 2.0)
                self.hormones.update(Hormone.BOREDOM, 1.0)
                
                # 食料探索をトリガー
                if random.random() < 0.1:
                    self._forage_food()
            
            # 4. 過食チェック
            if glucose > 80.0:
                self.hormones.update(Hormone.SEROTONIN, 1.0)
                self.hormones.update(Hormone.GLUCOSE, -0.5)
            
            # 5. サーカディアンリズム
            self._apply_circadian_rhythm(current_hour)
            
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
                print("🍽️ [Forage] No food in fridge...")
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
    
    def _apply_circadian_rhythm(self, hour: int):
        """サーカディアンリズムによるホルモン調整"""
        # 夜間 (22-6): セロトニン低下、眠気
        if hour >= 22 or hour < 6:
            self.hormones.update(Hormone.SEROTONIN, -0.5)
            self.hormones.update(Hormone.BOREDOM, 0.2)
        
        # 朝 (6-9): セロトニン上昇
        elif 6 <= hour < 9:
            self.hormones.update(Hormone.SEROTONIN, 0.5)
            self.hormones.update(Hormone.DOPAMINE, 0.3)
        
        # 昼 (12-14): 昼食後の眠気
        elif 12 <= hour < 14:
            glucose = self.hormones.get(Hormone.GLUCOSE)
            if glucose > 60:
                self.hormones.update(Hormone.BOREDOM, 0.3)
    
    def check_sleep_condition(self) -> bool:
        """睡眠条件をチェック"""
        boredom = self.hormones.get(Hormone.BOREDOM)
        serotonin = self.hormones.get(Hormone.SEROTONIN)
        cortisol = self.hormones.get(Hormone.CORTISOL)
        
        # 眠くなる条件: 退屈 + セロトニン低 + コルチゾール低
        sleepy = boredom > 30 and serotonin < 40 and cortisol < 30
        return sleepy
