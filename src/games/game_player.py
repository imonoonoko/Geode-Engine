import tkinter as tk
from PIL import Image, ImageTk
import io

# game_player.py
# Game AI Phase C: 統合コントローラー
# Kaname本体との連携

import time
import threading
import numpy as np
from typing import Optional, Dict, Any

from src.games.active_inference_agent import ActiveInferenceAgent
from src.games.game_translator import GameTranslator
from src.games.game_parser import GameParser


import tkinter as tk
# Tkinter import is no longer needed here, but kept if other modules need it?
# Actually good to remove tk from this process to avoid conflict.
import subprocess
import json
import base64
import io
import sys
import os

class GameViewerProcess:
    """外部プロセスとして実行されるゲームビューワーのラッパー"""
    def __init__(self, title="Kaname Game"):
        self.process = None
        self.title = title

    def start(self):
        if self.process and self.process.poll() is None:
            return
            
        viewer_script = os.path.join(os.path.dirname(__file__), "game_viewer.py")
        try:
            # python 実行コマンド (現在の python 環境を使用)
            python_exe = sys.executable
            # タイトルは引数で渡す？ 今は固定
            self.process = subprocess.Popen(
                [python_exe, viewer_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, # ログ抑制
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1 # Line buffered
            )
        except Exception as e:
            print(f"Failed to start viewer process: {e}")

    def update_frame(self, obs_np, score=0, info_text=""):
        if not self.process or self.process.poll() is not None:
            return
            
        try:
            # 画像変換 (np -> PIL -> JPEG -> Base64)
            img = Image.fromarray(obs_np)
            img = img.resize((200, 200), Image.Resampling.NEAREST)
            
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=80)
            img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            
            data = {
                "image": img_b64,
                "score": score,
                "info": info_text
            }
            
            # JSON送信
            json_line = json.dumps(data) + "\n"
            self.process.stdin.write(json_line)
            # flush は毎回しなくても bufsize=1 ならされるが、念のため
            # self.process.stdin.flush() 
            
        except Exception:
            # パイプ切断など
            pass

    def close(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
            except:
                pass
            self.process = None
        
    @property
    def is_open(self):
        return self.process is not None and self.process.poll() is None

# Alias for compatibility
GameWindow = GameViewerProcess


class GamePlayer:
    """
    ゲームプレイヤー
    
    - Brain と連動してゲームをプレイ
    - Python 純正エンジン (SimpleGames) を使用
    - GUI ウィンドウで観戦可能
    """
    
    def __init__(self, brain=None, body=None, headless: bool = False):
        """
        Args:
            brain: Kaname の Brainへの参照
            body: Kaname の Bodyへの参照
            headless: True=ウィンドウなし, False=ウィンドウあり
        """
        self.brain = brain
        self.body = body
        self.lock = threading.Lock()
        
        # ゲーム環境 (SimpleGames)
        self.simple_game = None
        self.agent = None
        
        # GUI ウィンドウ
        self.headless = headless
        self.window = None
        
        # プレイ状態
        self.current_game_type = "random"
        self.is_playing = False
        self.play_thread = None
        
        # 統計
        self.best_score = 0.0
        self.current_score = 0.0
        self.total_episodes = 0
        
        # 感情連動
        self.reward_to_dopamine_scale = 10.0
        self.gameover_cortisol_boost = 20.0
        
        # 実況設定
        self.commentary_enabled = True
        self.last_commentary_time = 0.0
        self.commentary_cooldown = 3.0
        
        # 外部コンポーネント
        self.vision = None
        self.game_browser = None

        # [Cognitive Game Loop]
        self.translator = GameTranslator()
        self.parser = GameParser()
        self.cognitive_mode = False # Default off for safety
        
        mode_str = "非表示" if headless else "ウィンドウ表示"
        print(f"🎮 Game Player Initialized ({mode_str})")

    def start_game(self, game_type: str = "random", 
                  action_mapping: Dict[int, str] = None,
                  region: Dict = None):
        """ゲームを開始"""
        if self.is_playing:
            print("⚠️ Already playing a game")
            return False
        
        from src.games.simple_games import SnakeGame, BreakoutGame
        
        with self.lock:
            if game_type == "random":
                # Snake か Breakout をランダムにするなど
                game_type = "snake" 

            self.current_game_type = game_type
            
            # ゲームエンジン初期化
            if game_type == "snake":
                self.simple_game = SnakeGame(10, 10)
                action_size = 4
            elif game_type == "breakout":
                self.simple_game = BreakoutGame(10, 10)
                action_size = 3
            else:
                self.simple_game = SnakeGame(10, 10)
                action_size = 4
                self.current_game_type = "snake"
            
            self.agent = ActiveInferenceAgent(
                action_size=action_size,
                brain=self.brain,
                precision=5.0, # Phase 1: 高精度（決定論的）にする
                curiosity=2.5  # Phase 2: 好奇心を高くして探索させる
            )
            
            # GUI ウィンドウ起動（headless=Falseの場合）
            if not self.headless:
                self.window = GameWindow(title=f"Kaname: {self.current_game_type}")
                self.window.start()
            
            self.is_playing = True
        
        self.play_thread = threading.Thread(target=self._play_loop, daemon=True)
        self.play_thread.start()
        
        print(f"🎮 Started playing: {game_type} (Internal Engine)")
        return True
    
    def stop_game(self):
        """ゲームを停止"""
        self.is_playing = False
        
        with self.lock:
             self.simple_game = None
        
        # ウィンドウを閉じる
        if self.window:
            self.window.close()
            self.window = None

        # スレッド待機（自分自身でない場合のみ）
        if self.play_thread and self.play_thread.is_alive():
            if threading.current_thread() != self.play_thread:
                try:
                    self.play_thread.join(timeout=2.0)
                except RuntimeError:
                    pass
        
        print("🎮 Game stopped.")

    def toggle_spectate(self):
        """観戦モード切り替え"""
        self.headless = not self.headless
        if not self.headless:
            # ウィンドウを開く
            if not self.window:
                self.window = GameWindow(title=f"Kaname: {self.current_game_type}")
                self.window.start()
            print("👁️ Visual ON")
        else:
            # ウィンドウを閉じる
            if self.window:
                self.window.close()
                self.window = None
            print("👁️ Visual OFF")
        return self.headless

    def _play_loop(self):
        """メインプレイループ"""
        import traceback
        try:
            while self.is_playing:
                self._play_episode()
                time.sleep(1)
                
                # 継続判定
                if not self.should_play():
                    # 終了理由の判定とフォローアップ
                    if self.brain and hasattr(self.brain, 'hormones'):
                        from src.body.hormones import Hormone
                        glucose = self.brain.hormones.get(Hormone.GLUCOSE)
                        fatigue = getattr(self.brain, 'hidden_fatigue', 0.0)
                        
                        if glucose < 20.0:
                            print("🎮 Stopped due to HUNGER (Survival Instinct).")
                            if hasattr(self.brain, 'input_stimulus'):
                                self.brain.input_stimulus("お腹が空きすぎてゲームどころじゃない...何か食べないと。")
                        elif fatigue > 80.0:
                            print("🎮 Stopped due to FATIGUE (Survival Instinct).")
                            if hasattr(self.brain, 'input_stimulus'):
                                self.brain.input_stimulus("目が回る...もう休まないと倒れる...")
                        else:
                            print("🎮 Satisfied (Boredom alleviated). Stopping game.")
                    else:
                        print("🎮 Stopping game (No brain connection).")
                        
                    self.is_playing = False
                    break
        except Exception as e:
            print(f"⚠️ Game loop error: {e}")
            traceback.print_exc()
        finally:
            self.is_playing = False
            self.stop_game()

    def _play_episode(self):
        """1エピソード実行"""
        if not self.agent or not self.simple_game:
            return
        
        obs = self.simple_game.reset()
        self.current_score = 0
        episode_steps = 0
        max_steps = 1000

        # Cognitive Modeかどうか (SnakeGameのみ対応)
        use_cognitive = self.cognitive_mode and self.current_game_type == "snake" and self.brain
        
        while self.is_playing and episode_steps < max_steps:
            
            if use_cognitive:
                # --- Cognitive Loop (Vision -> Thought -> Action) ---
                
                # 1. Vision (Translate)
                text_perception = self.translator.translate(self.current_game_type, obs)
                
                # 2. Brain (Think)
                # Brainに話しかけて独り言(Soliloquy)をもらう
                # ※ think_soliloquy は Brain に実装した同期メソッド
                if hasattr(self.brain, 'think_soliloquy'):
                    thought_text = self.brain.think_soliloquy(text_perception)
                else:
                    thought_text = "脳が思考できません..."
                
                # 3. Action (Parse)
                action = self.parser.parse(self.current_game_type, thought_text)
                
                # ログ出力 (Action)
                print(f"🎮 [ACTION] Input: {action} (from '{thought_text}')")
                
                # 遅延 (思考時間のシミュレーション)
                time.sleep(0.5) 

            else:
                # --- Fast Reflex Loop (Active Inference) ---
                action = self.agent.select_action(obs, self.current_game_type)
            
            if not self.simple_game:
                break
                
            next_obs, reward, done, info = self.simple_game.step(action)
            
            self.current_score = info.get("score", 0)
            
            # GUI更新（ウィンドウがある場合）
            if self.window and self.window.is_open:
                # 報酬などを表示
                txt = f"Step: {episode_steps} | Reward: {reward:.2f}"
                self.window.update_frame(next_obs, self.current_score, txt)
            
            # 学習
            self.agent.remember(obs, action, reward, next_obs, done, self.current_game_type)
            self.agent.learn()
            
            obs = next_obs
            episode_steps += 1
            
            self._update_emotions(reward, done)
            
            if done:
                break
            
            # ゲーム速度調整（GUIありなら見やすく少しゆっくり）
            if self.window:
                time.sleep(0.05)
            else:
                time.sleep(0.01) # 高速学習
        
        self.agent.end_episode()
        if self.current_score > self.best_score:
            self.best_score = self.current_score
            print(f"🏆 New Best Score: {self.best_score}")
    
    def _update_emotions(self, reward: float, done: bool):
        """ゲーム結果を感情に反映"""
        if not self.brain or not hasattr(self.brain, 'hormones'):
            return
        
        from src.body.hormones import Hormone
        
        # 報酬 → ドーパミン
        if reward > 0:
            dopamine_boost = reward * self.reward_to_dopamine_scale
            self.brain.hormones.update(Hormone.DOPAMINE, dopamine_boost)
        
        # ゲームオーバー → コルチゾール
        if done and reward < 0:
            self.brain.hormones.update(Hormone.CORTISOL, self.gameover_cortisol_boost)
    
    def _maybe_commentary(self):
        """ゲーム状況に基づいて発話を促す（コンテキストのみ）"""
        if not self.commentary_enabled or not self.vision:
            return
        
        now = time.time()
        if now - self.last_commentary_time < self.commentary_cooldown:
            return
        
        # コンテキストを取得（固定セリフではない）
        context = self.vision.get_commentary()
        
        if context:
            self.last_commentary_time = now
            
            # Brain に状況を通知（Kaname が自分で言葉を選ぶ）
            if self.brain and hasattr(self.brain, 'input_stimulus'):
                # ゲーム状況をテキスト形式で入力（発話内容は指定しない）
                stimulus = f"[ゲーム状況] score={context.get('score')} game_over={context.get('game_over')}"
                self.brain.input_stimulus(stimulus)
    
    def should_play(self) -> bool:
        """
        ゲームをプレイすべきか判定
        
        退屈度が高いときにTrueを返す... が、
        Flow State (没頭中) ならば、退屈や疲労を無視して「あと一回！」とプレイを継続する。
        """
        if not self.brain:
            return False
            
        from src.body.hormones import Hormone
        
        # --- 0. Survival Instinct (生存本能) ---
        # 命に関わる場合は、どんなに楽しくても中断する
        glucose = self.brain.hormones.get(Hormone.GLUCOSE)
        fatigue = getattr(self.brain, 'hidden_fatigue', 0.0)
        
        if glucose < 20.0:
            print(f"⚠️ Survival Override: Glucose Critical ({glucose:.1f})")
            return False
            
        if fatigue > 80.0:
             print(f"⚠️ Survival Override: Fatigue Critical ({fatigue:.1f})")
             return False

        # Flow State Check (Zone)
        if self.agent and hasattr(self.agent, 'flow_state'):
            if self.agent.flow_state > 0.5:
                # ゾーンに入っている時は止めない
                return True
        
        if not hasattr(self.brain, 'hormones'):
            return False
        
        boredom = self.brain.hormones.get(Hormone.BOREDOM)
        dopamine = self.brain.hormones.get(Hormone.DOPAMINE)
        
        # 1. 暇だからやる (Boredom > 80)
        # 2. 楽しいからやめない (Dopamine > 50) - 満足しても続ける中毒性
        return boredom > 80 or dopamine > 50
    
    def get_stats(self) -> Dict[str, Any]:
        """統計を取得"""
        stats = {
            "is_playing": self.is_playing,
            "headless": self.headless,
            "total_episodes": self.total_episodes,
            "best_score": round(self.best_score, 2),
            "current_score": round(self.current_score, 2),
            "agent_stats": self.agent.get_stats() if self.agent else None
        }
        
        # Vision 統計を追加
        if self.vision:
            stats["vision_stats"] = self.vision.get_stats()
        
        # Browser 統計を追加
        if self.game_browser:
            stats["browser_stats"] = self.game_browser.get_stats()
        
        return stats
    
    def _get_dummy_obs(self):
        """ダミー観測を生成"""
        import numpy as np
        return np.zeros((84, 84, 3), dtype=np.uint8)
    
    def _preprocess_obs(self, raw_obs) -> np.ndarray:
        """
        スクリーンショットを Agent 用に前処理
        (600, 800, 4) → (84, 84, 3)
        """
        import numpy as np
        from PIL import Image
        
        if raw_obs is None:
            return self._get_dummy_obs()
        
        try:
            # RGBA → RGB
            if raw_obs.shape[-1] == 4:
                raw_obs = raw_obs[:, :, :3]
            
            # リサイズ
            img = Image.fromarray(raw_obs)
            img = img.resize((84, 84), Image.Resampling.LANCZOS)
            
            return np.array(img, dtype=np.uint8)
        except Exception:
            return self._get_dummy_obs()
    
    def _estimate_reward(self, obs, next_obs) -> float:
        """画像の変化から報酬を推定（簡易的）"""
        try:
            import numpy as np
            # 画像の差分を計算
            diff = np.abs(obs.astype(float) - next_obs.astype(float))
            change = np.mean(diff)
            
            # 変化が大きい = 何かアクションが成功した可能性
            if change > 10:
                return 0.1
            return 0.0
        except Exception:
            return 0.0


# テスト用
if __name__ == "__main__":
    print("Game Player Test (dry run)")
    
    gp = GamePlayer()
    print(f"Stats: {gp.get_stats()}")
    print("Done!")
