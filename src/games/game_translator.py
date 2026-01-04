import numpy as np
from typing import Dict, Any, Tuple

class GameTranslator:
    """
    GameTranslator
    
    ゲームの視覚情報(Active Inference Agentの観測)を
    自然言語(日本語)に翻訳して脳に届ける役割を持つ。
    
    Vision -> Text
    """
    
    def translate(self, game_type: str, state: np.ndarray) -> str:
        """
        ゲーム状態を言語化する
        
        Args:
            game_type: "snake" など
            state: shape (H, W, 3) の ndarray (uint8)
                   Ch0=Body, Ch1=Food, Ch2=Head
        
        Returns:
            状況説明の日本語テキスト
        """
        if game_type == "snake":
            return self._translate_snake(state)
        else:
            return "未知のゲーム画面です。状況がわかりません。"

    def _translate_snake(self, state: np.ndarray) -> str:
        """SnakeGameのグリッドを解析して言語化"""
        H, W, _ = state.shape
        
        # ヘッド位置の特定 (Ch2)
        head_indices = np.where(state[:, :, 2] > 0)
        if len(head_indices[0]) == 0:
            return "視界不良。自分の位置がわかりません。"
        
        head_y, head_x = head_indices[0][0], head_indices[1][0]
        
        # 餌位置の特定 (Ch1)
        food_indices = np.where(state[:, :, 1] > 0)
        food_dist = 999
        food_dir_str = "見当たらない"
        
        if len(food_indices[0]) > 0:
            food_y, food_x = food_indices[0][0], food_indices[1][0]
            # マンハッタン距離
            food_dist = abs(head_y - food_y) + abs(head_x - food_x)
            
            # 方向判定
            dy = food_y - head_y
            dx = food_x - head_x
            
            dirs = []
            if dy < 0: dirs.append("上")
            elif dy > 0: dirs.append("下")
            
            if dx < 0: dirs.append("左")
            elif dx > 0: dirs.append("右")
            
            food_dir_str = "".join(dirs) + "方向"

        # 周囲の障害物判定 (Ch0=Body or 壁)
        # Note: 壁はGridの外だが、ここではGrid端を壁とする
        # Bodyは Ch0 > 0
        
        surroundings = []
        
        # 上
        if head_y == 0 or (head_y > 0 and state[head_y-1, head_x, 0] > 0):
            surroundings.append("北に壁か体")
        else:
            surroundings.append("北は空き")
            
        # 下
        if head_y == H - 1 or (head_y < H - 1 and state[head_y+1, head_x, 0] > 0):
            surroundings.append("南に壁か体")
        else:
            surroundings.append("南は空き")
            
        # 左
        if head_x == 0 or (head_x > 0 and state[head_y, head_x-1, 0] > 0):
            surroundings.append("西に壁か体")
        else:
            surroundings.append("西は空き")
            
        # 右
        if head_x == W - 1 or (head_x < W - 1 and state[head_y, head_x+1, 0] > 0):
            surroundings.append("東に壁か体")
        else:
            surroundings.append("東は空き")
            
        # 文章生成
        surround_text = "、".join(surroundings)
        text = f"現在位置から見て、{surround_text}です。餌は{food_dir_str}(距離{food_dist})にあります。"
        
        return text
