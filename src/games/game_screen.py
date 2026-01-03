# game_screen.py
# Game AI Phase A-1: スクリーンキャプチャ
# 既存の mss 基盤を活用

import time
import threading
import numpy as np
import cv2

try:
    import mss
except ImportError:
    print("⚠️ mss not found. pip install mss")
    mss = None


class GameScreen:
    """
    ゲーム画面のキャプチャと前処理
    
    既存の KanameSenses/Retina のコードを参考に、
    ゲームプレイに特化したシンプルな実装。
    """
    
    def __init__(self, target_window: str = None, target_region: dict = None):
        """
        Args:
            target_window: 対象ウィンドウ名（未指定でフルスクリーン）
            target_region: キャプチャ領域 {"top": y, "left": x, "width": w, "height": h}
        """
        self.target_window = target_window
        self.target_region = target_region
        
        # キャプチャ設定
        self.resize_to = (84, 84)  # RL用に縮小（Atari標準）
        self.grayscale = True      # グレースケール化
        
        # フレームバッファ（フレームスタッキング用）
        self.frame_buffer = []
        self.buffer_size = 4       # 4フレームスタック
        
        # 状態
        self.sct = None
        self.lock = threading.Lock()
        
        print("🎮 Game Screen Initialized.")
    
    def open(self):
        """スクリーンキャプチャを開始"""
        if mss is None:
            print("⚠️ mss not available")
            return False
        
        self.sct = mss.mss()
        print("🎮 Screen capture started.")
        return True
    
    def close(self):
        """リソースを解放"""
        if self.sct:
            self.sct.close()
            self.sct = None
    
    def capture(self) -> np.ndarray:
        """
        画面をキャプチャして前処理
        
        Returns:
            前処理済み画像 (H, W) or (H, W, C)
        """
        if not self.sct:
            self.open()
        
        try:
            # キャプチャ領域を決定
            if self.target_region:
                monitor = self.target_region
            else:
                monitor = self.sct.monitors[1]  # プライマリモニター
            
            # キャプチャ
            screenshot = self.sct.grab(monitor)
            frame = np.array(screenshot)
            
            # BGRA → BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            # 前処理
            frame = self._preprocess(frame)
            
            return frame
            
        except Exception as e:
            print(f"⚠️ Capture error: {e}")
            return np.zeros((self.resize_to[0], self.resize_to[1]), dtype=np.uint8)
    
    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        RL用の前処理
        
        1. リサイズ
        2. グレースケール化
        3. 正規化 (0-255 → 0-1)
        """
        # グレースケール
        if self.grayscale:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # リサイズ
        if self.resize_to:
            frame = cv2.resize(frame, self.resize_to, interpolation=cv2.INTER_AREA)
        
        return frame
    
    def get_stacked_frames(self) -> np.ndarray:
        """
        フレームスタッキング（動き情報を含める）
        
        Returns:
            (buffer_size, H, W) の3D配列
        """
        frame = self.capture()
        
        with self.lock:
            self.frame_buffer.append(frame)
            
            # バッファサイズを維持
            while len(self.frame_buffer) > self.buffer_size:
                self.frame_buffer.pop(0)
            
            # バッファが満たされていない場合は複製で埋める
            while len(self.frame_buffer) < self.buffer_size:
                self.frame_buffer.insert(0, frame.copy())
            
            stacked = np.stack(self.frame_buffer, axis=0)
        
        return stacked
    
    def get_raw_frame(self) -> np.ndarray:
        """
        生フレームを取得（デバッグ用）
        
        Returns:
            BGR画像 (H, W, 3)
        """
        if not self.sct:
            self.open()
        
        try:
            if self.target_region:
                monitor = self.target_region
            else:
                monitor = self.sct.monitors[1]
            
            screenshot = self.sct.grab(monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            return frame
            
        except Exception as e:
            print(f"⚠️ Raw capture error: {e}")
            return None
    
    def set_region(self, top: int, left: int, width: int, height: int):
        """キャプチャ領域を設定"""
        self.target_region = {
            "top": top,
            "left": left,
            "width": width,
            "height": height
        }
        print(f"🎮 Region set: {self.target_region}")
    
    def reset_buffer(self):
        """フレームバッファをクリア"""
        with self.lock:
            self.frame_buffer.clear()


# テスト用
if __name__ == "__main__":
    gs = GameScreen()
    gs.open()
    
    print("Capturing 5 frames...")
    for i in range(5):
        frame = gs.capture()
        print(f"  Frame {i+1}: shape={frame.shape}, dtype={frame.dtype}")
        time.sleep(0.1)
    
    stacked = gs.get_stacked_frames()
    print(f"Stacked frames: shape={stacked.shape}")
    
    gs.close()
    print("Done!")
