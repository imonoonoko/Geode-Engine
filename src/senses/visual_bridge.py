import time
import threading
# Phase 6.5: Import config from DNA
try:
    import src.dna.config as config
except ImportError:
    import config

# ==========================================
# 🌉 Visual Memory Bridge (Gemini Proposal Integration)
# "Converts 30fps frames into Geological Sediments"
# ==========================================
class VisualMemoryBridge:
    # Shared Translation Map (YOLO -> Japanese)
    YOLO_TO_JP = {
        "person": "人", "bicycle": "自転車", "car": "車", "motorcycle": "バイク",
        "airplane": "飛行機", "bus": "バス", "train": "電車", "truck": "トラック",
        "boat": "ボート", "traffic light": "信号機", "bird": "鳥", "cat": "猫",
        "dog": "犬", "horse": "馬", "sheep": "羊", "cow": "牛",
        "backpack": "リュック", "umbrella": "傘", "handbag": "バッグ", "tie": "ネクタイ",
        "suitcase": "スーツケース", "frisbee": "フリスビー", "skis": "スキー板",
        "snowboard": "スノーボード", "sports ball": "ボール", "kite": "凧",
        "baseball bat": "バット", "baseball glove": "グローブ", "skateboard": "スケボー",
        "surfboard": "サーフボード", "tennis racket": "ラケット", "bottle": "ボトル",
        "wine glass": "ワイングラス", "cup": "コップ", "fork": "フォーク",
        "knife": "ナイフ", "spoon": "スプーン", "bowl": "ボウル", "banana": "バナナ",
        "apple": "リンゴ", "sandwich": "サンドイッチ", "orange": "オレンジ",
        "broccoli": "ブロッコリー", "carrot": "ニンジン", "hot dog": "ホットドッグ",
        "pizza": "ピザ", "donut": "ドーナツ", "cake": "ケーキ", "chair": "椅子",
        "couch": "ソファ", "potted plant": "観葉植物", "bed": "ベッド",
        "dining table": "テーブル", "toilet": "トイレ", "tv": "テレビ",
        "laptop": "ノートPC", "mouse": "マウス", "remote": "リモコン",
        "keyboard": "キーボード", "cell phone": "スマホ", "microwave": "電子レンジ",
        "oven": "オーブン", "toaster": "トースター", "sink": "シンク",
        "refrigerator": "冷蔵庫", "book": "本", "clock": "時計", "vase": "花瓶",
        "scissors": "ハサミ", "teddy bear": "テディベア", "hair drier": "ドライヤー",
        "toothbrush": "歯ブラシ"
    }

    def __init__(self, memory, cortex):
        self.memory = memory # GeologicalMemory
        self.cortex = cortex # SedimentaryCortex
        self.current_focus = None
        self.focus_start_time = 0
        self.accumulated_emotion = {}
        
        # Reverse Map for Active Inference (Japanese -> YOLO)
        self.JP_TO_YOLO = {v: k for k, v in self.YOLO_TO_JP.items()}
        
        # Debounce Buffer
        self.pending_focus = None
        self.pending_start = 0
        self.persistence_threshold = 0.5 # New focus must be stable for 0.5s
        self.lock = threading.Lock() # Thread Safety
        
        # Reference to Senses (Injected later or via Brain)
        self.senses = None 

    def connect_senses(self, senses):
        """ Allow bridge to control senses (Active Inference) """
        self.senses = senses

    def set_expectation(self, concept_word):
        """ 
        Active Inference: Brain wants to see 'concept_word'. 
        Translate Japanese Concept -> YOLO Tag and notify Senses.
        """
        if not self.senses: return
        
        # Direct Match
        tag = self.JP_TO_YOLO.get(concept_word)
        
        # If no direct match, maybe simple heuristic? (Not for now)
        if tag:
            self.senses.set_expectation(tag)
        else:
            # Concept is abstract (e.g. "Peace"), cannot look for it with YOLO.
            pass

    def translate_tag(self, tag):
        """ Translate English YOLO tag to Japanese """
        return self.YOLO_TO_JP.get(tag, tag)

    def flush(self):
        """ Force commit current focus (for Shutdown) """
        with self.lock:
            if self.current_focus is not None:
                now = time.time()
                duration = now - self.focus_start_time
                if duration > 1.0:
                    self._commit_memory(self.current_focus, duration, self.accumulated_emotion)
                self.current_focus = None
                print("🚽 Visual Memory Flushed.")

    def update(self, detected_objects_en, current_chemicals):
        """
        毎フレーム呼び出されるが、記憶への書き込みは「注目対象が変わった時」だけ行う
        detected_objects_en: List of English strings (from sct/YOLO)
        current_chemicals: Dict of hormones
        """
        with self.lock:
            # 最も優先度の高い物体を特定
            primary_obj = detected_objects_en[0] if detected_objects_en else None
            
            now = time.time()
            
            if primary_obj != self.current_focus:
                # Candidate for change
                if primary_obj != self.pending_focus:
                    self.pending_focus = primary_obj
                    self.pending_start = now
                elif (now - self.pending_start) > self.persistence_threshold:
                    # Confirmed change
                    if self.current_focus is not None:
                        duration = now - self.focus_start_time - self.persistence_threshold
                        if duration > 2.0: 
                            self._commit_memory(self.current_focus, duration, self.accumulated_emotion)
                    
                    self.current_focus = primary_obj
                    self.focus_start_time = now
                    self.accumulated_emotion = current_chemicals.copy()
                    self.pending_focus = None
            else:
                self.pending_focus = None
                for chem, val in current_chemicals.items():
                    if val > self.accumulated_emotion.get(chem, 0):
                        self.accumulated_emotion[chem] = val

    def _commit_memory(self, obj_name_en, duration, emotions):
        """
        地質学的記憶へ書き込み
        Phase 6: ConceptLearner でハイブリッド学習
        """
        # 感情の最大成分を抽出
        dominant_emotion = "neutral"
        if emotions:
            dominant_emotion = max(emotions, key=emotions.get)
        
        # 化石化 (Fossilization) - 好き嫌いの形成
        valence_delta = 0.0
        # Phase 6: 0-100 スケールに対応
        if emotions.get("oxytocin", 0) > 60.0 or emotions.get("dopamine", 0) > 60.0:
            valence_delta = 0.1
        elif emotions.get("cortisol", 0) > 50.0:
            valence_delta = -0.1
        
        # Phase 6: ConceptLearner を使って翻訳
        jp_name = None
        is_known = False
        
        # brain への参照を取得 (VisualMemoryBridge は brain.visual_bridge として使われる)
        brain = getattr(self, '_brain_ref', None)
        if not brain and hasattr(self, 'memory') and hasattr(self.memory, '_parent_brain'):
            brain = self.memory._parent_brain
        
        if brain and hasattr(brain, 'concept_learner'):
            jp_name, is_known = brain.concept_learner.translate(obj_name_en)
            
            if not is_known:
                # 未知の物体 → 感情と共に一時記憶
                brain.concept_learner.encounter_unknown(obj_name_en, valence_delta)
        
        # フォールバック: 内蔵辞書
        if jp_name is None:
            jp_name = self.translate_tag(obj_name_en)
            is_known = (jp_name != obj_name_en)  # 辞書にあれば違う名前になる
            
        # 表示名の生成
        if is_known:
            display_name = f"{jp_name} ({obj_name_en})"
        else:
            display_name = f"❓ 何か ({obj_name_en})"
            jp_name = obj_name_en  # 記憶には英語タグで保存
            
        # Reinforce with Japanese name so memory stores Japanese
        if valence_delta != 0:
            self.memory.reinforce(jp_name, valence_delta)

        natural_text = jp_name
        
        memory_entry = {
            "role": "system_visual",
            "content": f"saw_object: {jp_name}",
            "text": natural_text,
            "meta": {
                "duration": round(duration, 1),
                "emotion_tag": dominant_emotion,
                "intensity": emotions.get(dominant_emotion, 0),
                "is_known": is_known
            }
        }
        
        self.cortex.deposit(memory_entry)
        print(f"📸 記憶形成: {display_name} を {duration:.1f}秒間 見つめた ({dominant_emotion})")
