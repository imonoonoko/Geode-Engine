# 🗺️ 機能アトラス (FUNCTION ATLAS)
> **生成日時**: 2026-01-02 02:10:35
> **ソース**: `src/`

---

## 📁 `src\body`
### 📄 `biorhythm.py`
- **class BioRhythm**
  - `def __init__(self)`
  - `def get_circadian_factor(self, current_hour)`
  - `def decay_hormone(self, current_val, half_life, delta_time=1.0)`
  - `def homeostasis_update(self, current_val, set_point, plasticity=0.05)`
  - `def generate_1f_noise(self)`
  - `def calculate_heart_rate(self, base_bpm, stress_load, excitement)`

### 📄 `body_interface.py`
- **class BodyProtocol**
  - 📝 *身体実装が満たすべきインターフェース (Protocol)*
  - `def apply_force(self, fx, fy)`
  - `def get_position(self)`
  - `def express(self, emotion)`
  - `def pulse(self, bpm)`
- **class BodyHAL**
  - 📝 *身体ハードウェア抽象化レイヤー*
  - `def __init__(self, body_impl=None)`
  - `def connect(self, body_impl)`
  - `def disconnect(self)`
  - `def is_connected(self)`
  - `def apply_force(self, fx, fy)`
  - `def get_position(self)`
  - `def express(self, emotion)`
  - `def pulse(self, bpm)`

### 📄 `feeder.py`
- **class DataFeeder**
  - `def __init__(self, food_folder='food')`
  - `def check_food(self)`
  - `def eat(self)`
  - `def eat_file(self, file_path_or_content, is_direct_text=False)`
  - `def has_food(self)`
  - `def get_stats(self)`

### 📄 `immune.py`
- **class KanameImmuneSystem**
  - `def __init__(self, brain_ref)`
  - `def protect_loop(self, target_loop_func, args=..., name='Unknown')`

### 📄 `kaname_body.py`
- **class KanameBody**
  - `def __init__(self, brain_ref)`
  - `def run_threads(self, immune_system=None)`
  - `def get_center_pos(self)`
  - `def update_state(self, heart_rate)`
  - `def say(self, text, speed=1.0)`
  - `def animation_loop(self)`
  - `def update_visual_senses(self, grid_motion)`
  - `def drift_loop(self)`
  - `def apply_force(self, fx, fy)`

### 📄 `maya_resonance.py`
- **class GeologicalResonance**
  - `def __init__(self, memory_ref, synapse_ref)`
  - `def stop(self)`
  - `def impact(self, word, force=1.0)`
  - `def drift_impact(self, word)`

### 📄 `maya_synapse.py`
- **class SynapticStomach**
  - `def __init__(self, memory_dir)`
  - `def load_graph(self)`
  - `def save_graph(self)`
  - `def eat(self, text)`
  - `def digest(self)`
  - `def forget_concepts(self, words)`

### 📄 `throat.py`
- **class KanameThroat**
  - `def __init__(self, geo_memory=None)`
  - `def speak(self, text, speed=1.0, geo_y=512, heart_rate=60)`
  - `def stop(self)`

## 📁 `src\brain_stem`
### 📄 `attention_manager.py`
- **class AttentionManager**
  - 📝 *興味・注意の統合コントローラー*
  - `def __init__(self, brain)`
  - `def update(self, peripheral_data, fovea_tags)`
  - `def get_status(self)`

### 📄 `brain.py`
- **class KanameBrain**
  - `def __init__(self)`
  - `def activate_concept(self, name, boost=1.0)`
  - `def prune_neurons(self)`
  - `def receive_sense(self, sense_data)`
  - `def think(self)`
  - `def input_stimulus(self, text)`
  - `def save_memory(self, async_mode=True)`
  - `def process_metabolism(self, cpu_percent, memory_percent, current_hour)`
  - `def process_autonomous_thought(self, heart_rate)`

### 📄 `main.py`
- **class MaiaSystem**
  - `def __init__(self)`
  - `def metabolism_loop(self)`
  - `def cognitive_loop(self)`
  - `def autonomous_loop(self)`
  - `def run(self)`

## 📁 `src\cells`
### 📄 `neuron.py`
- **class Neuron**
  - `def __init__(self, name, is_sensor=False)`
  - `def connect(self, other, weight=0.5)`
  - `def decay(self, hormone_bias=1.0)`
  - `def fire(self, current_time)`

## 📁 `src\cortex`
### 📄 `concept_learner.py`
- **class ConceptLearner**
  - 📝 *ハイブリッド学習: 感情記銘 + ユーザー教示*
  - `def __init__(self, brain, data_dir='memory')`
  - `def translate(self, yolo_tag)`
  - `def encounter_unknown(self, yolo_tag, valence=0.0)`
  - `def teach(self, name)`
  - `def get_recent_unknown(self)`
  - `def get_display_name(self, yolo_tag)`

