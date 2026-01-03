# Verification Plan: Active Inference

## 1. Observability Strategy

### The "Thought" Overlay
We need to see what Kaname is thinking.
- **Visual Encoder Output**: Show the reconstructed image from VAE (to see what Kaname *perceives*).
- **Prediction Ghost**: Show the `z_predicted` decoded back to an image (to see what Kaname *expects*).
- **Free Energy Heatmap**: If possible, overlay a heatmap on the screen showing which areas cause "Surprise".

### Metrics
We abandon "Score" as the primary metric. Instead we track:
- **Free Energy ($F$)**: Should decrease over time as the agent learns the environment.
- **Surprise ($-\ln P(o)$)**: Spikes when something unexpected happens (e.g., enemy spawns).
- **Attractor Distance**: Euclidean distance between Current ($z$) and Preferred ($z^*$).

## 2. Verification Scenarios

### Test A: The Dark Room (Infant Phase)
**Condition**: Initialize with empty Geological Memory (Flat Prior).
**Expectation**: Agent should **NOT** move. Moving causes visual change -> Surprise -> Cost. Staying still minimizes Free Energy.
**Success Criteria**: Agent performs `NO_OP` > 90% of the time.

### Test B: The Helping Hand (Learning Phase)
**Condition**: User plays continuously for 1 minute, engaging in specific behavior (e.g., always jumping at X=50).
**Expectation**: 
1. `GeologicalMemory` records X=50, Jump=True as a high-probability event (Attractor).
2. Agent, when placed at X=45, should autonomously jump at X=50.
**Success Criteria**: Agent replicates the specific behavioral pattern (jumping at the specific spot) without explicit coding.

### Test C: The Prophecy (Mastery Phase)
**Condition**: Manually inject a "Goal State" into `GeologicalMemory` as the strongest Attractor.
**Expectation**: Agent should navigate towards the goal state, even if obstacles (which increase free energy) are in the way, because the *path to the goal* minimizes the long-term Divergence from the Prior.
**Success Criteria**: Agent clears the level solely driven by the desire to "be at the goal".

## 3. Quality Assurance
- **Safety Valve**: Ensure `max_free_energy` threshold triggers a "Panic Mode" (Emergency Stop) rather than erratic flailing.
- **Degradation Check**: Ensure memory doesn't get corrupted by "bad dreams" (false correlations).
