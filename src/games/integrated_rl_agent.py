# integrated_rl_agent.py
# Game AI: Kaname 統合型強化学習エージェント
# GeologicalMemory, WorldModel, MetaLearner と連携

import time
import random
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import threading


@dataclass
class GameExperience:
    """ゲーム経験（地質学的堆積用）"""
    game_type: str
    state_hash: str
    action: int
    reward: float
    outcome: str  # "success", "failure", "neutral"
    emotion: float  # 感情価 (-1 to 1)
    timestamp: float = field(default_factory=time.time)


class IntegratedRLAgent:
    """
    Kaname 統合型強化学習エージェント
    
    - GeologicalMemory: ゲーム経験を地質学的に堆積
    - WorldModel: ゲーム状態を予測
    - MetaLearner: 学習率を動的調整
    """
    
    def __init__(self, 
                 action_size: int,
                 brain=None,
                 epsilon: float = 1.0,  # 探索率（Curiosity）として使用
                 epsilon_min: float = 0.1,
                 epsilon_decay: float = 0.995,
                 gamma: float = 0.99):
        """
        Args:
            action_size: アクション数
            brain: Kaname の Brain への参照
            epsilon: 探索率（Curiosity）
            epsilon_min: 最小探索率
            epsilon_decay: 減衰
            gamma: 割引率
        """
        self.action_size = action_size
        self.brain = brain
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.gamma = gamma
        
        # Q-table は廃止（強化学習を使わず、能動的推論を使用）
        # self.q_table = {} 
        self.lock = threading.Lock()
        
        # 統計
        self.total_steps = 0
        self.training_steps = 0
        self.episode_count = 0
        self.prediction_errors: List[float] = []
        
        # Kaname システムへの参照
        self.meta_learner = None
        self.world_model = None
        self.memory = None
        
        self._init_kaname_systems()
        
        print(f"🧠 Active Inference Agent Initialized.")
        print(f"   Actions: {action_size}, Curiosity: {epsilon:.2f}")
        print(f"   Kaname Integration: {'✅' if self.brain else '❌'}")
    
    def _init_kaname_systems(self):
        """Kaname システムへの参照を初期化"""
        if not self.brain:
            return
        
        # MetaLearner
        if hasattr(self.brain, 'meta_learner'):
            self.meta_learner = self.brain.meta_learner
            print("   📊 MetaLearner connected")
        
        # WorldModel
        if hasattr(self.brain, 'world_model'):
            self.world_model = self.brain.world_model
            print("   🌍 WorldModel connected")
        
        # GeologicalMemory
        if hasattr(self.brain, 'cortex') and self.brain.cortex:
            if hasattr(self.brain.cortex, 'memory'):
                self.memory = self.brain.cortex.memory
                print("   🪨 GeologicalMemory connected")
    
    def _state_to_key(self, state: np.ndarray) -> str:
        """状態をハッシュキーに変換（記憶のインデックス用）"""
        if not isinstance(state, np.ndarray):
            state = np.array(state)
        
        if state.ndim == 3 and state.shape[-1] == 3: small = state
        elif state.ndim > 1: small = state[0] if state.ndim == 3 else state
        else: small = state

        small = (small // 32).flatten()
        return small[:1000].tobytes().hex()
    
    def _get_learning_rate(self) -> float:
        """MetaLearner から学習率（適応度）を取得"""
        if self.meta_learner:
            return self.meta_learner.learning_rate
        return 0.1
    
    def select_action(self, state: np.ndarray, game_type: str = "generic") -> int:
        """
        アクションを選択（能動的推論: Active Inference）
        
        1. WorldModel で各アクション後の状態を予測
        2. 予測状態の「望ましさ（ゴール適合度）」を評価
        3. 最も望ましいアクションを選択
        4. 不確実性が高い場合は「好奇心」で探索
        """
        # 好奇心（探索）チェック
        exploration_rate = self.epsilon
        if self.meta_learner:
            exploration_rate = self.meta_learner.exploration_rate
        
        if random.random() < exploration_rate:
            return random.randint(0, self.action_size - 1)
        
        # WorldModel による予測と計画
        if self.world_model:
            state_vec = self._state_to_vector(state)
            
            # 簡易的なゴール: スコアが増えること
            # 本来は GeologicalMemory 内の「快」の概念に近づくことを目指すべき
            
            best_action = self.world_model.get_best_action(
                current_state=state_vec,
                goal_state={"score": 1.0},  # 理想状態
                available_actions=list(range(self.action_size))
            )
            if best_action is not None:
                return best_action
        
        # モデルがない、または予測不能な場合はランダム
        return random.randint(0, self.action_size - 1)
    
    def _state_to_vector(self, state: np.ndarray) -> Dict[str, float]:
        """状態をベクトル形式に変換"""
        if state.ndim > 1:
            flat = state.flatten()[:20] # 特徴量抽出（少し増やす）
        else:
            flat = state[:20]
        
        return {f"s{i}": float(v) / 255.0 for i, v in enumerate(flat)}
    
    def remember(self, state, action, reward, next_state, done, game_type: str = "generic"):
        """
        経験を処理（WorldModel更新 + GeologicalMemory堆積）
        ※ Q-Table更新は廃止
        """
        # GeologicalMemory に記録（感情体験として）
        if self.memory:
            # 報酬から感情を生成
            emotion = max(-1.0, min(1.0, reward))
            
            # 結果判定
            outcome = "neutral"
            if reward > 0: outcome = "success"
            elif reward < 0 or done: outcome = "failure"
            
            # 概念刻印: "game_snake_success" など
            # 感情が伴う場合のみ地形を隆起/沈降させる
            if abs(emotion) > 0.01:
                game_concept = f"gm_{game_type}_{outcome}"
                self.memory.modify_terrain(game_concept, emotion * 20)
                
                # エピソード的なキー記憶（位置情報として保存）
                # state_key = self._state_to_key(state)
                # self.memory.reinforce(state_key[:10], emotion) # あまり意味ないかも？
        
        # WorldModel を更新（世界の法則を学ぶ）
        if self.world_model:
            state_vec = self._state_to_vector(state)
            next_state_vec = self._state_to_vector(next_state)
            action_str = str(action)
            
            # 予測誤差を取得して学習
            error = self.world_model.update(state_vec, next_state_vec, action_str)
            self.prediction_errors.append(error)
        
        self.total_steps += 1
    
    def learn(self) -> float:
        """
        学習ステップ（MetaLearner連携のみ）
        ※ Q学習の update は行わない
        """
        # MetaLearner に予測誤差を報告して学習率（Curiosity）を調整
        if self.meta_learner and self.prediction_errors:
            avg_error = sum(self.prediction_errors[-10:]) / len(self.prediction_errors[-10:])
            self.meta_learner.adapt_learning_rate(avg_error)
        
        self.training_steps += 1
        
        # 好奇心の減衰
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return 0.0 # ダミー
    
    def record_outcome(self, success: bool):
        """結果をMetaLearnerに報告"""
        if self.meta_learner:
            self.meta_learner.record_outcome(success)
    
    def end_episode(self, final_score: float = 0.0):
        """エピソード終了時の処理"""
        self.episode_count += 1
        
        # MetaLearner に結果を報告
        success = final_score > 0
        self.record_outcome(success)
        
        # 予測誤差履歴をクリア
        self.prediction_errors = self.prediction_errors[-100:]
    
    def get_stats(self) -> Dict[str, Any]:
        """統計を取得"""
        stats = {
            "curiosity": round(self.epsilon, 4),
            "total_steps": self.total_steps,
            "training_steps": self.training_steps,
            "episode_count": self.episode_count,
            "type": "Active Inference (No RL)"
        }
        
        # Kaname システムの状態を追加
        if self.meta_learner:
            stats["meta_learning_rate"] = round(self.meta_learner.current_learning_rate, 4)
        if self.world_model:
            if hasattr(self.world_model, 'transition_table'):
                 stats["world_model_states"] = len(self.world_model.transition_table)
        if self.prediction_errors:
            stats["avg_prediction_error"] = round(
                sum(self.prediction_errors[-10:]) / len(self.prediction_errors[-10:]), 4
            )
        
        return stats


# テスト用
if __name__ == "__main__":
    print("Active Inference Agent Test")
    
    agent = IntegratedRLAgent(action_size=4)
    
    # シミュレーション
    dummy_state = np.random.randint(0, 256, (4, 84, 84), dtype=np.uint8)
    
    for i in range(50):
        action = agent.select_action(dummy_state, "test_game")
        # next_state, reward...
        
    print(f"\nStats: {agent.get_stats()}")
    print("Done!")
