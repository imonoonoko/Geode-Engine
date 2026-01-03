# Dependency Map: Active Inference Architecture

## 1. Component Interaction Diagram

```mermaid
graph TD
    User[User / Teacher] -->|Plays & Demonstrates| GameEnv[Game Environment]
    
    subgraph "Kaname Brain (Active Inference)"
        Agent[Active Inference Agent]
        WM[World Model]
        GM[Geological Memory]
        
        Encoder[Visual Encoder (VAE)]
        
        Agent -->|Action| GameEnv
        GameEnv -->|Observation (Pixels)| Encoder
        
        Encoder -->|Latent State z| Agent
        
        Agent -->|z_current, action_candidate| WM
        WM -->|z_predicted| Agent
        
        Agent -->|z_predicted| GM
        GM -->|z_preferred (Prior)| Agent
        
        subgraph "Learning Loop"
            User -->|Imitation Signal| GM
            WM -->|Prediction Error| WM
        end
    end
```

## 2. Key Dependencies & Risks

| Source | Target | Dependency Type | Risk Level | Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| **Agent** | **Visual Encoder** | Data Transformation | High | Pixel space is too high-dimensional for direct inference. Need a robust VAE or simple Downscaler first. |
| **Agent** | **Geological Memory** | Prior Retrieval | Critical | `GeologicalMemory` currently stores Text Concepts. Need a mechanism to map `Visual State` <-> `Memory Node`. |
| **World Model** | **Game Physics** | Simulation | High | If WM prediction is poor, Agent will hallucinate and fail. Needs pre-training or rapid online learning. |
| **User** | **Geological Memory** | Teaching Signal | Medium | User implementation of "Teaching Mode" is required to form initial Attractors (Dark Room exit). |

## 3. Critical Path
1.  **Visual Encoder**: Must be able to compress game screen into a compact vector (z).
2.  **Memory Bridge**: associating `z` with `Graph Nodes` (e.g., "Safe State", "Goal State").
3.  **Inference Loop**: The calculation of Free Energy (Divergence + Ambiguity) must be fast enough for real-time play.
