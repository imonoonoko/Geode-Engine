# game_env.py
# Game AI Phase A-3/A-4: ゲーム環境
# Gymnasium準拠の汎用ゲーム環境

import time
import numpy as np
from typing import Tuple, Dict, Any, Optional

try:
    import gymnasium as gym
    from gymnasium import spaces
    _GYM_AVAILABLE = True
except ImportError:
    print("⚠️ gymnasium not found. pip install gymnasium")
    _GYM_AVAILABLE = False
    gym = None
    spaces = None

from src.games.game_screen import GameScreen
from src.games.action_controller import ActionController


class GenericGameEnv:
    """
    汎用ゲーム環境
    
    Gymnasium準拠のインターフェースで、
    任意のゲームをRLエージェントがプレイできるようにする。
    """
    
    def __init__(self, 
                 action_mapping: Dict[int, str] = None,
                 frame_shape: Tuple[int, int] = (84, 84),
                 frame_stack: int = 4,
                 region: Dict = None):
        """
        Args:
            action_mapping: アクションID → キーのマッピング
            frame_shape: 画像サイズ (H, W)
            frame_stack: フレームスタック数
            region: キャプチャ領域
        """
        # スクリーンキャプチャ
        self.screen = GameScreen(target_region=region)
        self.screen.resize_to = frame_shape
        self.screen.buffer_size = frame_stack
        
        # アクションコントローラー
        self.action_controller = ActionController(action_mapping)
        
        # 空間定義
        self.frame_shape = frame_shape
        self.frame_stack = frame_stack
        self.observation_space_shape = (frame_stack, frame_shape[0], frame_shape[1])
        self.action_space_size = self.action_controller.get_action_space_size()
        
        # 状態
        self.episode_steps = 0
        self.episode_reward = 0.0
        self.prev_score = 0
        self.done = False
        
        # 報酬設定
        self.step_penalty = -0.01  # 生存ペナルティ（行動を促す）
        self.score_reward_scale = 1.0
        
        print(f"🎮 GenericGameEnv Initialized.")
        print(f"   Observation: {self.observation_space_shape}")
        print(f"   Actions: {self.action_space_size}")
    
    def reset(self) -> np.ndarray:
        """
        環境をリセット
        
        Returns:
            初期観測
        """
        self.episode_steps = 0
        self.episode_reward = 0.0
        self.prev_score = 0
        self.done = False
        
        self.screen.reset_buffer()
        self.action_controller.release_all()
        
        # 少し待機してゲーム画面を安定させる
        time.sleep(0.1)
        
        obs = self.screen.get_stacked_frames()
        return obs
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        1ステップ実行
        
        Args:
            action: アクションID
            
        Returns:
            (observation, reward, terminated, truncated, info)
        """
        # アクション実行
        self.action_controller.execute(action)
        
        # 少し待機（ゲームの反応時間）
        time.sleep(0.033)  # ~30 FPS
        
        # 観測取得
        obs = self.screen.get_stacked_frames()
        
        # 報酬計算（サブクラスでオーバーライド可能）
        reward = self._compute_reward(obs)
        
        # 終了判定
        terminated = self._check_terminated(obs)
        truncated = self.episode_steps >= 10000  # 最大ステップ
        
        # 統計更新
        self.episode_steps += 1
        self.episode_reward += reward
        self.done = terminated or truncated
        
        info = {
            "episode_steps": self.episode_steps,
            "episode_reward": self.episode_reward,
        }
        
        return obs, reward, terminated, truncated, info
    
    def _compute_reward(self, obs: np.ndarray) -> float:
        """
        報酬を計算（基本実装）
        
        サブクラスでオーバーライドして
        ゲーム固有の報酬を定義する。
        """
        # 基本: 生存ペナルティのみ
        return self.step_penalty
    
    def _check_terminated(self, obs: np.ndarray) -> bool:
        """
        終了判定（基本実装）
        
        サブクラスでオーバーライドして
        ゲームオーバー検出を実装する。
        """
        # 基本: 終了しない
        return False
    
    def render(self):
        """デバッグ表示"""
        frame = self.screen.get_raw_frame()
        if frame is not None:
            import cv2
            cv2.imshow("Game", frame)
            cv2.waitKey(1)
    
    def close(self):
        """リソース解放"""
        self.action_controller.disable()
        self.screen.close()
    
    def get_observation_space(self):
        """観測空間を取得（Gymnasium互換）"""
        if spaces:
            return spaces.Box(
                low=0, high=255,
                shape=self.observation_space_shape,
                dtype=np.uint8
            )
        return None
    
    def get_action_space(self):
        """アクション空間を取得（Gymnasium互換）"""
        if spaces:
            return spaces.Discrete(self.action_space_size)
        return None


class BreakoutEnv(GenericGameEnv):
    """
    ブロック崩し用環境
    
    ブロック崩しに特化した報酬・終了判定を実装。
    """
    
    def __init__(self, region: Dict = None):
        # ブロック崩し用アクションマッピング
        action_mapping = {
            0: "noop",   # 何もしない
            1: "left",   # 左
            2: "right",  # 右
        }
        
        super().__init__(
            action_mapping=action_mapping,
            region=region
        )
        
        print("🧱 Breakout Environment Ready.")
    
    def _compute_reward(self, obs: np.ndarray) -> float:
        """
        ブロック崩し用報酬
        
        画像の変化から報酬を推定
        （スコア検出は将来実装）
        """
        # 基本報酬
        reward = self.step_penalty
        
        # TODO: スコア変化検出
        # TODO: ブロック破壊検出
        
        return reward
    
    def _check_terminated(self, obs: np.ndarray) -> bool:
        """
        ゲームオーバー判定
        
        画面の大きな変化でゲームオーバーを推定
        """
        # TODO: ゲームオーバー画面検出
        return False


# __init__.py 用
__all__ = ["GenericGameEnv", "BreakoutEnv", "GameScreen", "ActionController"]
