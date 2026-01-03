# events.py
# Kaname Event System - Pub/Sub Pattern for Decoupled Architecture

from enum import Enum, auto
from typing import Callable, Dict, List, Any
import threading

class Event(Enum):
    """
    システム全体で使用するイベントタイプの定義。
    各イベントは「何が起きたか」を表し、「どう反応するか」は購読者が決める。
    """
    # ==========================================
    # 🖱️ User Interaction Events
    # ==========================================
    POKED = auto()           # つつかれた (クリック)
    PETTED = auto()          # 撫でられた (カーソル移動)
    DRAGGED = auto()         # ドラッグされた
    
    # ==========================================
    # 🍽️ Feeding Events
    # ==========================================
    FILE_RECEIVED = auto()   # ファイル受信開始
    DIGESTION_COMPLETE = auto() # 消化完了
    REJECTED_FOOD = auto()   # 食事拒否 (サプライズ高すぎ等)
    
    # ==========================================
    # 🧠 Cognitive Events
    # ==========================================
    THOUGHT_COMPLETE = auto() # 思考1サイクル完了
    MEMORY_FORMED = auto()    # 記憶形成
    SURPRISE_SPIKE = auto()   # 驚き急上昇
    
    # ==========================================
    # ⚠️ System Events
    # ==========================================
    ERROR_OCCURRED = auto()  # エラー発生 (免疫系)
    SYSTEM_TICK = auto()     # メインループ1回 (1Hz)
    SHUTDOWN = auto()        # シャットダウン開始


class EventBus:
    """
    シンプルな同期イベントバス。
    スレッドセーフなハンドラ登録と発火を提供。
    """
    def __init__(self):
        self._handlers: Dict[Event, List[Callable]] = {}
        self._lock = threading.Lock()
        self._emit_depth = 0  # 再帰検知用
        self._max_depth = 5   # 無限ループ防止
        self._debug = False   # デバッグログ
    
    def subscribe(self, event: Event, handler: Callable) -> None:
        """
        イベントにハンドラを登録する。
        同じハンドラを重複登録しても1つとして扱う。
        """
        with self._lock:
            if event not in self._handlers:
                self._handlers[event] = []
            if handler not in self._handlers[event]:
                self._handlers[event].append(handler)
                if self._debug:
                    print(f"📡 [EventBus] Subscribed: {event.name} -> {handler.__name__}")
    
    def unsubscribe(self, event: Event, handler: Callable) -> None:
        """
        ハンドラを登録解除する。
        """
        with self._lock:
            if event in self._handlers and handler in self._handlers[event]:
                self._handlers[event].remove(handler)
    
    def emit(self, event: Event, **kwargs) -> None:
        """
        イベントを発火し、登録された全ハンドラを呼び出す。
        再帰発火は _max_depth まで許可（無限ループ防止）。
        """
        # 再帰検知
        if self._emit_depth >= self._max_depth:
            print(f"⚠️ [EventBus] Max recursion depth reached for {event.name}")
            return
        
        self._emit_depth += 1
        
        if self._debug:
            print(f"🎯 [EventBus] Emit: {event.name} {kwargs if kwargs else ''}")
        
        # ハンドラリストのコピーを取得（発火中の登録変更に対応）
        with self._lock:
            handlers = list(self._handlers.get(event, []))
        
        for handler in handlers:
            try:
                handler(**kwargs)
            except Exception as e:
                print(f"⚠️ [EventBus] Handler error in {event.name}: {e}")
                # エラーが発生しても他のハンドラは続行
        
        self._emit_depth -= 1
    
    def set_debug(self, enabled: bool) -> None:
        """
        デバッグログの有効化/無効化。
        """
        self._debug = enabled
        print(f"📡 [EventBus] Debug mode: {'ON' if enabled else 'OFF'}")
    
    def get_handler_count(self, event: Event) -> int:
        """
        イベントに登録されているハンドラ数を取得。
        """
        with self._lock:
            return len(self._handlers.get(event, []))
