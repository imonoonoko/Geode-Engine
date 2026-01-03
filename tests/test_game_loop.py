# tests/test_game_loop.py
import sys
import os
import time
import threading

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.games.game_player import GamePlayer

def test_game_loop():
    print("=== Testing GamePlayer Loop & Stop ===")
    
    # Mocking brain/body
    player = GamePlayer(brain={"hormones": {}}, body=None)
    
    print("1. Starting Snake Game...")
    ret = player.start_game("snake")
    if not ret:
        print("FAILED to start game")
        return
    
    print(f"Game started. Thread alive: {player.play_thread.is_alive()}")
    time.sleep(2)
    
    print("2. Stopping Game (External stop)...")
    player.stop_game()
    time.sleep(0.5)
    
    if player.play_thread.is_alive():
        print("WARNING: Thread is still alive (might be finishing)")
    else:
        print("Thread stopped successfully.")
    
    print("\n3. Starting Breakout Game...")
    player.start_game("breakout")
    time.sleep(2)
    
    # 内部エラーによる停止をシミュレートするのは難しいが、
    # 正常終了を確認する
    print(f"Game running... (Score: {player.current_score})")
    
    print("4. Stopping Game again...")
    player.stop_game()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_game_loop()
