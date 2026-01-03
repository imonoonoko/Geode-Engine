# Synergy & Value Design: Biological Realism

# Synergy & Value Design: Biological Realism

## 1. Curiosity-Driven Exploration (The "Child" Concept)
Instead of relying on a teacher, Kaname learns through **Intrinsic Motivation**.
- **Observation**: Kaname explores the unknown.
- **Surprise**: High prediction error = "Interesting".
- **Geological Deposition**: "Interesting" events are carved into memory as weak attractors, leading to further exploration.
- **Success**: Accidental success (score) creates a strong attractor (Deep Valley).

**Value**: 
- **Zero Configuration**: User just watches. No need to teach or intervene.
- **Organic Growth**: Kaname starts clumsy, playing randomly, but gradually "figures it out" like a child.
- **Watching the Epiphany**: The moment Kaname discovers a strategy is purely her own achievement.

## 2. Visualization of "Thought" (`GameViewer` Expansion)
Since we now have a detached `GameViewer`, we can visualize the internal state:
- **Prediction Ghost**: Show a semi-transparent overlay of what Kaname *expects* to happen.
- **Surprise Meter**: Visualize "Free Energy" (Divergence + Ambiguity) as a stress bar.
    - Low bar = Confident/Bored.
    - High bar = Panicked/Surprised.

**Value**:
- **Explainability**: You can instantly see *why* Kaname failed (e.g., "She didn't predict the enemy moving left").
- **Entertainment**: Watching the AI "panic" or "relax" adds a layer of depth to the gameplay observation.

## 3. Sleep & Dream Learning (Efficiency)
Active Inference is computationally heavy during wakefulness (Interference).
- **Wake**: Fast, approximate inference.
- **Sleep**: Replay memories, refine `WorldModel` (reduce Ambiguity), consolidate `GeologicalMemory` (smooth out the terrain).

**Value**:
- **Performance**: Keeps real-time inference fast.
- **Biological Realism**: Kaname "needs to sleep" to get smarter. This reinforces the "ALife" feeling.
