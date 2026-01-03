# test_meta_learner.py
# Phase 13: MetaLearner のユニットテスト

from src.cortex.meta_learner import MetaLearner


def test_meta_learner_init():
    """初期化テスト"""
    ml = MetaLearner()
    assert ml.learning_rate == 0.1
    assert ml.exploration_rate == 0.3


def test_record_outcome():
    """結果記録テスト"""
    ml = MetaLearner()
    ml.record_outcome("speak", 0.5, 0.6)
    assert len(ml.error_history) == 1


def test_adapt_learning_rate_high_error():
    """高誤差時の学習率上昇テスト"""
    ml = MetaLearner()
    # 高誤差を複数回記録
    for _ in range(10):
        ml.record_outcome("action", 0.0, 1.0)  # 誤差 = 1.0
    
    old_lr = ml.learning_rate
    ml.adapt_learning_rate()
    assert ml.learning_rate > old_lr


def test_adapt_learning_rate_low_error():
    """低誤差時の学習率低下テスト"""
    ml = MetaLearner()
    # 低誤差を複数回記録
    for _ in range(10):
        ml.record_outcome("action", 0.5, 0.51)  # 誤差 = 0.01
    
    old_lr = ml.learning_rate
    ml.adapt_learning_rate()
    assert ml.learning_rate < old_lr


def test_learning_rate_clamp():
    """学習率クリップテスト"""
    ml = MetaLearner()
    # 極端に高い誤差を大量に記録
    for _ in range(100):
        ml.record_outcome("action", 0.0, 1.0)
        ml.adapt_learning_rate()
    
    assert ml.learning_rate <= ml.lr_max


def test_exploration_mode():
    """探索モード判定テスト"""
    ml = MetaLearner()
    # 100回試行して、探索が発生することを確認
    explorations = sum(1 for _ in range(100) if ml.should_explore())
    assert 10 < explorations < 90  # 確率的なので範囲で確認
