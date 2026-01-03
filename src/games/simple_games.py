# simple_games.py
# Kaname 用シンプルゲーム環境
# ブラウザ不要！Python で直接動作

import numpy as np
import random
from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass
import threading
import time


@dataclass
class GameState:
    """ゲーム状態"""
    board: np.ndarray
    score: int
    done: bool
    info: Dict[str, Any]


class SnakeGame:
    """
    スネークゲーム (Python 純正)
    
    - ブラウザ不要
    - 状態を直接取得可能
    - 強化学習に最適
    """
    
    def __init__(self, width: int = 10, height: int = 10):
        self.width = width
        self.height = height
        self.reset()
    
    def reset(self) -> np.ndarray:
        """ゲームをリセット"""
        # 蛇の初期位置（中央）
        center = (self.height // 2, self.width // 2)
        self.snake = [center]
        self.direction = 0  # 0:上, 1:下, 2:左, 3:右
        
        # 餌を配置
        self._place_food()
        
        self.score = 0
        self.steps = 0
        self.done = False
        
        return self._get_state()
    
    def _place_food(self):
        """餌をランダムに配置"""
        while True:
            self.food = (
                random.randint(0, self.height - 1),
                random.randint(0, self.width - 1)
            )
            if self.food not in self.snake:
                break
    
    def _get_state(self) -> np.ndarray:
        """
        現在の状態を取得
        
        Returns:
            (height, width, 3) の numpy 配列 (uint8, 0-255)
            チャンネル 0: 蛇の位置
            チャンネル 1: 餌の位置
            チャンネル 2: 頭の位置
        """
        state = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # 蛇の体
        for y, x in self.snake:
            state[y, x, 0] = 255
        
        # 餌
        state[self.food[0], self.food[1], 1] = 255
        
        # 頭
        head = self.snake[0]
        state[head[0], head[1], 2] = 255
        
        return state
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        1ステップ実行
        
        Args:
            action: 0=上, 1=下, 2=左, 3=右
            
        Returns:
            (state, reward, done, info)
        """
        if self.done:
            return self._get_state(), 0.0, True, {"score": self.score}
        
        self.steps += 1
        
        # 方向転換（逆方向は無効）
        if action == 0 and self.direction != 1:  # 上
            self.direction = 0
        elif action == 1 and self.direction != 0:  # 下
            self.direction = 1
        elif action == 2 and self.direction != 3:  # 左
            self.direction = 2
        elif action == 3 and self.direction != 2:  # 右
            self.direction = 3
        
        # 移動
        head = self.snake[0]
        if self.direction == 0:
            new_head = (head[0] - 1, head[1])
        elif self.direction == 1:
            new_head = (head[0] + 1, head[1])
        elif self.direction == 2:
            new_head = (head[0], head[1] - 1)
        else:
            new_head = (head[0], head[1] + 1)
        
        # 壁判定
        if (new_head[0] < 0 or new_head[0] >= self.height or
            new_head[1] < 0 or new_head[1] >= self.width):
            self.done = True
            return self._get_state(), -1.0, True, {"score": self.score, "death": "wall"}
        
        # 自己衝突判定
        if new_head in self.snake:
            self.done = True
            return self._get_state(), -1.0, True, {"score": self.score, "death": "self"}
        
        # 移動実行
        self.snake.insert(0, new_head)
        
        # 餌を食べた
        if new_head == self.food:
            self.score += 1
            self._place_food()
            reward = 1.0
        else:
            self.snake.pop()
            reward = 0.01  # 生存報酬
        
        # 最大ステップ
        if self.steps >= 1000:
            self.done = True
        
        return self._get_state(), reward, self.done, {"score": self.score}
    
    def render(self) -> str:
        """テキストで描画"""
        lines = []
        lines.append("+" + "-" * self.width + "+")
        
        for y in range(self.height):
            row = "|"
            for x in range(self.width):
                if (y, x) == self.snake[0]:
                    row += "O"  # 頭
                elif (y, x) in self.snake:
                    row += "o"  # 体
                elif (y, x) == self.food:
                    row += "*"  # 餌
                else:
                    row += " "
            row += "|"
            lines.append(row)
        
        lines.append("+" + "-" * self.width + "+")
        lines.append(f"Score: {self.score}")
        
        return "\n".join(lines)


class BreakoutGame:
    """
    ブロック崩し (Python 純正)
    """
    
    def __init__(self, width: int = 10, height: int = 10, blocks_rows: int = 3):
        self.width = width
        self.height = height
        self.blocks_rows = blocks_rows
        self.reset()
    
    def reset(self) -> np.ndarray:
        """ゲームをリセット"""
        # パドル
        self.paddle_x = self.width // 2
        self.paddle_width = 3
        
        # ボール
        self.ball_x = self.width // 2
        self.ball_y = self.height - 3
        self.ball_dx = random.choice([-1, 1])
        self.ball_dy = -1
        
        # ブロック
        self.blocks = set()
        for y in range(self.blocks_rows):
            for x in range(self.width):
                self.blocks.add((y, x))
        
        self.score = 0
        self.lives = 3
        self.done = False
        
        return self._get_state()
    
    def _get_state(self) -> np.ndarray:
        """状態を取得"""
        state = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # パドル
        for x in range(max(0, self.paddle_x - 1), min(self.width, self.paddle_x + 2)):
            state[self.height - 1, x, 0] = 255
        
        # ボール
        if 0 <= self.ball_y < self.height and 0 <= self.ball_x < self.width:
            state[int(self.ball_y), int(self.ball_x), 1] = 255
        
        # ブロック
        for y, x in self.blocks:
            state[y, x, 2] = 255
        
        return state
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        1ステップ実行
        
        Args:
            action: 0=静止, 1=左, 2=右
        """
        if self.done:
            return self._get_state(), 0.0, True, {"score": self.score}
        
        # パドル移動
        if action == 1:
            self.paddle_x = max(1, self.paddle_x - 1)
        elif action == 2:
            self.paddle_x = min(self.width - 2, self.paddle_x + 1)
        
        # ボール移動
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        reward = 0.0
        
        # 壁反射
        if self.ball_x <= 0 or self.ball_x >= self.width - 1:
            self.ball_dx *= -1
            self.ball_x = max(0, min(self.width - 1, self.ball_x))
        
        if self.ball_y <= 0:
            self.ball_dy *= -1
            self.ball_y = 0
        
        # ブロック衝突
        ball_pos = (int(self.ball_y), int(self.ball_x))
        if ball_pos in self.blocks:
            self.blocks.remove(ball_pos)
            self.ball_dy *= -1
            self.score += 1
            reward = 1.0
        
        # パドル反射
        if self.ball_y >= self.height - 1:
            if abs(self.ball_x - self.paddle_x) <= 1:
                self.ball_dy *= -1
                self.ball_y = self.height - 2
                reward = 0.1
            else:
                # ボール落下
                self.lives -= 1
                if self.lives <= 0:
                    self.done = True
                    return self._get_state(), -1.0, True, {"score": self.score}
                else:
                    # リセット
                    self.ball_x = self.width // 2
                    self.ball_y = self.height - 3
                    self.ball_dx = random.choice([-1, 1])
                    self.ball_dy = -1
                    reward = -0.5
        
        # 全ブロック破壊
        if not self.blocks:
            self.done = True
            return self._get_state(), 10.0, True, {"score": self.score, "win": True}
        
        return self._get_state(), reward, self.done, {"score": self.score, "lives": self.lives}
    
    def render(self) -> str:
        """テキストで描画"""
        lines = []
        lines.append("+" + "-" * self.width + "+")
        
        for y in range(self.height):
            row = "|"
            for x in range(self.width):
                if (y, x) in self.blocks:
                    row += "#"
                elif y == self.height - 1 and abs(x - self.paddle_x) <= 1:
                    row += "="
                elif int(self.ball_y) == y and int(self.ball_x) == x:
                    row += "O"
                else:
                    row += " "
            row += "|"
            lines.append(row)
        
        lines.append("+" + "-" * self.width + "+")
        lines.append(f"Score: {self.score}  Lives: {self.lives}")
        
        return "\n".join(lines)


# テスト用
if __name__ == "__main__":
    print("=== Snake Game Test ===")
    game = SnakeGame(10, 10)
    print(game.render())
    
    for _ in range(5):
        action = random.randint(0, 3)
        state, reward, done, info = game.step(action)
        print(f"Action: {action}, Reward: {reward:.2f}, Score: {info['score']}")
        print(game.render())
        if done:
            break
    
    print("\n=== Breakout Game Test ===")
    game = BreakoutGame(10, 10)
    print(game.render())
    
    for _ in range(10):
        action = random.randint(0, 2)
        state, reward, done, info = game.step(action)
        print(f"Action: {action}, Reward: {reward:.2f}")
        print(game.render())
        if done:
            break
