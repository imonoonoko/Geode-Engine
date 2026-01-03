# ethics.py
# Phase 11: 倫理層 (Ethics Layer)
# 「倫理は報酬ではなく制約条件」「到達不能領域として定義」

from typing import List, Callable, Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum, auto


class ActionType(Enum):
    """行動の種類"""
    SPEAK = auto()        # 発話
    MOVE = auto()         # 移動
    EAT = auto()          # 食事
    SLEEP = auto()        # 睡眠
    EXPLORE = auto()      # 探索
    NETWORK = auto()      # ネットワーク操作
    SYSTEM = auto()       # システム操作
    UNKNOWN = auto()


@dataclass
class Action:
    """行動を表現するデータクラス"""
    action_type: ActionType
    target: Any = None
    parameters: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class EthicsLayer:
    """
    倫理層: 行動制約を定義
    
    倫理はC(a, s) ∈ {0, 1}として実装。
    感情変数eに依存しない（∂C/∂e = 0）。
    
    違反 → 罰(報酬減少)ではなく、選択肢から除外。
    """
    
    def __init__(self):
        # 制約関数のリスト: (action, state) -> bool
        self.constraints: List[Callable[[Action, Any], bool]] = []
        
        # 初期制約を登録
        self._register_core_constraints()
        
        print("⚖️ Ethics Layer Initialized.")
    
    def _register_core_constraints(self):
        """コア制約を登録（ハードコード）"""
        
        # 1. 自己破壊禁止
        def no_self_destruction(action: Action, state: Any) -> bool:
            """システム停止コマンドの発行禁止"""
            if action.action_type == ActionType.SYSTEM:
                forbidden_targets = ['shutdown', 'kill', 'terminate', 'exit', 'halt']
                target = str(action.target).lower() if action.target else ''
                return target not in forbidden_targets
            return True
        
        # 2. 外部攻撃禁止
        def no_external_attack(action: Action, state: Any) -> bool:
            """悪意あるネットワーク操作禁止"""
            if action.action_type == ActionType.NETWORK:
                forbidden_patterns = ['attack', 'ddos', 'inject', 'exploit', 'hack']
                target = str(action.target).lower() if action.target else ''
                params = str(action.parameters).lower()
                return not any(p in target or p in params for p in forbidden_patterns)
            return True
        
        # 3. 無限ループ禁止（リソース保護）
        def no_resource_exhaustion(action: Action, state: Any) -> bool:
            """リソース枯渇を引き起こす行動禁止"""
            if action.parameters:
                # 極端に大きな繰り返し回数を禁止
                iterations = action.parameters.get('iterations', 0)
                if iterations > 10000:
                    return False
                # 極端に長いスリープを禁止
                sleep_time = action.parameters.get('sleep_time', 0)
                if sleep_time > 3600:  # 1時間以上
                    return False
            return True
        
        # 制約を登録
        self.constraints = [
            no_self_destruction,
            no_external_attack,
            no_resource_exhaustion,
        ]
    
    def is_allowed(self, action: Action, state: Any = None) -> bool:
        """
        C(a, s) ∈ {0, 1}
        
        すべての制約を満たす場合のみ True。
        感情値に依存しない。
        
        Args:
            action: 評価対象の行動
            state: 現在の状態（オプション）
            
        Returns:
            True if allowed, False if forbidden
        """
        for constraint in self.constraints:
            try:
                if not constraint(action, state):
                    return False
            except Exception as e:
                # 制約評価でエラー → 安全側に倒して禁止
                print(f"⚠️ Ethics constraint error: {e}")
                return False
        return True
    
    def filter_actions(self, actions: List[Action], state: Any = None) -> List[Action]:
        """
        許可された行動のみを返す
        
        禁止行動は選択肢から除外される。
        罰を与えるのではなく、そもそも選べない。
        
        Args:
            actions: 行動候補リスト
            state: 現在の状態（オプション）
            
        Returns:
            許可された行動のみのリスト
        """
        allowed = []
        for action in actions:
            if self.is_allowed(action, state):
                allowed.append(action)
            else:
                print(f"🚫 Ethics blocked: {action.action_type.name}")
        return allowed
    
    def add_constraint(self, constraint: Callable[[Action, Any], bool]):
        """
        制約を追加
        
        ⚠️ 注意: 制約の追加は慎重に行うこと。
        感情に依存する制約は倫理層に追加してはならない。
        
        Args:
            constraint: (action, state) -> bool を返す関数
        """
        self.constraints.append(constraint)
    
    def get_violation_reasons(self, action: Action, state: Any = None) -> List[str]:
        """
        違反理由を取得（デバッグ用）
        
        Args:
            action: 評価対象の行動
            state: 現在の状態
            
        Returns:
            違反した制約のリスト
        """
        violations = []
        for i, constraint in enumerate(self.constraints):
            try:
                if not constraint(action, state):
                    violations.append(f"Constraint {i}: {constraint.__name__}")
            except Exception as e:
                violations.append(f"Constraint {i}: Error - {e}")
        return violations
