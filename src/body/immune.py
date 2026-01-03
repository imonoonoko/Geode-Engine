import threading
import time
import traceback
import src.dna.config as config

import collections

class KanameImmuneSystem:
    def __init__(self, brain_ref):
        print("🛡️ Initializing Immune System (White Blood Cells)...")
        self.brain = brain_ref
        self.error_log = collections.deque(maxlen=100) # Ring Buffer (Phase 16)

    def protect_loop(self, target_loop_func, args=(), name="Unknown"):
        """ 
        Wraps an infinite loop function (like drift_loop). 
        If it crashes, it logs the error, spikes Pain, and RESTARTS the loop.
        """
        def _wrapper():
            # Death Counter (Phase 19 Demon Fix)
            death_count = 0
            last_death_time = time.time()
            
            while self.brain.is_alive:  # Resurrection Loop
                try:
                    target_loop_func(*args)
                    break 
                except Exception as e:
                    now = time.time()
                    if now - last_death_time < 60.0: # Stricter penalty (60s window)
                        death_count += 1
                    else:
                         death_count = 1 # Reset if survived long enough
                    last_death_time = now
                    
                    if death_count > 5:
                        print(f"💀 FATAL ERROR: {name} died too many times ({death_count}). Giving up.")
                        self._handle_infection(e, f"{name} (FATAL)")
                        break # Stop resurrection (Let thread die)

                    self._handle_infection(e, name)
                    print(f"🩹 Immune System repairing {name}... (Restarting in 2s)")
                    time.sleep(2.0) # Recovery time (Fever state)
        return _wrapper

    def _handle_infection(self, error, name):
        """ Error Handling Logic: Infection -> Pain """
        print(f"⚠️ IMMUNE ALERT: Infection detected in {name}!")
        print(f"🦠 Virus: {error}")
        # traceback.print_exc()

        # 1. Feel Pain (via Event System)
        if self.brain:
            # Phase 8 Step 3: Event-Driven Architecture
            from src.body.events import Event
            self.brain.events.emit(Event.ERROR_OCCURRED, source=name, error=str(error))

        # 2. Log
        self.error_log.append({"time": time.time(), "source": name, "error": str(error)})
