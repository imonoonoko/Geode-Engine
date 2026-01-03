# game_browser.py
# Selenium ベースのゲーム専用ブラウザ
# スレッドセーフ！ユーザー操作に影響を与えずにゲームをプレイ

import time
import threading
from typing import Optional, Dict, Any
import numpy as np

# Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
    _SELENIUM_AVAILABLE = True
except ImportError:
    _SELENIUM_AVAILABLE = False
    print("⚠️ selenium not found. pip install selenium")


class GameBrowser:
    """
    ゲーム専用ブラウザ (Selenium ベース)
    
    - Selenium で独立したブラウザを起動
    - スレッドセーフ！（Playwright と違ってマルチスレッド対応）
    - ユーザーの操作に影響しない
    - 観戦モード / バックグラウンドモード切り替え可能
    """
    
    # ゲームURL
    GAME_URLS = {
        "breakout": "https://elgoog.im/breakout/",
        "snake": "https://playsnake.org/",
        "shooter": "https://www.crazygames.com/game/1v1-battle",
        "tetris": "https://tetris.com/play-tetris",
    }
    
    # ゲームごとのキーマッピング
    KEY_MAPPINGS = {
        "breakout": {0: None, 1: Keys.ARROW_LEFT, 2: Keys.ARROW_RIGHT},
        "snake": {0: None, 1: Keys.ARROW_UP, 2: Keys.ARROW_DOWN, 3: Keys.ARROW_LEFT, 4: Keys.ARROW_RIGHT},
        "shooter": {0: None, 1: Keys.ARROW_LEFT, 2: Keys.ARROW_RIGHT, 3: Keys.ARROW_UP, 4: Keys.ARROW_DOWN, 5: Keys.SPACE},
        "generic": {0: None, 1: Keys.ARROW_LEFT, 2: Keys.ARROW_RIGHT, 3: Keys.ARROW_UP, 4: Keys.ARROW_DOWN, 5: Keys.SPACE},
    }
    
    def __init__(self, headless: bool = False):
        """
        Args:
            headless: True=バックグラウンド（見えない）, False=観戦モード（見える）
        """
        self.headless = headless
        self.lock = threading.Lock()
        
        # Selenium WebDriver
        self._driver: Optional[webdriver.Chrome] = None
        
        # 状態
        self.is_running = False
        self.current_game: Optional[str] = None
        self.action_count = 0
        
        mode_str = "バックグラウンド" if headless else "観戦モード"
        print(f"🎮 Game Browser Initialized ({mode_str}) [Selenium]")
        
        if not _SELENIUM_AVAILABLE:
            print("⚠️ Selenium not available")
    
    def start(self, game_type: str = "breakout") -> bool:
        """
        ゲームを開始
        
        Args:
            game_type: ゲームタイプ
            
        Returns:
            成功したかどうか
        """
        if not _SELENIUM_AVAILABLE:
            print("⚠️ Selenium not installed. pip install selenium")
            return False
        
        if self.is_running:
            print("⚠️ Already running")
            return False
        
        url = self.GAME_URLS.get(game_type, self.GAME_URLS.get("breakout"))
        
        try:
            # Chrome オプション設定
            options = Options()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--window-size=800,600")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # 競合を避けるため一時プロファイルを毎回新規作成
            import uuid
            temp_profile = self._get_temp_profile_dir() + "_" + str(uuid.uuid4())[:8]
            options.add_argument("--user-data-dir=" + temp_profile)
            
            # WebDriver 起動
            print(f"🌐 Starting Chrome...")
            self._driver = webdriver.Chrome(options=options)
            
            # ゲームページに移動
            print(f"🌐 Opening: {url}")
            self._driver.get(url)
            
            # ページ読み込み待ち
            time.sleep(2)
            
            self.is_running = True
            self.current_game = game_type
            
            print(f"🎮 Game browser started: {game_type}")
            return True
            
        except Exception as e:
            print(f"⚠️ Failed to start game browser: {e}")
            self.stop()
            return False
    
    def _get_temp_profile_dir(self) -> str:
        """一時プロファイルディレクトリを取得"""
        import tempfile
        import os
        return os.path.join(tempfile.gettempdir(), "kaname_game_browser")
    
    def stop(self):
        """ブラウザを停止"""
        with self.lock:
            self.is_running = False
            
            if self._driver:
                try:
                    self._driver.quit()
                except Exception:
                    pass
                self._driver = None
            
            self.current_game = None
            print("🎮 Game browser stopped")
    
    def press_key(self, action_id: int) -> bool:
        """
        キーを押す（ブラウザ内のみ）
        
        Args:
            action_id: アクションID
            
        Returns:
            成功したかどうか
        """
        if not self.is_running or not self._driver:
            return False
        
        # キーマッピングを取得
        mapping = self.KEY_MAPPINGS.get(self.current_game, self.KEY_MAPPINGS["generic"])
        key = mapping.get(action_id)
        
        if key is None:  # noop
            return True
        
        try:
            with self.lock:
                # body 要素にキーを送信
                body = self._driver.find_element(By.TAG_NAME, "body")
                body.send_keys(key)
                self.action_count += 1
            return True
        except Exception as e:
            print(f"⚠️ Key press error: {e}")
            return False
    
    def get_screenshot(self) -> Optional[np.ndarray]:
        """
        スクリーンショットを取得
        
        Returns:
            numpy array (RGB)
        """
        if not self.is_running or not self._driver:
            return None
        
        try:
            with self.lock:
                screenshot_png = self._driver.get_screenshot_as_png()
            
            # PNG bytes → numpy array
            import io
            from PIL import Image
            img = Image.open(io.BytesIO(screenshot_png))
            return np.array(img)
            
        except Exception as e:
            print(f"⚠️ Screenshot error: {e}")
            return None
    
    def toggle_visibility(self) -> bool:
        """
        観戦モード ↔ バックグラウンド 切り替え
        
        Returns:
            新しい headless 状態
        """
        current_game = self.current_game
        
        # ブラウザを停止
        self.stop()
        
        # モード切り替え
        self.headless = not self.headless
        mode_str = "バックグラウンド" if self.headless else "観戦モード"
        print(f"🔄 Switching to: {mode_str}")
        
        # 再起動
        if current_game:
            self.start(current_game)
        
        return self.headless
    
    def get_stats(self) -> Dict[str, Any]:
        """統計を取得"""
        return {
            "is_running": self.is_running,
            "headless": self.headless,
            "current_game": self.current_game,
            "action_count": self.action_count,
            "selenium_available": _SELENIUM_AVAILABLE,
        }


# テスト用
if __name__ == "__main__":
    print("Game Browser Test (Selenium)")
    
    if not _SELENIUM_AVAILABLE:
        print("❌ Selenium not installed")
        print("   pip install selenium")
    else:
        gb = GameBrowser(headless=False)
        print(f"Stats: {gb.get_stats()}")
        
        # テスト実行（コメントアウトを外すと実行）
        # gb.start("breakout")
        # time.sleep(5)
        # gb.press_key(1)  # Left
        # gb.press_key(2)  # Right
        # screenshot = gb.get_screenshot()
        # print(f"Screenshot shape: {screenshot.shape if screenshot is not None else None}")
        # gb.stop()
        
        print("Done!")
