# 🪨 Geode-Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Geological Memory AI** — An experimental artificial life simulation inspired by neuroscience and geology.

> [!WARNING]
> **Work in Progress**: This project is an early-stage experimental prototype and is still far from its ultimate goal of a fully autonomous digital lifeform. Many features are incomplete, and breaking changes are expected.

[日本語 README はこちら](README_ja.md)

---

## 🌟 Overview

Geode-Engine is a unique AI architecture that models cognition using **geological metaphors**:

| Concept | Biological Analog | Implementation |
|:---|:---|:---|
| **Geological Memory** | Long-term memory | Concepts accumulate like sedimentary layers |
| **Hormonal System** | Neuromodulators | Dopamine, Cortisol, Serotonin affect decisions |
| **Predictive Coding** | Active Inference | Free Energy Principle for perception |
| **Dream Consolidation** | Sleep | Memory compression during idle time |

---

## 🧠 Architecture

```
Geode-Engine/
├── src/
│   ├── brain_stem/      # Core brain logic
│   │   ├── brain.py     # Main GeodeBrain class
│   │   ├── motor_cortex.py
│   │   ├── sensory_cortex.py
│   │   └── dream_engine.py
│   ├── cortex/          # Memory and cognition
│   │   ├── memory.py         # GeologicalMemory (HDC)
│   │   ├── sedimentary.py    # Long-term memory (SQLite)
│   │   ├── knowledge_graph.py # Tiered memory system
│   │   ├── hdc_bridge.py     # **Phase 19: HDC-LLM Bridge**
│   │   ├── agni_translator.py # LLM integration
│   │   └── logic.py          # Reasoning engine
│   ├── body/            # Hormones and metabolism
│   │   ├── hormones.py       # Neuromodulator system
│   │   └── metabolism.py     # Circadian rhythm
│   ├── senses/          # Perception
│   │   ├── visual_bridge.py  # Visual memory
│   │   └── mentor.py         # Agni Accelerator (Gemini)
│   └── games/           # Minecraft integration
│       └── minecraft/
├── docs/                # Documentation
├── tests/               # Unit tests
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

**Required:**
- Python 3.10+ (3.11 recommended)
- 8GB+ RAM (16GB recommended for optimal performance)
- Windows 10/11, Linux, or macOS

**Optional (for enhanced features):**
- **Ollama** (for local LLM inference)
  - Download from: https://ollama.ai
  - Recommended models: `gemma2:2b` or `phi3:mini`
- **Google Gemini API Key** (for Agni Accelerator)
  - Free tier available at: https://ai.google.dev
- **Node.js 18+** (for Minecraft integration)
  - Download from: https://nodejs.org

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/imonoonoko/Geode-Engine.git
cd Geode-Engine

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY (optional)

# 5. Run
python src/brain_stem/main.py
# Or use the startup script (Windows):
# start_geode.bat
```

---

## 🔑 Key Features

### 1. Hyperdimensional Computing (HDC)
- SimHash-based concept encoding (768→1024 bit)
- Efficient similarity search with KD-Tree

### 2. HDC-LLM Bridge (Phase 19) 🆕
- **Memory Recall**: Retrieves relevant memories from KnowledgeGraph and SedimentaryCortex
- **G-Calculation**: Expected Free Energy minimization for action selection
- **Dynamic Prompt Injection**: LLM prompts enriched with recalled memories
- Enables context-aware conversations grounded in internal knowledge

### 3. Agni Accelerator
- Gemini API integration for knowledge injection
- "Teacher → Graduation" paradigm (temporary dependency)

### 4. Modular Brain Architecture
- **MotorCortex**: Movement control
- **SensoryCortex**: Visual perception
- **DreamEngine**: Autonomous thought
- **MetabolismManager**: Energy and circadian rhythm

### 4. Minecraft Integration
- Mineflayer-based embodiment
- Spatial memory mapping
- Emotion-driven behavior

---

## 📊 Configuration

Key settings in `src/dna/config.py`:

| Variable | Default | Description |
|:---|:---|:---|
| `EDUCATION_MODE` | `False` | Enable Agni background tutoring |
| `THRESHOLD_LOW` | `30.0` | Low hormone threshold |
| `THRESHOLD_HIGH` | `70.0` | High hormone threshold |
| `MEMORY_SAVE_INTERVAL` | `300` | Auto-save interval (seconds) |

---

## ⚙️ Feature Toggles

You can enable/disable various AI features in `src/dna/config.py`:

| Feature | Config Variable | Default | Description |
|:---|:---|:---:|:---|
| **Digital Tutoring** | `EDUCATION_MODE` | `False` | Agni (Gemini) background knowledge injection |
| **Sleep Learning** | `AGNI_HYPNOPEDIA` | `False` | Continue learning while the AI is "sleeping" |
| **Auto-Harvesting** | `MENTOR_AUTO_TEACH` | `False` | Automatically fetch and learn from web sources |
| **Voice Ops** | `USE_VOICE_GENERATION` | `True` | Use MeloTTS for voice output |
| **Minecraft Link** | `self.minecraft` | `None` | (Internal) Link to Mineflayer agent |

---

---

## 🧪 Testing

```bash
# Run all tests
python run_tests.py

# Run specific test
python -m pytest tests/test_motor_cortex.py -v
```

---

## 📚 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Roadmap](docs/ROADMAP.md)
- [Contributing Guide](CONTRIBUTING.md)

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by Free Energy Principle (Karl Friston)
- Hyperdimensional Computing concepts from Kanerva's work
- Mineflayer for Minecraft integration

---

**Made with 🧠 by the Geode-Engine Team**
