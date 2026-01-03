# attention_manager.py
"""
Phase 6: Attention Manager
興味関心に基づく視線・移動の統合コントローラー

責任:
- 周辺視野からの動き検出 → 興味方向の決定
- 中心視野での新規発見 → 探索モードの終了
- 退屈状態 → 探索モードの開始
- 上記を統合して移動指令を生成

依存:
- brain.chemicals (ホルモン状態)
- brain.memory.concepts (既知の概念)
- brain.visual_bridge (YOLO→日本語変換)
"""

import time
import random
import threading


class AttentionManager:
    """
    興味・注意の統合コントローラー
    """
    
    def __init__(self, brain):
        """
        Args:
            brain: GeodeBrain インスタンス
        """
        self.brain = brain
        self.lock = threading.Lock()
        
        # 内部状態
        self.current_interest = None      # 今興味を持っている概念 (日本語)
        self.exploration_mode = False     # 探索モードかどうか
        self.last_novelty_time = 0        # 最後に新発見した時刻
        self.last_motion_time = 0         # 最後に動きを検出した時刻
        
        # 設定値 (将来的にconfigに移動可能)
        self.curiosity_threshold = 50.0   # boredomがこれを超えると探索開始 (0-100)
        self.motion_interest_threshold = 3.0  # 動き検出の閾値
        self.novelty_cooldown = 30.0      # 発見後、探索を再開するまでの秒数
        self.exploration_log_rate = 0.05  # 探索ログの出力確率
        
        print("🎯 Attention Manager Initialized.")
    
    def update(self, peripheral_data: dict, fovea_tags: list) -> tuple:
        """
        毎フレーム呼び出される更新ループ
        
        Args:
            peripheral_data: Senses.retina からの周辺視野データ
            fovea_tags: 中心窩で検出されたYOLOタグのリスト
            
        Returns:
            (fx, fy): 移動指令ベクトル (-1.0 ~ 1.0)
        """
        with self.lock:
            # 1. 周辺視野からの興味引き (動き検出)
            motion_direction = self._analyze_peripheral_interest(peripheral_data)
            
            # 2. 中心視野からの新規発見
            novelty = self._check_novelty(fovea_tags)
            
            # 3. 探索モード判定
            self._update_exploration_mode()
            
            # 4. 移動指令生成
            force = self._generate_movement(motion_direction, novelty)
            
            return force
    
    def _analyze_peripheral_interest(self, peripheral_data: dict) -> tuple:
        """
        周辺視野の動き → 興味方向
        
        Args:
            peripheral_data: {"motion_grid": [[...], ...], ...}
            
        Returns:
            (fx, fy): 動きの方向ベクトル
        """
        if not peripheral_data:
            return (0.0, 0.0)
        
        motion_grid = peripheral_data.get("motion_grid", [])
        if not motion_grid:
            return (0.0, 0.0)
        
        # 最も動きが大きいグリッドを探す
        max_motion = 0
        max_row, max_col = 1, 1  # 中央がデフォルト
        
        for row_idx, row in enumerate(motion_grid):
            for col_idx, val in enumerate(row):
                if val > max_motion:
                    max_motion = val
                    max_row, max_col = row_idx, col_idx
        
        # 動きが閾値以上なら興味
        if max_motion > self.motion_interest_threshold:
            # グリッド位置 (0,1,2) → 方向 (-0.3, 0, 0.3)
            # 中央(1,1)が0、端が±0.3
            fx = (max_col - 1) * 0.3
            fy = (max_row - 1) * 0.3
            
            self.last_motion_time = time.time()
            return (fx, fy)
        
        return (0.0, 0.0)
    
    def _check_novelty(self, fovea_tags: list) -> dict:
        """
        中心視野に未知の物体があるか確認
        
        Args:
            fovea_tags: YOLOタグのリスト (英語)
            
        Returns:
            {"tag": str, "jp": str, "novel": bool} or None
        """
        if not fovea_tags or not hasattr(self.brain, 'visual_bridge'):
            return None
        
        for tag in fovea_tags:
            jp_name = self.brain.visual_bridge.translate_tag(tag)
            
            # 記憶にない = 未知
            if jp_name not in self.brain.memory.concepts:
                self.last_novelty_time = time.time()
                self.exploration_mode = False  # 発見したので探索終了
                self.current_interest = jp_name
                
                print(f"✨ [Attention] NEW DISCOVERY: {jp_name} ({tag})")
                return {"tag": tag, "jp": jp_name, "novel": True}
        
        return None
    
    def _update_exploration_mode(self):
        """
        退屈状態に基づいて探索モードを更新
        """
        from src.body.hormones import Hormone
        boredom = self.brain.hormones.get(Hormone.BOREDOM)
        now = time.time()
        
        # 探索開始条件: 退屈 + 最近発見がない
        time_since_novelty = now - self.last_novelty_time
        
        if boredom > self.curiosity_threshold and time_since_novelty > self.novelty_cooldown:
            if not self.exploration_mode:
                print(f"🔍 [Attention] Entering exploration mode (boredom={boredom:.1f})")
            self.exploration_mode = True
        elif time_since_novelty < self.novelty_cooldown:
            # 最近発見があれば探索しない
            self.exploration_mode = False
    
    def _generate_movement(self, motion_direction: tuple, novelty: dict) -> tuple:
        """
        興味に基づく移動指令を生成
        
        優先度:
        1. 動きへの反応 (周辺視野)
        2. 探索モード (ランダム移動)
        3. ホルモンによる移動 (これは brain.py 側で処理)
        
        Args:
            motion_direction: 動き検出による方向
            novelty: 新規発見情報
            
        Returns:
            (fx, fy): 移動指令
        """
        fx, fy = 0.0, 0.0
        
        # 優先度1: 動きへの反応
        if motion_direction != (0.0, 0.0):
            fx, fy = motion_direction
            print(f"👀 [Attention] Motion detected → ({fx:.2f}, {fy:.2f})")
            return (fx, fy)
        
        # 優先度2: 探索モード (ランダム移動)
        if self.exploration_mode:
            fx = random.uniform(-0.2, 0.2)
            fy = random.uniform(-0.2, 0.2)
            
            # ログは低頻度で出力
            if random.random() < self.exploration_log_rate:
                print(f"🔍 [Attention] Exploring... → ({fx:.2f}, {fy:.2f})")
            
            return (fx, fy)
        
        # それ以外は移動なし (ホルモンによる移動は brain 側で処理)
        return (0.0, 0.0)
    
    def get_status(self) -> dict:
        """
        デバッグ/テレメトリ用のステータス取得
        """
        with self.lock:
            return {
                "current_interest": self.current_interest,
                "exploration_mode": self.exploration_mode,
                "time_since_novelty": time.time() - self.last_novelty_time,
                "time_since_motion": time.time() - self.last_motion_time,
            }
