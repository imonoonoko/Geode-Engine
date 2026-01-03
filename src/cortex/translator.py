import json
import threading
import os
import random
import src.dna.config as config
from src.tools.cortex_generator import SimpleRNN
from src.body.feeder import DataFeeder

class MaiaTranslator:
    def __init__(self, memory_ref=None, cortex_ref=None):
        print(f"👂 Initializing Translator (Char-RNN System)...")
        # Expanded Brain: 128 -> 512 (Phase User Request)
        self.model = SimpleRNN(hidden_size=512)
        self.memory = memory_ref
        self.cortex = cortex_ref
        self.feeder = DataFeeder(food_folder="food")  # 食べさせるシステム
        self.training_lock = threading.Lock() # Init BEFORE first use
        
        # Check and Train
        if not os.path.exists(self.model.model_path):
            self.train_from_memory()
        else:
            # Load vocab even if model exists
            self._load_combined_corpus(train=False)

    def _load_combined_corpus(self, train=True):
        """ Combine Static Corpus + Geological Memory + Fresh Food """
        data = ""
        
        # 1. Base Corpus (Personality)
        corpus_path = os.path.join(config.BASE_DIR, "docs", "kaname_corpus.txt")
        if os.path.exists(corpus_path):
             with open(corpus_path, "r", encoding="utf-8") as f:
                 data += f.read() + "\n"
        
        # 2. Geological Memory (Acquired Knowledge)
        if self.memory:
            # Concept Keys (Nouns/Keywords)
            # Repeated to reinforce importance
            with self.memory.lock:
                mem_keys = list(self.memory.concepts.keys())
            if mem_keys:
                data += " ".join(mem_keys) + "\n"
                
        if self.cortex:
            # Sediments (Contextual fragments)
            # Recent memories have higher weight? For now, just dump all.
            # Limit to last 1000 fragments to keep training fast
            with self.cortex.lock:
                recent_frags = self.cortex.all_fragments[-1000:]
            for f in recent_frags:
                text = f.get('text', '')
                if text:
                    data += text + "。\n"

        # 3. 🍽️ Fresh Food (New text files in food/ folder)
        fresh_food = self.feeder.eat()
        if fresh_food:
            print(f"🍽️ Feeding fresh food to RNN! ({len(fresh_food)} chars)")
            data += fresh_food

        if not data: return
        
        self.model.load_data(data)
        
        if train:
            print(f"🎓 Learning from Memory (Size: {len(data)} chars)...")
            # Dynamic Epochs based on data size (keep it snappy)
            # Approx 1000 steps per cycle
            self.model.train(data, epochs=1000, seq_length=20)
            print("🎓 Memory Assimilated.")

    def train_from_memory(self):
        """ Public method to trigger retraining """
        if self.training_lock.locked():
            print("⏳ Training skipped (Already running).")
            return

        def _train_wrapper(do_train):
            with self.training_lock:
                 self._load_combined_corpus(do_train)
                 
        threading.Thread(target=_train_wrapper, args=(True,), daemon=True).start()

    def translate(self, ir_data):
        """
        RNN Generation based on Active Inference Strategy
        """
        strategy = ir_data.get("strategy", "RESONATE")
        concept = ir_data.get("concept", "私")
        
        emotions = ir_data.get("emotions", {})
        surprise = emotions.get("surprise", 0.0)
        
        # 1. Determine Temperature (Chaos Level)
        # Active Inference: Temperature scales with Prediction Error (Surprise)
        chaos_factor = surprise * 0.8  # Max +0.8 to temp
        
        temperature = 1.0
        if strategy == "RESONATE":
            temperature = 0.5 + (chaos_factor * 0.5) # Even resonance gets shaky if surprised
        elif strategy == "PROBE":
            temperature = 1.0 + chaos_factor         # Curiosity + Confusion
        elif strategy == "FRICTION":
            temperature = 2.0 + chaos_factor         # Pure chaos
        elif strategy == "REJECT":
            temperature = 0.2                        # Cold denial (Robot mode)
            
        # 2. Determine Seed
        # Use the concept + a particle to guide grammar roughly
        seed = concept
        if len(seed) < 2:
             seed += random.choice(["は", "が", "の", "も"])

        # Phase 6: Deep Context Priming
        deep_memories = ir_data.get("deep_memory", [])
        if deep_memories:
            context = deep_memories[0]
            # Priming: Prepend context to seed to bias the RNN state
            # FIX: Use natural concatenation instead of confusing parentheses
            # Old: seed = f"({context[:20]}...) {seed}"
            # New: Just flow naturally.
            seed = f"{context[-20:]}。{seed}"
            print(f"💭 Deep Context Applied: ...{context[-10:]} -> {concept}")
             
        # Generate with Strategy
        try:
            # === Epistemic Inquiry (Phase 28: Generate & Select) ===
            if strategy == "PROBE":
                # 問いが生まれるまで試行する (Max 3 retries)
                # Template is banned. We rely on Chaos (High Temp) and Selection.
                
                best_candidate = "..."
                found_question = False
                
                # Boost chaos for curiosity
                probe_temp = max(1.0, temperature + 0.3) 
                
                for _ in range(3):
                    candidate = self.model.generate(seed, length=40, temperature=probe_temp)
                    
                    # 疑問の兆候があるか？
                    # "なに", "だれ", "？", "?", "どう"
                    if any(q in candidate for q in ["？", "?", "何", "誰", "どう"]):
                        best_candidate = candidate
                        found_question = True
                        print(f"🕵️ Autonomous Question Generated: {candidate}")
                        break
                    
                    # Keep the longest one as fallback
                    if len(candidate) > len(best_candidate):
                        best_candidate = candidate
                
                return best_candidate
            
            # Normal Generation
            text = self.model.generate(seed, length=40, temperature=temperature)
            return text
            
        except Exception as e:
            print(f"⚠️ RNN Generation Failed: {e}")
            return "..."

