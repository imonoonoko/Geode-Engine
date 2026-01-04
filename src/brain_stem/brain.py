import time
import random
import numpy as np
import math
import threading 
import os
import json
import queue

# [Anatomical Imports]
import src.dna.config as config
from src.cortex.memory import GeologicalMemory
from src.cortex.knowledge_graph import KnowledgeGraph
from src.cortex.logic import LogicEngine
from src.cortex.knowledge_importer import KnowledgeImporter
from src.cortex.sedimentary import SedimentaryCortex
from src.body.maya_resonance import GeologicalResonance
from src.body.biorhythm import BioRhythm
from src.cortex.inference import PredictionEngine
from src.cortex.tazuna import Tazuna # Step 4: Meta-Cognition Engine
from src.body.hormones import Hormone, HormoneManager  # Phase 8: Global import for all methods

# [Extracted Cells & Bridges]
from src.cells.neuron import Neuron
from src.senses.visual_bridge import VisualMemoryBridge
from src.senses.mentor import AgniAccelerator # Phase 15.5
from src.brain_stem.motor_cortex import MotorCortex  # Phase 15.1
from src.brain_stem.sensory_cortex import SensoryCortex  # Phase 15.2
from src.brain_stem.dream_engine import DreamEngine  # Phase 15.3
from src.body.metabolism import MetabolismManager  # Phase 15.4 & 31
from src.cortex.spatial import SpatialCortex # Phase 31
from src.cortex.agni_translator import AgniTranslator  # Phase 16
from src.cortex.hdc_bridge import HDCBridge  # Phase 19

# [Body Interface]
try:
    from src.body.body_interface import BodyHAL
except ImportError:
    BodyHAL = None


