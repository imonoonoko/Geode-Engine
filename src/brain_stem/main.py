# main.py
import tkinter as tk
import threading
import time
import math
import random
import psutil
import numpy as np
from datetime import datetime
import os
import src.dna.config as config
from src.brain_stem.brain import GeodeBrain 
from src.body.Geode_body import GeodeBody 
from src.senses.Geode_senses import GeodeSenses 
from src.body.throat import GeodeThroat 
from src.body.immune import GeodeImmuneSystem
from src.tools.telemetry_server import TelemetryServer
import warnings

# --- Suppress startup warnings ---
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")
warnings.filterwarnings("ignore", category=FutureWarning, module="google.api_core")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch")
# ---------------------------------

# ==========================================
# 🍬 M.A.I.A. Core (Orchestrator)
# ==========================================
class MaiaSystem:
    def __init__(self):
        print("🍬 Initializing M.A.I.A. System Orchestrator...")
        self.is_active = True
        self.is_alive = True 
        
        # 🧠 Brain (Logic)
        self.brain = GeodeBrain()
        self.time_step = 0
        
        # 👻 Body (UI & Physics)
        self.body = GeodeBody(self.brain)
        
        # 👁️ Senses (Async)
        self.senses = GeodeSenses()
        
        # Phase 28: Connect Brain to Senses (Active Inference)
        self.brain.visual_bridge.connect_senses(self.senses)
        
        # Phase 29: Connect Senses to Body (Motor Cortex needs body reference)
        self.senses.body = self.body
        
        # 🔊 Voice (Async Load)
        # Prevent blocking startup. Initialize in background.
        self.throat = None
        threading.Thread(target=self._init_throat_async, daemon=True).start()
        
        # Vitals
        self.heart_rate = 60
        self.cpu_percent = 0
        
        # 🛡️ Immune System (Phase 12)
        self.immune = GeodeImmuneSystem(self.brain)
        
        # 🍽️ Wire up Feed Callback
        self.body.on_feed_file = self._handle_feed_file
        
        # 📡 Telemetry Server (for React Dashboard)
        self.telemetry = TelemetryServer(self.brain, ws_port=8765)
        self.telemetry.run_in_thread()
        
        # Phase 6: Connect Body HAL (DEF-02 修正)
        if hasattr(self.brain, 'body_hal') and self.brain.body_hal:
            self.brain.body_hal.connect(self.body)
        
        print("✅ System Initialization Complete.")



    def _init_throat_async(self):
        """ Background initialization for heavy voice model """
        try:
             self.throat = GeodeThroat(self.brain.memory)
        except Exception as e:
             print(f"⚠️ Throat Async Init Failed: {e}")

    def _handle_feed_file(self, content):
        """ Handle direct file feeding from UI (Active Inference Integrated) """
        print(f"🍽️ Received content to feed ({len(content)} chars)")
        
        # 1. PANIC CHECK (Surprise Barrier)
        # Note: surprise uses 0-1 scale, different from 0-100 hormones
        from src.body.hormones import Hormone
        surprise = self.brain.hormones.get(Hormone.SURPRISE)
        if surprise > 0.8:
            print(f"🚫 REJECTED FEEDING: Too much surprise ({surprise:.2f})")
            self.brain.cortex.speak("今は...頭がいっぱいで...読めない...", strategy="REJECT")
            # Phase 8: HormoneManager
            from src.body.hormones import Hormone
            self.brain.hormones.update(Hormone.CORTISOL, 5.0) # Increase cortisol on rejection
            return False

        # 2. APPETITE CHECK (Epistemic Value)
        boredom = self.brain.hormones.get(Hormone.BOREDOM)
        craving_multiplier = 1.0
        
        if boredom > 0.6:
            craving_multiplier = 2.0
            print("😋 CRAVING: Geode is hungry for data!")
            
        # Eat (Clean/Shuffle) - Phase 6: Feederは直接brainに移動
        text = self.brain.feeder.eat_file(content, is_direct_text=True)
        if not text: return False

        # 3. METABOLIC RESPONSE
        char_count = len(text)
        
        # Hormones
        # Assuming file_size and file_path are available or can be derived for the new logic
        # For now, let's use char_count as a proxy for file_size if not explicitly passed.
        file_size = char_count # Placeholder
        file_path = "temp.txt" # Placeholder, actual path not available here

        from src.body.hormones import Hormone
        
        with self.brain.lock:
            # 1. 食べた満足感 (Satisfaction)
            # 大きいファイルほど満腹になる (Max +50.0)
            glucose_gain = min(50.0, file_size / 1024 / 10) 
            self.brain.hormones.update(Hormone.GLUCOSE, glucose_gain)
            
            # 2. 味覚 (Taste) -> Dopamine
            # 拡張子ごとの味覚定義 (configに移動すべきだが、一旦ここにハードコード)
            flavor_bonus = 0.0
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.py', '.js', '.ts']: # 大好物 (Logic)
                flavor_bonus = 20.0
            elif ext in ['.md', '.txt']: # 主食 (Data)
                flavor_bonus = 10.0
            elif ext in ['.png', '.jpg']: # おやつ (Visual)
                flavor_bonus = 15.0
            else: # ゲテモノ
                flavor_bonus = -5.0
            
            # ドーパミン (Delicious!) - 0-100 scale
            # gain は Phase 6 で 0.3 -> 30.0 に修正済みだが、ここでも再確認
            if flavor_bonus > 0:
                self.brain.hormones.update(Hormone.DOPAMINE, 30.0 + flavor_bonus)
                self.brain.hormones.update(Hormone.SEROTONIN, 10.0)
            else:
                 # 不味い
                self.brain.hormones.update(Hormone.CORTISOL, 5.0)
            
            # Update boredom based on craving_multiplier
            boredom_loss = 20.0 * craving_multiplier
            self.brain.hormones.update(Hormone.BOREDOM, -boredom_loss) # Decrease boredom

            # Serotonin for large files
            if char_count > 5000:
                 self.brain.hormones.update(Hormone.SEROTONIN, 10.0)

        # Voice Reaction
        if craving_multiplier > 1.5:
             self.brain.cortex.speak("こういうの...待ってた！", strategy="JOY")
        else:
             self.brain.cortex.speak("もぐもぐ...", strategy="RESONATE")

        # Trigger Learning (Synapse)
        print("🎓 Starting immediate learning (Synaptic Connection)...")
        # Phase 6 Fix: Route to SynapticStomach instead of missing Translator
        threading.Thread(target=self.brain.cortex.stomach.eat, args=(text,), daemon=True).start()
        
        return True

    def metabolism_loop(self):
        """ 生理・物理層の更新ループ (Body Update) """
        print("🧬 Metabolism Loop Started.")
        while self.is_active:
            # PC状態取得
            self.cpu_percent = psutil.cpu_percent(interval=0.5)
            memory_percent = psutil.virtual_memory().percent
            
            # 心拍数: CPU + メモリで加速
            self.heart_rate = 60 + int(self.cpu_percent * 0.8) + int(memory_percent * 0.4)
            
            # 脳の代謝更新
            hour = datetime.now().hour
            self.brain.process_metabolism(self.cpu_percent, memory_percent, hour)
            
            # 体の状態更新 (Brainの状態を反映)
            # 色や心拍をBodyに伝える
            self.body.update_state(self.heart_rate)
            
            # Body Movement Guided by Senses - Moved to Cognitive Loop for speed (10Hz)
            # g_data = self.senses.get_grid_motion()
            # if g_data:
            #     self.body.update_visual_senses(g_data) 
            
            # Phase 5: Automatic Feeding based on Appetite
            if self.time_step % 5 == 0:
                 files = self.brain.feeder.check_food()
                 if files:
                     try:
                         # Read one file
                         t_path = files[0]
                         with open(t_path, 'r', encoding='utf-8', errors='ignore') as f:
                             content = f.read()
                         
                         # Attempt to feed (Subject to Active Inference Panic Check)
                         # If success, delete file
                         # If rejected, keep file
                         if self._handle_feed_file(content):
                             try:
                                 os.remove(t_path)
                                 print(f"🗑️ Consumed and removed: {os.path.basename(t_path)}")
                             except: pass
                     except Exception as e:
                         print(f"⚠️ Feeding Error: {e}")

            time.sleep(1)
            self.time_step += 1

    def cognitive_loop(self):
        """ 視覚・思考層の更新ループ (Senses -> Brain -> Body) """
        print("🧠 Cognitive Loop Started.")
        while self.is_active:
            # 1. 視覚入力 (Senses -> Brain)
            # Update Focus (Foveated Vision)
            bx, by = self.body.get_center_pos()
            self.senses.update_focus(bx, by)
            
            v_data = self.senses.get_global_vision()
            if v_data: 
                self.brain.receive_sense(v_data)
            
            # Phase 14: Retina Guided Movement (Reflex)
            # Fetch Motion Grid independently (High Speed 10Hz)
            m_data = self.senses.get_grid_motion()
            if m_data:
                self.body.update_visual_senses(m_data)
            
            env_effect = self.senses.get_atmosphere()
            if env_effect: self.brain.receive_sense(env_effect)

            # Local Vision is now handled by Fovea, so explicit request is removed.
            
            # 2. 思考更新 (Brain Think)
            speech_payload = self.brain.think()
            
            # 3. 発話・行動 (Body/Throat Act)
            if speech_payload:
                text = speech_payload["text"]
                self.body.say(text) # Visual Bubble
                
                # Async Voice Request
                speed = config.VOICE_SPEED_NORMAL
                from src.body.hormones import Hormone
                if self.brain.hormones.get(Hormone.DOPAMINE) > config.THRESHOLD_HIGH: speed = config.VOICE_SPEED_JOY
                elif self.brain.is_drowsy or self.brain.is_sleeping: speed = config.VOICE_SPEED_SLEEP
                
                if self.throat:
                    self.throat.speak(
                        text, 
                        speed=speed, 
                        geo_y=self.brain.current_geo_y,
                        heart_rate=self.heart_rate
                    )
                
                print(f"🧠 Focus: {speech_payload['focus']} ({text}) @ {speech_payload['context']}")
            
            time.sleep(0.1)

    def autonomous_loop(self):
        """ Phase 18: 自律思考スレッド (Autonomous Life) """
        print("🌌 Autonomous Loop Started (Dream Waves)...")
        while self.is_active:
            # Dream Waves: Interval based on Heart Rate
            # User Request: Less frequent
            beat_time = 60.0 / max(30, self.heart_rate)
            
            if self.heart_rate < 70:
                multiplier = random.uniform(6.0, 10.0) # Relaxed (was 3-5)
            elif self.heart_rate > 90:
                multiplier = random.uniform(3.0, 5.0) # Excited (was 1-2)
            else:
                multiplier = random.uniform(4.0, 7.0) # Normal (was 2-3)
                
            interval = beat_time * multiplier
            
            time.sleep(interval)
            
            # Execute Thought
            speech_payload = self.brain.process_autonomous_thought(self.heart_rate)
            
            # Soliloquy Output
            if speech_payload:
                text = speech_payload["text"]
                print(f"💭 Soliloquy: {text}")
                
                # Small bubble, whisper speed
                self.body.say(text, speed=0.8) 
                
                # Phase 20: Voice Speed Scaling (Glucose)
                voice_speed = 0.9 # Default whisper
                with self.brain.lock:
                    from src.body.hormones import Hormone
                    glucose = self.brain.hormones.get(Hormone.GLUCOSE)
                    if glucose < config.THRESHOLD_LOW:
                        voice_speed = 0.75 # Weak
                    elif glucose > 80.0:
                        voice_speed = 1.1 # Excited

                # Voice (Quietly)
                if self.throat:
                    self.throat.speak(
                        text, 
                        speed=voice_speed, 
                        geo_y=self.brain.current_geo_y, 
                        heart_rate=self.heart_rate
                    )


    def run(self):
        print("🚀 Starting Threads...")
        
        # Wrap Logic with Immune System (White Blood Cells)
        protected_metabolism = self.immune.protect_loop(self.metabolism_loop, name="Metabolism")
        protected_cognitive = self.immune.protect_loop(self.cognitive_loop, name="Cognitive")
        protected_autonomous = self.immune.protect_loop(self.autonomous_loop, name="Autonomous")

        
        # Start Threads
        threads = [
            threading.Thread(target=protected_metabolism, daemon=True),
            threading.Thread(target=protected_cognitive, daemon=True),
            threading.Thread(target=protected_autonomous, daemon=True),
        ]

        for t in threads: t.start()
        
        print("🚀 Starting Body Threads...")
        # Start Body Threads (Physics & Animation)
        self.body.run_threads(self.immune)
        
        print("M.A.I.A. Core Type-G Running (Full Async Architecture)...")
        
        # Main Thread: UI Event Loop
        try:
            if self.body.root:
                print("📺 Entering Mainloop...")
                self.body.root.mainloop()
            else:
                print("❌ UI Root is None!")
        except KeyboardInterrupt:
            print("🛑 KeyboardInterrupt caught.")
            self.is_active = False
            self.is_alive = False
        except Exception as e:
            print(f"❌ Main Loop Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
             self._shutdown()

    def _shutdown(self):
        print("\nShutdown Sequence Initiated...")
        self.is_active = False
        self.is_alive = False
        self.body.is_alive = False
        self.senses.stop()
        if self.throat: self.throat.stop()
        self.brain.resonance.stop() # Phase 9: Stop resonance cleanup worker
        self.telemetry.stop() # Phase 17: Stop Telemetry Server
        self.brain.save_memory(async_mode=False) # Force Synchronous Save (Prevent Data Loss)
        print("Brain Saved.")

if __name__ == "__main__":
    print("⏳ Init M.A.I.A. ...")
    try:
        maia = MaiaSystem()
        print("✅ Init Complete. Running...")
        maia.run()
    except Exception as e:
        print(f"❌ Critical Init Error: {e}")
        import traceback
        traceback.print_exc()
