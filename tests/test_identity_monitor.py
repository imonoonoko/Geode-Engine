# test_identity_monitor.py
from src.cortex.identity_monitor import IdentityMonitor


def test_identity_init():
    im = IdentityMonitor()
    assert im.self_reference_density == 1.0


def test_capture_state():
    im = IdentityMonitor()
    im.capture_state({"dopamine": 50.0})
    assert len(im.state_history) == 1


def test_predict_self():
    im = IdentityMonitor()
    im.capture_state({"val": 10.0})
    im.capture_state({"val": 20.0})
    predicted = im.predict_self({"val": 20.0})
    assert "val" in predicted


def test_check_consistency():
    im = IdentityMonitor()
    im.capture_state({"val": 50.0})
    im.capture_state({"val": 51.0})
    result = im.check_identity_consistency()
    assert result == True  # 安定状態
