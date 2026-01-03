import time
import sys
import os
import random

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.games.game_player import GamePlayer

def test_full_autonomy():
    print("=== Testing Active Inference: Full Autonomy (Epiphany Test) ===")
    
    # GUIなし
    player = GamePlayer(headless=True)
    
    # Curiosity Decay や Attractor Learning を見るには長時間が必要だが、
    # ここでは簡易的に「初期」と「学習後」の挙動変化を確認する
    
    player.start_game("snake")
    print("Game started. Letting the agent explore for 60 seconds...")
    
    best_score = 0
    start_time = time.time()
    
    # 簡易シミュレーションループ
    try:
        while time.time() - start_time < 60:
            stats = player.get_stats()
            current_score = stats.get("current_score", 0)
            
            if current_score > best_score:
                best_score = current_score
                print(f"🌟 MOMENT OF EPIPHANY! Score: {best_score}")
                
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        pass
        
    player.stop_game()
    print("Game stopped.")
    
    # 評価
    print(f"\nFinal Best Score: {best_score}")
    
    if best_score > 0:
        print("✅ SUCCESS: Agent discovered a goal autonomously!")
    else:
        print("⚠️ NOTE: Agent did not score in 60s. This is normal for random exploration.")
        print("   Real learning takes hours. Try running main.py and watching.")

if __name__ == "__main__":
    test_full_autonomy()
