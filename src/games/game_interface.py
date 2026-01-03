# 統一ゲームインターフェース
# すべてのゲーム（Minecraft, Breakout, Snake等）に共通のインターフェースを提供

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import time
import threading

class GameEnvironment(ABC):
    """
    すべてのゲーム環境の基底クラス。
    カナメの脳と接続するための統一インターフェースを定義。
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.is_running = False
        self.current_state = {}
        self.total_reward = 0.0
        self.step_count = 0
        self.episode_count = 0
    
    @abstractmethod
    def connect(self) -> bool:
        """ゲームに接続"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """ゲームから切断"""
        pass
    
    @abstractmethod
    def step(self, action: Any) -> Tuple[Any, float, bool, Dict]:
        """
        1ステップ実行。
        
        Returns:
            (observation, reward, done, info)
        """
        pass
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """現在の状態を取得"""
        pass
    
    @abstractmethod
    def create_action(self, intent: str, **kwargs) -> Any:
        """意図をゲームアクションに変換"""
        pass
    
    @property
    def is_connected(self) -> bool:
        return self.current_state.get("connected", False)
    
    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return {
            "episodes": self.episode_count,
            "steps": self.step_count,
            "total_reward": self.total_reward,
        }


class GameManager:
    """
    複数のゲーム環境を管理するマネージャー。
    脳と接続し、適切なゲームを選択・実行する。
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.active_game: Optional[GameEnvironment] = None
        self.available_games: Dict[str, type] = {}
        self.game_thread: Optional[threading.Thread] = None
        self.is_playing = False
        
        # ゲームを登録
        self._register_default_games()
    
    def _register_default_games(self):
        """利用可能なゲームを登録"""
        # Minecraft Java
        try:
            from src.games.minecraft.java_env import MinecraftJavaEnv
            self.available_games["minecraft_java"] = MinecraftJavaEnv
        except ImportError:
            pass
        
        # Minecraft Bedrock
        try:
            from src.games.minecraft.manager import MinecraftManager
            # ラッパーを作成してGameEnvironmentに適合させる
            self.available_games["minecraft_bedrock"] = MinecraftManager
        except ImportError:
            pass
        
        # 内蔵ゲーム
        # TODO: Breakout, Snake, Shooter をラップして追加
    
    def list_games(self) -> list:
        """利用可能なゲーム一覧を取得"""
        return list(self.available_games.keys())
    
    def start_game(self, game_name: str, **kwargs) -> bool:
        """
        ゲームを開始。
        
        Args:
            game_name: "minecraft_java", "minecraft_bedrock", etc.
        """
        if self.is_playing:
            print("⚠️ Already playing a game. Stop first.")
            return False
        
        if game_name not in self.available_games:
            print(f"❌ Unknown game: {game_name}")
            print(f"   Available: {self.list_games()}")
            return False
        
        try:
            # ゲームインスタンスを作成
            game_class = self.available_games[game_name]
            self.active_game = game_class(brain=self.brain, **kwargs)
            
            # 接続
            if not self.active_game.connect():
                print("❌ Failed to connect to game.")
                self.active_game = None
                return False
            
            self.is_playing = True
            
            # ホルモンプリセットを適用
            if self.brain:
                try:
                    from src.dna.hormone_presets import HormonePresets
                    HormonePresets.apply_to_brain(self.brain, "game")
                except:
                    pass
            
            print(f"🎮 Started: {game_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error starting game: {e}")
            return False
    
    def stop_game(self):
        """ゲームを停止"""
        if self.active_game:
            self.active_game.disconnect()
            self.active_game = None
        self.is_playing = False
        print("🛑 Game stopped.")
    
    def run_autonomous(self, agent=None, steps_per_tick: int = 1):
        """
        自律ゲームループを開始（バックグラウンド）。
        
        Args:
            agent: 行動決定エージェント（なければ脳から取得）
            steps_per_tick: 1思考あたりのステップ数
        """
        if not self.active_game:
            print("❌ No active game.")
            return None
        
        def _loop():
            print("🤖 Autonomous game loop started (BACKGROUND)...")
            
            while self.is_playing and self.active_game:
                try:
                    # 状態を取得
                    state = self.active_game.get_state()
                    
                    # 意図を決定
                    if agent:
                        intent = agent.decide_action(state)
                    elif self.brain:
                        # 脳から直接意図を取得（簡易版）
                        intent = self._get_intent_from_brain(state)
                    else:
                        intent = "MOVE_FORWARD"  # デフォルト
                    
                    # アクションに変換して実行
                    action = self.active_game.create_action(intent)
                    obs, reward, done, info = self.active_game.step(action)
                    
                    # 報酬が脳を更新（すでにゲーム内で行われているはず）
                    
                    time.sleep(0.05)
                    
                except Exception as e:
                    print(f"⚠️ Game loop error: {e}")
                    time.sleep(1.0)
            
            print("🛑 Autonomous loop ended.")
        
        self.game_thread = threading.Thread(target=_loop, daemon=True)
        self.game_thread.start()
        return self.game_thread
    
    def _get_intent_from_brain(self, state: Dict) -> str:
        """脳からゲーム意図を取得（簡易版）"""
        import random
        from src.body.hormones import Hormone
        
        if not self.brain:
            return "MOVE_FORWARD"
        
        # ホルモンに基づいて行動を選択
        dopamine = self.brain.hormones.get(Hormone.DOPAMINE)
        boredom = self.brain.hormones.get(Hormone.BOREDOM)
        adrenaline = self.brain.hormones.get(Hormone.ADRENALINE)
        
        # 退屈が高い → 探索的行動
        if boredom > 60:
            return random.choice(["TURN_LEFT", "TURN_RIGHT", "JUMP"])
        
        # アドレナリンが高い → 攻撃的行動
        if adrenaline > 70:
            return random.choice(["ATTACK", "JUMP", "MOVE_FORWARD"])
        
        # ドーパミンが高い → 積極的行動
        if dopamine > 50:
            return random.choice(["MOVE_FORWARD", "JUMP"])
        
        # デフォルト
        return random.choice(["MOVE_FORWARD", "TURN_RIGHT", "TURN_LEFT"])
