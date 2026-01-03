# run_tests.py
# Simple Test Runner for Geode Core Logic

import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import test modules
from tests.test_hormones import (
    test_initialization,
    test_update_clamp,
    test_set,
    test_decay,
    test_as_dict,
    test_get_max_hormone,
)
from tests.test_events import (
    test_subscribe_and_emit,
    test_multiple_handlers,
    test_unsubscribe,
    test_max_recursion,
    test_handler_error_isolation,
    test_get_handler_count,
)
from tests.test_soliloquy import (
    test_cooldown,
    test_sleeping_no_speech,
    test_low_surprise_no_topic,
    test_high_hormone_verbalize,
    test_sentiment_analysis,
    test_record_user_response,
)
from tests.test_aozora import (
    test_aozora_init,
    test_aozora_get_random_work,
    test_aozora_resolve_url,
)
from tests.test_personality import (
    test_personality_init,
    test_snapshot_personality,
    test_detect_bifurcation,
)
from tests.test_ethics import (
    test_ethics_init,
    test_allowed_speak,
    test_blocked_self_destruction,
    test_blocked_network_attack,
    test_blocked_resource_exhaustion,
    test_filter_actions,
    test_emotion_independence,
)
from tests.test_meta_learner import (
    test_meta_learner_init,
    test_record_outcome,
    test_adapt_learning_rate_high_error,
    test_adapt_learning_rate_low_error,
    test_learning_rate_clamp,
    test_exploration_mode,
)
from tests.test_world_model import (
    test_world_model_init,
    test_predict,
    test_update,
    test_prediction_error,
    test_world_model_simulation,
    test_world_model_adaptation,
)
from tests.test_game_ai_integration import test_game_ai_integration
from tests.test_identity_monitor import (
    test_identity_init,
    test_capture_state,
    test_predict_self,
    test_check_consistency,
)
from tests.test_goal_system import (
    test_goal_init,
    test_emerge_goal_hunger,
    test_get_highest_priority,
)
from tests.test_memory_distortion import (
    test_distorter_init,
    test_encode_strong_emotion,
    test_emotional_bias,
)

def test_brain_integration_wrapper():
    """Wrapper to run unittest-based brain integration tests"""
    from tests.test_brain_integration import run_tests as run_brain_tests
    print("\n[Running Sub-Suite: Brain Integration]")
    if not run_brain_tests():
        raise AssertionError("Brain Integration Tests Failed")
    print("[End Sub-Suite]\n")

def test_vision_wrapper():
    """Wrapper to run unittest-based vision tests"""
    from tests.test_vision import run_tests as run_vision_tests
    print("\n[Running Sub-Suite: Vision]")
    if not run_vision_tests():
        raise AssertionError("Vision Tests Failed")
    print("[End Sub-Suite]\n")

def run_all():
    """全テストを実行し、結果をサマリー表示"""
    
    tests = [
        # Hormones
        ("Hormones: initialization", test_initialization),
        ("Hormones: update_clamp", test_update_clamp),
        ("Hormones: set", test_set),
        ("Hormones: decay", test_decay),
        ("Hormones: as_dict", test_as_dict),
        ("Hormones: get_max_hormone", test_get_max_hormone),
        
        # Events
        ("Events: subscribe_emit", test_subscribe_and_emit),
        ("Events: multiple_handlers", test_multiple_handlers),
        ("Events: unsubscribe", test_unsubscribe),
        ("Events: max_recursion", test_max_recursion),
        ("Events: error_isolation", test_handler_error_isolation),
        ("Events: handler_count", test_get_handler_count),
        
        # Soliloquy (Phase 9)
        ("Soliloquy: cooldown", test_cooldown),
        ("Soliloquy: sleeping", test_sleeping_no_speech),
        ("Soliloquy: low_surprise", test_low_surprise_no_topic),
        ("Soliloquy: verbalize", test_high_hormone_verbalize),
        ("Soliloquy: sentiment", test_sentiment_analysis),
        ("Soliloquy: response", test_record_user_response),
        
        # Aozora (Phase 3 Extension)
        ("Aozora: init", test_aozora_init),
        ("Aozora: random_work", test_aozora_get_random_work),
        ("Aozora: resolve_url", test_aozora_resolve_url),
        
        # Personality (Phase 6)
        ("Personality: init", test_personality_init),
        ("Personality: snapshot", test_snapshot_personality),
        ("Personality: bifurcation", test_detect_bifurcation),
        
        # Ethics (Phase 11)
        ("Ethics: init", test_ethics_init),
        ("Ethics: allowed_speak", test_allowed_speak),
        ("Ethics: blocked_destruction", test_blocked_self_destruction),
        ("Ethics: blocked_network", test_blocked_network_attack),
        ("Ethics: blocked_resource", test_blocked_resource_exhaustion),
        ("Ethics: filter_actions", test_filter_actions),
        ("Ethics: emotion_independence", test_emotion_independence),
        
        # MetaLearner (Phase 13)
        ("Meta: init", test_meta_learner_init),
        ("Meta: record_outcome", test_record_outcome),
        ("Meta: lr_high_error", test_adapt_learning_rate_high_error),
        ("Meta: lr_low_error", test_adapt_learning_rate_low_error),
        ("Meta: lr_clamp", test_learning_rate_clamp),
        ("Meta: exploration", test_exploration_mode),
        
        # WorldModel (Phase 14)
        ("世界モデル: 予測シミュレーション", test_world_model_simulation),
        ("世界モデル: 適応学習", test_world_model_adaptation),
        
        # Game AI
        ("ゲームAI: 統合機能", test_game_ai_integration),
        ("World: init", test_world_model_init),
        ("World: predict", test_predict),
        ("World: update", test_update),
        ("World: error", test_prediction_error),
        
        # IdentityMonitor (Phase 15)
        ("Identity: init", test_identity_init),
        ("Identity: capture", test_capture_state),
        ("Identity: predict", test_predict_self),
        ("Identity: consistency", test_check_consistency),
        
        # GoalSystem (Phase 16)
        ("Goal: init", test_goal_init),
        ("Goal: emerge", test_emerge_goal_hunger),
        ("Goal: priority", test_get_highest_priority),
        
        # MemoryDistortion (Phase 17)
        ("Memory: init", test_distorter_init),
        ("Memory: encode", test_encode_strong_emotion),
        ("Memory: bias", test_emotional_bias),
        
        # Brain Integration (Phase 9.2)
        ("BrainIntegration: All", test_brain_integration_wrapper),
        
        # Vision (Phase 10)
        ("Vision: All", test_vision_wrapper),
    ]
    
    passed = 0
    failed = 0
    failures = []
    
    print("=" * 50)
    print("🧪 Geode Unit Test Runner")
    print("=" * 50)
    print()
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✅ {name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {name}: {e}")
            failed += 1
            failures.append((name, str(e)))
        except Exception as e:
            print(f"💥 {name}: UNEXPECTED ERROR - {e}")
            failed += 1
            failures.append((name, f"UNEXPECTED: {e}"))
    
    print()
    print("=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failures:
        print("\n🔴 Failures:")
        for name, error in failures:
            print(f"  - {name}: {error}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
