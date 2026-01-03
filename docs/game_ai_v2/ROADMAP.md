# Roadmap: active Inference Evolution

## Phase 1: The Dark Room (Core Logic)
**Objective**: Implement the Active Inference loop and verify "Stillness" (Dark Room Problem).
- [ ] **Step 1.1**: Rewrite `ActiveInferenceAgent.step()` to calculate Free Energy.
    - Implement `divergence(z_predicted, z_preferred)`.
    - Implement `ambiguity(z_predicted)`.
- [ ] **Step 1.2**: Implement `GeologicalMemory.get_preferred_state()`.
    - Initially, return a "Flat Prior" (all states equal) or "Current State" (homing instinct).
- [ ] **Step 1.3**: Verification (Dark Room Test).
    - Ensure agent stays still when initialized with empty memory.

## Phase 2: The Curious Child (Intrinsic Motivation)
**Objective**: Boost curiosity to make Kaname explore and discover goals autonomously.
- [ ] **Step 2.1**: Implement `Curiosity Drive` in `ActiveInferenceAgent`.
    - `reward = prediction_error + novelty_bonus`.
- [ ] **Step 2.2**: Implement `GeologicalMemory.reinforce_novelty()`.
    - Automatically create Attractors for new/rare states.
- [ ] **Step 2.3**: Verification (Curiosity Test).
    - Initialize agent in a corner. Verify it eventually explores the whole map without user input.

## Phase 3: The Eye (Visual grounding)
**Objective**: Connect the logic to the actual game screen (Pixels).
- [ ] **Step 3.1**: Implement a simple VAE (Variational Autoencoder) or Downscaler.
    - Compress 84x84x3 image into a 64-dim Latent Vector ($z$).
- [ ] **Step 3.2**: Retrain `WorldModel` to predict $z_{t+1}$ instead of raw states.
- [ ] **Step 3.3**: Update `GeologicalMemory` to store $z$ vectors.

## Resource Limits & Circuit Breaker
- **Time Boxing**: Each Phase should not exceed 3 hours of implementation.
- **Rollback**: If Active Inference is too slow (< 10FPS), revert to Hybrid model but keep the "Geological Memory" bias.
