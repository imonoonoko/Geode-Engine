# test_events.py
# Unit Tests for EventBus

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.body.events import Event, EventBus


def test_subscribe_and_emit():
    """基本的な Pub/Sub が動作するか"""
    bus = EventBus()
    called = []
    
    def handler(**kwargs):
        called.append(kwargs)
    
    bus.subscribe(Event.POKED, handler)
    bus.emit(Event.POKED, source="test")
    
    assert len(called) == 1, f"Expected 1 call, got {len(called)}"
    assert called[0].get("source") == "test", f"Expected source='test', got {called[0]}"


def test_multiple_handlers():
    """複数ハンドラが呼ばれるか"""
    bus = EventBus()
    count = [0]
    
    def handler1(**kwargs):
        count[0] += 1
    
    def handler2(**kwargs):
        count[0] += 1
    
    bus.subscribe(Event.POKED, handler1)
    bus.subscribe(Event.POKED, handler2)
    
    bus.emit(Event.POKED)
    assert count[0] == 2, f"Expected 2 calls, got {count[0]}"


def test_unsubscribe():
    """ハンドラの登録解除が機能するか"""
    bus = EventBus()
    count = [0]
    
    def handler(**kwargs):
        count[0] += 1
    
    bus.subscribe(Event.POKED, handler)
    bus.unsubscribe(Event.POKED, handler)
    bus.emit(Event.POKED)
    
    assert count[0] == 0, f"Expected 0 calls after unsubscribe, got {count[0]}"


def test_max_recursion():
    """無限ループ防止が機能するか"""
    bus = EventBus()
    depth = [0]
    
    def recursive_handler(**kwargs):
        depth[0] += 1
        bus.emit(Event.POKED)  # 再帰発火
    
    bus.subscribe(Event.POKED, recursive_handler)
    bus.emit(Event.POKED)
    
    # Should stop at max_depth (default 5)
    assert depth[0] <= 6, f"Recursion not stopped, depth={depth[0]}"


def test_handler_error_isolation():
    """1つのハンドラがエラーでも他は実行されるか"""
    bus = EventBus()
    results = []
    
    def bad_handler(**kwargs):
        raise ValueError("Intentional Error")
    
    def good_handler(**kwargs):
        results.append("success")
    
    bus.subscribe(Event.POKED, bad_handler)
    bus.subscribe(Event.POKED, good_handler)
    
    # Should not raise, and good_handler should run
    bus.emit(Event.POKED)
    
    assert "success" in results, "Good handler was not called after bad handler error"


def test_get_handler_count():
    """ハンドラ数の取得が正しいか"""
    bus = EventBus()
    
    assert bus.get_handler_count(Event.POKED) == 0
    
    bus.subscribe(Event.POKED, lambda **k: None)
    bus.subscribe(Event.POKED, lambda **k: None)
    
    assert bus.get_handler_count(Event.POKED) == 2, \
        f"Expected 2, got {bus.get_handler_count(Event.POKED)}"
