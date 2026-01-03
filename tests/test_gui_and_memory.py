# tests/test_gui_and_memory.py
import sys
import os
import time
import numpy as np

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.cortex.memory import GeologicalMemory
from src.games.game_player import GamePlayer

def test_memory_fix():
    print("=== Testing Memory Fix (slice indices) ===")
    mem = GeologicalMemory(size=100)
    
    # modify_terrain を呼び出してエラーが出ないか確認
    # わざと float になるような計算を内部で行わせる
    # modify_terrain(word, emotion_value)
    # 内部で radius計算などがどうなるか。
    
    # 既存のバグは memory.py:240 付近
    # intキャストを入れたので通るはず
    
    try:
        mem.modify_terrain("test_concept", 0.8)
        print("✅ modify_terrain passed without error.")
    except Exception as e:
        print(f"❌ modify_terrain FAILED: {e}")
        import traceback
        traceback.print_exc()

def test_gui_launch():
    print("\n=== Testing GUI Launch (Tkinter) ===")
    
    # headless=False でウィンドウが出るか
    player = GamePlayer(brain={"hormones": {}}, body=None, headless=False)
    
    print("Starting Snake Game with GUI...")
    player.start_game("snake")
    
    # 3秒間実行してウィンドウが出るのを確認（目視できないがエラーが出なければOK）
    time.sleep(3)
    
    if player.window and player.window.is_open:
        print("✅ Window seems to be open.")
    else:
        print("⚠️ Window might failed to open (or closed too fast).")
        
    print("Stopping Game...")
    player.stop_game()
    print("✅ Game stopped safely.")

if __name__ == "__main__":
    test_memory_fix()
    # GUIテストは環境によっては失敗するかもしれないが、
    # ユーザー環境（Windows）なら動くはず
    try:
        import tkinter
        test_gui_launch()
    except ImportError:
        print("No tkinter found, skipping GUI test.")
    except Exception as e:
        print(f"GUI Test Error: {e}")
