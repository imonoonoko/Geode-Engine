import time
import sys
import os
import random

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.games.game_player import GamePlayer

def test_flow_state():
    print("=== Testing Active Inference: The Flow State (Zone) ===")
    
    # GUIなし
    player = GamePlayer(headless=True)
    player.start_game("snake")
    
    print("Game started. Forcing Flow State conditions...")
    time.sleep(1.0)
    
    agent = player.agent
    if not agent:
        print("❌ Agent not initialized")
        return

    # 強制的にフロー状態を作る
    # 1. 予測誤差を小さくする (Mastery)
    agent.prediction_errors = [0.01] * 10 
    # 2. 好奇心を高く維持する (Challenge)
    agent.curiosity = 1.2
    
    print("Simulating gameplay to build up Flow...")
    
    # 数ステップ進めて Flow を蓄積させる
    for _ in range(20):
        agent.prediction_errors.append(0.01) # ずっと上手くいっている
        agent.learn() # ここで Flow 計算される
        
        stats = agent.get_stats()
        # print(f"Flow: {stats.get('flow')} Precision: {stats.get('precision')}")
        
    final_stats = agent.get_stats()
    flow = final_stats.get('flow', 0.0)
    precision = final_stats.get('precision', 0.0)
    
    print(f"\nFinal Flow State: {flow}")
    print(f"Boosted Precision: {precision} (Base: 5.0)")
    
    # 退屈チェックのオーバーライド確認
    # flow > 0.5 なので、should_play は True (辞めない) になるはず
    should_play = player.should_play()
    print(f"Should Play (Boredom Override): {should_play}")
    
    player.stop_game()
    
    if flow > 0.5 and should_play:
        print("✅ SUCCESS: Agent entered The Zone and ignored boredom.")
    else:
        print("❌ FAILURE: Flow state did not trigger properly.")

if __name__ == "__main__":
    test_flow_state()
