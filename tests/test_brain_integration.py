"""
Phase 9.2 Brain統合 自動テスト
Minecraftに接続せずにBrain統合が正しく動作するかテストする
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestHormonePresets(unittest.TestCase):
    """ホルモンプリセットのテスト"""
    
    def test_game_mode_preset_exists(self):
        """GAME_MODEプリセットが存在する"""
        from src.dna.hormone_presets import HormonePresets
        preset = HormonePresets.get_preset("game")
        self.assertIsNotNone(preset)
        self.assertIn("dopamine", preset)
        self.assertIn("boredom", preset)
    
    def test_game_mode_values(self):
        """GAME_MODEプリセットの値が正しい"""
        from src.dna.hormone_presets import HormonePresets
        preset = HormonePresets.GAME_MODE
        self.assertEqual(preset["dopamine"], 70.0)
        self.assertEqual(preset["boredom"], 10.0)
    
    def test_all_presets_exist(self):
        """すべてのプリセットが存在する"""
        from src.dna.hormone_presets import HormonePresets
        presets = ["game", "exploration", "survival", "relax", "learning"]
        for name in presets:
            preset = HormonePresets.get_preset(name)
            self.assertIsNotNone(preset, f"Preset '{name}' not found")


class TestMineflayerEnv(unittest.TestCase):
    """MineflayerEnvのテスト（モック使用）"""
    
    def test_brain_reference_can_be_set(self):
        """Brain参照を設定できる"""
        from src.games.minecraft.mineflayer_env import MineflayerEnv
        
        env = MineflayerEnv()
        mock_brain = Mock()
        env.brain = mock_brain
        
        self.assertEqual(env.brain, mock_brain)
    
    def test_create_action_forward(self):
        """MOVE_FORWARDアクションを作成できる"""
        from src.games.minecraft.mineflayer_env import MineflayerEnv
        
        env = MineflayerEnv()
        action = env.create_action("MOVE_FORWARD", duration=0.5)
        
        self.assertEqual(action["type"], "MOVE_FORWARD")
        self.assertEqual(action["duration"], 500)  # 秒→ミリ秒
    
    def test_reward_calculation_positive(self):
        """移動成功時に正の報酬が計算される"""
        from src.games.minecraft.mineflayer_env import MineflayerEnv
        
        env = MineflayerEnv()
        env._last_position = {"x": 0, "y": 64, "z": 0}
        
        prev_state = {"position": {"x": 0, "y": 64, "z": 0}, "health": 20}
        new_state = {"position": {"x": 5, "y": 64, "z": 5}, "health": 20}
        action = {"type": "MOVE_FORWARD"}
        
        reward = env._calculate_reward(prev_state, new_state, action)
        self.assertGreater(reward, 0, "移動成功時は正の報酬")
    
    def test_reward_calculation_stuck(self):
        """移動失敗時（引っかかり）に負の報酬が計算される"""
        from src.games.minecraft.mineflayer_env import MineflayerEnv
        
        env = MineflayerEnv()
        env._last_position = {"x": 0, "y": 64, "z": 0}
        
        prev_state = {"position": {"x": 0, "y": 64, "z": 0}, "health": 20}
        new_state = {"position": {"x": 0, "y": 64, "z": 0}, "health": 20}  # 動いていない
        action = {"type": "MOVE_FORWARD"}
        
        reward = env._calculate_reward(prev_state, new_state, action)
        self.assertLess(reward, 0, "移動失敗時は負の報酬")


class TestBrainIntegration(unittest.TestCase):
    """Brain統合のテスト"""
    
    @patch('src.games.minecraft.mineflayer_env.requests')
    def test_reward_updates_hormones(self, mock_requests):
        """報酬がホルモンを更新する"""
        from src.games.minecraft.mineflayer_env import MineflayerEnv
        from src.body.hormones import Hormone
        
        # モックBrainを作成
        mock_brain = Mock()
        mock_brain.hormones = Mock()
        mock_brain.hormones.get = Mock(return_value=50.0)
        
        env = MineflayerEnv()
        env.brain = mock_brain
        
        # 正の報酬を送信
        env._send_reward_to_brain(1.0)
        
        # ドーパミンが更新されたことを確認
        mock_brain.hormones.update.assert_called()
    
    def test_get_intent_from_brain_high_boredom(self):
        """退屈度が高い時は探索的行動が選ばれる"""
        from src.games.minecraft.mineflayer_env import MineflayerEnv
        from src.body.hormones import Hormone
        
        # モックBrainを作成（高い退屈度）
        mock_brain = Mock()
        mock_brain.hormones = Mock()
        mock_brain.hormones.get = Mock(side_effect=lambda h: 80.0 if h == Hormone.BOREDOM else 30.0)
        
        env = MineflayerEnv()
        env.brain = mock_brain
        
        # 複数回テストして探索的行動が含まれることを確認
        intents = [env._get_intent_from_brain({}) for _ in range(10)]
        exploratory = ["TURN_LEFT", "TURN_RIGHT", "JUMP"]
        
        has_exploration = any(intent in exploratory for intent in intents)
        self.assertTrue(has_exploration, "退屈時は探索的行動が含まれるべき")
    
    def test_process_spatial_memory_is_called(self):
        """意図取得時に空間記憶処理が呼ばれる"""
        from src.games.minecraft.mineflayer_env import MineflayerEnv
        
        mock_brain = Mock()
        mock_brain.hormones = Mock()
        mock_brain.hormones.get = Mock(return_value=50.0)
        mock_brain.process_spatial_memory = Mock()
        # intentもbrainに委譲されるようになったためMock
        mock_brain.decide_minecraft_intent = Mock(return_value="MOVE_FORWARD")
        
        env = MineflayerEnv()
        env.brain = mock_brain
        
        state = {"position": {"x": 100, "y": 64, "z": 200}}
        env._get_intent_from_brain(state)
        
        # process_spatial_memoryが呼ばれたか確認
        mock_brain.process_spatial_memory.assert_called_with(state["position"])

    def test_spatial_memory_logic(self):
        """空間記憶ロジックが正しくホルモンを更新する"""
        from src.brain_stem.brain import KanameBrain
        from src.body.hormones import Hormone
        from unittest.mock import MagicMock
        
        brain = KanameBrain()
        brain.memory = MagicMock()
        brain.hormones = MagicMock()
        # Fix: Recursive Mocking for SpatialCortex
        if hasattr(brain, 'spatial'):
            brain.spatial.memory = brain.memory
            brain.spatial.hormones = brain.hormones
        
        # Case A: New Location (count <= 1)
        brain.memory.get_coords.return_value = [512, 512]
        brain.memory.concepts.get.return_value = [512, 512, 0, 1, 0.0] 
        
        brain.process_spatial_memory({"x": 160, "y": 64, "z": 160})
        
        update_calls = [args[0] for args, kwargs in brain.hormones.update.call_args_list]
        self.assertIn(Hormone.DOPAMINE, update_calls)
    
    def test_decide_minecraft_intent(self):
        """勾配に基づく行動決定ロジックのテスト"""
        from src.brain_stem.brain import KanameBrain
        from src.body.hormones import Hormone
        from unittest.mock import MagicMock
        
        brain = KanameBrain()
        brain.hormones = MagicMock()
        brain.memory = MagicMock()
        # Fix: Recursive Mocking for SpatialCortex
        if hasattr(brain, 'spatial'):
            brain.spatial.memory = brain.memory
            brain.spatial.hormones = brain.hormones
        
        # Mock memory gradient: North is best (3.14)
        # North scores highest
        brain.memory.get_spatial_gradient.return_value = {
            "North": 0.9, "South": 0.1, "East": 0.1, "West": 0.1
        }
        
        # Current State: Facing South (Yaw=0)
        # Should turn LEFT or RIGHT towards North (PI)
        # Diff = PI - 0 = PI (Positive) -> TURN_LEFT
        state = {"position": {"x": 0, "y": 64, "z": 0, "yaw": 0.0}}
        
        # Ensure move_chance passes
        with patch('random.random', return_value=0.0): # 0.0 < move_chance
             intent = brain.decide_minecraft_intent(state)
             
        self.assertIn(intent, ["TURN_LEFT", "TURN_RIGHT"])



class TestStartScriptImports(unittest.TestCase):
    """起動スクリプトのインポートテスト"""
    
    def test_can_import_hormone_presets(self):
        """HormonePresetsをインポートできる"""
        try:
            from src.dna.hormone_presets import HormonePresets
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import HormonePresets: {e}")
    
    def test_can_import_mineflayer_env(self):
        """MineflayerEnvをインポートできる"""
        try:
            from src.games.minecraft.mineflayer_env import MineflayerEnv
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import MineflayerEnv: {e}")


def run_tests():
    """テストを実行"""
    print("=" * 60)
    print("🧪 Phase 9.2 Brain Integration Tests")
    print("=" * 60)
    print()
    
    # テストスイートを作成
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # すべてのテストクラスを追加
    suite.addTests(loader.loadTestsFromTestCase(TestHormonePresets))
    suite.addTests(loader.loadTestsFromTestCase(TestMineflayerEnv))
    suite.addTests(loader.loadTestsFromTestCase(TestBrainIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestStartScriptImports))
    
    # テストを実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
