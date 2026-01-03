# MineRL Java Edition Environment Wrapper
# ヘッドレスでMinecraft Java版を実行し、強化学習を行う

import time
import numpy as np
from typing import Dict, Any, Optional, Tuple
import threading

# MineRL is optional - graceful degradation
try:
    import minerl
    import gym
    MINERL_AVAILABLE = True
except ImportError:
    MINERL_AVAILABLE = False
    print("⚠️ MineRL not installed. Run: pip install minerl")
    print("   Also requires JDK 8: https://minerl.readthedocs.io/")

class MinecraftJavaEnv:
    """
    MineRL環境ラッパー。
    Java版Minecraftをヘッドレスで実行し、Geodeの脳と接続する。
    
    特徴:
    - バックグラウンド実行可能
    - 直接的な状態取得（画面解析不要）
    - OpenAI Gym互換インターフェース
    """
    
    # 利用可能な環境（簡単→難しい順）
    AVAILABLE_ENVS = [
        "MineRLNavigateDense-v0",      # ナビゲーション（簡単）
        "MineRLTreechop-v0",           # 木を切る
        "MineRLObtainDiamond-v0",      # ダイヤモンド取得（難しい）
    ]
    
    def __init__(self, brain=None, env_name: str = "MineRLNavigateDense-v0"):
        self.brain = brain
        self.env_name = env_name
        self.env = None
        self.is_running = False
        self.current_obs = None
        self.total_reward = 0.0
        self.episode_count = 0
        self.step_count = 0
        
        # 状態キャッシュ
        self.current_state = {
            "connected": False,
            "position": {"x": 0, "y": 64, "z": 0},
            "health": 20,
            "hunger": 20,
            "inventory": {},
        }
        
        # 学習履歴
        self.reward_history = []
        self.action_history = []
        
    def is_available(self) -> bool:
        """MineRLが利用可能かチェック"""
        return MINERL_AVAILABLE
    
    def connect(self) -> bool:
        """MineRL環境に接続"""
        if not MINERL_AVAILABLE:
            print("❌ MineRL is not available. Please install it first.")
            return False
        
        try:
            print(f"🎮 Starting Minecraft Java Edition ({self.env_name})...")
            self.env = gym.make(self.env_name)
            self.current_obs = self.env.reset()
            self.current_state["connected"] = True
            self.is_running = True
            print("✅ Minecraft Java connected!")
            return True
        except Exception as e:
            print(f"❌ Failed to start MineRL: {e}")
            return False
    
    def disconnect(self):
        """環境を終了"""
        self.is_running = False
        if self.env:
            self.env.close()
            self.env = None
        self.current_state["connected"] = False
        print("🔌 Minecraft Java disconnected.")
    
    def step(self, action: Dict[str, Any]) -> Tuple[Any, float, bool, Dict]:
        """
        1ステップ実行。
        
        Args:
            action: MineRLアクション辞書
                {
                    "forward": 1,
                    "back": 0,
                    "left": 0,
                    "right": 0,
                    "jump": 0,
                    "attack": 0,
                    "camera": [0, 0],  # [pitch, yaw]
                    ...
                }
        
        Returns:
            obs, reward, done, info
        """
        if not self.env:
            return None, 0.0, True, {}
        
        obs, reward, done, info = self.env.step(action)
        self.current_obs = obs
        self.total_reward += reward
        self.step_count += 1
        
        # 状態を更新
        self._update_state_from_obs(obs, info)
        
        # 脳に報酬を送信
        if self.brain and reward != 0:
            self._send_reward_to_brain(reward)
        
        # 履歴を保存
        self.reward_history.append(reward)
        if len(self.reward_history) > 1000:
            self.reward_history.pop(0)
        
        if done:
            self.episode_count += 1
            print(f"🏁 Episode {self.episode_count} finished. Total reward: {self.total_reward:.2f}")
            self.total_reward = 0.0
            self.current_obs = self.env.reset()
            self._update_state_from_obs(self.current_obs, {})
        
        return obs, reward, done, info
    
    def _update_state_from_obs(self, obs: Dict, info: Dict):
        """観測から状態を更新"""
        # POV（視点画像）がある場合
        if "pov" in obs:
            # 画像データは脳には送らない（重すぎる）
            pass
        
        # インベントリ情報
        if "inventory" in obs:
            self.current_state["inventory"] = obs["inventory"]
        
        # 位置情報（環境によって異なる）
        if "compassAngle" in obs:
            # ナビゲーション環境
            pass
    
    def _send_reward_to_brain(self, reward: float):
        """報酬を脳に送信"""
        if not self.brain:
            return
        
        from src.body.hormones import Hormone
        
        if reward > 0:
            # 正の報酬 → ドーパミン増加
            self.brain.hormones.update(Hormone.DOPAMINE, reward * 10)
            self.brain.hormones.update(Hormone.BOREDOM, -5.0)
        else:
            # 負の報酬 → コルチゾール増加
            self.brain.hormones.update(Hormone.CORTISOL, abs(reward) * 5)
    
    def create_action_from_intent(self, intent: str, **kwargs) -> Dict[str, Any]:
        """
        Geodeの意図をMineRLアクションに変換。
        
        Args:
            intent: "MOVE_FORWARD", "TURN_LEFT", "JUMP", "ATTACK" など
        
        Returns:
            MineRLアクション辞書
        """
        # デフォルトアクション（何もしない）
        action = self.env.action_space.noop() if self.env else {}
        
        if intent == "MOVE_FORWARD":
            action["forward"] = 1
        elif intent == "MOVE_BACK":
            action["back"] = 1
        elif intent == "TURN_RIGHT":
            strength = kwargs.get("strength", 10)
            action["camera"] = [0, strength]  # Yaw
        elif intent == "TURN_LEFT":
            strength = kwargs.get("strength", 10)
            action["camera"] = [0, -strength]
        elif intent == "LOOK_UP":
            action["camera"] = [-10, 0]  # Pitch
        elif intent == "LOOK_DOWN":
            action["camera"] = [10, 0]
        elif intent == "JUMP":
            action["jump"] = 1
        elif intent == "ATTACK":
            action["attack"] = 1
        elif intent == "USE":
            action["use"] = 1
        
        return action
    
    def run_autonomous_loop(self, agent, steps_per_tick: int = 1):
        """
        自律的なゲームループを実行。
        バックグラウンドスレッドで動作。
        
        Args:
            agent: ActiveInferenceAgent インスタンス
            steps_per_tick: 1回の思考で実行するステップ数
        """
        def _loop():
            print("🤖 Starting autonomous Minecraft loop (HEADLESS)...")
            
            while self.is_running:
                try:
                    # エージェントから行動を取得
                    intent = agent.decide_action(self.current_state)
                    action = self.create_action_from_intent(intent)
                    
                    # ステップ実行
                    for _ in range(steps_per_tick):
                        if not self.is_running:
                            break
                        obs, reward, done, info = self.step(action)
                        
                        # エージェントに結果を報告
                        agent.receive_feedback(obs, reward, done)
                    
                    # CPU負荷軽減
                    time.sleep(0.05)
                    
                except Exception as e:
                    print(f"⚠️ Autonomous loop error: {e}")
                    time.sleep(1.0)
            
            print("🛑 Autonomous loop stopped.")
        
        thread = threading.Thread(target=_loop, daemon=True)
        thread.start()
        return thread
    
    def get_stats(self) -> Dict[str, Any]:
        """学習統計を取得"""
        avg_reward = np.mean(self.reward_history) if self.reward_history else 0.0
        return {
            "episodes": self.episode_count,
            "total_steps": self.step_count,
            "avg_reward": avg_reward,
            "max_reward": max(self.reward_history) if self.reward_history else 0.0,
        }


# === Installation Helper ===

def check_minerl_installation():
    """MineRLのインストール状態を確認"""
    print("=" * 60)
    print("MineRL Installation Check")
    print("=" * 60)
    
    # Python version
    import sys
    print(f"Python: {sys.version}")
    
    # Java version
    import subprocess
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        print(f"Java: {result.stderr.split(chr(10))[0]}")
    except:
        print("Java: ❌ Not found")
        print("  → Install JDK 8: https://adoptium.net/")
    
    # MineRL
    if MINERL_AVAILABLE:
        print(f"MineRL: ✅ Available")
    else:
        print("MineRL: ❌ Not installed")
        print("  → Install: pip install minerl")
    
    print("=" * 60)
    return MINERL_AVAILABLE


if __name__ == "__main__":
    check_minerl_installation()