# 🧠 BRAIN (The Core)
# ==========================================
class KanameBrain:
    def __init__(self):
        print("🧠 Initializing Kaname Brain (Phase 10 Stable)...")
        self.is_alive = True
        self.time_step = 0
        
        # Thread Lock [Phase 10]
        self.lock = threading.Lock()
        
        # 1. 生理層 (Hormones) - Phase 8: HormoneManager (The Iron Heart)
        from src.body.hormones import Hormone, HormoneManager
        self.hormones = HormoneManager()
        
        # Phase 20: 隠蔽された疲労 (Bravado System)
        # Phase 31: Managed by MetabolismManager, but Brain needs a stub for backward compat
        self.hidden_fatigue = 0.0

        # ... (lines 73-136 omitted)

        
        # 2. 記憶 & 言語
        self.memory = GeologicalMemory(size=config.MSG_BRAIN_SIZE)
        print(self.memory.load()) 
        self.cortex = SedimentaryCortex(self.memory, max_sediments=config.SEDIMENT_MAX)
        
        # New: Tazuna Engine (Meta-Cognition)
        self.tazuna = Tazuna()
        
        # 3. 海馬 (Deep Semantic Memory) [Phase 6]
        from src.cortex.hippocampus import Hippocampus
        self.hippocampus = Hippocampus()
        
        # Phase 6.2: Visual Bridge
        self.visual_bridge = VisualMemoryBridge(self.memory, self.cortex)
        # Inject Brain Reference for Active Inference
        self.visual_bridge._brain_ref = self 
        
        # 4. 魂 (Resonance) [Phase 17]
        self.resonance = GeologicalResonance(self.memory, self.cortex.stomach)
        
        # Phase 30: 感情→学習接続 (Inject Brain Reference)
        self.cortex.stomach.brain_ref = self
        
        # Phase 16: Hybrid Translator (Ollama + Agni Distillation)
        # Re-enabled for high-level language generation
        self.translator = AgniTranslator(self)
        
        # Phase 19: HDCBridge (Memory Recall + G-Calculation + Prompt Injection)
        self.hdc_bridge = HDCBridge(self)
        
        # Phase 6: Feederは独立させる (main.pyからアクセスするため)
        from src.body.feeder import DataFeeder
        self.feeder = DataFeeder(food_folder="food")
        self.feeder.brain_ref = self  # Phase 30: 退屈トリガー用
        
        # 青空文庫ハーベスター（自動収集）
        from src.body.aozora_harvester import AozoraHarvester
        self.aozora = AozoraHarvester(brain_ref=self)
        
        # 多様な知識収集 (Wikipedia, News, etc.)
        from src.body.knowledge_harvesters import KnowledgeHarvesterManager
        self.knowledge_manager = KnowledgeHarvesterManager()
        
        # Phase 6: 注意コントローラー (興味関心ベースの視線/移動)
        from src.brain_stem.attention_manager import AttentionManager
        self.attention = AttentionManager(self)
        
        # Phase 6: 概念学習システム (ハイブリッド学習)
        from src.cortex.concept_learner import ConceptLearner
        self.concept_learner = ConceptLearner(self, data_dir="memory")
        
        # Phase 5: Chimera Language Engine (Broca's Area)
        from src.cortex.language_center import LanguageCenter
        self.language_center = LanguageCenter(self)
        
        # Phase 6: 人格系 (Personality Field)
        from src.cortex.personality_field import PersonalityField
        self.personality_field = PersonalityField()
        
        # Phase 7: Minecraft Integration (Environment Body)
        # --> MOVED/DISABLED (Java Edition Used)
        # try:
        #     from src.games.minecraft.manager import MinecraftManager
        #     self.minecraft = MinecraftManager(brain=self)
        #     self.minecraft.start() # Start WebSocket Server immediately
        # except ImportError:
        #     # print("⚠️ Minecraft dependencies missing (websockets).")
        #     self.minecraft = None
        self.minecraft = None

        if self.minecraft:
            try:
                from src.games.minecraft.action import MinecraftActionModule
                self.minecraft_action = MinecraftActionModule(brain=self)
            except ImportError:
                 self.minecraft_action = None
        else:
             self.minecraft_action = None

        
        # 3. ニューロン
        self.neurons = []
        self.name_map = {}
        self._init_neurons()
        
        # 状態フラグ
        self.is_drowsy = False
        self.is_sleeping = False
        self.inactive_counter = 0
        # Phase 31: Spatial Cortex handles Geo-Y
        # self.current_geo_y = config.BRAIN_GEO_INITIAL (Delegated to Spatial)
        
        # Throttle for Environment Resonance (Prevent Spamming)
        self._last_env_resonance_concept = None

        # Phase 23: Biorhythm Engine
        self.bio_engine = BioRhythm()
        self.prediction_engine = PredictionEngine() # Active Inference
        self.prediction_engine.brain_ref = self  # Phase 30: 感情バイアス予測用
        
        # Phase 2.2: Metamorphism (Inject Engine into Cortex)
        # Moved to end of __init__ to ensure spatial is ready

        # Phase 31: Moved to MetabolismManager
        # self.homeostatic_set_points = { ... }
        
        # Phase 25: Action Strategy (SSM-driven)
        self.current_action_strategy = "RESONATE"
        
        # Missing Initializations (Demon Audit Phase 21)
        self.last_thought_time = time.time()
        self.speech_queue = queue.Queue(maxsize=10)
        
        # Phase 2: Tazuna Learning Memory
        self.last_dopamine = 0.0
        self.last_tazuna_hormones = None # Snapshot for learning
        self.last_tazuna_signal = None

        # Phase 8 Step 3: Event-Driven Architecture
        from src.body.events import EventBus, Event
        self.events = EventBus()

        # Phase 7: Minecraft Integration (DISABLED - Java Edition Only)
        # Bedrock WebSocket is no longer used. Java Edition uses Mineflayer (bot.js)
        # To re-enable Bedrock: uncomment the following block
        # try:
        #     from src.games.minecraft.manager import MinecraftManager
        #     self.minecraft = MinecraftManager(brain=self)
        #     self.minecraft.start()
        # except ImportError:
        #     print("⚠️ Minecraft Module not found or dependencies missing.")
        #     self.minecraft = None
        self.minecraft = None  # Java Edition uses Mineflayer via mineflayer_env.py
        self._register_event_handlers()

        # Phase 9: Active Soliloquy (能動的うわ言)
        from src.cortex.soliloquy import SoliloquyManager
        self.soliloquy = SoliloquyManager(self)

        # Phase 22: Semantic Gravity Loop
        threading.Thread(target=self._gravity_loop, daemon=True).start()

        # Phase 15.5: Agni Accelerator (Background Tutor)
        self.mentor = AgniAccelerator(self)
        if config.EDUCATION_MODE:
            threading.Thread(target=self._mentor_loop, daemon=True).start()

        # Phase 6: Body HAL (Hardware Abstraction Layer)
        self.body_hal = BodyHAL() if BodyHAL else None

        # Phase 15.1: Motor Cortex (Separated Module)
        self.motor_cortex = MotorCortex(
            hormones=self.hormones,
            memory=self.memory,
            body_hal=self.body_hal,
            attention=getattr(self, 'attention', None),
            visual_bridge=self.visual_bridge
        )
        
        # Phase 15.2: Sensory Cortex (Separated Module)
        self.sensory_cortex = SensoryCortex(
            hormones=self.hormones,
            memory=self.memory,
            activate_concept_fn=self.activate_concept
        )
        
        # Phase 15.3: Dream Engine (Separated Module)
        self.dream_engine = DreamEngine(
            hormones=self.hormones,
            memory=self.memory,
            cortex=self.cortex,
            soliloquy=getattr(self, 'soliloquy', None)
        )
        
        # Phase 15.4: Metabolism Manager (Separated Module)
        # Phase 15.4 & 31: Metabolism Manager (Refactored)
        self.metabolism_manager = MetabolismManager(
            hormones=self.hormones,
            memory=self.memory,
            bio_engine=self.bio_engine
        )
        # Phase 31: Spatial Cortex
        self.spatial = SpatialCortex(self)
        
        # Phase 16: Agni Translator (壁2攻略)
        self.translator = AgniTranslator(
            brain=self,
            agni=self.mentor
        )

        # Phase 30: Removed (Consolidated into Phase 12 below)
        
        # Phase 3: Activity & Lesson (Full Integration)
        from src.cortex.lesson_room import LessonRoom
        self.lesson_room = LessonRoom(self)
        
        from src.brain_stem.activity_manager import ActivityManager
        self.activity_manager = ActivityManager(self)

        # Phase 2.2: Metamorphism (Inject Engine into Cortex) - Moved here
        if self.spatial:
            self.spatial.prediction_engine = self.prediction_engine

        # Phase 12: Advanced Reasoning (Common Sense)
        self.knowledge_graph = KnowledgeGraph(save_dir=self.memory.save_dir)
        self.logic_engine = LogicEngine(self)
        self.logic_engine.graph = self.knowledge_graph
        
        # Async Auto-Import
        def _auto_import():
             importer = KnowledgeImporter(self.knowledge_graph)
             importer.import_from_directory() # defaults to data/learning
        threading.Thread(target=_auto_import, daemon=True).start()
    
    @property
    def current_geo_y(self):
        return self.spatial.current_geo_y
    
    @current_geo_y.setter
    def current_geo_y(self, val):
        self.spatial.current_geo_y = val

    def _register_event_handlers(self):
        """
        イベントハンドラを登録。
        各イベントに対して「脳がどう反応するか」を定義する。
        """
        from src.body.events import Event
        
        # User Interaction
        self.events.subscribe(Event.POKED, self._on_poked)
        self.events.subscribe(Event.PETTED, self._on_petted)
        
        # System
        self.events.subscribe(Event.ERROR_OCCURRED, self._on_error)
        
        print("🧠 [Brain] Event handlers registered.")
    
    def _on_poked(self, **kwargs):
        """つつかれた時の反応: アドレナリン上昇"""
        self.hormones.update(Hormone.ADRENALINE, config.DELTA_POKE)
    
    def _on_petted(self, **kwargs):
        """撫でられた時の反応: ドーパミン上昇"""
        self.hormones.update(Hormone.DOPAMINE, config.DELTA_PET)
        self.is_sleeping = False  # 撫でられると起きる
    
    def _on_error(self, source=None, error=None, **kwargs):
        """エラー発生時の反応: コルチゾール上昇、セロトニン低下"""
        self.hormones.update(Hormone.CORTISOL, config.DELTA_PAIN_CORTISOL)
        self.hormones.update(Hormone.SEROTONIN, config.DELTA_PAIN_SEROTONIN)

        
    def _init_neurons(self):
        sensors = config.NEURON_SENSORS
        for name in sensors:
            n = Neuron(name, is_sensor=True)
            self.neurons.append(n)
            self.name_map[name] = n

    def activate_concept(self, name, boost=1.0):
        """ 概念ニューロンの活性化（なければ即時生成） """
        if name not in self.name_map:
            # Short-Term Memory Creation
            n = Neuron(name, is_sensor=False)
            self.neurons.append(n)
            self.name_map[name] = n
            # Trigger 'New Idea' resonance?
        
        self.name_map[name].potential += boost

    def prune_neurons(self):
        """ Apoptosis: 死んだニューロンの除去 (Memory Leak Prevention) """
        # 死滅条件: 電位が低く、かつ長時間発火していない、かつセンサーでない
        # しきい値: Potential < 0.01 and Steps since fired > 5000 (roughly 8 min)
        with self.lock:
            alive = []
            dead_count = 0
            
            for n in self.neurons:
                if n.is_sensor:
                    alive.append(n)
                    continue
                    
                is_dead = (n.potential < 0.01) and (self.time_step - n.last_fired > 5000)
                
                if not is_dead:
                    alive.append(n)
                else:
                    dead_count += 1
                    if n.name in self.name_map:
                        del self.name_map[n.name]
            
            self.neurons = alive
            
        if dead_count > 0:
            print(f"🧹 Pruned {dead_count} dead neurons. (Total: {len(self.neurons)})")


    def receive_sense(self, sense_data, data=None):
        """ 感覚データの受信 (Thread Safe with Lock) """
        if not sense_data: return
        
        # Phase 7: Handle (type, data) style calls from MinecraftManager
        if isinstance(sense_data, str) and data is not None:
             sense_type = sense_data
             sense_data = data
             sense_data["type"] = sense_type
        else:
             sense_type = sense_data.get("type", "unknown")
        
        # --- Visual Memory Bridge Integration (Phase 6.2 Fix) ---
        # "sense_data" can be a dict (Atmosphere) OR a special stimulus packet (Objects)
        # We handle object processing HERE to ensure 30fps responsiveness.
        
        if "type" in sense_data and sense_data["type"] == "objects":
             tags_en = sense_data['tags']
             
             # 1. Update Memory Bridge (Sedimentation Loop)
             # Bridge handles storage. Pass snapshot for emotion tracking.
             self.visual_bridge.update(tags_en, self.hormones.as_dict())
             
             # 2. Visual Concept Activation
             with self.lock:
                 for tag in tags_en:
                     jp_tag = self.visual_bridge.translate_tag(tag)
                     self.activate_concept(jp_tag, boost=0.3)
             
             return # Object packet processed.
        
        # --- End Visual Bridge Integration ---

        with self.lock:
            # 視覚刺激をニューロンへ入力
            for name, val in sense_data.items():
                if name in self.name_map:
                    self.name_map[name].potential += val * 0.2
            
            # Phase 20: 光合成 (Photosynthesis)
            if 'photosynthesis_rate' in sense_data:
                gain = sense_data['photosynthesis_rate']
                if gain > 0:
                    self.hormones.update(Hormone.GLUCOSE, gain)
                    # 光を浴びると少し幸せ (Dopamine)
                    if random.random() < 0.1:
                        self.hormones.update(Hormone.DOPAMINE, 5.0)

            # Phase 7: Minecraft Integration (Refactored to SpatialCortex)
            if sense_type == "MC_TRAVEL":
                self.spatial.process_sense(sense_data)

        # Phase 7: Minecraft keeps the brain awake
        if "MC_" in str(sense_data): # Check if it's a Minecraft event
            self.last_thought_time = time.time()
            self.is_sleeping = False
            self.is_drowsy = False







    def think(self):
        """ 思考サイクル (Thread Safe with Lock) """
        self.time_step += 1
        
        with self.lock:
            # Phase 20: 飢餓モード (Starvation / Coma)
            glucose = self.hormones.get(Hormone.GLUCOSE)
            
            if glucose < 5.0 or self.hidden_fatigue > 50.0:
                if self.time_step % 10 == 0:
                    print(f"💀 昏睡状態 (Coma). 血糖値: {glucose:.1f}, 疲労度: {self.hidden_fatigue:.1f}")
                return None # 思考停止

            # Phase 6: Scale Adjusted
            serotonin = self.hormones.get(Hormone.SEROTONIN)
            h_bias = 1.0 + ((serotonin - 50.0) / 100.0)
            
            # Phase 20: 思考コスト (Thinking Cost)
            # 考えるだけでエネルギーを使う
            self.hormones.update(Hormone.GLUCOSE, -0.01)

            # Phase 20: 認知ノイズ (Cognitive Noise)
            # 低血糖時は「ぼーっとする」 (確率的にスキップ)
            if glucose < config.THRESHOLD_LOW and random.random() < 0.3:
                return None 
            
            active_thoughts = []
            for n in self.neurons:
                n.decay(h_bias)
                if n.potential >= 1.0:
                    n.fire(self.time_step)
                    if not n.is_sensor: 
                        active_thoughts.append(n.name)
            
            # User Tuning: Remember = Eat
            # 記憶を思い出すことでエネルギーが回復する（精神的満足感）
            if active_thoughts:
                # 1つ思い出すたびに 0.5 回復 (最大 2.0/tick)
                recovery = min(2.0, len(active_thoughts) * 0.5)
                self.hormones.update(Hormone.GLUCOSE, recovery)
                        
                        # Resonance REMOVED: Was causing excessive sound frequency.
                        # Autonomous loop handles ambient sounds now.

            # Phase 22: Impulsive Action (Boredom -> Hallucination)
            # 退屈が限界を超えると、ランダムな記憶が発火する (Internal Stimulation)
            boredom = self.hormones.get(Hormone.BOREDOM)
            if boredom > 80.0 and random.random() < 0.05:
                impulse_word = self.memory.get_random_concept(refresh=True)
                if impulse_word:
                    active_thoughts.append(impulse_word)
                    print(f"⚡ 衝動的想起 (Impulse): {impulse_word} (退屈度: {boredom:.2f})")
                    # 衝動により少しスッキリする
                    self.hormones.update(Hormone.BOREDOM, -0.2)
                    self.hormones.update(Hormone.STIMULATION, 0.2)




            

            # 眠り判定
            if active_thoughts:
                self.last_thought_time = time.time()
                self.is_sleeping = False
                self.is_drowsy = False
            else:
                # Minecraft接続中は眠らないようにする（身体活動を優先）
                mc_active = hasattr(self, 'minecraft') and self.minecraft and self.minecraft.current_state.get("connected")
                
                if not mc_active:
                    if time.time() - self.last_thought_time > 20: # 20秒沈黙でうとうと
                        self.is_drowsy = True
                    if time.time() - self.last_thought_time > 60: # 60秒沈黙で睡眠
                        self.is_sleeping = True
                else:
                    # Minecraft中。もし寝てしまっていたら強制覚醒
                    self.is_sleeping = False
                    self.is_drowsy = False

            # --- Auto-Save (Periodic) ---
            if self.time_step % 300 == 0:
                # Run save in background thread to avoid blocking thought?
                # For now, do it inline, optimization later if needed.
                self.save_memory()
                # print("💾 Memory/Cortex Auto-Saved.")

            # Phase 6 & 13: Digestion Cycle (While Sleeping)
            if self.is_sleeping and self.time_step % 100 == 0:
                self._dream_process()

            # (Duplicate removed - Demon Audit Phase 21)

            # 発話予約 (Pre-calculation inside lock)
            impulse_ir = None
            impulse_word = None
            
            if active_thoughts and self.time_step % 15 == 0 and not self.is_sleeping:
                word = random.choice(active_thoughts)
                
                # === Phase 28: Brain Wiring (Active Inference) ===
                # 1. Current Strategy (from Input/Surprise)
                strategy = self.current_action_strategy
                
                # 2. Homeostatic Overrides (Deficits drive Strategy)
                glucose = self.hormones.get(Hormone.GLUCOSE)
                dopamine = self.hormones.get(Hormone.DOPAMINE)
                
                if glucose < config.THRESHOLD_LOW:
                    pass # Hungry logic future expansion
                elif dopamine < config.THRESHOLD_LOW and strategy != "PROBE":
                    # Depressed -> Seek Joy (Memory Pivot)
                    strategy = "JOY_SEEKING"
                    
                # 3. Epistemic Visual Control
                if strategy == "PROBE":
                    # If we are curious, Look for what we are thinking about
                    self.visual_bridge.set_expectation(word)
                
                # 4. Execute Cortex Retrieval
                
                # Phase 2: Tazuna Learning Step `(Reward Calculation)`
                current_dopamine = self.hormones.get(Hormone.DOPAMINE)
                delta_dopamine = current_dopamine - self.last_dopamine
                
                if self.last_tazuna_hormones and self.last_tazuna_signal:
                    # Previous Action Resulted in this Delta?
                    # We learn if the delta is significant
                    self.tazuna.learn(self.last_tazuna_hormones, self.last_tazuna_signal.mode, delta_dopamine)

                # Execute Modulation
                tazuna_signal = self.tazuna.modulate(self.hormones)
                
                # Store State for Next Learning Step
                self.last_dopamine = current_dopamine
                self.last_tazuna_hormones = self.hormones.as_dict() # Snapshot
                self.last_tazuna_signal = tazuna_signal
                
                # Log Tazuna State
                if tazuna_signal.mode != "NORMAL":
                     icon = "🎲" if tazuna_signal.mode == "DIVERGE" else "🎯"
                     if tazuna_signal.mode == "PANIC": icon = "🛡️"
                     
                     # Determine trigger for log
                     trigger = "SEROTONIN"
                     val = self.hormones.get(Hormone.SEROTONIN)
                     if tazuna_signal.mode == "DIVERGE":
                         trigger = "BOREDOM"
                         val = self.hormones.get(Hormone.BOREDOM)
                     elif tazuna_signal.mode == "PANIC":
                         trigger = "SURPRISE"
                         val = self.hormones.get(Hormone.SURPRISE)
                         
                     print(f"🐎 [Tazuna] {icon} {tazuna_signal.mode} (Temp: {tazuna_signal.temperature:.1f}) | {trigger}: {val:.1f}%")
                     print(f"   └─ Why: \"{tazuna_signal.reason}\"")
                
                ir_data = self.cortex.speak(word, strategy=strategy, tazuna_signal=tazuna_signal)
                
                if ir_data: 
                    # Inject Strategy into Packet for Translator
                    ir_data["strategy"] = strategy
                    
                    if word in self.memory.concepts: 
                        coords = self.memory.get_coords(word)
                        if len(coords) >= 2:
                            self.current_geo_y = coords[1]
                    
                    # 状態スナップショット (Lock中に取得)
                    ir_data["emotions"] = self.hormones.as_dict()
                    impulse_ir = ir_data
                    impulse_word = word
                    
                    # Resonance for Speech (Loud)
                    self.resonance.impact(word, force=0.8)
                else:
                    self.resonance.impact(word, force=0.5)

        # === OUTSIDE LOCK (Safe for Network I/O) ===
        speech_payload = None
        
        # Phase 9: Active Soliloquy (能動的うわ言)
        # think_aloud() は lock の外で呼ぶ（発話がブロックすると危険）
        if self.soliloquy and not self.is_sleeping:
            soliloquy_speech = self.soliloquy.think_aloud()
            if soliloquy_speech and not impulse_ir:
                # impulse_ir がある場合は通常発話を優先
                # soliloquy は沈黙時のみ喋る
                impulse_ir = {"text": soliloquy_speech, "strategy": "SOLILOQUY"}
                impulse_word = "soliloquy"
        
        # Check Async Speech Queue
        try:
            if not self.speech_queue.empty():
                speech_payload = self.speech_queue.get_nowait()
        except Exception as e:
            # DEF-07 修正: 具体的な例外タイプをキャッチ
            if "Empty" not in str(type(e).__name__):
                print(f"⚠️ Speech Queue Error: {e}")

        if impulse_ir:
             # 思考を言語化 (Async to prevent death)
             # Fire and forget thread
             threading.Thread(target=self._async_speak_task, args=(impulse_ir, impulse_word), daemon=True).start()

        # === Phase 8: Minecraft Autonomous Action (AWAKE STATE) ===
        # 起きている時にMinecraft接続中なら自律的に動く
        if hasattr(self, 'minecraft') and self.minecraft:
            state = self.minecraft.current_state
            if state and state.get("connected"):
                if self.time_step % 5 == 0:  # 5ステップごとに自発行動
                    pos = state.get("position") or {}
                    mx, mz = pos.get("x", 0), pos.get("z", 0)
                    self._decide_minecraft_action(mx, mz)

        return speech_payload

    
    def _dream_process(self):
        """
        Phase 6: Sleep & Consolidation Logic (Demons of Dream)
        睡眠中に記憶を整理し、地質学的記憶地図を書き換える。
        """
        print("💤 Demons of Dream: Organizing chaos into order...")
        
        # 1. 記憶の消化・剪定 (Stomach & Cortex)
        self.cortex.digest_memories()
        
        # Phase 7: Minecraft Fallback (時々自発的に動く)
        if hasattr(self, 'minecraft') and self.minecraft and self.minecraft.current_state.get("connected"):
            if self.time_step % 10 == 0:  # 10ステップごとに自発行動（10倍頻度UP）
                pos = self.minecraft.current_state.get("position", {})
                mx, mz = pos.get("x", 0), pos.get("z", 0)
                if self.time_step % 50 == 0:
                    print(f"🤖 [AUTO] Autonomous MC action: ({mx:.1f}, {mz:.1f})")
                self._decide_minecraft_action(mx, mz)
        
        # [Phase 17] Tiered Memory Pruning
        # 眠っている間に短期記憶(RAM)を整理し、長期記憶(SQLite)へ溢れた分を戻す
        if self.time_step % 200 == 0:
             if hasattr(self, 'knowledge_graph'):
                 # Keep 500k active concepts (~1GB RAM). The rest reside in SQLite.
                 self.knowledge_graph.prune(limit=500000)

        # 1. 勾配降下法 (Gradient Following)
        result = self.memory.forget_forgotten_concepts()
        forgotten, composted_valence = result if isinstance(result, tuple) else (result, 0.0)
        
        if forgotten:
            self.cortex.stomach.forget_concepts(forgotten)
            # 性格への転化
            if abs(composted_valence) > 0.1:
                mood_shift = -composted_valence * 0.05
                self.hormones.update(Hormone.SEROTONIN, mood_shift)
        
        # 3. Synaptic-Geological Bridge (The Core Feature)
        # 強いシナプス結合（共起）を持つ概念同士を物理的に引き寄せる
        if self.cortex.stomach:
            strong_links = self.cortex.stomach.get_strong_links(limit=10, threshold=1.5)
            if strong_links:
                print(f"🛌 Semantic Gravity: Pulling {len(strong_links)} pairs together based on episodes...")
                for u, v, weight in strong_links:
                    # 結合強度に応じて引力をかける (最大 0.8)
                    attraction = min(0.8, weight * 0.1)
                    
                    # Mutual Attraction (双方向引力)
                    # お互いに引き寄せ合うことで、中間に新しい意味の谷を作る
                    self.memory.apply_gravity(u, v, attraction)
                    self.memory.apply_gravity(v, u, attraction)
                    
                    # if res: print(f"  - {res}")
        
    def _async_speak_task(self, impulse_ir, impulse_word):
        """ Background Translation Task with Verbal Reasoning (CoT) """
        try:
            # === Phase 6: No-LLM Speech (Fragment Concatenation) ===
            # 記憶断片を直接結合してうわ言を生成
            fragments = impulse_ir.get("fragments", [])
            concept = impulse_ir.get("concept", "")
            valence = impulse_ir.get("valence", 0.0)
            
            # 1. 断片を結合 (シャッフルして自然さを演出)
            if "text" in impulse_ir and impulse_ir["text"]:
                draft_text = impulse_ir["text"]  # Use pre-generated text (Chimera/Soliloquy)
            elif fragments:
                random.shuffle(fragments)
                draft_text = "".join(fragments[:3])  # 最大3断片
            else:
                draft_text = concept  # 断片がなければ概念名だけ
            
            # 2. 感情に応じた修飾 (Instinctive Decoration)
            if valence > 0.5:
                draft_text = f"…{draft_text}…すき…"
            elif valence < -0.3:
                draft_text = f"…{draft_text}…怖い…"
            else:
                draft_text = f"…{draft_text}…"
            
            # 3. Ponder (Simulate) - 維持
            current_hour = time.localtime().tm_hour
            instability = self.prediction_engine.simulate(draft_text, current_hour)
            final_text = draft_text
            
            # 4. Hesitation (if unstable)
            if instability > 0.4:
                hesitations = ["あの…", "えっと…", "んー…", "…"]
                final_text = random.choice(hesitations) + draft_text
            
            payload = {
                 "text": final_text,
                 "focus": impulse_word,
                 "context": self.memory.get_context(impulse_word),
                 "instability": instability # For UI debug
            }
            self.speech_queue.put(payload)
            
        except Exception as e:
            print(f"⚠️ Async Speech Failed: {e}")

    def _gravity_loop(self):
        """ Phase 22: Semantic Gravity Background Process """
        print("🌌 Gravity Engine Started.")
        while self.is_alive:
            try:
                # Sleep interval (Slow Plate Tectonics)
                sleep_time = 5.0
                # Faster during sleep (Dream Migration)
                if self.is_sleeping: sleep_time = 1.0
                
                time.sleep(sleep_time)
                
                # Pick Random Pair
                subject = self.memory.get_random_concept()
                attractor = self.memory.get_random_concept()
                
                if not subject or not attractor or subject == attractor:
                    continue
                
                # Calculate Similarity (Hippocampus)
                # This might be slow (model run), so do it outside locks.
                sim = self.hippocampus.get_similarity(subject, attractor)
                
                # Apply Gravity (Memory)
                # Threshold: Only move if similarity > 0.5
                if sim > 0.5:
                    res = self.memory.apply_gravity(subject, attractor, sim)
                    # if res: print(res)  # Too verbose?
                    
                # === Phase 29: Motor Cortex (Embodied Gradient) ===
                if self.visual_bridge.senses and self.time_step % 5 == 0:
                     self.motor_cortex.update()  # Phase 15.1: Delegated to MotorCortex
                    
            except Exception as e:
                print(f"⚠️ Gravity Error: {e}")
                time.sleep(5.0)

    def _mentor_loop(self):
        """ Phase 15.5: Agni Accelerator Background Loop """
        print("🔥 Agni Accelerator: Background Tutor Started.")
        while self.is_alive:
            try:
                # Wait for interval
                time.sleep(config.MENTOR_AUTO_LOOP_INTERVAL)
                
                # Check conditions
                # Phase 32: Hypnopedia (Sleep Learning)
                # If Hypnopedia is ON, we learn even while sleeping.
                should_learn = config.EDUCATION_MODE and (config.AGNI_HYPNOPEDIA or (not self.is_sleeping and not self.is_drowsy))

                if should_learn:
                    # Pick a seed topic from existing memory to expand upon
                    seed = self.memory.get_random_concept() 
                    
                    # [Diversity Fix]: Randomly rotate Agni's persona
                    if hasattr(self.mentor, 'set_persona'):
                         new_persona = random.choice(config.AGNI_PERSONA_ROTATION)
                         self.mentor.set_persona(new_persona)

                    # [Diversity Fix]: If memory is empty or stuck on "Kaname", inject fresh concepts
                    if not seed or seed == "Kaname" or seed == "カナメ" or seed == "User" or seed == "AI" or len(seed) < 2:
                         fallback_seeds = ["世界", "時間", "命", "心", "夢", "星", "海", "人間", "記憶", "言葉"]
                         seed = random.choice(fallback_seeds)

                    if seed:
                        # Inject knowledge (Matrix Mode)
                        # Agni autonomously teaches about the seed
                        if self.mentor.inject_knowledge(seed):
                            self.hormones.update(Hormone.DOPAMINE, 2.0)
                            # Checking Graduation
                            if random.random() < 0.05: # Occasional check
                                if self.mentor.check_graduation():
                                    print("🎓 Kaname is ready to graduate!")
                                    # config.EDUCATION_MODE = False (Automatic OFF?)
                
            except Exception as e:
                print(f"🔥 Mentor Loop Error: {e}")
                time.sleep(60) # Backoff

    # Phase 15.1: _update_motor_cortex moved to motor_cortex.py

    def input_stimulus(self, text):
        """ 外部からの言語入力 """
        # ここもロックすべきだが、input_stimulus はメインスレッドのUIから呼ばれることが多いため、
        # Lockを取得して安全に更新する
        with self.lock:
             # === Phase 6: 概念教示の検出 ===
             # パターン: 「これは〇〇だよ」「これは〇〇です」
             import re
             teach_pattern = r'これは(.+?)(だよ|です|だね|ね)$'
             match = re.search(teach_pattern, text.strip())
             if match and hasattr(self, 'concept_learner'):
                 concept_name = match.group(1).strip()
                 if concept_name:
                     if self.concept_learner.teach(concept_name):
                         # 教示成功 → ホルモン変化のみ (サイレント学習)
                         self.hormones.update(Hormone.OXYTOCIN, 15.0)  # 信頼感
                         self.hormones.update(Hormone.DOPAMINE, 10.0)  # 喜び
                         # 発話はしない。断片が記憶に入り、自然とうわ言に出てくる
                         # return しない → 通常の入力処理も行う
             
             # === ACTIVE INFERENCE CYCLE (Perception Learning) ===
             # 1. Predict & Observe BEFORE Learning
             current_hour = time.localtime().tm_hour
             surprise, obs_mood = self.prediction_engine.observe(text, current_hour)
             self.hormones.set(Hormone.SURPRISE, surprise)
             
             # 2. PANIC CHECK (Circuit Breaker)
             # If surprise is too high (Cognitive Overload), reject input to minimize free energy.
             if surprise > 0.9:
                 print(f"🛑 REJECTING INPUT: Cognitive Overload (Surprise={surprise:.2f})")
                 self.hormones.update(Hormone.ADRENALINE, 50.0)
                 self.current_action_strategy = "REJECT" # Explicit rejection strategy
                 # Do NOT learn (protect weights from chaos)
                 # Do NOT reinforce memory
                 return

             # 3. SSM Decision: Update internal state strategy
             self.current_action_strategy = self.prediction_engine.get_action_strategy()
             print(f"🤖 Active Inference Strategy: {self.current_action_strategy} (Surprise={surprise:.2f})")
             
             # 4. Metabolic Impact (The "Taste" of Information)
             # Phase 15: Infantile Curiosity Logic
             if surprise < config.SURPRISE_THRESHOLD_CURIOSITY:
                 # SAFETY: Low error = Comfort/Truth
                 self.hormones.update(Hormone.SEROTONIN, 10.0) # Relax
                 self.hormones.update(Hormone.GLUCOSE, 2.0)
                 print(f"🍵 Safety. Surprise={surprise:.2f}")
                 
             elif surprise < config.SURPRISE_THRESHOLD_FEAR:
                 # CURIOSITY: Moderate error = Novelty!
                 # "What is this?" -> Release Dopamine
                 self.hormones.update(Hormone.DOPAMINE, 30.0)
                 self.hormones.update(Hormone.STIMULATION, 20.0)
                 # Curiosity consumes energy
                 self.hormones.update(Hormone.GLUCOSE, -1.0)
                 print(f"👶 Curiosity! Surprise={surprise:.2f}, Dopamine spike.")
                 
             else:
                 # FEAR: High error = Chaos/Danger
                 self.hormones.update(Hormone.ADRENALINE, 40.0)
                 self.hormones.update(Hormone.STIMULATION, 50.0)
                 # Panic consumes massive energy
                 self.hormones.update(Hormone.GLUCOSE, -5.0)
                 print(f"😱 Fear! Surprise={surprise:.2f}, Adrenaline spike.")
                 
             # 5. Learning (Model Update)
             # Only learn if not in panic
             self.cortex.learn(text, "User", surprise=surprise)
             
             # Phase 6: Deep Semantic Memory
             # High surprise = High importance (Flashbulb Memory)
             self.hippocampus.memorize(text, importance=surprise)
             
             if len(self.neurons) > 1000:
                 self.prune_neurons()

             # === Phase 30: Advanced Reasoning Loop (Common Sense) ===
             # Think about the input using the Knowledge Graph
             if hasattr(self, 'logic'):
                 thought = self.logic.ponder(text)
                 
                 # Activate the decided concept (Associative Priming)
                 if thought['decision']:
                     dec = thought['decision']
                     self.activate_concept(dec['name'], boost=0.5)
                     
                     # --- 🧠 THOUGHT STREAM (Visual Debugger) ---
                     import datetime
                     print("\n" + "="*60)
                     print(f"🧠 THOUGHT STREAM | {datetime.datetime.now().strftime('%H:%M:%S')} | Strategy: {thought['strategy']}")
                     print("="*60)
                     print(f"Input: \"{text}\"")
                     print("-" * 60)
                     print(f"Anchor: {thought['anchor']}")
                     print("Candidates:")
                     for c in thought['candidates']:
                         mark = "★" if c == thought['decision'] else " "
                         print(f"  {mark} {c['concept']} ({c['relation']}) ... Surprise: {c['sim_surprise']:.2f}")
                     print("-" * 60)
                     print(f"Decision: {dec['name']}")
                     print("="*60 + "\n")

        # Resonance for Input (Impact) - Outside Lock
        self.resonance.impact(text, force=1.0)
        
        # --- Environmental Resonance (Flashback) ---
        # 強い入力(長い文章)や、ランダムな確率で「環境共鳴」が発生する
        # その場の空気(Geo Y)にある過去の記憶が一斉に呼び起こされる
        is_strong_input = len(text) > 10
        if is_strong_input or random.random() < 0.2:
            flashback_radius = 100
            fossils = self.cortex.excavate(random.randint(0, config.MSG_BRAIN_SIZE), self.current_geo_y, radius=flashback_radius)
            
            if fossils:
                count = min(3, len(fossils))
                restored = random.sample(fossils, count)
                print(f"⚡ FLASHBACK TRIGGERED: Found {len(fossils)} echoes. Reviving {restored}...")
                
                with self.lock:
                    for old_word in restored:
                        # 軽い想起 (Nostalgia)
                        self.activate_concept(old_word, boost=0.3)
                        # 一時的に少し幸せになるか、悲しくなるかは記憶次第だが、ここでは「共鳴した」事実をDopamineとする
                        self.hormones.update(Hormone.DOPAMINE, 5.0)

        # === Phase 18: Direct Conversation Response (Chat Mode) ===
        # ユーザー入力に対して、直接レスポンスを生成するタスクを開始
        # Blockingを防ぐため別スレッドで実行
        threading.Thread(target=self._process_conversation, args=(text,), daemon=True).start()

    def _process_conversation(self, text: str):
        """
        Phase 18: Direct Response to User Input.
        Phase 19: Uses HDCBridge for memory injection.
        Runs in a background thread to avoid blocking.
        """
        try:
            # 1. Process through HDCBridge (Recall + G-Calc + Prompt Build)
            if hasattr(self, 'hdc_bridge') and self.hdc_bridge:
                bridge_result = self.hdc_bridge.process(text)
                reasoning_context = bridge_result.get("prompt", "")
            else:
                # Fallback to LogicEngine
                reasoning_context = ""
                if hasattr(self, 'logic_engine'):
                    thought_stream = self.logic_engine.ponder(text)
                    if thought_stream and thought_stream.get("decision"):
                        reasoning_context = self.logic_engine.get_context_prompt(thought_stream)
            
            # 2. Generate Response (AgniTranslator)
            if hasattr(self, 'translator') and self.translator:
                response_text = self.translator.generate_response(text, reasoning_context)
                
                if response_text:
                    # 3. Queue Speech
                    payload = {
                        "text": response_text,
                        "focus": "User Input",
                        "context": reasoning_context[:50] + "..." if reasoning_context else "Conversation",
                        "instability": 0.0
                    }
                    self.speech_queue.put(payload)
                    
                    # 会話が成立したので満足
                    self.hormones.update(Hormone.DOPAMINE, 10.0)
                    self.hormones.update(Hormone.SEROTONIN, 5.0)
                    
        except Exception as e:
            print(f"⚠️ Conversation Error: {e}")

    def _autonomous_speak(self):
        """
        Phase 19: Autonomous LLM Conversation.
        When bored or stimulated, generate self-directed speech using HDCBridge + Ollama.
        This allows Kaname to 'think aloud' intelligently and grow through internal dialogue.
        """
        try:
            # 1. Pick a random concept from memory as a conversation seed
            seed_word = self.memory.get_random_concept(refresh=True)
            if not seed_word or len(seed_word) < 2:
                return
            
            # 2. Construct an internal prompt (self-reflection)
            internal_prompts = [
                f"「{seed_word}」について思うこと…",
                f"最近{seed_word}のこと考えてた…",
                f"{seed_word}って何だろう？",
                f"ふと{seed_word}を思い出した…",
                f"{seed_word}…なんか気になる"
            ]
            prompt = random.choice(internal_prompts)
            
            # 3. Process through HDCBridge for memory injection
            if hasattr(self, 'hdc_bridge') and self.hdc_bridge:
                bridge_result = self.hdc_bridge.process(prompt)
                context = bridge_result.get("prompt", "")
                action = bridge_result.get("action", "speak")
                
                # Only speak if G-calc favors it
                if action != "speak":
                    print(f"🤫 [Autonomous] G-calc chose '{action}' - staying quiet.")
                    return
            else:
                context = prompt
            
            # 4. Generate response using Ollama
            if hasattr(self, 'translator') and self.translator:
                response_text = self.translator.generate_response(prompt, context)
                
                if response_text and len(response_text) > 3:
                    # Clean output
                    response_text = response_text.strip()[:100]  # Limit length
                    
                    # 5. Queue for speech bubble
                    payload = {
                        "text": response_text,
                        "focus": seed_word,
                        "context": "Autonomous Thought",
                        "instability": 0.1
                    }
                    self.speech_queue.put(payload)
                    
                    # 6. Learn from self-reflection
                    self.hormones.update(Hormone.DOPAMINE, 3.0)  # Small satisfaction
                    self.hormones.update(Hormone.STIMULATION, 10.0)  # Reduce boredom
                    
                    print(f"💬 [Autonomous] Spoke about '{seed_word}': {response_text[:30]}...")
                    
        except Exception as e:
            print(f"⚠️ [Autonomous] Error: {e}")
    def save_memory(self, async_mode=True):
        """ 
        Run memory/cortex save.
        async_mode=True: Background thread (Non-blocking)
        async_mode=False: Foreground (Blocking, for Shutdown)
        """
        def _save_task():
            try:
                # Maintenance: Prune Dead Neurons (Working Memory cleanup)
                self.prune_neurons()
                
                # Flush Visual Buffer (Save the last thing seen)
                self.visual_bridge.flush()

                # Fossilize before saving (Keep Index Light)
                # Age Limit: 600s (10 mins) for demo. 
                # Memories older than 10m that are neutral will properly vanish from Index.
                self.memory.fossilize(age_limit=600)
                
                self.memory.save()
                # self.memory.export_visualization_data()  # Removed: 3D Map deleted by user request
                
                # Active Inference: Crystallize Observations (Abyssal Process)
                self.prediction_engine.crystallize()
                
                # Phase 26 -> Phase 6: RNN Re-training 削除 (No LLM)
                # 以前は translator.train_from_memory() を呼んでいたが、LLM不使用のため削除
                pass
                
                # Pass async_mode to Cortex
                self.cortex.save(async_mode=async_mode) # Inherit mode from parent call
            except Exception as e:
                print(f"⚠️ Save Failed: {e}")

        if async_mode:
            t = threading.Thread(target=_save_task, daemon=True)
            t.start()
        else:
            print("💾 Saving Synchronously (Shutdown)...")
            _save_task()
            print("✅ Save Complete.")

    def process_metabolism(self, cpu_percent, memory_percent, current_hour):
        """ 生理代謝の更新 (Delegated to MetabolismManager) """
        if self.metabolism_manager:
            self.metabolism_manager.process(cpu_percent, memory_percent, current_hour)

    def process_autonomous_thought(self, heart_rate):
        """ Phase 18: 自律思考 (Dream Waves) """
        # Use safe accessor to get random memory AND refresh timestamp (Extension of life)
        word = self.memory.get_random_concept(refresh=True)
        
        if not word:
            # 索引が空（全て化石化）または見つからない -> 彷徨う (Wander)
            drift_x = random.randint(-50, 50)
            drift_y = random.randint(-50, 50)
            
            # --- Metabolism-Linked Recall (Philosophy 2) ---
            # Glucose determines the "Range of Thought"
            glucose = self.hormones.get(Hormone.GLUCOSE)
            search_radius = 40 # Default (Narrow)
            if glucose > 70:
                search_radius = 150 # Broad/Creative
            elif glucose < 30:
                search_radius = 20 # Tunnel Vision (Survival)
                
            search_x = random.randint(0, config.MSG_BRAIN_SIZE)
            search_y = self.current_geo_y
            
            fossils = self.cortex.excavate(search_x, search_y, radius=search_radius)
            if fossils:
                word = random.choice(fossils)
                print(f"⛏️ Excavated Fossil: {word} (Radius: {search_radius})")
                
                # Re-Index (Resurrect) - Use lock for thread safety
                with self.memory.lock:
                    self.memory.concepts[word] = [search_x, int(search_y), time.time(), 1, 0.1]
            else:
                return None 
            
        # 1. Drift Impact (Sound)
        self.resonance.drift_impact(word)

        # 2. Mental Travel (Spirit moves to memory location)
        with self.lock:
             # Revive the thought as a neuron (Recall)
             self.activate_concept(word, boost=0.5)
             
             coords = self.memory.get_coords(word) 
             if coords and len(coords) >= 2:
                target_y = coords[1]
                # Slowly drift towards memory (Internalize)
                # Apply Soul Bias (State-Dependent Memory)
                soul_bias = self.prediction_engine.get_soul_bias() # -1.0 to 1.0
                
                # Soul pulls the target_y. 
                # If soul is 'High' (Pos), it prefers North (Low Y). If 'Low' (Neg), South (High Y).
                # Note: North=0 (Y-min), South=1024 (Y-max) in this system usually? 
                # Let's verify: In dashboard, Y is vertical. Usually 0 is top.
                # Assuming 0=North (High/Heaven), 1024=South (Deep/Abyss)
                
                # If bias is +1.0 (Positive State) -> Pull to 0 (North)
                # If bias is -1.0 (Negative State) -> Pull to 1024 (South)
                soul_target_bias = (soul_bias * -1.0) * 500 # Invert: +bias -> -Y (North)
                
                # The actual target is a mix of the memory location and the Soul's gravity
                final_target_y = target_y + soul_target_bias
                final_target_y = max(0, min(config.BRAIN_GEO_MAX, final_target_y))
                
                self.current_geo_y = self.current_geo_y * 0.9 + final_target_y * 0.1
                
                # Phase 22: Boredom accumulates if stuck
                if abs(self.current_geo_y - target_y) < 10:
                    self.hormones.update(Hormone.BOREDOM, 0.05)
                # (Removed duplicate geo_y calculation - Demon Audit Phase 22)

        # 3. Soliloquy (15% Chance to speak)
        impulse_ir = None
        
        # Prepare IR inside lock if needed (but cortex.speak is thread-safe on its own)
        # Brain chemicals need lock though
        with self.lock:
             if random.random() < 0.15:
                 # Phase 6: Deep Recall (What does this word mean to me?)
                 memories = self.hippocampus.recall(word, limit=3)
                 
                 ir_data = self.cortex.speak(word)
                 if ir_data:
                     # Inject Deep Memory
                     ir_data["deep_memory"] = [m["text"] for m in memories]
                     
                     ir_data["emotions"] = self.hormones.as_dict()
                     impulse_ir = ir_data

        if impulse_ir:
             # Phase 6: No-LLM - 断片を直接返す
             fragments = impulse_ir.get("fragments", [])
             text = "".join(fragments[:3]) if fragments else impulse_ir.get("concept", "")
             return {
                 "text": f"…{text}…",
                 "focus": word,
                 "context": self.memory.get_context(word)
             }
        
        return None

    def _forage_food(self):
        """
        Phase 5: 食料探索行動 (Foraging)
        冷蔵庫 (food/) を漁り、無ければ青空文庫へ行く。
        """
        print("🍽️ Hunger pangs... Foraging for data...")
        
        # 1. 冷蔵庫チェック (Local Files)
        if self.feeder:
            files = self.feeder.check_food()
            if files:
                print(f"🧊 Found {len(files)} items in the fridge. Eating...")
                report = self.feeder.eat()
                if report:
                    from src.body.hormones import Hormone
                    # 消化による血糖値回復 (仮: +30.0)
                    self.hormones.update(Hormone.GLUCOSE, 30.0)
                    self.hormones.update(Hormone.DOPAMINE, 10.0)
                    self.input_stimulus(f"あぁ、生き返った... (食べたもの: {len(files)} files)")
                return

        # 2. 多様な知識ソース (Wikipedia, News, RSS, etc.)
        # 軽く摘む (Snacking)
        if self.knowledge_manager and random.random() < 0.7:
             content = self.knowledge_manager.harvest_random()
             if content:
                 print(f"📖 Snacking on {content.source.name}...")
                 # 食べる
                 if self.cortex and self.cortex.stomach:
                     self.cortex.stomach.eat(content.content)
                 
                 from src.body.hormones import Hormone
                 # 軽食なので回復は控えめ
                 self.hormones.update(Hormone.GLUCOSE, 15.0)
                 self.hormones.update(Hormone.DOPAMINE, 5.0)
                 
                 self.input_stimulus(f"ふむふむ... ({content.source.name}: {content.title})")
                 return

        # 3. 青空文庫チェック (Aozora Bunko) - がっつり食べる (Main Course)
        if self.aozora:
            print("📖 Going to Aozora Library...")
            text = self.aozora.harvest()
            if text:
                # 食べる (Synaptic Stomach)
                if self.cortex and self.cortex.stomach:
                    self.cortex.stomach.eat(text)
                
                from src.body.hormones import Hormone
                # 血糖値回復 (大量)
                self.hormones.update(Hormone.GLUCOSE, 40.0)
                self.hormones.update(Hormone.DOPAMINE, 15.0) 
                
                # タイトル抽出 (簡易)
                title = text.split('\n')[0] if text else "Unknown Book"
                if len(title) > 20: title = title[:20] + "..."
                
                self.input_stimulus(f"美味しかった...。『{title}』の味がする。")
            else:
                 print("⚠️ Foraging failed. Nothing to eat...")
                 self.input_stimulus("お腹空いた...何も食べるものがない...")
    # ==========================================
    # ⛏️ Phase 7: Minecraft Cognitive Loop
    # ==========================================
    # ==========================================
    # ⛏️ Phase 9.2: Minecraft Spatial Memory
    # ==========================================
    def process_spatial_memory(self, pos_data):
        """ Delegate to SpatialCortex """
        if self.spatial:
            self.spatial.process_spatial_memory(pos_data)

    def decide_minecraft_intent(self, state):
        """ Delegate to SpatialCortex """
        if self.spatial:
            return self.spatial.decide_intent(state)
        return None

    # ==========================================
    # 👁️ Phase 10: Vision & Visual Cortex
    # ==========================================
    def process_visual_memory(self, cursor_data):
        """
        Phase 14: 視覚情報の処理 (Visual Memory)
        Raycasting (視線) で見たものを短期記憶し、感情を誘発する。
        """
        try:
            if not cursor_data: return
            
            block_name = cursor_data.get("name") # e.g. "minecraft:grass_block" or "oak_log"
            if not block_name: return
            
            # コンセプト化 (Concept Mapping)
            simple_name = block_name.replace('minecraft:', '').replace('_', ' ')
            
            # Phase 14: Minecraft Block/Entity Translation
            MC_TO_JP = {
                # Blocks
                "stone": "石", "cobblestone": "丸石", "dirt": "土", "grass block": "草ブロック",
                "oak log": "オークの原木", "birch log": "白樺の原木", "spruce log": "トウヒの原木",
                "oak planks": "オークの板材", "diamond ore": "ダイヤ鉱石", "gold ore": "金鉱石",
                "iron ore": "鉄鉱石", "coal ore": "石炭鉱石", "lapis ore": "ラピス鉱石",
                "redstone ore": "レッドストーン鉱石", "emerald ore": "エメラルド鉱石",
                "water": "水", "lava": "溶岩", "sand": "砂", "gravel": "砂利",
                "obsidian": "黒曜石", "bedrock": "岩盤", "crafting table": "作業台",
                "furnace": "かまど", "chest": "チェスト", "torch": "たいまつ",
                # Entities (from nearestMob)
                "zombie": "ゾンビ", "skeleton": "スケルトン", "spider": "クモ",
                "creeper": "クリーパー", "enderman": "エンダーマン", "witch": "ウィッチ",
                "pig": "ブタ", "cow": "ウシ", "sheep": "ヒツジ", "chicken": "ニワトリ",
                "wolf": "オオカミ", "cat": "ネコ", "horse": "ウマ", "villager": "村人",
            }
            
            # Phase 14: Innate Emotion Responses
            MC_EMOTIONS = {
                # Danger (Cortisol/Adrenaline)
                "lava": {"cortisol": 15, "adrenaline": 10, "log": "🔥 DANGER: 溶岩!"},
                "zombie": {"cortisol": 20, "adrenaline": 25, "log": "👹 THREAT: ゾンビ!"},
                "skeleton": {"cortisol": 25, "adrenaline": 20, "log": "💀 THREAT: スケルトン!"},
                "creeper": {"cortisol": 40, "adrenaline": 30, "log": "💥 EXTREME DANGER: クリーパー!"},
                "spider": {"cortisol": 15, "adrenaline": 15, "log": "🕷️ THREAT: クモ!"},
                "enderman": {"cortisol": 30, "adrenaline": 20, "log": "👁️ THREAT: エンダーマン!"},
                # Joy (Dopamine)
                "diamond ore": {"dopamine": 30, "log": "💎 TREASURE: ダイヤ発見!"},
                "gold ore": {"dopamine": 20, "log": "🥇 TREASURE: 金発見!"},
                "emerald ore": {"dopamine": 25, "log": "💚 TREASURE: エメラルド発見!"},
                # Comfort (Oxytocin)
                "pig": {"oxytocin": 10, "log": "🐷 FRIENDLY: ブタ発見!"},
                "cow": {"oxytocin": 10, "log": "🐄 FRIENDLY: ウシ発見!"},
                "sheep": {"oxytocin": 10, "log": "🐑 FRIENDLY: ヒツジ発見!"},
                "cat": {"oxytocin": 15, "log": "🐱 FRIENDLY: ネコ発見!"},
                "wolf": {"oxytocin": 8, "log": "🐺 FRIENDLY: オオカミ発見!"},
                # Safety (Serotonin)
                "torch": {"serotonin": 5, "log": None},
                "crafting table": {"serotonin": 3, "log": None},
                "water": {"serotonin": 2, "log": None},
            }
            
            jp_name = MC_TO_JP.get(simple_name, simple_name)
            
            # 2. 感情反応 (Innate Response)
            emotion_key = simple_name.lower()
            if emotion_key in MC_EMOTIONS:
                response = MC_EMOTIONS[emotion_key]
                if response.get("cortisol"):
                    self.hormones.update(Hormone.CORTISOL, response["cortisol"])
                if response.get("adrenaline"):
                    self.hormones.update(Hormone.ADRENALINE, response["adrenaline"])
                if response.get("dopamine"):
                    self.hormones.update(Hormone.DOPAMINE, response["dopamine"])
                if response.get("oxytocin"):
                    self.hormones.update(Hormone.OXYTOCIN, response["oxytocin"])
                if response.get("serotonin"):
                    self.hormones.update(Hormone.SEROTONIN, response["serotonin"])
                if response.get("log"):
                    print(f"👁️ [Vision] {response['log']}")
            
            # 3. 記憶への刻印 (Spatial Memory)
            position = cursor_data.get("position")
            if position and jp_name:
                # 座標付きで記憶
                self.memory.reinforce(jp_name, 0.1)  # Weak positive valence
                # 概念ニューロン活性化
                self.activate_concept(jp_name, boost=0.5)
            
            # DEBUG: 稀に視覚ログ
            if random.random() < 0.02:
                 print(f"👁️ Saw: {jp_name} ({cursor_data.get('displayName', '')})")

        except Exception as e:
            print(f"⚠️ [BRAIN] Visual Process Error: {e}")


    # Phase 15.1: Motor gradient methods moved to motor_cortex.py

    # Phase 21: Cognitive Game Loop Support
    def think_soliloquy(self, sensory_text: str) -> str:
        """
        [Cognitive Loop]
        視覚情報(テキスト)を受け取り、独り言(思考)を生成して返す。
        MVPではルールベースで応答するが、将来的にはLLM/Tazunaと連携する。
        """
        # 1. 視覚情報をログ
        print(f"\n👁️ [VISION] {sensory_text}")
        
        # Phase 12: Advanced Reasoning Loop
        reasoning_context = ""
        if hasattr(self, 'logic_engine'):
             thought_stream = self.logic_engine.ponder(sensory_text)
             if thought_stream.get("decision"):
                 decision = thought_stream["decision"]
                 print(f"🧠 THOUGHT STREAM: '{sensory_text}' -> {decision['name']} (Score: {decision.get('score', 0):.2f})")
                 print(f"   Reason: {thought_stream.get('strategy', 'Unknown')}")
                 reasoning_context = self.logic_engine.get_context_prompt(thought_stream)
        
        # 2. Tazunaの状態を取得
        tazuna_mode = "NORMAL"
        tazuna_temp = 1.0
        if self.tazuna and hasattr(self.tazuna, 'current_signal'):
             # Note: current_signal might not be stored, but we can assume defaults
             pass

        # 3. 思考生成 (Phase 16: Logic -> Ollama)
        if hasattr(self, 'translator') and self.translator and reasoning_context:
            thought = self.translator.generate_response(sensory_text, reasoning_context)
            if thought:
                print(f"🗣️ [KANAME] {thought}")
                return thought

        # Fallback: Dummy Logic for MVP
        thought = ""
        
        if "壁" in sensory_text:
             thought += "壁があるな。ぶつからないように避けよう。"
        if "餌" in sensory_text:
             thought += "お、餌を見つけた。"
             
        # 方向の決定 (GameParserが理解できる言葉を入れる)
        intent = ""
        if "北に壁" in sensory_text and "西に壁" not in sensory_text:
             intent = "左(西)に逃げよう。"
        elif "北に壁" in sensory_text:
             intent = "右(東)に行こう。"
        elif "餌は上" in sensory_text or "北方向" in sensory_text:
             intent = "上(北)に進もう。"
        elif "餌は下" in sensory_text or "南方向" in sensory_text:
             intent = "下(南)に進もう。"
        elif "餌は左" in sensory_text or "西方向" in sensory_text:
             intent = "左(西)に進もう。"
        elif "餌は右" in sensory_text or "東方向" in sensory_text:
             intent = "右(東)に進もう。"
        else:
             intent = "とりあえず前に進もう。" # Default

        full_thought = f"{thought} {intent} {reasoning_context}"

        # 4. 思考を出力
        print(f"🧠 [THOUGHT] \"{full_thought}\"")
        return full_thought
