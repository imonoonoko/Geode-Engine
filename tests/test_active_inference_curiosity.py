import time
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.games.game_player import GamePlayer
from src.games.active_inference_agent import ActiveInferenceAgent

def test_curiosity_behavior():
    print("=== Testing Active Inference: Curiosity Behavior ===")
    
    # GUIなしで起動
    player = GamePlayer(headless=True)
    
    # Curiosityが有効化されている GamePlayer を使用
    # (game_player.py で curiosity=2.5 に設定済み)
    player.start_game("snake")
    
    print("Game started. Monitoring actions for 5 seconds...")
    time.sleep(1.0)
    
    # 統計監視
    action_log = []
    
    for _ in range(5):
        stats = player.get_stats()
        agent_stats = stats.get("agent_stats")
        if agent_stats:
            print(f"Stats: {agent_stats}")
            if "last_decision" in agent_stats:
                action_log.append(agent_stats["last_decision"])
        time.sleep(1.0)
        
    player.stop_game()
    print("Game stopped.")
    
    # 評価
    # Move (Not Act:0) Count
    move_count = sum(1 for log in action_log if "Act:0" not in log)
    total_samples = len(action_log)
    
    print(f"\nStats Summary:")
    print(f"Move (Action > 0) Count: {move_count} / {total_samples}")
    
    if total_samples > 0 and move_count / total_samples >= 0.5:
        print("✅ SUCCESS: Agent is EXPLORING (Curiosity Driven).")
    else:
        print("❌ FAILURE: Agent is still stuck in the Dark Room.")
        print("Curiosity parameter might be too low.")

if __name__ == "__main__":
    test_curiosity_behavior()
