import unittest
from unittest.mock import MagicMock, patch, ANY
import threading
import time
import sys
import os
import random

# プロジェクトルートをパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.brain_stem.brain import GeodeBrain
from src.body.hormones import Hormone
from src.body.knowledge_harvesters import SourceType, HarvestedContent

class TestAutonomousFeeding(unittest.TestCase):
    def setUp(self):
        # Brain の生成
        self.brain = GeodeBrain()
        
        # モック化
        self.brain.feeder = MagicMock()
        self.brain.aozora = MagicMock()
        self.brain.knowledge_manager = MagicMock() # 追加
        self.brain.cortex = MagicMock()
        self.brain.cortex.stomach = MagicMock()
        
        # 初期状態チェック
        self.brain.hormones.set(Hormone.GLUCOSE, 50.0)

    def test_hunger_trigger(self):
        """血糖値が下がると foraging が呼ばれるか"""
        
        # 1. 血糖値を危険域まで下げる
        self.brain.hormones.set(Hormone.GLUCOSE, 10.0)
        
        # 2. process_metabolism を実行 (time_step を調整してスロットルを回避)
        self.brain.time_step = 10 
        self.brain.process_metabolism(cpu_percent=10, memory_percent=10, current_hour=12)
        
        # 3. Feeder.check_food が呼ばれたか確認
        self.brain.feeder.check_food.assert_called()
        
    def test_forage_and_eat_local(self):
        """冷蔵庫に食料がある場合、それを食べるか"""
        
        # Feeder がファイルを返すように設定
        self.brain.feeder.check_food.return_value = ["dummy.txt"]
        self.brain.feeder.eat.return_value = "Digestion Report"
        
        self.brain.hormones.set(Hormone.GLUCOSE, 10.0)
        self.brain.time_step = 10
        
        # Act
        self.brain.process_metabolism(10, 10, 12)
        
        # Assert
        self.brain.feeder.eat.assert_called()
        
        # 血糖値が回復しているか (30足されて40になるはず)
        # update は非同期ロックなどあるかもしれないが、同期的に更新されるはず
        glucose = self.brain.hormones.get(Hormone.GLUCOSE)
        print(f"Glucose after eating local: {glucose}")
        self.assertGreater(glucose, 10.0)

    def test_forage_aozora(self):
        """冷蔵庫が空なら青空文庫に行くか"""
        
        # Feeder は空
        self.brain.feeder.check_food.return_value = []
        
        # Aozora がテキストを返す
        self.brain.aozora.harvest.return_value = "吾輩は猫である..."
        
        self.brain.hormones.set(Hormone.GLUCOSE, 10.0)
        self.brain.time_step = 10
        
        # Act
        self.brain.process_metabolism(10, 10, 12)
        
        # Assert
        self.brain.aozora.harvest.assert_called()
        self.brain.cortex.stomach.eat.assert_called_with("吾輩は猫である...")
        
        glucose = self.brain.hormones.get(Hormone.GLUCOSE)
        print(f"Glucose after eating Aozora: {glucose}")
        self.assertGreater(glucose, 10.0)

    def test_forage_diverse(self):
        """多様な知識ソースから摂取するか"""
        
        # Feeder は空
        self.brain.feeder.check_food.return_value = []
        
        # Knowledge Manager がコンテンツを返す
        dummy_content = HarvestedContent(
            source=SourceType.WIKIPEDIA,
            title="Python",
            content="Python is a programming language...",
            url="http://wiki"
        )
        self.brain.knowledge_manager.harvest_random.return_value = dummy_content
        
        self.brain.hormones.set(Hormone.GLUCOSE, 10.0)
        self.brain.time_step = 10
        
        # random.random < 0.7 で多様なソースを選ぶようにモック
        with patch('random.random') as mock_random:
            mock_random.return_value = 0.5 # 0.7未満なら KnowledgeHarvest
            
            # Act
            self.brain.process_metabolism(10, 10, 12)
            
            # Assert
            self.brain.knowledge_manager.harvest_random.assert_called()
            self.brain.cortex.stomach.eat.assert_called_with("Python is a programming language...")
            
            glucose = self.brain.hormones.get(Hormone.GLUCOSE)
            print(f"Glucose after snacking: {glucose}")
            # 10.0 + 15.0 = 25.0 (約)
            self.assertTrue(24.0 < glucose < 26.0)

if __name__ == "__main__":
    unittest.main()
