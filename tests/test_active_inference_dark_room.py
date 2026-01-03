import time
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.games.game_player import GamePlayer
from src.games.active_inference_agent import ActiveInferenceAgent

def test_dark_room_behavior():
    print("=== Testing Active Inference: Dark Room Behavior ===")
    
    # GUIなしで起動
    player = GamePlayer(headless=True)
    
    # ゲーム開始 (ActiveInferenceAgent, Precision=5.0)
    player.start_game("snake")
    
    print("Game started. Monitoring actions for 5 seconds...")
    time.sleep(1.0) # 初期化待ち
    
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
    # last_decision 例: "Act:0 G:1.00 ..."
    stay_count = sum(1 for log in action_log if "Act:0" in log)
    total_samples = len(action_log)
    
    print(f"\nStats Summary:")
    print(f"Stay (Action 0) Count: {stay_count} / {total_samples}")
    
    if total_samples > 0 and stay_count / total_samples >= 0.8:
        print("✅ SUCCESS: Agent stays in the Dark Room (Minimizing Surprise).")
    else:
        print("❌ FAILURE: Agent moved too much.")
        print("Logic check required.")

if __name__ == "__main__":
    test_dark_room_behavior()
