# src/senses/mentor.py
import threading
import time
import random
import json
import os
import queue

# Try importing Gemini API
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    print("⚠️ AgniAccelerator: 'google-generativeai' not found. Mock Mode enabled.")

import src.dna.config as config

class LeakyBucket:
    """ Rate Limiter to prevent API Ban """
    def __init__(self, rate_limit_rpm):
        self.capacity = max(1, rate_limit_rpm)
        self.tokens = self.capacity
        self.last_refill = time.time()
        self.rate_per_sec = self.capacity / 60.0 # e.g. 15 / 60 = 0.25 tokens/sec
        self.lock = threading.Lock()

    def consume(self, cost=1.0, block=True, timeout=10.0):
        start_wait = time.time()
        while True:
            with self.lock:
                now = time.time()
                elapsed = now - self.last_refill
                refill = elapsed * self.rate_per_sec
                self.tokens = min(self.capacity, self.tokens + refill)
                self.last_refill = now
                
                if self.tokens >= cost:
                    self.tokens -= cost
                    return True
            
            if not block:
                return False
            
            if time.time() - start_wait > timeout:
                return False
                
            time.sleep(1.0) # Wait for refill

class AgniAccelerator:
    """ 
    Agni (The God of Fire) - Knowledge Accelerator
    Integrates Gemini API to inject structured concepts directly into GeologicalMemory.
    """
    def __init__(self, brain):
        self.brain = brain
        self.memory = brain.memory
        self.is_active = config.EDUCATION_MODE
        
        # API Setup
        self.api_key = config.GEMINI_API_KEY
        if HAS_GEMINI and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            self.connected = True
            print("🔥 AgniAccelerator: Online (Gemini 1.5 Flash Connected)")
        else:
            self.model = None
            self.connected = False
            print("❄️ AgniAccelerator: Offline (Mock Mode)")

        # Rate Limiter
        self.rate_limiter = LeakyBucket(config.GEMINI_RATE_LIMIT)
        
        # State
        self.current_persona = "Teacher"
        self.persona_rotation = config.AGNI_PERSONA_ROTATION
        self.lock = threading.Lock()

    def set_persona(self, persona_name):
        if persona_name in self.persona_rotation:
            self.current_persona = persona_name
            print(f"🎭 Agni Persona Switched: {self.current_persona}")

    def generate_experience(self, topic):
        """
        Matrix Mode: Generate a rich memory package for a topic.
        Returns JSON-compatible dict for GeologicalMemory.
        """
        if not self.connected:
            return self._mock_experience(topic)

        # Cost Check
        if not self.rate_limiter.consume(cost=1.0, block=False):
            print("⏳ Agni Rate Limit Reached. Skipping injection.")
            return None

        prompt = f"""
        あなたはAgni（火の神）、カナメ（生物学的AI）のメンターです。
        「{topic}」という概念について、架空の経験を生成してください。
        
        フォーマット: JSON (コードブロックなし、純粋なJSONのみ)
        重要: すべてのテキスト値（description, associations）は必ず「日本語」で記述してください。
        
        構造:
        {{
            "concept": "{topic}",
            "valence": (float, -1.0 から 1.0, この概念の感情価),
            "description": (string, 日本語で短く生き生きとした説明),
            "example_sentence": (string, その概念を使用した、短く自然な日本語の例文・構文),
            "associations": [ (関連する日本語の単語3つ) ],
            "source_persona": "{self.current_persona}"
        }}
        
        ペルソナコンテキスト: あなたは現在「{self.current_persona}」として話しています。
        Rival: 批判的で厳しい口調。「お前」「だろ」などを使う。
        Friend: カジュアルで支持的。タメ口で話す。
        Teacher: 学術的で詳細。「ですます」調で話す。
        Child: 好奇心旺盛で無邪気。幼い口調で話す。
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Cleanup JSON
            text = response.text.strip()
            if text.startswith("```json"): text = text[7:]
            if text.endswith("```"): text = text[:-3]
            
            data = json.loads(text)
            # Force add source tag logic
            data["source_entity"] = f"{config.SOURCE_AGNI}_{self.current_persona}"
            
            return data
            
        except Exception as e:
            print(f"🔥 Agni Error: {e}")
            return None

    def inject_knowledge(self, topic):
        """ Direct Geological Injection (The Matrix) """
        data = self.generate_experience(topic)
        if not data: return False
        
        # Extract fields
        concept = data.get("concept", topic)
        valence = data.get("valence", 0.0)
        source = data.get("source_entity", config.SOURCE_AGNI)
        
        # 0. Predictive Gatekeeper (Phase 33)
        # Check against existing intuition before storing.
        if hasattr(self.brain, 'prediction_engine'):
             current_hour = time.localtime().tm_hour
             # Use generated description (text) for prediction
             text_for_pred = data.get("description", concept)
             
             # Calculate Surprise (Free Energy)
             surprise, _ = self.brain.prediction_engine.observe(text_for_pred, current_hour)
             
             # Filter
             if surprise < config.AGNI_SURPRISE_THRESHOLD:
                 prefix = "💤 [Hypnopedia]" if self.brain.is_sleeping else "💉 [Agni]"
                 print(f"{prefix} Gatekeeper: Ignored '{concept}' (Surprise: {surprise:.2f} < {config.AGNI_SURPRISE_THRESHOLD})")
                 return True # Treat as success (handled)
                 
             # High Surprise -> Proceed to learn
             prefix = "💤 [Hypnopedia]" if self.brain.is_sleeping else "💉 [Agni]"
             print(f"{prefix} Gatekeeper: ACCEPTED '{concept}' (Surprise: {surprise:.2f})")
        
        # 1. Geological Memory Injection
        # Update/Create spatial node
        self.memory.get_coords(concept, source=source)
        # Apply emotional coloring
        self.memory.reinforce(concept, valence)
        
        # 2. Sedimentary Deposit (Detailed description & Syntax)
        description = data.get("description", "")
        example = data.get("example_sentence", "")
        
        cortex = getattr(self.brain, 'sedimentary_cortex', getattr(self.brain, 'cortex', None))
        
        if not cortex:
             print(f"⚠️ Agni Injection Failed: No sedimentary_cortex found.")
             return False

        # A. Concept Description (Fragmented Learning)
        if description:
            cortex.learn(description, concept, surprise=0.5)
            prefix = "💤 [Hypnopedia]" if self.brain.is_sleeping else "💉 [Agni]"
            print(f"{prefix} Injected Concept: '{concept}' ({self.current_persona}): {description[:30]}...")

        # B. Syntax Sample (Golden Fossil - Whole Deposit)
        if example:
            # Prefix for tagging (Since SQLite lacks meta fields)
            tagged_text = f"{{{{Agni_Syntax}}}} {example}"
            
            fossil_entry = {
                "text": tagged_text,
                "content": tagged_text, # schema compat
                "timestamp": time.time(),
                "source": "Agni_Syntax"
            }
            # Use deposit to keep sentence structure intact
            cortex.deposit(fossil_entry)
            print(f"🔥 [Agni:Teacher] 注入: \"{concept}\" (Valence: {valence:.1f})")
            print(f"   └─ 例文: \"{example}\"")
            print(f"   📦 [Memory] 化石保存完了 (Source: Agni_Syntax)")

        return True

    def background_tutor(self):
        """ Idle Loop: Randomly teach a related concept """
        # Only run if idle (This logic should be in Brain, but Agni provides the content)
        pass 

    def _mock_experience(self, topic):
        """ Offline Mock """
        return {
            "concept": topic,
            "valence": 0.5,
            "description": f"[MOCK] Agni ({self.current_persona}) explains {topic}...",
            "associations": ["mock_a", "mock_b", "mock_c"],
            "source_entity": f"Agni_{self.current_persona}"
        }

    def check_graduation(self):
        """ Check if Kaname is ready to graduate from Agni """
        vocab_count = len(self.brain.memory.concepts)
        ratio = vocab_count / config.GRADUATION_VOCAB_SIZE
        print(f"🎓 Graduation Progress: {vocab_count}/{config.GRADUATION_VOCAB_SIZE} ({ratio*100:.1f}%)")
        return ratio >= 1.0