### 📄 `hippocampus.py`
- **class Hippocampus**
  - `def __init__(self, save_dir='memory_data')`
  - `def memorize(self, text, importance=0.5, emotion='NEUTRAL')`
  - `def recall(self, query_text, limit=3, min_score=0.3)`
  - `def get_similarity(self, text_a, text_b)`

### 📄 `inference.py`
- **class PredictionEngine**
  - `def __init__(self)`
  - `def load_model(self)`
  - `def save_model(self)`
  - `def observe(self, input_text, current_hour)`
  - `def simulate(self, input_text, current_hour)`
  - `def crystallize(self)`
  - `def get_soul_bias(self)`
  - `def get_action_strategy(self)`

### 📄 `memory.py`
- **class GeologicalMemory**
  - `def __init__(self, size=1024)`
  - `def load(self)`
  - `def save(self)`
  - `def fossilize(self, age_limit=3600)`
  - `def get_coords(self, word)`
  - `def reinforce(self, word, delta)`
  - `def get_valence(self, word)`
  - `def modify_terrain(self, word, emotion_value)`
  - `def forget_forgotten_concepts(self)`
  - `def get_context(self, word)`
  - `def get_random_concept(self, refresh=False)`
  - `def get_concepts_in_range(self, y_min, y_max, limit=10)`
  - `def apply_gravity(self, subject, attractor, similarity)`

### 📄 `sedimentary.py`
- **class SedimentaryCortex**
  - `def __init__(self, memory_system, max_sediments=...)`
  - `def load(self)`
  - `def save(self, async_mode=True)`
  - `def learn(self, text, trigger_word, surprise=0.0)`
  - `def deposit(self, memory_entry)`
  - `def speak(self, trigger_word, strategy='RESONATE')`
  - `def digest_memories(self)`
  - `def excavate(self, x, y, radius=50)`
  - `def get_emotional_gradient(self, x, y, radius=100)`

### 📄 `translator.py`
- **class MaiaTranslator**
  - `def __init__(self, memory_ref=None, cortex_ref=None)`
  - `def train_from_memory(self)`
  - `def translate(self, ir_data)`

## 📁 `src\dna`
### 📄 `config.py`
*公開定義が見つかりません。*

## 📁 `src\senses`
### 📄 `kaname_senses.py`
- **class Retina**
  - `def __init__(self)`
  - `def watch(self, sct, char_x, char_y, do_inference=True)`
- **class KanameSenses**
  - `def __init__(self)`
  - `def update_focus(self, x, y)`
  - `def set_expectation(self, tag)`
  - `def request_local_vision(self, region)`
  - `def get_global_vision(self)`
  - `def get_local_vision(self)`
  - `def get_atmosphere(self)`
  - `def get_grid_motion(self)`
  - `def stop(self)`

### 📄 `visual_bridge.py`
- **class VisualMemoryBridge**
  - `def __init__(self, memory, cortex)`
  - `def connect_senses(self, senses)`
  - `def set_expectation(self, concept_word)`
  - `def translate_tag(self, tag)`
  - `def flush(self)`
  - `def update(self, detected_objects_en, current_chemicals)`

## 📁 `src\tools`
### 📄 `clean_memory_tags.py`
- **def clean_memory()**

### 📄 `cortex_generator.py`
- **class CharLSTM**
  - `def __init__(self, hidden_size=128, learning_rate=0.1)`
  - `def initialize_weights(self)`
  - `def resize_weights(self, new_vocab)`
  - `def load_data(self, data)`
  - `def train(self, data, epochs=1000, seq_length=25)`
  - `def save(self)`
- **class SimpleRNN**
  - 📝 *Vanilla RNN for simplicity and 'Glitchy' aesthetic*
  - `def initialize_weights(self)`
  - `def step(self, x, h)`
  - `def softmax(self, x)`
  - `def train(self, data, epochs=1000, seq_length=25)`
  - `def generate(self, seed_text, length=50, temperature=1.0)`

### 📄 `generate_atlas.py`
- **def get_function_signature(node)**
  - 📝 *Reconstruct function signature/arguments from AST node.*
- **def parse_file(filepath)**
  - 📝 *Parse a python file and return structure.*
- **def generate_atlas()**
  - 📝 *Main Generation Loop*

### 📄 `inspect_backup.py`
- **def inspect()**

### 📄 `telemetry_server.py`
- **class TelemetryServer**
  - `def __init__(self, brain_ref, host='localhost', ws_port=8765, http_port=8080)`
  - `def get_telemetry(self)`
  - `def run_in_thread(self)`
  - `def stop(self)`

### 📄 `test_gravity.py`
- **def test_gravity()**
