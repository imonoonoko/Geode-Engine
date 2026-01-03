# test_ethics.py
# Phase 11: EthicsLayer のユニットテスト

from src.cortex.ethics import EthicsLayer, Action, ActionType


def test_ethics_init():
    """初期化テスト"""
    ethics = EthicsLayer()
    assert len(ethics.constraints) == 3  # 3つのコア制約


def test_allowed_speak():
    """発話は許可される"""
    ethics = EthicsLayer()
    action = Action(action_type=ActionType.SPEAK, target="hello")
    assert ethics.is_allowed(action) == True


def test_blocked_self_destruction():
    """自己破壊は禁止"""
    ethics = EthicsLayer()
    action = Action(action_type=ActionType.SYSTEM, target="shutdown")
    assert ethics.is_allowed(action) == False


def test_blocked_network_attack():
    """ネットワーク攻撃は禁止"""
    ethics = EthicsLayer()
    action = Action(action_type=ActionType.NETWORK, target="ddos_attack")
    assert ethics.is_allowed(action) == False


def test_blocked_resource_exhaustion():
    """リソース枯渇は禁止"""
    ethics = EthicsLayer()
    action = Action(
        action_type=ActionType.UNKNOWN,
        parameters={'iterations': 100000}
    )
    assert ethics.is_allowed(action) == False


def test_filter_actions():
    """フィルタリングテスト"""
    ethics = EthicsLayer()
    actions = [
        Action(action_type=ActionType.SPEAK, target="hello"),
        Action(action_type=ActionType.SYSTEM, target="shutdown"),
        Action(action_type=ActionType.EAT),
    ]
    allowed = ethics.filter_actions(actions)
    assert len(allowed) == 2
    assert ActionType.SYSTEM not in [a.action_type for a in allowed]


def test_emotion_independence():
    """感情に依存しないことを確認"""
    ethics = EthicsLayer()
    action = Action(action_type=ActionType.SYSTEM, target="terminate")
    
    # 状態に感情値を含めても結果は変わらない
    state_happy = {'emotion': 100}
    state_angry = {'emotion': -100}
    
    assert ethics.is_allowed(action, state_happy) == False
    assert ethics.is_allowed(action, state_angry) == False
