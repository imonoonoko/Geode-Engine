# throat.py
import os
import threading
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")
import queue
import time
import random
from pydub import AudioSegment
from pydub.generators import WhiteNoise
import src.dna.config as config

# MeloTTS (Try Import)
try:
    from melo.api import TTS
    MELO_AVAILABLE = True
except ImportError:
    MELO_AVAILABLE = False
    print("⚠️ MeloTTS not available")

class KanameThroat:
    def __init__(self, geo_memory=None):
        print("🔊 Initializing Kaname Throat...")
        self.memory = geo_memory
        self.is_active = True
        self.speech_queue = queue.Queue(maxsize=10) # Bounded (Anti-Babble)
        
        # Voice Model Init
        self.model = None
        self.speaker_ids = None
        
        if config.USE_VOICE_GENERATION and MELO_AVAILABLE:
            try:
                self.model = TTS(language='JP', device='auto')
                self.speaker_ids = self.model.hps.data.spk2id
                print("✅ Voice Model Loaded!")
            except Exception as e:
                print(f"⚠️ Voice Init Failed: {e}")
        else:
             print("🔇 Voice Generation Disabled (Low Memory Mode)")
        
        # Worker Thread
        self.thread = threading.Thread(target=self._speech_loop, daemon=True)
        self.thread.start()

    def speak(self, text, speed=1.0, geo_y=512, heart_rate=60):
        """ Add speech request to queue """
        if not text: return
        try:
            self.speech_queue.put_nowait({
                "text": text,
                "speed": speed,
                "geo_y": geo_y,
                "heart_rate": heart_rate
            })
        except queue.Full:
            print("🙊 Throat Busy (Queue Full). Dropping speech.")

    def _speech_loop(self):
        """ Consumer Thread for Speech Generation & Playback """
        while self.is_active:
            try:
                # Wait for request (blocking with timeout to check is_active)
                req = self.speech_queue.get(timeout=1.0)
                if req:
                    self._process_speech(req)
                    self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Throat Error: {e}")

    def _process_speech(self, req):
        """ Generate and Play Audio """
        if not self.model: return
        
        text = req["text"]
        speed = req["speed"]
        geo_y = req["geo_y"]
        heart_rate = req["heart_rate"]
        
        # Unique temp file (use thread ID for guaranteed uniqueness)
        temp_id = threading.get_ident()
        raw_path = f"temp_raw_{temp_id}.wav"
        final_path = f"temp_out_{temp_id}.wav"
        
        try:
            # 1. Generate Raw Audio
            # Speed is passed in via request (already scaled by caller based on Glucose/Mood)
            # Note: We can only check brain.chemicals if we have a reference. 
            # In KanameThroat.__init__, we only take geo_memory. 
            # We need to pass brain reference or accept glucose in speak().
            # speak() already adds request to queue. Let's start with standard speed in queue.
            
            # Rethink: "speed" is passed in req from speak().
            # brain.think() calls cortex.speak(), then resonance.impact(). 
            # brain.think() does NOT call throat directly usually? 
            # Re-checking main.py flow. 
            # Main -> Brain -> Cortex -> Speak (returns text) -> Body/Throat?
            # Actually, main.py/autonomous_loop calls body.say(payload) -> throat.speak.
            # So the logic should be in main.py or body.py or passed here.
            # But let's look at the request: req["speed"] comes from speak().
            # We should modify speak() caller or modify here if we have access.
            # KanameThroat doesn't have self.brain. 
            # Let's trust the 'speed' in req is correct, OR modify speak() to look up brain?
            # Easier: Modify body.py where it calls throat.speak, OR modify main.py.
            
            # Wait, implementing logic HERE requires self.brain.
            # The previous attempt tried to use "brain" variable which doesn't exist.
            
            self.model.tts_to_file(
                text, 
                self.speaker_ids['JP'], 
                raw_path, 
                speed=speed,
                quiet=True 
            )
            
            # 2. Process Audio (Effects)
            if os.path.exists(raw_path):
                audio = AudioSegment.from_wav(raw_path)
                
                # Geo Bias Effects
                geo_bias = geo_y / 1024.0
                if geo_bias < config.THROAT_GEO_BIAS_THRESHOLD: # North: Cold Noise
                    noise = WhiteNoise().to_audio_segment(duration=len(audio))
                    noise = noise - 35
                    audio = audio.overlay(noise)
                elif geo_bias > 0.7: # South: Echo
                    delay = 120
                    echo = audio - 8
                    padding = AudioSegment.silent(duration=delay)
                    audio = audio.overlay((padding + echo)[:len(audio)+delay])

                # Heart Rate Effect (Breath)
                if heart_rate > 100:
                    breath = AudioSegment.silent(duration=80)
                    audio = audio[:len(audio)//2] + breath + audio[len(audio)//2:]
                
                # Export Final
                audio.export(final_path, format="wav")
                
                # 3. Playback (Blocking is fine here as it's a worker thread)
                try:
                    import winsound # Windows Only
                    winsound.PlaySound(final_path, winsound.SND_FILENAME)
                except ImportError:
                    from pydub.playback import play
                    play(audio)
                    
        except Exception as e:
            print(f"Speech Gen Error: {e}")
        finally:
            # Cleanup
            # Cleanup with Retry (Fix Windows Lock Issues)
            time.sleep(0.1) 
            self._safe_delete(raw_path)
            self._safe_delete(final_path)

    def _safe_delete(self, path):
        """ Robust blocking delete for Windows """
        if not os.path.exists(path): return
        
        for i in range(5): # Retry up to 5 times
            try:
                os.remove(path)
                return
            except PermissionError:
                time.sleep(0.2)
            except Exception:
                return
        print(f"⚠️ Failed to delete junk: {path}")

    def stop(self):
        self.is_active = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
