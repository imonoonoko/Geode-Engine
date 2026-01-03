import numpy as np
import os

BACKUP_PATH = "memory_data/rnn_weights_128.npy.bak"

def inspect():
    if not os.path.exists(BACKUP_PATH):
        print(f"❌ Backup file not found at: {BACKUP_PATH}")
        return

    print(f"📦 Loading Backup: {BACKUP_PATH}")
    try:
        data = np.load(BACKUP_PATH, allow_pickle=True).item()
        
        print("\n--- 🧠 Old Brain Specs (128 Units) ---")
        for key, val in data.items():
            print(f"  • {key}: {val.shape}")

        # Calculate Metrics
        wxh = data.get("Wxh")
        whh = data.get("Whh")
        
        if wxh is not None:
            energy = np.mean(np.abs(wxh)) + np.mean(np.abs(whh))
            print(f"\n🔋 Energy (Synaptic Strength): {energy:.4f}")
            
        if whh is not None:
            roughness = np.std(whh)
            print(f"🌊 Roughness await(Complexity): {roughness:.4f}")
            
        print("\n✅ Verification: This is a valid frozen brain file.")
        
    except Exception as e:
        print(f"⚠️ Error reading file: {e}")

if __name__ == "__main__":
    inspect()
