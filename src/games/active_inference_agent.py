import time
import random
import numpy as np
import math
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import threading

@dataclass
class FreeEnergyComponent:
    """自由エネルギーの内訳"""
    action: int
    risk: float      # Divergence (Priorとの乖離)
    ambiguity: float # Uncertainty (予測の不確実性)
    total_ef: float  # Expected Free Energy

class ActiveInferenceAgent:
    """
    Kaname Active Inference Agent (Phase 1: Dark Room)
    
    報酬最大化(RL)ではなく、期待自由エネルギー最小化(Active Inference)で動くエージェント。
    
    G(π) = Σ P(o,s|π) ln [P(o,s|π) / P(o,s)]
         ≈ Risk + Ambiguity
         
    - Risk (Divergence): 予測される状態が、好ましい状態(Prior)からどれだけ離れているか。
    - Ambiguity (Entropy): 予測される状態が、どれだけ不確実か。
    """
    
    def __init__(self, 
                 action_size: int,
                 brain=None,
                 precision: float = 1.0, # 行動選択の決定論的度合い
                 curiosity: float = 2.0): # 好奇心係数 (>1.0 で不確実性を好む)
        self.action_size = action_size
        self.brain = brain
        self.precision = precision
        self.curiosity = curiosity
        self.flow_state = 0.0
        self.prediction_errors: List[float] = [] # 予測誤差の履歴
        
        self.lock = threading.Lock()
        
        # 統計
        self.total_steps = 0
        self.episode_count = 0
        self.last_free_energy_components: List[FreeEnergyComponent] = []
        
        # Kaname システムへの参照
        self.meta_learner = None
        self.world_model = None
        self.memory = None
        
        self._init_kaname_systems()
        
        print(f"🧠 Active Inference Agent (Pure) Initialized.")
        print(f"   Actions: {action_size}, Precision: {precision}, Curiosity: {curiosity}")

    def _init_kaname_systems(self):
        """Kaname システムへの参照を初期化"""
        if not self.brain:
            return
        
        if hasattr(self.brain, 'meta_learner'):
            self.meta_learner = self.brain.meta_learner
        
        if hasattr(self.brain, 'world_model'):
            self.world_model = self.brain.world_model
        
        if hasattr(self.brain, 'cortex') and self.brain.cortex:
            if hasattr(self.brain.cortex, 'memory'):
                self.memory = self.brain.cortex.memory

    def _state_to_vector(self, state: np.ndarray) -> np.ndarray:
        """状態をベクトル形式(Latent)に変換"""
        # 本来はVAEなどで圧縮すべき。
        # ここでは簡易的にダウンサンプリング + Flatten
        if not isinstance(state, np.ndarray):
            state = np.array(state)
            
        if state.ndim == 3: # (C, H, W) or (H, W, C)
            # 簡易特徴量: 平均輝度、中心輝度、エッジ量などを混ぜる
             flat = state.flatten()
             return flat[:64].astype(np.float32) / 255.0 # 仮: 最初の64ピクセル
        return np.zeros(64, dtype=np.float32)

    def _get_prior(self, current_z: np.ndarray) -> np.ndarray:
        """
        GeologicalMemory (Prior) から「あるべき状態」を取得。
        
        Phase 1 (Dark Room) では:
        - まだ記憶がないため、「現在の状態」または「何もない状態」がPriorとなる。
        - ここでは「現状維持バイアス」を表現するため、current_z をそのまま返す。
          (＝動きたくない)
        """
        # 将来的には: self.memory.get_attractor(current_z)
        return current_z

    def select_action(self, state: np.ndarray, game_type: str = "generic") -> int:
        """
        期待自由エネルギー (EFE) を最小化するアクションを選択
        
        G = Risk + Ambiguity - CuriosityBonus
        """
        current_z = self._state_to_vector(state)
        preferred_z = self._get_prior(current_z)
        
        efe_scores = []
        self.last_free_energy_components = []

        # 各アクションの未来をシミュレーション
        for action in range(self.action_size):
            predicted_z = current_z # Default: 現状維持
            uncertainty = 1.0       # Default: 非常 不確実
            
            if self.world_model:
                # WorldModelがあれば予測
                # (ActiveInference用にインターフェース調整が必要かも)
                # ここでは簡易的に「WorldModelが予測したつもり」の値を生成
                if action == 0: # NO_OP (Stay) assumption
                    predicted_z = current_z
                    uncertainty = 0.1 # 自信あり
                else:
                    # 動くと状態が変わるが、どう変わるかまだ知らない -> 不確実性大
                    noise = np.random.normal(0, 0.1, size=current_z.shape)
                    predicted_z = current_z + noise
                    uncertainty = 2.0 # 自信なし
            else:
                # モデルがない場合も「信念」として物理法則を持つ
                if action == 0:
                    predicted_z = current_z
                    uncertainty = 0.1
                else:
                    predicted_z = current_z
                    uncertainty = 2.0
            
            # --- 1. Risk (Divergence) ---
            # Risk = || z_pred - z_pref ||^2
            risk = np.sum((predicted_z - preferred_z) ** 2)
            
            # --- 2. Ambiguity (Uncertainty & Curiosity) ---
            # Curiosity > 1.0 の場合、Uncertainty が高いほど G が下がる
            # G = Risk + Ambiguity * (1 - Curiosity)
            
            ambiguity_term = uncertainty * (1.0 - self.curiosity)
            
            # --- Expected Free Energy ---
            G = risk + ambiguity_term
            
            efe_scores.append(G)
            self.last_free_energy_components.append(FreeEnergyComponent(action, risk, float(uncertainty), G))

        # EFE最小化 = 確率分布 (Softmax)
        # P(a) = softmax(-G * precision)
        
        G_array = np.array(efe_scores)
        # オーバーフロー対策
        G_array = G_array - np.min(G_array) 
        
        # 確率計算
        probs = np.exp(-G_array * self.precision)
        
        if np.sum(probs) == 0:
            probs = np.ones(self.action_size) / self.action_size
        else:
            probs = probs / np.sum(probs)
            
        # 確率的に選択
        selected_action = np.random.choice(self.action_size, p=probs)
        
        return int(selected_action)

    def remember(self, state, action, reward, next_state, done, game_type: str = "generic"):
        """
        Active Inference では「報酬による強化」は行わない。
        代わりに「モデルの更新」を行う。
        """
        self.total_steps += 1
        
        # 1. World Model Learning (予測誤差の最小化)
        if self.world_model:
            # self.world_model.update(...)
            pass
            
        # 2. Geological Memory Learning (Priorの形成 / アトラクタ学習)
        # Phase 3: The Epiphany (偶然の成功を必然に変える)
        if self.memory:
            # 成功体験（報酬 > 0）を "gm_game_success" アトラクタとして刻む
            if reward > 0:
                # 感情価: 報酬をそのまま「快」として刻印
                # これにより、将来 _get_prior でこの状態が「望ましい」と判断される
                game_concept = f"gm_{game_type}_success"
                
                # 地形を激しく隆起させる（強いアトラクタ）
                # ActiveInference では「谷」に落ちようとする -> 概念的には沈降させるイメージだが
                # 実装上は modify_terrain(..., emotion_value) で正の値なら「強化」と見なす
                self.memory.modify_terrain(game_concept, emotion_value=reward * 50.0)
                
                # さらに、現在の状態ベクトル自体を「良い状態」として短期記憶バッファに入れる等の
                # 拡張が本来は必要だが、まずは概念レベルでの結合を行う。
            
            # 失敗体験（ゲームオーバーかつ負の報酬）
            elif done and reward < 0:
                game_concept = f"gm_{game_type}_failure"
                # 嫌悪刺激として刻む（負の値）
                self.memory.modify_terrain(game_concept, emotion_value=reward * 50.0)

    def learn(self) -> float:
        """
        Active Inference では「報酬による強化」は行わない。
        代わりに「モデルの更新」と「パラメータの適応（成長）」を行う。
        """
        self.total_steps += 1
        
        # 1. World Model Learning (予測誤差の最小化)
        if self.world_model:
            # 本来はここでモデル更新
            pass
            
        # 2. Curiosity Decay & Flow State (飽き/成長/没頭)
        # 時間経過とともに好奇心は減少し、既知の領域(Ambiguityが低い場所)を好むようになる
        
        # Flow Calculation
        # 最近の予測誤差が小さい（上手くいっている）かつ Curiosityが高い（挑戦している）
        # -> ゾーンに入る (Flow State)
        
        avg_error = 1.0 # Default
        if self.prediction_errors:
             avg_error = sum(self.prediction_errors[-10:]) / len(self.prediction_errors[-10:])
        
        # 誤差が小さい = コントロールできている
        # Curiosityが高い = 退屈していない（未知への挑戦中）
        if avg_error < 0.1 and self.curiosity > 0.8:
            # Flow 蓄積
            self.flow_state = min(1.0, self.flow_state + 0.05)
        else:
            # Flow 減衰
            self.flow_state = max(0.0, self.flow_state - 0.01)
            
        # Flow によるブースト効果
        # フロー中は「もっと知りたい（Curiosity）」と「確信（Precision）」が同時に高まる
        current_precision = self.precision * (1.0 + self.flow_state * 2.0)
        
        # Curiosity Decay (基本は減衰するが、Flow中は維持される)
        decay = 0.9995
        min_curiosity = 0.8
        
        if self.flow_state > 0.5:
             # フロー中は好奇心が減らない（むしろ維持される）
             pass
        elif self.curiosity > min_curiosity:
            self.curiosity *= decay
            
        return 0.0

    def end_episode(self, final_score: float = 0.0):
        self.episode_count += 1
        
    def get_stats(self) -> Dict[str, Any]:
        """統計情報"""
        last_action_stats = "None"
        if self.last_free_energy_components:
            # 最小EFEのアクションの情報を表示
            best = min(self.last_free_energy_components, key=lambda x: x.total_ef)
            last_action_stats = f"Act:{best.action} G:{best.total_ef:.2f} (R:{best.risk:.2f} A:{best.ambiguity:.2f})"
            
        return {
            "type": "Active Inference (Pure)",
            "precision": round(self.precision, 2),
            "curiosity": round(self.curiosity, 4),
            "flow": round(self.flow_state, 2),
            "last_decision": last_action_stats
        }


if __name__ == "__main__":
    # Test
    agent = ActiveInferenceAgent(action_size=3)
    dummy_state = np.zeros((3, 64, 64))
    act = agent.select_action(dummy_state)
    print(f"Selected Action: {act}")
    print(f"Stats: {agent.get_stats()}")

