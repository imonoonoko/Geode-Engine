# motor_cortex.py
"""
Phase 15.1: Motor Cortex Module
運動制御の責務を担う。brain.py から分離された運動関連ロジック。

責務:
- ホルモン状態に基づく運動ベクトルの計算
- AttentionManager との連携
- 空間勾配に基づく移動決定（Minecraft用）
- BodyHAL への力の伝達

設計原則:
- 状態を持たない（計算のみ）
- 依存性注入（DI）で循環参照を回避
- オブジェクト属性の変更のみ（再代入を避ける）
"""

import math
import random
import threading

import src.dna.config as config
from src.body.hormones import Hormone


class MotorCortex:
    """
    運動皮質: 意図を物理的な動きに変換する。
    
    依存:
    - hormones: HormoneManager (参照渡し)
    - memory: GeologicalMemory (参照渡し、勾配計算用)
    - body_hal: BodyHAL (参照渡し、力の適用)
    - attention: AttentionManager (参照渡し、興味ベース移動)
    - visual_bridge: VisualMemoryBridge (senses アクセス用)
    """
    
    def __init__(self, hormones, memory, body_hal=None, attention=None, visual_bridge=None):
        """
        Args:
            hormones: HormoneManager インスタンス (参照)
            memory: GeologicalMemory インスタンス (参照)
            body_hal: BodyHAL インスタンス (オプション)
            attention: AttentionManager インスタンス (オプション)
            visual_bridge: VisualMemoryBridge インスタンス (オプション)
        """
        self.hormones = hormones
        self.memory = memory
        self.body_hal = body_hal
        self.attention = attention
        self.visual_bridge = visual_bridge
        
        self.lock = threading.Lock()
        self.time_step = 0  # デバッグ用カウンター
        
        # 空間勾配計算用 (Minecraft座標 → グリッド座標)
        self.last_mx = 0
        self.last_mz = 0
        
        print("🧠 MotorCortex Initialized (Phase 15.1)")
    
    def update(self) -> tuple:
        """
        運動ベクトルを計算し、BodyHAL に力を適用する。
        
        Returns:
            (fx, fy): 適用された力のベクトル
        """
        with self.lock:
            self.time_step += 1
            
            # 視覚ブリッジ未接続なら何もしない
            if not self.visual_bridge or not self.visual_bridge.senses:
                return (0.0, 0.0)
            
            dopamine = self.hormones.get(Hormone.DOPAMINE)
            adrenaline = self.hormones.get(Hormone.ADRENALINE)
            boredom = self.hormones.get(Hormone.BOREDOM)
            
            # DEBUG: 定期的にホルモン状態を出力
            if self.time_step % 50 == 0:
                print(f"🧪 [Motor Debug] dopamine={dopamine:.1f}, "
                      f"adrenaline={adrenaline:.1f}, "
                      f"boredom={boredom:.1f}")
            
            # === Attention Manager (興味ベースの移動) ===
            att_fx, att_fy = 0.0, 0.0
            if self.attention:
                peripheral_data = {}
                fovea_tags = []
                if hasattr(self.visual_bridge.senses, 'last_vision_data'):
                    vision = self.visual_bridge.senses.last_vision_data
                    if vision:
                        peripheral_data = vision.get("peripheral", {})
                        fovea_tags = vision.get("fovea", [])
                
                att_fx, att_fy = self.attention.update(peripheral_data, fovea_tags)
            
            # 1. Environment Gradient (Thermotaxis / Phototaxis)
            env_fx, env_fy = 0.0, 0.0
            
            if adrenaline > config.THRESHOLD_HIGH:
                env_fy = -0.5  # Go Up
                print(f"🏃 [Motor] Adrenaline high ({adrenaline:.1f}) → Moving UP")
            elif dopamine < config.THRESHOLD_LOW:
                env_fy = 0.3  # Go Down
                print(f"🏃 [Motor] Dopamine low ({dopamine:.1f}) → Moving DOWN")
            
            # 2. 統合: Attention優先、なければホルモン
            final_fx = att_fx if abs(att_fx) > 0.1 else env_fx
            final_fy = att_fy if abs(att_fy) > 0.1 else env_fy
            
            # 3. Send Command to Body (via HAL)
            if abs(final_fx) > 0.05 or abs(final_fy) > 0.05:
                if self.time_step % 10 == 0:
                    print(f"🚀 [Motor] Applying force: fx={final_fx:.2f}, fy={final_fy:.2f}")
                
                if self.body_hal and self.body_hal.is_connected:
                    self.body_hal.apply_force(final_fx, final_fy)
                elif self.visual_bridge.senses and hasattr(self.visual_bridge.senses, 'body'):
                    self.visual_bridge.senses.body.apply_force(final_fx, final_fy)
            
            return (final_fx, final_fy)
    
    def decide_direction_from_gradient(self, state: dict) -> str:
        """
        空間勾配に基づく移動決定 (Minecraft用)
        
        Args:
            state: {"yaw": float, ...}
        
        Returns:
            "MOVE_FORWARD", "TURN_LEFT", "TURN_RIGHT" のいずれか
        """
        yaw = state.get("yaw", 0)
        
        # Yawから現在向いている方向(Index 0-3)を算出
        current_dir_idx = int(((yaw + math.pi + (math.pi / 4)) % (2 * math.pi)) / (math.pi / 2))
        
        # 記憶から空間勾配を取得
        scores = self.memory.get_spatial_gradient(self.last_mx, self.last_mz)
        best_dir_idx = scores.index(max(scores))
        
        # 向いている方向と行きたい方向の差分
        diff = (best_dir_idx - current_dir_idx + 4) % 4
        if diff == 0:
            return "MOVE_FORWARD"
        elif diff == 1:
            return "TURN_LEFT"
        elif diff == 3:
            return "TURN_RIGHT"
        return "TURN_RIGHT"  # 180度なら適当に
    
    def calculate_gradient_action(self, pos: dict) -> str:
        """
        地質学的記憶の勾配に基づき、行動を決定 (Minecraft用)
        
        Args:
            pos: {"x": float, "z": float, "yaw": float}
        
        Returns:
            "MOVE_FORWARD", "TURN_LEFT", "TURN_RIGHT" のいずれか
        """
        mx, mz = pos.get('x', 0), pos.get('z', 0)
        yaw = pos.get('yaw', 0)
        
        grid_x = int(mx) // 16
        grid_z = int(mz) // 16
        
        # 周辺スコアを取得
        scores = self.memory.get_spatial_gradient(grid_x, grid_z)
        
        # ベストな方向
        best_dir = max(scores, key=scores.get)
        best_score = scores[best_dir]
        
        # スコアに差がない（どれも0.5前後）ならランダム性強め
        if best_score < 0.6 and random.random() < 0.3:
            return random.choice(["MOVE_FORWARD", "TURN_RIGHT", "TURN_LEFT"])
        
        print(f"🧭 [Nav] Best Dir: {best_dir} (Score: {best_score:.2f})")
        
        # 目標Yawへのマッピング
        target_yaws = {
            "South": 0,
            "West": 1.57,
            "North": 3.14,
            "East": -1.57
        }
        target_yaw_val = target_yaws.get(best_dir, 0)
        
        # Yaw差分の計算 (正規化: -PI ~ PI)
        diff = target_yaw_val - yaw
        while diff > 3.14159:
            diff -= 6.28318
        while diff < -3.14159:
            diff += 6.28318
        
        # 許容誤差 (0.5ラジアン ~= 30度)
        if abs(diff) < 0.5:
            return "MOVE_FORWARD"
        elif diff > 0:
            return "TURN_LEFT"
        else:
            return "TURN_RIGHT"
    
    def set_last_position(self, mx: int, mz: int):
        """グリッド座標を更新 (Brain から呼び出される)"""
        self.last_mx = mx
        self.last_mz = mz
