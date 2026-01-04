import unittest
from unittest.mock import MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.brain_stem.brain import KanameBrain
from src.body.hormones import Hormone

class TestVision(unittest.TestCase):
    def setUp(self):
        # Brain init might take time, maybe mock parts of it?
        # For unit test speed, we might want to mock heavy components if possible.
        # But KanameBrain init is relatively fast except for Embedding loading.
        # We'll use the real one but maybe mock heavy internal methods if needed.
        self.brain = KanameBrain()
        
        # Mock hormones.update to verify calls without side effects
        self.brain.hormones.update = MagicMock()

    def test_visual_concept_mapping(self):
        """視覚データが概念(VISUAL:xxx)に変換されるか (エラーなし)"""
        cursor_data = {
            "name": "minecraft:oak_log",
            "position": {"x": 10, "y": 64, "z": 10},
            "displayName": "Oak Log"
        }
        # 実行
        self.brain.process_visual_memory(cursor_data)
        # 現状は内部副作用(print等)のみなので、エラーが出なければOKとする
        
    def test_visual_emotion_trigger_danger(self):
        """溶岩を見て恐怖(CORTISOL)が出るか"""
        cursor_data = {
            "name": "minecraft:lava",
            "displayName": "Lava"
        }
        self.brain.process_visual_memory(cursor_data)
        
        # update(Hormone.CORTISOL, 15) が呼ばれたか (MC_INNATE_EMOTIONS の値)
        self.brain.hormones.update.assert_any_call(Hormone.CORTISOL, 15)

    def test_visual_emotion_trigger_riches(self):
        """ダイヤモンドを見て快感(DOPAMINE)が出るか"""
        cursor_data = {
            "name": "minecraft:diamond_ore",
            "displayName": "Diamond Ore"
        }
        self.brain.process_visual_memory(cursor_data)
        
        # update(Hormone.DOPAMINE, 30) が呼ばれたか (MC_INNATE_EMOTIONS の値)
        self.brain.hormones.update.assert_any_call(Hormone.DOPAMINE, 30)

    def test_ignore_empty_data(self):
        """空データは無視されるか"""
        self.brain.process_visual_memory(None)
        self.brain.process_visual_memory({})
        
        # 何も呼ばれていないはず
        self.brain.hormones.update.assert_not_called()

    def test_peripheral_vision_scan(self):
        """周辺視野(Scan)で複数のブロックを処理できるか"""
        # nearbyBlocks データ (mineflayer_envから渡される形式)
        # mineflayer_env側で個別に process_visual_memory を呼ぶため、
        # ここでは process_visual_memory が単体で呼ばれることを想定
        
        block_data = {
            "name": "minecraft:gold_ore",
            "position": {"x": 12, "y": 10, "z": 5}
        }
        
        self.brain.process_visual_memory(block_data)
        
        # 金鉱石なのでドーパミン20が出るはず (MC_INNATE_EMOTIONS の値)
        self.brain.hormones.update.assert_any_call(Hormone.DOPAMINE, 20)

def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVision)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    run_tests()
