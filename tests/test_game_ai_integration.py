# tests/test_game_ai_integration.py
# Game AI 統合機能のテスト

import unittest
import numpy as np
from unittest.mock import MagicMock
from src.games.integrated_rl_agent import IntegratedRLAgent
import time

class TestGameAIIntegration(unittest.TestCase):
    
    def setUp(self):
        # モック Brain の作成
        self.brain_mock = MagicMock()
        
        # MetaLearner モック
        self.meta_learner_mock = MagicMock()
        self.meta_learner_mock.current_learning_rate = 0.15
        self.meta_learner_mock.current_exploration_rate = 0.25
        # プロパティアクセスのモック設定
        type(self.meta_learner_mock).learning_rate = 0.1
        type(self.meta_learner_mock).exploration_rate = 0.1
        
        # WorldModel モック
        self.world_model_mock = MagicMock()
        self.world_model_mock.get_best_action.return_value = 1
        self.world_model_mock.update.return_value = 0.05  # 予測誤差
        
        # GeologicalMemory モック
        self.memory_mock = MagicMock()
        
        # モック Brain に各モジュールをアタッチ
        self.brain_mock.meta_learner = self.meta_learner_mock
        self.brain_mock.world_model = self.world_model_mock
        self.brain_mock.cortex = MagicMock()
        self.brain_mock.cortex.memory = self.memory_mock
    
    def test_Geode_integration_initialization(self):
        """Geode のモジュールと正しく接続されるかテスト"""
        agent = IntegratedRLAgent(action_size=4, brain=self.brain_mock)
        
        self.assertIsNotNone(agent.meta_learner)
        self.assertIsNotNone(agent.world_model)
        self.assertIsNotNone(agent.memory)
        self.assertEqual(agent.meta_learner, self.meta_learner_mock)
    
    def test_select_action_with_world_model(self):
        """WorldModel の予測を使用してアクションを選択するかテスト"""
        agent = IntegratedRLAgent(action_size=4, brain=self.brain_mock)
        
        # 探索を無効化（常に WorldModel を使うように）
        agent.epsilon = 0.0
        # MetaLearner の探索率をモックで制御
        type(self.meta_learner_mock).exploration_rate = unittest.mock.PropertyMock(return_value=0.0)
        
        state = np.zeros((4, 84, 84), dtype=np.uint8)
        
        # WorldModel がアクション 1 を推奨
        self.world_model_mock.get_best_action.return_value = 1
        
        action = agent.select_action(state, "test_game")
        
        # WorldModel が呼ばれたか確認
        self.world_model_mock.get_best_action.assert_called()
        self.assertEqual(action, 1)
        
    def test_remember_records_to_memory(self):
        """経験が GeologicalMemory に記録されるかテスト"""
        agent = IntegratedRLAgent(action_size=4, brain=self.brain_mock)
        
        state = np.zeros((4, 84, 84), dtype=np.uint8)
        next_state = np.zeros((4, 84, 84), dtype=np.uint8)
        
        # 経験を記録（成功体験）
        agent.remember(state, action=1, reward=10.0, next_state=next_state, done=False, game_type="test_game")
        
        # modify_terrain が呼ばれたか確認
        self.memory_mock.modify_terrain.assert_called()
        args = self.memory_mock.modify_terrain.call_args[0]
        
        # 概念名が gm_test_game_success 形式
        self.assertIn("gm_test_game_success", args[0])
        # 感情値が正（報酬が正なので）
        self.assertGreater(args[1], 0)
        


def test_game_ai_integration():
    """run_tests.py から呼び出すためのラッパー"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGameAIIntegration)
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    if not result.wasSuccessful():
        raise AssertionError("Game AI Integration Tests Failed")
