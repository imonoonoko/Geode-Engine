# action_controller.py
# Game AI Phase A-2: アクション出力
# キーボード/マウス操作

import time
import threading
from typing import List, Optional, Dict
from enum import Enum, auto

try:
    import pyautogui
    pyautogui.PAUSE = 0.01  # 高速化
    pyautogui.FAILSAFE = True  # 緊急停止（マウスを左上隅へ）
    _PYAUTOGUI_AVAILABLE = True
except ImportError:
    print("⚠️ pyautogui not found. pip install pyautogui")
    _PYAUTOGUI_AVAILABLE = False


class ActionType(Enum):
    """アクションの種類"""
    NOOP = auto()      # 何もしない
    KEY_PRESS = auto() # キーを押す
    KEY_HOLD = auto()  # キーを押し続ける
    KEY_RELEASE = auto()  # キーを離す
    MOUSE_MOVE = auto()   # マウス移動
    MOUSE_CLICK = auto()  # マウスクリック


class ActionController:
    """
    ゲーム操作コントローラー
    
    離散アクション空間をキーボード/マウス操作に変換
    """
    
    def __init__(self, action_mapping: Optional[Dict[int, str]] = None, simulation_mode: bool = True):
        """
        Args:
            action_mapping: アクションID → キーのマッピング
                例: {0: "noop", 1: "left", 2: "right", 3: "space"}
            simulation_mode: True=仮想操作（ユーザーに影響なし）, False=実操作
        """
        self.lock = threading.Lock()
        
        # シミュレーションモード（デフォルト: True = ユーザーに影響しない）
        self.simulation_mode = simulation_mode
        
        # デフォルトのアクションマッピング（ブロック崩し用）
        self.action_mapping = action_mapping or {
            0: "noop",   # 何もしない
            1: "left",   # 左
            2: "right",  # 右
            3: "space",  # 発射/スタート
        }
        
        # 現在押しているキー
        self.held_keys: set = set()
        
        # 安全装置
        self.enabled = True
        self.action_count = 0
        self.max_actions_per_second = 30
        self.last_action_time = 0
        
        mode_str = "シミュレーション" if simulation_mode else "実操作（⚠️ユーザーに影響）"
        print(f"🎮 Action Controller Initialized ({mode_str})")
        if not _PYAUTOGUI_AVAILABLE and not simulation_mode:
            print("⚠️ pyautogui not available - actions will be logged only")
    
    def execute(self, action_id: int) -> bool:
        """
        アクションを実行
        
        Args:
            action_id: アクションID
            
        Returns:
            成功したかどうか
        """
        if not self.enabled:
            return False
        
        # レート制限
        now = time.time()
        if now - self.last_action_time < 1.0 / self.max_actions_per_second:
            return False
        self.last_action_time = now
        
        with self.lock:
            key = self.action_mapping.get(action_id, "noop")
            
            if key == "noop":
                return True
            
            # シミュレーションモード: 実キー操作なし
            if self.simulation_mode:
                self.action_count += 1
                return True
            
            # 実操作モード
            if not _PYAUTOGUI_AVAILABLE:
                print(f"[Action] {action_id} -> '{key}'")
                return True
            
            try:
                pyautogui.press(key)
                self.action_count += 1
                return True
            except Exception as e:
                print(f"⚠️ Action error: {e}")
                return False
    
    def hold_key(self, key: str):
        """キーを押し続ける"""
        if not _PYAUTOGUI_AVAILABLE or not self.enabled:
            return
        
        with self.lock:
            if key not in self.held_keys:
                pyautogui.keyDown(key)
                self.held_keys.add(key)
    
    def release_key(self, key: str):
        """キーを離す"""
        if not _PYAUTOGUI_AVAILABLE:
            return
        
        with self.lock:
            if key in self.held_keys:
                pyautogui.keyUp(key)
                self.held_keys.discard(key)
    
    def release_all(self):
        """全てのキーを離す"""
        with self.lock:
            for key in list(self.held_keys):
                if _PYAUTOGUI_AVAILABLE:
                    pyautogui.keyUp(key)
            self.held_keys.clear()
    
    def set_action_mapping(self, mapping: Dict[int, str]):
        """アクションマッピングを設定"""
        with self.lock:
            self.action_mapping = mapping
        print(f"🎮 Action mapping updated: {mapping}")
    
    def get_action_space_size(self) -> int:
        """アクション空間のサイズを取得"""
        return len(self.action_mapping)
    
    def enable(self):
        """コントローラーを有効化"""
        self.enabled = True
        print("🎮 Controller enabled")
    
    def disable(self):
        """コントローラーを無効化"""
        self.enabled = False
        self.release_all()
        print("🎮 Controller disabled")
    
    def get_stats(self) -> Dict:
        """統計を取得"""
        return {
            "action_count": self.action_count,
            "enabled": self.enabled,
            "held_keys": list(self.held_keys)
        }


# テスト用
if __name__ == "__main__":
    print("Action Controller Test")
    print("- Press Ctrl+C to stop")
    print("- Move mouse to top-left corner for emergency stop")
    
    ac = ActionController()
    
    print("\nSimulating actions (dry run)...")
    for i in range(4):
        ac.execute(i)
        time.sleep(0.2)
    
    print(f"\nStats: {ac.get_stats()}")
    print("Done!")
