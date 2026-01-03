# rl_agent.py
# Game AI Phase A-3: 強化学習エージェント
# DQN（Deep Q-Network）ベースの学習エージェント

import time
import random
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import deque
import threading


@dataclass
class Experience:
    """経験（遷移）"""
    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool


class ReplayBuffer:
    """
    経験リプレイバッファ
    
    過去の経験を保存し、ランダムサンプリングで学習を安定化
    """
    
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)
        self.lock = threading.Lock()
    
    def push(self, exp: Experience):
        """経験を追加"""
        with self.lock:
            self.buffer.append(exp)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """ランダムサンプリング"""
        with self.lock:
            return random.sample(list(self.buffer), min(batch_size, len(self.buffer)))
    
    def __len__(self):
        return len(self.buffer)


class SimpleQNetwork:
    """
    シンプルなQ関数（ニューラルネットなし版）
    
    状態をハッシュ化してテーブルで管理。
    小規模なゲームや、PyTorchなしでの動作確認用。
    """
    
    def __init__(self, action_size: int, learning_rate: float = 0.1):
        self.action_size = action_size
        self.lr = learning_rate
        self.q_table: Dict[str, np.ndarray] = {}
        self.lock = threading.Lock()
    
    def _state_to_key(self, state: np.ndarray) -> str:
        """状態をハッシュキーに変換"""
        # 状態を粗く量子化してキーにする
        if state.ndim > 1:
            small = state[0] if state.ndim == 3 else state
            small = (small // 32).flatten()[:100]  # 最初の100要素のみ使用
        else:
            small = (state // 32)[:100]
        return small.tobytes()
    
    def get_q_values(self, state: np.ndarray) -> np.ndarray:
        """Q値を取得"""
        key = self._state_to_key(state)
        with self.lock:
            if key not in self.q_table:
                self.q_table[key] = np.zeros(self.action_size)
            return self.q_table[key].copy()
    
    def update(self, state: np.ndarray, action: int, target: float):
        """Q値を更新"""
        key = self._state_to_key(state)
        with self.lock:
            if key not in self.q_table:
                self.q_table[key] = np.zeros(self.action_size)
            # TD学習
            self.q_table[key][action] += self.lr * (target - self.q_table[key][action])
    
    def get_state(self) -> Dict:
        """状態を取得"""
        return {
            "table_size": len(self.q_table),
            "learning_rate": self.lr
        }


class RLAgent:
    """
    強化学習エージェント
    
    ε-greedy方策でアクションを選択し、
    Q学習で価値関数を更新する。
    """
    
    def __init__(self, 
                 action_size: int,
                 epsilon: float = 1.0,
                 epsilon_min: float = 0.1,
                 epsilon_decay: float = 0.995,
                 gamma: float = 0.99,
                 learning_rate: float = 0.1,
                 batch_size: int = 32):
        """
        Args:
            action_size: アクション数
            epsilon: 探索率（初期値）
            epsilon_min: 探索率（最小値）
            epsilon_decay: 探索率の減衰率
            gamma: 割引率
            learning_rate: 学習率
            batch_size: バッチサイズ
        """
        self.action_size = action_size
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.gamma = gamma
        self.batch_size = batch_size
        
        # Q関数
        self.q_network = SimpleQNetwork(action_size, learning_rate)
        
        # 経験リプレイ
        self.memory = ReplayBuffer(capacity=10000)
        
        # 統計
        self.total_steps = 0
        self.training_steps = 0
        self.episode_count = 0
        
        print(f"🤖 RL Agent Initialized.")
        print(f"   Actions: {action_size}, ε: {epsilon:.2f}")
    
    def select_action(self, state: np.ndarray) -> int:
        """
        アクションを選択（ε-greedy）
        """
        if random.random() < self.epsilon:
            # 探索: ランダム
            return random.randint(0, self.action_size - 1)
        else:
            # 活用: Q値最大
            q_values = self.q_network.get_q_values(state)
            return int(np.argmax(q_values))
    
    def remember(self, state, action, reward, next_state, done):
        """経験を記憶"""
        exp = Experience(state, action, reward, next_state, done)
        self.memory.push(exp)
        self.total_steps += 1
    
    def learn(self) -> float:
        """
        経験リプレイから学習
        
        Returns:
            平均損失（または0）
        """
        if len(self.memory) < self.batch_size:
            return 0.0
        
        # サンプリング
        batch = self.memory.sample(self.batch_size)
        
        total_loss = 0.0
        for exp in batch:
            # ターゲット計算
            if exp.done:
                target = exp.reward
            else:
                next_q = self.q_network.get_q_values(exp.next_state)
                target = exp.reward + self.gamma * np.max(next_q)
            
            # 更新
            current_q = self.q_network.get_q_values(exp.state)[exp.action]
            loss = abs(target - current_q)
            total_loss += loss
            
            self.q_network.update(exp.state, exp.action, target)
        
        self.training_steps += 1
        
        # ε減衰
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return total_loss / len(batch)
    
    def end_episode(self):
        """エピソード終了時の処理"""
        self.episode_count += 1
    
    def get_stats(self) -> Dict:
        """統計を取得"""
        return {
            "epsilon": round(self.epsilon, 4),
            "total_steps": self.total_steps,
            "training_steps": self.training_steps,
            "episode_count": self.episode_count,
            "memory_size": len(self.memory),
            "q_table_size": self.q_network.get_state()["table_size"]
        }


# テスト用
if __name__ == "__main__":
    print("RL Agent Test")
    
    agent = RLAgent(action_size=4)
    
    # シミュレーション
    dummy_state = np.random.randint(0, 256, (4, 84, 84), dtype=np.uint8)
    
    for i in range(100):
        action = agent.select_action(dummy_state)
        next_state = np.random.randint(0, 256, (4, 84, 84), dtype=np.uint8)
        reward = random.random() - 0.5
        done = random.random() < 0.05
        
        agent.remember(dummy_state, action, reward, next_state, done)
        agent.learn()
        
        dummy_state = next_state
        
        if done:
            agent.end_episode()
    
    print(f"\nStats: {agent.get_stats()}")
    print("Done!")
