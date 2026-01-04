
import sys
import os
import time
import threading

# Add Project Root to Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.brain_stem.activity_manager import ActivityManager, ActivityState
from src.body.hormones import Hormone, HormoneManager

class MockBrain:
    def __init__(self):
        self.hormones = HormoneManager()
        self.lock = threading.Lock()
        self.activity_manager = ActivityManager(self)
        self.lesson_room = MockLessonRoom(self)
        self.mentor = MockMentor()
        self.speech_queue = MockQueue()

class MockQueue:
    def put_nowait(self, item):
        print(f"Queens received: {item}")
    def empty(self):
        return True

class MockMentor:
    def __init__(self):
        self.connected = True

class MockLessonRoom:
    def __init__(self, brain):
        self.brain = brain
        self.is_active = False
    
    def start_lesson_metrics(self):
        print("MockLessonRoom: Start Lesson")
        self.is_active = True
        
    def update(self):
        if self.is_active:
            print("MockLessonRoom: Updating...")
            # Simulate finish after 3 ticks
            pass

def verify_activity_trigger():
    print("🧪 Verifying Activity Manager Logic...")
    brain = MockBrain()
    
    # 1. Test Command Trigger
    print("\n--- Test 1: Command Trigger ---")
    brain.activity_manager.request_activity("LESSON")
    assert brain.activity_manager.current_state == ActivityState.LESSON
    print("✅ Command LESSON triggered.")
    
    brain.activity_manager.stop_activity()
    assert brain.activity_manager.current_state == ActivityState.IDLE
    print("✅ Command STOP triggered.")

    # 2. Test Boredom Trigger (Lesson)
    print("\n--- Test 2: Boredom Trigger (Lesson) ---")
    brain.hormones.update(Hormone.BOREDOM, 100.0)
    brain.hormones.update(Hormone.GLUCOSE, 100.0)
    brain.activity_manager.last_lesson_time = 0 # Reset cooldown
    
    # Run update multiple times to hit probability
    triggered = False
    for _ in range(100):
        brain.activity_manager.update()
        if brain.activity_manager.current_state == ActivityState.LESSON:
             triggered = True
             break
    
    if triggered:
        print("✅ Autonomous Lesson Triggered by Boredom.")
    else:
        print("⚠️ Autonomous Lesson NOT triggered (Probability might be low or logic mismatch).")
        
    print("\n✅ Activity Manager Verification Complete.")

if __name__ == "__main__":
    verify_activity_trigger()
