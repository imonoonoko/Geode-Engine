# game_vision.py
# ゲーム画面のOCR + 概念学習
# ゲーム内の文字を読み取り、Kanameの概念として学習

import time
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

# OCR ライブラリ（easyocr または pytesseract）
try:
    import easyocr
    _OCR_AVAILABLE = True
    _OCR_TYPE = "easyocr"
except ImportError:
    try:
        import pytesseract
        _OCR_AVAILABLE = True
        _OCR_TYPE = "pytesseract"
    except ImportError:
        _OCR_AVAILABLE = False
        _OCR_TYPE = None


@dataclass
class GameText:
    """ゲーム内の認識テキスト"""
    text: str
    confidence: float
    position: Tuple[int, int, int, int]  # x1, y1, x2, y2
    timestamp: float = field(default_factory=time.time)


class GameVision:
    """
    ゲーム視覚システム
    
    - OCR でゲーム画面の文字を読み取る
    - 読み取った文字を概念として記録
    - WordStateBinding と連携して文字の意味を学習
    """
    
    def __init__(self, brain=None, languages: List[str] = None):
        """
        Args:
            brain: Kaname の Brain への参照
            languages: OCR対応言語（デフォルト: 日英）
        """
        self.brain = brain
        self.lock = threading.Lock()
        
        # OCR エンジン
        self.ocr_engine = None
        self.languages = languages or ['ja', 'en']
        
        # テキスト履歴
        self.text_history: List[GameText] = []
        self.max_history = 100
        
        # 概念キャッシュ（同じ単語を何度も処理しない）
        self.known_concepts: Dict[str, float] = {}  # word -> last_seen
        
        # ゲームコンテキスト
        self.game_context: Dict[str, Any] = {
            "score": None,
            "hp": None,
            "level": None,
            "game_over": False,
            "messages": []
        }
        
        # WordStateBinding への参照
        self.word_binding = None
        
        self._init_ocr()
        self._init_kaname_systems()
        
        status = "✅" if _OCR_AVAILABLE else "❌ (pip install easyocr)"
        print(f"👁️ Game Vision Initialized. OCR: {status}")
    
    def _init_ocr(self):
        """OCR エンジンを初期化"""
        if not _OCR_AVAILABLE:
            return
        
        try:
            if _OCR_TYPE == "easyocr":
                self.ocr_engine = easyocr.Reader(self.languages, gpu=False)
                print(f"   OCR Engine: EasyOCR ({', '.join(self.languages)})")
            elif _OCR_TYPE == "pytesseract":
                # pytesseract は都度呼び出しなので engine は不要
                self.ocr_engine = "pytesseract"
                print(f"   OCR Engine: Tesseract")
        except Exception as e:
            print(f"⚠️ OCR Init Error: {e}")
            self.ocr_engine = None
    
    def _init_kaname_systems(self):
        """Kaname システムへの参照を初期化"""
        if not self.brain:
            return
        
        # WordStateBinding
        if hasattr(self.brain, 'cortex') and self.brain.cortex:
            if hasattr(self.brain.cortex, 'word_binding'):
                self.word_binding = self.brain.cortex.word_binding
                print("   🔗 WordStateBinding connected")
    
    def read_screen(self, frame) -> List[GameText]:
        """
        画面からテキストを読み取る
        
        Args:
            frame: OpenCV 形式の画像 (numpy array)
            
        Returns:
            認識されたテキストのリスト
        """
        if not _OCR_AVAILABLE or self.ocr_engine is None:
            return []
        
        results = []
        
        try:
            if _OCR_TYPE == "easyocr":
                ocr_results = self.ocr_engine.readtext(frame)
                for bbox, text, conf in ocr_results:
                    if conf > 0.3 and len(text.strip()) > 0:
                        # bbox は [[x1,y1],[x2,y1],[x2,y2],[x1,y2]]
                        x1, y1 = int(bbox[0][0]), int(bbox[0][1])
                        x2, y2 = int(bbox[2][0]), int(bbox[2][1])
                        
                        gt = GameText(
                            text=text.strip(),
                            confidence=conf,
                            position=(x1, y1, x2, y2)
                        )
                        results.append(gt)
                        
            elif _OCR_TYPE == "pytesseract":
                import pytesseract
                data = pytesseract.image_to_data(frame, output_type=pytesseract.Output.DICT)
                
                for i, text in enumerate(data['text']):
                    if text.strip() and data['conf'][i] > 30:
                        gt = GameText(
                            text=text.strip(),
                            confidence=data['conf'][i] / 100.0,
                            position=(
                                data['left'][i],
                                data['top'][i],
                                data['left'][i] + data['width'][i],
                                data['top'][i] + data['height'][i]
                            )
                        )
                        results.append(gt)
                        
        except Exception as e:
            print(f"⚠️ OCR Error: {e}")
        
        # 履歴に追加
        with self.lock:
            self.text_history.extend(results)
            if len(self.text_history) > self.max_history:
                self.text_history = self.text_history[-self.max_history:]
        
        # 概念として処理
        self._process_concepts(results)
        
        # ゲームコンテキストを更新
        self._update_game_context(results)
        
        return results
    
    def _process_concepts(self, texts: List[GameText]):
        """読み取ったテキストを概念として処理"""
        if not self.word_binding:
            return
        
        now = time.time()
        
        for gt in texts:
            word = gt.text
            
            # 最近見た単語はスキップ
            if word in self.known_concepts:
                if now - self.known_concepts[word] < 5.0:  # 5秒以内
                    continue
            
            self.known_concepts[word] = now
            
            # 現在の状態を取得
            state = self._get_current_state()
            emotion = self._estimate_emotion(word)
            
            # WordStateBinding に記録
            self.word_binding.bind(
                word=word,
                state=state,
                emotion=emotion,
                memory_fragments=[f"ゲーム中に見た: {word}"]
            )
    
    def _get_current_state(self) -> Dict[str, float]:
        """現在の内部状態を取得"""
        if not self.brain or not hasattr(self.brain, 'hormones'):
            return {}
        
        from src.body.hormones import Hormone
        return {
            "dopamine": self.brain.hormones.get(Hormone.DOPAMINE),
            "adrenaline": self.brain.hormones.get(Hormone.ADRENALINE),
            "cortisol": self.brain.hormones.get(Hormone.CORTISOL)
        }
    
    def _estimate_emotion(self, word: str) -> float:
        """単語から感情を推定"""
        # 簡易的なキーワードベース
        positive_words = ["クリア", "勝利", "成功", "win", "clear", "success", "bonus"]
        negative_words = ["ゲームオーバー", "失敗", "game over", "fail", "dead", "lose"]
        
        word_lower = word.lower()
        
        for pw in positive_words:
            if pw.lower() in word_lower:
                return 0.8
        
        for nw in negative_words:
            if nw.lower() in word_lower:
                return -0.8
        
        return 0.0  # 中立
    
    def _update_game_context(self, texts: List[GameText]):
        """ゲームコンテキストを更新"""
        for gt in texts:
            text = gt.text.lower()
            
            # スコア検出
            if "score" in text or "スコア" in text:
                # 数字を抽出
                import re
                numbers = re.findall(r'\d+', gt.text)
                if numbers:
                    self.game_context["score"] = int(numbers[-1])
            
            # HP検出
            if "hp" in text or "体力" in text or "life" in text:
                import re
                numbers = re.findall(r'\d+', gt.text)
                if numbers:
                    self.game_context["hp"] = int(numbers[0])
            
            # ゲームオーバー検出
            if "game over" in text or "ゲームオーバー" in text:
                self.game_context["game_over"] = True
    
    def get_commentary(self) -> Optional[Dict[str, Any]]:
        """
        ゲーム状況のコンテキストを取得
        
        Returns:
            状況コンテキスト（Kanameが自分で言葉を選ぶ材料）
            または None（話すことがない場合）
        """
        if not self.text_history:
            return None
        
        # 最新のテキストを取得
        recent = self.text_history[-5:]
        
        # コンテキストを構築（固定セリフではなく、状況データを返す）
        context = {
            "game_over": self.game_context.get("game_over", False),
            "score": self.game_context.get("score"),
            "hp": self.game_context.get("hp"),
            "recent_words": [gt.text for gt in recent],
            "emotion": self._get_current_state().get("dopamine", 0) / 100.0  # -1 to 1
        }
        
        # 話すべき状況かどうかを判定（セリフは返さない）
        if context["game_over"] or context["score"] or context["recent_words"]:
            return context
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """統計を取得"""
        return {
            "ocr_available": _OCR_AVAILABLE,
            "ocr_type": _OCR_TYPE,
            "text_history_size": len(self.text_history),
            "known_concepts": len(self.known_concepts),
            "game_context": self.game_context
        }


# テスト用
if __name__ == "__main__":
    print("Game Vision Test")
    
    gv = GameVision()
    print(f"Stats: {gv.get_stats()}")
    
    if _OCR_AVAILABLE:
        import numpy as np
        # ダミー画像でテスト
        dummy_frame = np.zeros((100, 300, 3), dtype=np.uint8)
        results = gv.read_screen(dummy_frame)
        print(f"OCR Results: {len(results)}")
    
    print("Done!")
