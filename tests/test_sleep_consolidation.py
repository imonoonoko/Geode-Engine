import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import time
import math

# Project Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.brain_stem.brain import GeodeBrain
from src.cortex.memory import GeologicalMemory
from src.body.maya_synapse import SynapticStomach
from src.body.hormones import Hormone

class TestSleepConsolidation(unittest.TestCase):
    def setUp(self):
        # 簡易的なBrainの構成
        self.brain = GeodeBrain()
        
        # Memory と Synapse をリセット (クリーンテスト)
        self.brain.memory = GeologicalMemory(size=100) # 小さいサイズでテスト
        self.brain.cortex.stomach = SynapticStomach(memory_dir="test_memory", brain_ref=self.brain)
        self.brain.cortex.memory = self.brain.memory # Cortexの参照も更新
        
        # グラフ初期化
        self.brain.cortex.stomach.brain_graph.clear()
        self.brain.memory.concepts = {}

    def test_semantic_gravity_in_sleep(self):
        """ 睡眠中の意味的引力 (Semantic Gravity) の検証 """
        
        # 1. コンセプトを配置 (遠くに離す)
        # Apple: (10, 10), Sweet: (90, 90)
        self.brain.memory.concepts["Apple"] = [10.0, 10.0, time.time(), 1, 0.5]
        self.brain.memory.concepts["Sweet"] = [90.0, 90.0, time.time(), 1, 0.5]
        
        dist_before = math.sqrt((90-10)**2 + (90-10)**2)
        print(f"Distance Before: {dist_before:.2f}")
        
        # 2. シナプス結合を形成 (強く結びつける)
        # 通常は eat() で形成されるが、ここでは直接グラフに追加
        self.brain.cortex.stomach.brain_graph.add_edge("Apple", "Sweet", weight=5.0) # 強力な結合
        
        # 3. 睡眠プロセス実行
        # get_strong_links が "Apple"-"Sweet" を返すはず
        strong_links = self.brain.cortex.stomach.get_strong_links(limit=5, threshold=2.0)
        self.assertEqual(len(strong_links), 1)
        self.assertEqual(strong_links[0][2], 5.0)
        
        # _dream_process を呼び出す (モック不要、実ロジック動作確認)
        self.brain._dream_process()
        
        # 4. 座標確認
        pos_apple = self.brain.memory.concepts["Apple"]
        pos_sweet = self.brain.memory.concepts["Sweet"]
        
        dist_after = math.sqrt((pos_sweet[0]-pos_apple[0])**2 + (pos_sweet[1]-pos_apple[1])**2)
        print(f"Distance After: {dist_after:.2f}")
        
        # 引力が働いていれば、距離は縮まっているはず
        self.assertLess(dist_after, dist_before)
        
        # AppleがSweetの方へ、SweetがAppleの方へ移動している
        # 10.0 より増えているはず
        self.assertGreater(pos_apple[0], 10.0)
        # 90.0 より減っているはず
        self.assertLess(pos_sweet[0], 90.0)

if __name__ == "__main__":
    unittest.main()
