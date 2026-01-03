# body_interface.py
"""
Phase 6: Body Hardware Abstraction Layer (HAL)
身体制御の抽象化レイヤー。
将来的に2D画面、Live2D、ロボットなど様々な身体実装に対応可能にする。
"""

from typing import Protocol, Tuple, Optional
from abc import ABC, abstractmethod


class BodyProtocol(Protocol):
    """
    身体実装が満たすべきインターフェース (Protocol)
    Python 3.8+ の typing.Protocol を使用。
    """
    
    def apply_force(self, fx: float, fy: float) -> None:
        """
        身体に力を加える (移動指令)
        fx: X方向の力 (-1.0 ~ 1.0)
        fy: Y方向の力 (-1.0 ~ 1.0)
        """
        ...
    
    def get_position(self) -> Tuple[float, float]:
        """
        現在の位置を取得
        戻り値: (x, y)
        """
        ...
    
    def express(self, emotion: str) -> None:
        """
        感情を表現する (表情変更、色変更など)
        emotion: "joy", "sadness", "anger", "fear", "love", "sleep" など
        """
        ...
    
    def pulse(self, bpm: int) -> None:
        """
        心拍を表現する (点滅、振動など)
        bpm: 心拍数
        """
        ...


class BodyHAL:
    """
    身体ハードウェア抽象化レイヤー
    実際の身体実装への橋渡し役。
    """
    
    def __init__(self, body_impl: Optional[BodyProtocol] = None):
        """
        body_impl: BodyProtocol を満たす実装 (KanameBodyなど)
        """
        self._body = body_impl
        self.brain_ref = None
    
    def connect(self, body_impl: BodyProtocol) -> None:
        """身体実装を接続する"""
        self._body = body_impl
        print("🤖 Body HAL: Connected to body implementation.")
    
    def disconnect(self) -> None:
        """身体実装を切断する"""
        self._body = None
        print("🤖 Body HAL: Disconnected.")
    
    @property
    def is_connected(self) -> bool:
        return self._body is not None
    
    def apply_force(self, fx: float, fy: float) -> None:
        """脳からの移動指令を身体に伝達"""
        if self._body:
            self._body.apply_force(fx, fy)
    
    def get_position(self) -> Tuple[float, float]:
        """身体の現在位置を取得"""
        if self._body:
            return self._body.get_position()
        return (0.0, 0.0)
    
    def send_sense(self, sense_type: str, data: str = ""):
        """ 感覚データを脳へ送信 """
        if self.brain_ref:
            # 辞書形式にラップして送信
            payload = {sense_type: 1.0, "data": data}
            self.brain_ref.receive_sense(payload)
    
    def express(self, emotion: str) -> None:
        """感情表現を身体に伝達"""
        if self._body:
            self._body.express(emotion)
    
    def pulse(self, bpm: int) -> None:
        """心拍表現を身体に伝達"""
        if self._body:
            self._body.pulse(bpm)

