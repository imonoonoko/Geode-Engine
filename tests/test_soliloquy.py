# test_soliloquy.py
# Unit Tests for SoliloquyManager

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from unittest.mock import MagicMock, PropertyMock

# Mock brain for testing
class MockHormoneManager:
    def __init__(self):
        self.data = {
            'DOPAMINE': 30.0,
            'SEROTONIN': 50.0,
            'ADRENALINE': 20.0,
            'CORTISOL': 10.0,
            'SURPRISE': 0.3,
            'BOREDOM': 20.0,
            'GLUCOSE': 50.0,
        }
    
    def get(self, hormone):
        return self.data.get(hormone.name, 0.0)
    
    def get_max_hormone(self):
        from src.body.hormones import Hormone
        # Return highest non-glucose hormone
        max_h = Hormone.SEROTONIN
        max_v = 0
        for name, val in self.data.items():
            if name not in ['GLUCOSE', 'SURPRISE'] and val > max_v:
                max_v = val
                try:
                    max_h = getattr(Hormone, name)
                except:
                    pass
        return (max_h, max_v)


class MockBrain:
    def __init__(self):
        self.hormones = MockHormoneManager()
        self.is_sleeping = False
        self.neurons = []
        self.cortex = None


def test_cooldown():
    """クールダウン中は発話しない"""
    from src.cortex.soliloquy import SoliloquyManager
    
    brain = MockBrain()
    sm = SoliloquyManager(brain)
    
    # 直後に連続呼び出し
    sm.last_utterance_time = time.time()
    
    result = sm.think_aloud()
    assert result is None, "Should not speak during cooldown"


def test_sleeping_no_speech():
    """睡眠中は発話しない"""
    from src.cortex.soliloquy import SoliloquyManager
    
    brain = MockBrain()
    brain.is_sleeping = True
    sm = SoliloquyManager(brain)
    sm.last_utterance_time = 0  # Reset cooldown
    
    result = sm.think_aloud()
    assert result is None, "Should not speak while sleeping"


def test_low_surprise_no_topic():
    """surprise が低い時は Lv1 からトピックを選ばない"""
    from src.cortex.soliloquy import SoliloquyManager
    
    brain = MockBrain()
    brain.hormones.data['SURPRISE'] = 0.1  # Low surprise
    sm = SoliloquyManager(brain)
    
    topic = sm.select_topic_by_surprise()
    assert topic is None, "Should not select topic with low surprise"


def test_high_hormone_verbalize():
    """高いホルモン状態で概念が返される (存在確認のみ)"""
    from src.cortex.soliloquy import SoliloquyManager
    from src.body.hormones import Hormone
    
    brain = MockBrain()
    brain.hormones.data['DOPAMINE'] = 80.0  # High dopamine
    sm = SoliloquyManager(brain)
    
    # 概念が存在しない場合は None
    result = sm.verbalize_internal_state()
    # None is expected because no memory/cortex exists
    assert result is None, "Should return None when concept doesn't exist in memory"


def test_sentiment_analysis():
    """感情分析が正しく動作するか"""
    from src.cortex.soliloquy import SoliloquyManager
    
    brain = MockBrain()
    sm = SoliloquyManager(brain)
    
    # Positive
    score = sm._analyze_sentiment("楽しいね！ありがとう！")
    assert score > 0, f"Expected positive score, got {score}"
    
    # Negative
    score = sm._analyze_sentiment("嫌だ、黙れ")
    assert score < 0, f"Expected negative score, got {score}"
    
    # Neutral (no sentiment words)
    score = sm._analyze_sentiment("今日は雨だ")
    assert score == 0.0, f"Expected 0, got {score}"


def test_record_user_response():
    """ユーザー反応の記録が正しく動作するか"""
    from src.cortex.soliloquy import SoliloquyManager
    
    brain = MockBrain()
    sm = SoliloquyManager(brain)
    sm.last_utterance = "テスト発話"
    
    sm.record_user_response("ありがとう！嬉しい！")
    
    assert len(sm.user_response_history) == 1
    assert sm.user_response_history[0]['utterance'] == "テスト発話"
    assert sm.user_response_history[0]['score'] > 0
