
import os
import json
import sqlite3
import glob

MEMORY_DIR = "memory_data"

def hard_reset():
    print("🧹 STARTING HARD MEMORY RESET (EXORCISM) 🧹")
    
    # 1. Delete Sediments (Short Term Memory / Conversation Logs)
    targets = [
        "brain_sediments.db",
        "brain_sediments.json",
        "brain_sediments.json.migrated",
        "brain_stomach_data.json", # Synaptic Stomach
        "digestion_log.json",
        "brain_combat.json",
        # HDC (Soul) Files - The Zombie hides here!
        "brain_hashes.pkl",
        "brain_terrain.npy",
        "rnn_vocab.json"
    ]
    
    for t in targets:
        path = os.path.join(MEMORY_DIR, t)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"✅ Deleted: {t}")
            except Exception as e:
                print(f"❌ Failed to delete {t}: {e} (Is Kaname still running?)")
    
    # 2. Clean Concepts (Long Term Memory) - Remove Text Blobs
    concepts_path = os.path.join(MEMORY_DIR, "brain_concepts.json")
    if os.path.exists(concepts_path):
        try:
            with open(concepts_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            concepts = data.get("concepts", {})
            original_count = len(concepts)
            
            # Filter out keys that look like sentences (Zombie Phrases)
            # Threshold: Length > 10 AND contains specific patterns or just too long
            new_concepts = {}
            deleted_count = 0
            
            for k, v in concepts.items():
                is_zombie = False
                if len(k) > 15: is_zombie = True
                if "カナメ" in k and len(k) > 6: is_zombie = True
                if "良い子" in k: is_zombie = True
                
                if is_zombie:
                    print(f"💀 Detected Zombie Concept: {k}")
                    deleted_count += 1
                else:
                    new_concepts[k] = v
            
            data["concepts"] = new_concepts
            
            with open(concepts_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
                
            print(f"✅ Cleaned Concepts: {original_count} -> {len(new_concepts)} (Purged {deleted_count})")
            
        except Exception as e:
            print(f"❌ Failed to clean concepts: {e}")

    print("\n✨ RESET COMPLETE. PLEASE RESTART KANAME. ✨")

if __name__ == "__main__":
    hard_reset()
