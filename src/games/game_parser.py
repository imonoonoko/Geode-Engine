import re
import random

class GameParser:
    """
    GameParser
    
    脳の「独り言(Soliloquy)」から
    実際のゲームアクション(Intent)を抽出する役割を持つ。
    
    Thought -> Action
    """
    
    def parse(self, game_type: str, thought_text: str) -> int:
        """
        思考テキストからアクションIDを抽出する
        
        Args:
            game_type: "snake" など
            thought_text: 脳が発した日本語テキスト
            
        Returns:
            action_id (int)
        """
        if game_type == "snake":
            return self._parse_snake(thought_text)
        else:
            return 0 # Default (Stay/Up)

    def _parse_snake(self, text: str) -> int:
        """
        SnakeGameのアクションマッピング
        0:上, 1:下, 2:左, 3:右
        """
        text = text.lower() # 一応小文字化
        
        # 優先度順に判定 (後ろの言葉ほど最新の意思決定の可能性が高いが、
        # ここでは単純なキーワードマッチを行う)
        
        # 明示的な方向指示
        if "上" in text or "北" in text:
            return 0
        if "下" in text or "南" in text:
            return 1
        if "左" in text or "西" in text:
            return 2
        if "右" in text or "東" in text:
            return 3
            
        # 相対的な指示 (未実装: 現在の向きが必要)
        # "真っすぐ" -> 現在の向き
        
        # 何もなければランダム (迷い)
        # 実際にはBrainが必ず方向を含むようにすべきだが、Fallbackとして。
        print(f"⚠️ GameParser: No intent found in '{text}'. Choosing random.")
        return random.randint(0, 3)
