# Analysis & Decomposition Report: Kaname Active Inference Evolution

## 1. Project Overview
**Objective**: Transform Kaname's game AI from a hybrid RL/Active Agent into a **Pure Active Inference Agent** based on the Free Energy Principle.
**Core Philosophy**: Shift from "Reward Maximization" to "Surprise Minimization".
**Key Documents**: 
- `docs/知能について.md` (Intelligence & Emotion Theory)
- `docs/AIゲーム学習についてのセッション.md` (Active Inference Architecture for Games)

## 2. Structural Analysis (As-Is)

### Current Architecture (`IntegratedRLAgent`)
- **Action Selection**: Hybrid. Uses `WorldModel` if available, falls back to random (curiosity). 
- **Learning**: `GeologicalMemory` stores "Emotion" (Reward) into terrain. `WorldModel` learns transitions.
- **Limitation**:
    - Still relies on "Reward" concept (converting reward to emotion).
    - No "Preferred State" (Prior) concept implemented.
    - No "Dark Room" behavior (default is random walk, not stillness).
    - `GeologicalMemory` is write-only (used for terrain viz, not for action bias).

### Codebase Analysis
- `src/games/integrated_rl_agent.py`: The shell class. Needs complete rewrite of `select_action`.
- `src/games/simple_games.py`: The environment. Provides observation (H, W, 3).
- `src/body/maya_synapse.py` / `src/cortex/memory.py`: The definition of `GeologicalMemory`. Currently stores text/concept based terrain. Needs to store "State Vectors" or "Visual Latents" to serve as Attractors.

## 3. Intent Verification (To-Be)

The target architecture represents a **Biological Paradigm Shift**:

1.  **Prediction (World Model)**: "If I do A, state becomes S'."
2.  **Prior (Geological Memory)**: "I should be in state S* (Safe/Good)."
3.  **Inference**: "Choose A that minimizes distance(S', S*) + uncertainty(S')."

**Crucial Behavioral Shifts:**
- **Infant Phase**: Do nothing (minimize surprise).
- **Learning Phase**: Imitate User (User sets the Prior).
- **Mastery Phase**: Chase the "Goal" state (which is now the strongest Prior).

## 4. Technical Debt & Risks
- **Memory Modality Mismatch**: `GeologicalMemory` is optimized for semantic concepts (Words), but game states are Visual (Pixels). We need a `VAE` or `Autoencoder` to map Pixels -> Latent Space -> Memory Coordinates.
- **Computational Cost**: Active Inference requires simulating multiple futures per step. Python performance might be a bottleneck.
- **Bootstrapping**: Without user intervention (Teaching), the agent will stay in the Dark Room forever. We need a robust "Ghost Learning" (Imitation) system.
