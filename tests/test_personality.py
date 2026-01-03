
from src.cortex.personality_field import PersonalityField
import numpy as np

class MockBrain:
    class MockHormones:
        def get(self, name): return 50.0
        def as_dict(self): return {"feature": 50.0}
    
    class MockPredictionEngine:
        def __init__(self):
            self.state_vector = np.random.rand(10)
            self.surprise_history = [0.1, 0.2]

    class MockMemory:
        def get_all_concepts(self): return ["test", "concept"]

    class MockStomach:
        def __init__(self):
            # NetworkX graph like object
            self.brain_graph = self
        def edges(self, data=False): return [("a", "b", {"weight": 1.0})]

    class MockCortex:
        def __init__(self):
            self.stomach = MockBrain.MockStomach()

    def __init__(self):
        self.hormones = self.MockHormones()
        self.prediction_engine = self.MockPredictionEngine()
        self.memory = self.MockMemory()
        self.cortex = self.MockCortex()

def test_personality_init():
    """初期化テスト"""
    pf = PersonalityField()
    assert pf.personalities == {}

def test_snapshot_personality():
    """スナップショット取得テスト"""
    pf = PersonalityField()
    brain = MockBrain()
    
    p_id = pf.snapshot_personality(brain)
    assert p_id in pf.personalities
    
    snapshot = pf.personalities[p_id]
    snapshot = pf.personalities[p_id]
    assert hasattr(snapshot, "state_vector")
    assert hasattr(snapshot, "meaning_generation")
    
    assert 0.0 <= snapshot.meaning_generation <= 1.0

def test_detect_bifurcation():
    """分岐検出テスト"""
    pf = PersonalityField()
    brain = MockBrain()
    
    # 1つ目のスナップショット
    id1 = pf.snapshot_personality(brain)
    
    # 状態を大きく変更
    brain.prediction_engine.state_vector = np.random.rand(10) * 100
    id2 = pf.snapshot_personality(brain)
    
    # 辞書が返される
    result = pf.detect_bifurcation(id1, id2)
    assert result["total_distance"] > 0.0
    assert "is_bifurcated" in result
