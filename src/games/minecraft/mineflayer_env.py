# Mineflayer Python Bridge
# HTTP API経由でNode.js Mineflayerボットを制御

import requests
import time
import threading
import subprocess
import os
from typing import Dict, Any, Optional, Tuple

class MineflayerEnv:
    """
    Mineflayer環境ラッパー。
    HTTP API経由でNode.jsボットと通信し、Pythonから制御する。
    
    特徴:
    - 完全バックグラウンド動作
    - ヘッドレス（画面不要）
    - Java版Minecraft対応
    """
    
    def __init__(self, api_port: int = 3001):
        self.api_url = f"http://localhost:{api_port}"
        self.api_port = api_port
        self.bot_process: Optional[subprocess.Popen] = None
        self.brain = None
        self.minecraft_brain = None # Phase 11.0: Brain Separation (Lazy Init)
        self.is_running = False
        
        # 状態キャッシュ
        self.current_state = {
            "connected": False,
            "position": {"x": 0, "y": 64, "z": 0},
            "health": 20,
            "food": 20,
            "inventory": [],
            "nearbyEntities": [],
        }
        
        # 学習統計
        self.step_count = 0
        self.episode_count = 0
        self.total_reward = 0.0
        self.reward_history = []
        
        # 前回の位置（移動検知用）
        self._last_position = None
    
    def start_bot_server(self) -> bool:
        """Node.js ボットサーバーを起動"""
        bot_dir = os.path.join(
            os.path.dirname(__file__), "bot"
        )
        bot_js = os.path.join(bot_dir, "bot.js")
        
        if not os.path.exists(bot_js):
            print("❌ bot.js not found. Run scripts/setup_mineflayer.py first.")
            return False
        
        try:
            print(f"🚀 Starting Mineflayer server on port {self.api_port}...")
            env = os.environ.copy()
            env["BOT_PORT"] = str(self.api_port)
            
            self.bot_process = subprocess.Popen(
                ["node", "bot.js"],
                cwd=bot_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True
            )
            
            # サーバー起動を待つ
            time.sleep(2)
            
            # 接続確認
            try:
                resp = requests.get(f"{self.api_url}/state", timeout=2)
                if resp.status_code == 200:
                    print("✅ Mineflayer server is running!")
                    return True
            except:
                pass
            
            print("⚠️ Server may still be starting...")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start bot server: {e}")
            return False
    
    def stop_bot_server(self):
        """ボットサーバーを停止"""
        if self.bot_process:
            self.bot_process.terminate()
            self.bot_process = None
        self.is_running = False
        print("🛑 Bot server stopped.")
    
    def connect(self, host: str = "localhost", port: int = 25565, 
                username: str = "GeodeAI") -> bool:
        """
        MinecraftサーバーにBotを接続。
        
        Args:
            host: サーバーアドレス
            port: サーバーポート（デフォルト: 25565）
            username: ボットのユーザー名
        """
        try:
            resp = requests.post(
                f"{self.api_url}/connect",
                json={"host": host, "port": port, "username": username},
                timeout=10
            )
            result = resp.json()
            
            if result.get("success"):
                print(f"✅ Bot connecting to {host}:{port} as {username}...")
                self.is_running = True
                
                # 接続完了を待つ
                for _ in range(30):  # 最大30秒待つ
                    time.sleep(1)
                    state = self.get_state()
                    if state.get("connected"):
                        print("✅ Bot connected to Minecraft!")
                        return True
                
                print("⚠️ Connection may still be in progress...")
                return True
            else:
                print(f"❌ Connection failed: {result.get('error')}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to bot server. Is it running?")
            print("   → Run: cd src/games/minecraft/bot && node bot.js")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def disconnect(self):
        """Botを切断"""
        try:
            requests.get(f"{self.api_url}/disconnect", timeout=5)
        except:
            pass
        self.current_state["connected"] = False
        self.is_running = False
        print("🔌 Bot disconnected.")
    
    def get_state(self) -> Dict[str, Any]:
        """現在の状態を取得"""
        try:
            resp = requests.get(f"{self.api_url}/state", timeout=2)
            self.current_state = resp.json()
            return self.current_state
        except:
            return self.current_state
    
    def step(self, action: Dict[str, Any]) -> Tuple[Dict, float, bool, Dict]:
        """
        1ステップ実行。
        
        Args:
            action: {"type": "MOVE_FORWARD", "duration": 500}
        
        Returns:
            (observation, reward, done, info)
        """
        # 前の状態を保存
        prev_state = self.get_state()
        self._last_position = prev_state.get("position", {}).copy()
        
        # アクション実行
        try:
            resp = requests.post(
                f"{self.api_url}/action",
                json=action,
                timeout=5
            )
            result = resp.json()
        except Exception as e:
            result = {"success": False, "error": str(e)}
        
        # 少し待ってから状態を取得
        time.sleep(0.1)
        new_state = self.get_state()
        
        # 報酬計算
        reward = self._calculate_reward(prev_state, new_state, action)
        
        # 終了判定
        done = new_state.get("health", 20) <= 0
        
        # 統計更新
        self.step_count += 1
        self.total_reward += reward
        self.reward_history.append(reward)
        if len(self.reward_history) > 1000:
            self.reward_history.pop(0)
        
        # 脳に報酬を送信
        if self.brain and reward != 0:
            self._send_reward_to_brain(reward)
        
        return new_state, reward, done, {"action_result": result}
    
    def _calculate_reward(self, prev_state: Dict, new_state: Dict, 
                          action: Dict) -> float:
        """報酬計算（内部メソッド）"""
        reward = 0.0
        
        # 1. 移動報酬（移動できた = 成功）
        if self._last_position:
            prev_pos = self._last_position
            new_pos = new_state.get("position", {})
            
            dx = new_pos.get("x", 0) - prev_pos.get("x", 0)
            dz = new_pos.get("z", 0) - prev_pos.get("z", 0)
            distance = (dx**2 + dz**2) ** 0.5
            
            if action.get("type") in ["MOVE_FORWARD", "MOVE_BACK"]:
                if distance > 0.1:
                    reward += 0.1  # 移動成功
                else:
                    reward -= 0.1  # 移動失敗（引っかかった）
        
        # 2. 体力ペナルティ
        prev_health = prev_state.get("health", 20)
        new_health = new_state.get("health", 20)
        if new_health < prev_health:
            reward -= (prev_health - new_health) * 0.5  # ダメージペナルティ
        
        # 3. 探索ボーナス（新しい場所）
        # TODO: 訪問済み場所の追跡
        
        return reward
    
    def _send_reward_to_brain(self, reward: float):
        """報酬を脳に送信"""
        if not self.brain:
            return
        
        from src.body.hormones import Hormone
        
        if reward > 0:
            self.brain.hormones.update(Hormone.DOPAMINE, reward * 20)
            self.brain.hormones.update(Hormone.BOREDOM, -5.0)
        else:
            self.brain.hormones.update(Hormone.CORTISOL, abs(reward) * 10)
    
    def create_action(self, intent: str, **kwargs) -> Dict[str, Any]:
        """意図をアクションに変換"""
        action = {"type": intent}
        if "duration" in kwargs:
            action["duration"] = int(kwargs["duration"] * 1000)  # 秒→ミリ秒
        return action
    
    def run_autonomous_loop(self, agent=None):
        """
        自律的なゲームループを実行（バックグラウンド）。
        """
        def _loop():
            print("🤖 Starting autonomous Mineflayer loop...")
            
            while self.is_running:
                try:
                    state = self.get_state()
                    
                    if not state.get("connected"):
                        time.sleep(1)
                        continue
                    
                    # 意図を決定
                    if agent:
                        intent = agent.decide_action(state)
                    elif self.brain:
                        intent = self._get_intent_from_brain(state)
                    else:
                        import random
                        intent = random.choice([
                            "MOVE_FORWARD", "TURN_LEFT", "TURN_RIGHT", "JUMP"
                        ])
                    
                    # 実行
                    action = self.create_action(intent, duration=0.5)
                    self.step(action)
                    
                    time.sleep(0.2)
                    
                except Exception as e:
                    print(f"⚠️ Autonomous loop error: {e}")
                    time.sleep(1)
            
            print("🛑 Autonomous loop stopped.")
        
        thread = threading.Thread(target=_loop, daemon=True)
        thread.start()
        return thread
    
    def _get_intent_from_brain(self, state: Dict) -> str:
        """脳からゲーム意図を取得"""
        import random
        from src.body.hormones import Hormone
        
        if not self.brain:
            return random.choice(["MOVE_FORWARD", "TURN_LEFT", "TURN_RIGHT"])
        
        # Phase 11.3: Event Processing (Feedback Loop)
        events = state.get("events", [])
        if events:
            for event in events:
                evt_type = event.get("type")
                
                if evt_type == "damage":
                    amount = event.get("amount", 1)
                    print(f"💥 [PAIN] Taken {amount} damage! Cortisol rising.")
                    self.brain.hormones.update(Hormone.CORTISOL, 10.0 * amount)
                    self.brain.hormones.update(Hormone.DOPAMINE, -5.0)
                    
                elif evt_type == "kill":
                    mob = event.get("mob", "unknown")
                    print(f"⚔️ [WIN] Defeated {mob}! Learning success.")
                    self.brain.hormones.update(Hormone.DOPAMINE, 20.0)
                    self.brain.hormones.update(Hormone.CORTISOL, -20.0)
                    # Memory feedback
                    if hasattr(self.brain, "memory") and hasattr(self.brain.memory, "update_combat_experience"):
                        self.brain.memory.update_combat_experience(mob, "WIN")

                elif evt_type == "error":
                    print(f"⚠️ [BOT ERROR] {event.get('message')}")

        # 1. 座標情報をBrainの空間記憶に送る
        pos_data = state.get("position", {})
        if pos_data:
            self.brain.process_spatial_memory(pos_data)

        # 1.5. 視覚情報(Raycast)をBrainに送る (Phase 10)
        cursor_data = state.get("cursor", None)
        if cursor_data:
            self.brain.process_visual_memory(cursor_data)
            
        # 1.6. 周辺視野(Phase 10.2)
        nearby_data = state.get("nearby", [])
        if nearby_data:
            # 負荷軽減のためランダムにサンプリングして渡す
            import random
            if random.random() < 0.3: # 30%の確率でスキャン
                for block in nearby_data:
                    self.brain.process_visual_memory(block)
        
        # 2. GameBrainに次のアクションを決定させる (Phase 11.0: Brain Separation)
        if not self.minecraft_brain:
            # Lazy Load
            from src.games.minecraft.game_brain import MinecraftBrain
            if self.brain:
                self.minecraft_brain = MinecraftBrain(self.brain)
            else:
                 return "WAIT" # Brainがないなら動かない

        intent = self.minecraft_brain.decide_intent(state)
        
        return intent

    def get_stats(self) -> Dict[str, Any]:
        """学習統計を取得"""
        import numpy as np
        avg_reward = np.mean(self.reward_history) if self.reward_history else 0.0
        return {
            "episodes": self.episode_count,
            "total_steps": self.step_count,
            "avg_reward": avg_reward,
            "max_reward": max(self.reward_history) if self.reward_history else 0.0,
        }
