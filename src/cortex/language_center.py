import random
import threading
from janome.tokenizer import Tokenizer
import numpy as np

class LanguageCenter:
    """
    Chimera Language Engine (Broca's Area)
    
    Generates speech by:
    1. Shell Retrieval: Finding a past memory (sediment) that matches the current mood.
    2. Morphological Surgery: Stripping content words (N/V/Adj) to create a grammatical shell.
    3. Core Injection: Filling slots with words closest to the current thought vector.
    """
    def __init__(self, brain):
        self.brain = brain
        self.tokenizer = Tokenizer()
        self.lock = threading.Lock()
        
        # Phase 5: Hormone-based Syntax Templates
        # {Emotion: [Template List]}
        # Slots: {N}oun, {V}erb, {A}djective, {EX}clamation
        self.templates = {
            "ANGER": [
                "{N}は{A}だ！", 
                "{N}、{V}しろ！", 
                "許せない、{N}！"
            ],
            "JOY": [
                "わぁ、{N}だ！",
                "{N}はとても{A}ね！",
                "もっと{V}したい！"
            ],
            "SADNESS": [
                "{N}は{A}...",
                "{N}、{V}したくない...",
                "どうして{N}は{A}なの？"
            ],
            "CURIOSITY": [
                "{N}って何？",
                "{N}は{A}かな？",
                "{N}を{V}してみたい！"
            ],
            "CALM": [
                "{N}は{A}です。",
                "{N}があります。",
                "静かに{V}しましょう。"
            ],
            "FEAR": [
                "{N}が怖い...",
                "{N}から{V}して！",
                "{A}よ..."
            ]
        }
        print("🦁 Chimera Language Engine (Broca's Area): Online (Phase 5 Templates Ready)")

    def speak(self, thought_vector, valence_state=0.0, trigger_source="EXTERNAL"):
        """
        Generate a sentence based on the thought vector and hormone state.
        Phase 12: trigger_source (EXTERNAL/IMPULSE) handling.
        """
        if thought_vector is None:
            return None

        # 0. Detect Dominant Emotion (Hormone) based on DEVIATION
        current_emotion = "CALM"
        if hasattr(self.brain, 'hormones'):
            from src.body.hormones import Hormone
            hormones = self.brain.hormones
            
            # Phase 12: Personality Bias (Deviation from Baseline)
            # Baseline is assumed 50.0. Deviation > 20.0 triggers emotion.
            baseline = 50.0
            threshold = 20.0  # Sensitivity
            
            # Helper to check deviation
            def get_dev(h): return hormones.get(h) - baseline

            # Hierarchy: Anger > Joy > Fear > Sadness
            if get_dev(Hormone.ADRENALINE) > threshold:
                current_emotion =  "ANGER"
            elif get_dev(Hormone.DOPAMINE) > threshold:
                current_emotion = "JOY"
                if hormones.get(Hormone.SURPRISE) > 0.4:
                     current_emotion = "CURIOSITY"
            elif get_dev(Hormone.CORTISOL) > threshold:
                current_emotion = "FEAR"
            elif valence_state < -0.3:
                 current_emotion = "SADNESS"
                 
        if trigger_source == "IMPULSE":
            # 独り言は少し控えめに？ または逆に情熱的に？
            # 今は通常のロジックと同じでOK
            pass
        
        # 1. Shell Retrieval (Memory Dive) - Specific to emotion?
        # For Phase 5, let's prioritize Templates to verify them, 
        # or use Shells only if highly resonant.
        shell_text = self._retrieve_shell(valence_state)
        
        # Chance to use Template (increases if no shell found)
        use_template = False
        if not shell_text: use_template = True
        elif random.random() < 0.5: use_template = True # Mix it up
        
        generated_text = ""
        
        if use_template:
            # 2a. Template Strategy
            template = self._retrieve_template(current_emotion)
            generated_text = self._fill_template(template, thought_vector)
            # print(f"🗣️ Using Template ({current_emotion}): {template} -> {generated_text}")
        else:
            # 2b. Shell Strategy (Legacy Chimera)
            shell_structure = self._extract_shell(shell_text)
            generated_text = self._inject_core(shell_structure, thought_vector)
            # print(f"🗣️ Using Shell: {shell_text} -> {generated_text}")

        return generated_text

    def _retrieve_template(self, emotion):
        """ Select a random template for the emotion """
        candidates = self.templates.get(emotion, self.templates["CALM"])
        return random.choice(candidates)
        
    def _fill_template(self, template, thought_vector):
        """ Phase 5: Fill rigid templates with semantic words """
        import re
        # Slots: {N}, {V}, {A}
        
        def replace_slot(match):
            slot_type = match.group(1) # N, V, A
            target_pos = "名詞"
            if slot_type == "V": target_pos = "動詞"
            if slot_type == "A": target_pos = "形容詞"
            
            # Find best word
            # For templates, we don't have an 'original word' to lean on.
            # We must search purely by vector. 
            # Current _find_best_word relies on 'original_word' fallback.
            # We need a pure search.
            word = self._find_pure_word(target_pos, thought_vector)
            
            # Phase 12: Garbage Filter (Return valid placeholders only)
            import re
            # ASCII only tokens are likely garbage in this context (e.g. 'expl)', 'eache]')
            if re.match(r'^[a-zA-Z0-9_\W]+$', word) and not re.search(r'[ぁ-んァ-ン一-龥]', word):
                 # Fallback to safe word if garbage
                 if target_pos == "名詞": return "あれ" 
                 if target_pos == "動詞": return "する"
                 if target_pos == "形容詞": return "すごい"
            
            return word
            return word
            
        return re.sub(r'\{(N|V|A)\}', replace_slot, template)

    def _find_pure_word(self, target_pos, thought_vector):
        """ Find CLOSEST word in memory matching POS (No fallback to original) """
        # Re-use _find_best_word logic logic but strictly return best match
        # If no match, return a placeholder?
        best = self._find_best_word(target_pos, thought_vector, original_word="")
        if not best:
            if target_pos == "名詞": return "あれ"
            if target_pos == "動詞": return "する"
            if target_pos == "形容詞": return "すごい"
        return best

    def _retrieve_shell(self, target_valence):
        """ Find a sediment with similar emotional valence to use as a template. """
        # Access SedimentaryCortex
        cortex = getattr(self.brain, 'sedimentary_cortex', None)
        if not cortex:
            cortex = getattr(self.brain, 'cortex', None) # Legacy name
            
        if not cortex or not cortex.all_fragments:
            return None
            
        # Optimization: Sample 50 random fragments and pick the best valence match
        # (Linear scan of all might be slow later, but okay for now)
        best_frag = None
        min_diff = 10.0
        
        with cortex.lock:
            # Random sample to avoid repetition
            candidates = random.sample(cortex.all_fragments, min(50, len(cortex.all_fragments)))
            
            for frag in candidates:
                text = frag.get('text', '')
                if len(text) < 5: continue # Too short
                
                # Get valence of this fragment (using Cortex's method or Memory lookup)
                # We need a robust way to get valence. 
                # Let's use the Brain's memory valence lookup for the text (if it's a concept)
                # Or if it's a sentence, we might not have a valence.
                # Heuristic: Check valence of the 'trigger word' if stored?
                # Stored fragments don't have valence tag usually.
                # We will approximate via "Memory.get_valence(text)" -> might fail for long text.
                # So we assume the text IS the experience description.
                # Let's try to infer valence from the text (Janome -> average words).
                
                # For now, simplistic random pick slightly biased by length? 
                # No, User requested "Similar Mood/Situation".
                # Let's just pick random for V1 Scaffolding, and refine retrieval later.
                pass
            
            # Temporary: Random valid fragment
            valid = [f['text'] for f in candidates if len(f.get('text','')) > 5]
            if valid:
                return random.choice(valid)
                
        return None

    def _extract_shell(self, text):
        """
        Parse text and replace content words with Slots.
        Returns list of tokens/slots.
        """
        tokens = self.tokenizer.tokenize(text)
        structure = []
        
        for token in tokens:
            pos = token.part_of_speech.split(',')
            main_pos = pos[0] # 名詞, 動詞, etc.
            
            # Keep particles (助詞), auxiliary verbs (助動詞), symbols (記号)
            if main_pos in ['助詞', '助動詞', '記号']:
                structure.append({'type': 'fixed', 'text': token.surface})
            
            # Replace Content Words (名詞, 形容詞, 動詞)
            # Exclude '非自立' (e.g. "の" in "もの") or suffixes if possible
            elif main_pos in ['名詞', '形容詞', '動詞']:
                 # Keep logic simple: Replace ALL content words?
                 structure.append({'type': 'slot', 'pos': main_pos, 'surface': token.surface})
            
            else:
                 # Default: Keep (Adverbs, etc. might be context specific, but let's keep for flavor)
                 structure.append({'type': 'fixed', 'text': token.surface})
                 
        return structure

    def _inject_core(self, shell_structure, thought_vector):
        """
        Fill slots with words close to thought_vector.
        """
        result = []
        for item in shell_structure:
            if item['type'] == 'fixed':
                result.append(item['text'])
            else:
                # Find best matching word for this POS from memory
                target_pos = item['pos']
                original_word = item['surface']
                
                # Search memory for concepts with matching POS and high similarity to thought_vector
                best_word = self._find_best_word(target_pos, thought_vector, original_word)
                result.append(best_word)
                
        return "".join(result)

    def _find_best_word(self, target_pos, thought_vector, original_word):
        """
        Search GeologicalMemory for the concept closest to thought_vector 
        that matches the target POS (heuristically).
        """
        memory = self.brain.memory
        engine = self.brain.prediction_engine
        
        if not memory.concepts:
            return original_word
            
        best_word = original_word
        max_sim = -1.0
        
        # --- Phase 3: HDC Fast Search (Hamming) ---
        # 1. Try to find similar words using bitwise operations (SimHash)
        hdc_candidates = memory.find_similar_by_hash(thought_vector, limit=20, min_sim=0.3)
        
        if hdc_candidates:
            # print(f"🧱 HDC Hits: {len(hdc_candidates)}")
            # HDC gives us candidates sorted by Hamming similarity.
            # We still verify POS and maybe check exact Cosine similarity if critical?
            # For now, trust SimHash ranking.
            
            for word, sim in hdc_candidates:
                # POS Check
                if self._check_pos(word, target_pos):
                    # Found best match!
                    return word
            
            # If no HDC candidate passed POS check, fallback?
            # Or just return original.
            
        # --- Fallback: Legacy Linear Scan (Slow) ---
        # Only runs if HDC has no data or no hits.
        # (Same implementation as before, simplified for brevity in this diff if possible, 
        # but I will keep it for robustness during migration)
        
        # Check Cache
        candidates = []
        with memory.lock:
             candidates = list(memory.concepts.keys())

        cached_candidates = []
        for word in candidates:
            vec = engine.embedding_cache.get(word)
            if vec is not None:
                cached_candidates.append((word, vec))
        
        if not cached_candidates:
            return original_word

        target_norm = np.linalg.norm(thought_vector)
        
        for word, vec in cached_candidates:
            dot = np.dot(thought_vector, vec)
            norm = np.linalg.norm(vec)
            sim = dot / (target_norm * norm) if (target_norm * norm) > 0 else 0
            
            if sim > max_sim:
                if self._check_pos(word, target_pos):
                    max_sim = sim
                    best_word = word
        
        if max_sim < 0.3:
            return original_word
            
        return best_word

    def _check_pos(self, word, target_pos):
        """ Check if word matches target POS """
        # Only check the first token's POS
        tokens = self.tokenizer.tokenize(word)
        for t in tokens:
            return t.part_of_speech.startswith(target_pos)
        return False
