import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.brain_stem.brain import KanameBrain
from src.cortex.lesson_room import LessonRoom

def verify_agni_teaching():
    print("🧪 Starting Agni Language Teaching Verification...")
    
    # 1. Initialize Brain
    print("🧠 Initializing Brain...")
    brain = KanameBrain()
    
    # Check Agni connection
    if not brain.mentor.connected:
        print("⚠️ Agni is Offline (Mock Mode). Verification will use mock data.")
    else:
        print("🔥 Agni is Online.")

    # 2. Test Injection (Golden Fossil)
    print("\n🧪 [Test 1] Injection (Mentor)...")
    topic = "桜"
    print(f"   Injecting knowledge about '{topic}'...")
    brain.mentor.inject_knowledge(topic)
    
    # Wait for async threads? existing code seems sync enough for console print
    time.sleep(1)
    
    # 3. Test Excavation (Chimera)
    print("\n🧪 [Test 2] Excavation (Chimera)...")
    # Verify if the injected syntax is used.
    # We need to simulate a thought about '桜' or similar emotion.
    # Get vector for '桜'
    if hasattr(brain, 'prediction_engine'):
        vec = brain.prediction_engine._get_embedding_api(topic)
        if vec is not None:
            print(f"   Generating speech for '{topic}'...")
            speech = brain.language_center.speak(vec, valence_state=0.8)
            print(f"   🦁 Spoke: {speech}")
            
            # Check if it looks like a shell usage (simple heuristic)
            if speech:
                print("   ✅ Speech generated.")
            else:
                print("   ❌ No speech generated.")
        else:
            print("   ⚠️ Could not get vector for topic.")

    # 4. Test Lesson (LessonRoom)
    print("\n🧪 [Test 3] Interactive Lesson...")
    lesson = LessonRoom(brain)
    lesson.start_lesson(topic="猫", turns=2)

    print("\n✅ Verification Script Completed.")

if __name__ == "__main__":
    verify_agni_teaching()
