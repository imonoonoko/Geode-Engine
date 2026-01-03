# test_world_model.py
# Phase 14: WorldModel のユニットテスト

from src.cortex.world_model import WorldModel


def test_world_model_init():
    """初期化テスト"""
    wm = WorldModel()
    assert wm.learning_rate == 0.1
    assert len(wm.transition_model) == 0


def test_predict():
    """予測テスト"""
    wm = WorldModel()
    state = {"dopamine": 50.0, "cortisol": 30.0}
    predicted = wm.predict(state, "eat")
    assert "dopamine" in predicted
    assert "cortisol" in predicted


def test_update():
    """更新テスト"""
    wm = WorldModel()
    state = {"dopamine": 50.0}
    predicted = wm.predict(state, "eat")
    actual = {"dopamine": 60.0}
    
    error = wm.update(predicted, actual, "eat")
    assert error > 0


def test_prediction_error():
    """予測誤差計算テスト"""
    wm = WorldModel()
    
    # 複数の予測と更新
    for i in range(10):
        state = {"val": float(i)}
        predicted = wm.predict(state, "act")
        actual = {"val": float(i + 1)}
        wm.update(predicted, actual, "act")
    
    error = wm.get_prediction_error()
    assert error >= 0

def test_world_model_simulation():
    """シミュレーションテスト（run_tests.py から参照）"""
    wm = WorldModel()
    state = {"pos_x": 0.0}
    actions = ["move_right", "move_right", "move_left"]
    
    # 遷移モデルを学習させる
    wm.transition_model[("move_right", "pos_x")] = 1.0
    wm.transition_model[("move_left", "pos_x")] = -1.0
    
    trajectory = wm.simulate(state, actions)
    
    assert len(trajectory) == 4  # 初期状態 + 3アクション
    assert trajectory[-1]["pos_x"] == 1.0  # 0 + 1 + 1 - 1 = 1


def test_world_model_adaptation():
    """適応学習テスト（run_tests.py から参照）"""
    wm = WorldModel()
    state = {"val": 10.0}
    
    # 最初は予測が外れる
    predicted = wm.predict(state, "up")
    actual = {"val": 15.0} # +5
    
    error1 = wm.update(predicted, actual, "up")
    
    # 学習後の予測
    predicted2 = wm.predict(state, "up")
    # 学習率0.1なので、予測誤差5.0 * 0.1 = 0.5 だけ遷移モデルが更新される
    # 次の予測は 10.0 + 0.5 = 10.5
    
    assert predicted2["val"] > predicted["val"]
