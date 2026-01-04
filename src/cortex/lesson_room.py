import time
import json
import threading
import enum
import queue
import src.dna.config as config
from src.senses.mentor import AgniAccelerator

class LessonState(enum.Enum):
    IDLE = "idle"
    INIT = "init"
    STUDENT_THINKING = "student_thinking"
    TEACHER_THINKING = "teacher_thinking"
    FEEDBACK_DISPLAY = "feedback_display"
    FINISHED = "finished"

class LessonRoom:
    """
    Agni's Interactive Lesson Room (Async State Machine)
    
    Refactored to be non-blocking for main.py integration.
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.lock = threading.Lock()
        
        # State
        self.state = LessonState.IDLE
        self.is_active = False
        self.state_start_time = 0.0
        
        # Config
        self.topic = "無題"
        self.max_turns = 3
        self.current_turn = 0
        
        # Data
        self.last_utterance = ""
        self.last_correction = None
        self.step_delay = 1.0 # Min time per state
        
        # Agni Background Processing
        self.agni_queue = queue.Queue()
        self.agni_result = None
        
        # Agni Reference
        if hasattr(brain, 'mentor'):
             self.agni: AgniAccelerator = brain.mentor
        elif hasattr(brain, 'metabolism_manager') and hasattr(brain.metabolism_manager, 'mentor'):
             self.agni: AgniAccelerator = brain.metabolism_manager.mentor
        else:
             print("⚠️ LessonRoom: Agni not found in Brain, creating ad-hoc instance.")
             self.agni = AgniAccelerator(brain)
             
        print("🎓 Async Lesson Room Initialized.")

    def start_lesson_metrics(self, topic="今日のこと", turns=3):
        """ Reset metrics for new lesson """
        with self.lock:
            self.topic = topic
            self.max_turns = turns
            self.current_turn = 0
            self.state = LessonState.INIT
            self.is_active = True
            self.state_start_time = time.time()
            print(f"🎓 Lesson Started: {topic}")
            self._say_ui(f"Agni先生とのレッスン: '{topic}'", speed=1.0)
            
    def update(self):
        """ Called every tick from ActivityManager """
        if not self.is_active:
            return
            
        now = time.time()
        elapsed = now - self.state_start_time
        
        if elapsed < self.step_delay:
            return # Wait for minimum visibility
            
        # State Machine
        if self.state == LessonState.INIT:
            self._next_turn()
            
        elif self.state == LessonState.STUDENT_THINKING:
            # Kaname speaks immediately (non-blocking enough)
            self._student_speak()
            self._transition(LessonState.TEACHER_THINKING)
            
        elif self.state == LessonState.TEACHER_THINKING:
            # Check if background thread finished
            if self.agni_result:
                # Result Ready
                self.last_correction = self.agni_result
                self.agni_result = None
                self._transition(LessonState.FEEDBACK_DISPLAY)
            elif not hasattr(self, '_agni_thread') or not self._agni_thread.is_alive():
                # Start Thread
                self._say_ui("Agni先生が添削中...", speed=1.0)
                self._agni_thread = threading.Thread(
                    target=self._run_agni_correction_thread, 
                    args=(self.topic, self.last_utterance),
                    daemon=True
                )
                self._agni_thread.start()
            
        elif self.state == LessonState.FEEDBACK_DISPLAY:
            # Feedback logic done in transition entry
            # Wait for user to read?
            if elapsed > 4.0: # 4 seconds to read feedback
                if self.current_turn < self.max_turns:
                    self._next_turn()
                else:
                    self._finish_lesson()
                    
        elif self.state == LessonState.FINISHED:
             self.is_active = False

    def _next_turn(self):
        self.current_turn += 1
        print(f"\n--- Turn {self.current_turn}/{self.max_turns} ---")
        self._say_ui(f"Turn {self.current_turn}: カナメの番...", speed=1.0)
        self._transition(LessonState.STUDENT_THINKING)

    def _student_speak(self):
        # 1. Kaname Speaks
        if hasattr(self.brain, 'prediction_engine'):
             vector = self.brain.prediction_engine._get_embedding_api(self.topic)
        else:
             vector = None
             
        if vector is None:
             utterance = f"{self.topic}..."
        else:
             utterance = self.brain.language_center.speak(vector, valence_state=0.5, trigger_source="LESSON")
             if not utterance:
                 utterance = f"{self.topic}が好き。"
        
        self.last_utterance = utterance
        print(f"🦁 [Kaname]: \"{utterance}\"")
        self._say_ui(f"🦁 {utterance}", speed=1.0)
        time.sleep(1.0) # Small pause for rhythm

    def _run_agni_correction_thread(self, topic, utterance):
         """ Background API Call """
         result = self._get_teacher_correction(topic, utterance)
         self.agni_result = result
         
    def _transition(self, new_state):
        self.state = new_state
        self.state_start_time = time.time()
        
    def _finish_lesson(self):
        print("🎓 Lesson Finished.")
        self._say_ui("レッスン終了。ありがとうございました。", speed=1.0)
        self._transition(LessonState.FINISHED)

    def _say_ui(self, text, speed=1.0):
        """ Visualize via Brain Speech Queue (Main Loop will pick it up) """
        if hasattr(self.brain, 'speech_queue'):
            payload = {
                "text": text,
                "focus": "LESSON",
                "context": f"Lesson: {self.topic}",
                "instability": 0.0
            }
            try:
                self.brain.speech_queue.put_nowait(payload)
            except:
                print(f"⚠️ Lesson Speech Queue Full: {text}")
        else:
            print(f"🗣️ [Lesson]: {text}")

    # --- Logic from previous version ---

    def _get_teacher_correction(self, topic, student_utterance):
        # ... (Same as before) ...
        if not self.agni.connected:
            time.sleep(1) # Fake delay
            return {
                "corrected_sentence": f"{student_utterance}です。",
                "feedback": "Mock correction."
            }
            
        # Safety: Truncate input to allow Agni to process avoiding max token limits
        safe_utterance = student_utterance[:500] if student_utterance else ""
        if len(student_utterance) > 500: safe_utterance += "..."

        prompt = f"""
        あなたは日本語教師のAgniです。生徒（AI）の発言を添削してください。
        トピック: {topic}
        生徒の発言: "{safe_utterance}"
        タスク: 自然な日本語に直し、先生としてのフィードバックをJSONで返してください。
        また、このトピックに関連する「覚えるべき単語」を3つ挙げてください。
        {{ 
          "corrected_sentence": "...", 
          "feedback": "...", 
          "is_correction_needed": true,
          "new_words": ["単語1", "単語2", "単語3"]
        }}
        """
        try:
            response = self.agni.model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            # Clean up potential leading/trailing non-json chars
            if "{" in text:
                text = text[text.find("{"):text.rfind("}")+1]
            return json.loads(text)
        except Exception as e:
            print(f"🔥 Lesson Error: {e} (Raw: {response.text[:50] if 'response' in locals() else 'None'})")
            # Fallback to avoid crash
            return {
                "corrected_sentence": student_utterance[:100] + "...", 
                "feedback": "エラーが発生したため、添削をスキップしました。",
                "error": str(e)
            }

    # In State Machine, we call this AFTER getting result
    def _save_correction(self, topic, sentence):
        """ Save the corrected sentence as Agni Syntax """
        tagged_text = f"{{{{Agni_Syntax}}}} {sentence}"
        cortex = getattr(self.brain, 'sedimentary_cortex', getattr(self.brain, 'cortex', None))
        
        if cortex:
            entry = {
                "text": tagged_text,
                "content": tagged_text,
                "timestamp": time.time(),
                "source": "Agni_Syntax_Lesson",
                "topic": topic
            }
            cortex.deposit(entry)
            print(f"   📦 [Memory] Saved: \"{sentence}\"")
            cortex.learn(sentence, topic, surprise=0.1)

    # Override transition to display feedback
    def _transition(self, new_state):
        self.state = new_state
        self.state_start_time = time.time()
        
        if new_state == LessonState.FEEDBACK_DISPLAY:
             if self.last_correction:
                 fb = self.last_correction.get('feedback', '')
                 cs = self.last_correction.get('corrected_sentence', '')
                 print(f"🔥 [Agni]: {fb}\n   Correct: {cs}")
                 self._say_ui(f"🔥 {fb}", speed=0.8)
                 
                 # Save
                 self._save_correction(self.topic, cs)
                 
                 # Phase 16: Learn New Words
                 new_words = self.last_correction.get('new_words', [])
                 if new_words:
                     print(f"📚 [Agni] Taught new words: {new_words}")
                     for word in new_words:
                         if isinstance(word, str):
                            # Learn concept
                            self.brain.activate_concept(word, boost=0.5)
                            # Maybe ui feedback?
                            pass
