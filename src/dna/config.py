import os
from dotenv import load_dotenv

# ==========================================
# ⚙️ System Configuration
# ==========================================
DEBUG_MODE = True # Toggle detailed logs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEMORY_DIR = os.path.join(BASE_DIR, "memory_data")
TEMP_DIR = os.path.join(os.environ.get("TEMP", "."), "kaname_temp")

# Load .env file (Explicit Path)
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Ensure directories exist
os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# ==========================================
# 🧠 Brain Settings
# ==========================================
MSG_BRAIN_SIZE = 1024
SEDIMENT_MAX = 10000 # Reduced from 1M to prevent JSON Save Freeze (10k items ~10MB)
NEURON_COUNT = 5 # Ignored if using named sensors, but kept for future
HORMONE_DECAY = 0.95 # Balanced for Flow (Growth) vs Depression (Decay)

# Brain Structure
NEURON_SENSORS = ["視覚:赤", "視覚:緑", "視覚:青", "視覚:明", "視覚:動"]

# Logic Constants
BRAIN_GEO_INITIAL = 512
BRAIN_GEO_MAX = 1024
BRAIN_GEO_MIN = 0

# ==========================================
# 🧬 Hormone System (Phase 6: Biological Resonance)
# ==========================================
# スケール: 0.0 - 100.0 (仕様書準拠)
HORMONE_MAX = 100.0

# ドーパミン (快楽・意欲)
DOPAMINE_BASE = 10.0       # 渇望しやすい状態
DOPAMINE_HALFLIFE = 300    # 半減期: 5分 (秒)

# セロトニン (安定・抑制)
SEROTONIN_BASE = 50.0      # 安定状態
SEROTONIN_HALFLIFE = 21600 # 半減期: 6時間 (秒)

# アドレナリン (興奮・恐怖)
ADRENALINE_BASE = 0.0      # 通常は0
ADRENALINE_HALFLIFE = 60   # 半減期: 1分 (秒)

# オキシトシン (愛着・信頼)
OXYTOCIN_BASE = 20.0       # やや孤独
OXYTOCIN_HALFLIFE = 86400  # 半減期: 24時間 (秒)

# コルチゾール (ストレス・痛み)
CORTISOL_BASE = 0.0        # ストレスフリー
CORTISOL_HALFLIFE = 1800   # 半減期: 30分 (秒)

# 忘却曲線パラメータ
MEMORY_TAU_BASE = 3600     # 基本半減期: 1時間 (秒)
MEMORY_VALENCE_FACTOR = 5  # 感情が強いほど忘れにくい係数

# --- Phase 8 Step 2: ホルモン閾値 (Thresholds) ---
# 行動判断の閾値 (0-100スケール)
# Phase 14: Igniting Curiosity - Lowered thresholds for active behavior
THRESHOLD_HIGH = 50.0       # 興奮状態の閾値 (> 50%)
THRESHOLD_MEDIUM = 30.0     # 中間状態
THRESHOLD_LOW = 15.0        # 低下状態 (飢餓・鬱)

THRESHOLD_MOVEMENT_BOREDOM = 40.0 # Boredom > 40 triggers exploration

# Phase 15: Infantile Curiosity Thresholds
# Surprise (Predictive Error): 0.0 ~ 1.4 (Max sqrt(1^2 + 1^2))
# < 0.2: Safety (Serotonin)
# 0.2 ~ 0.8: Curiosity (Dopamine)
# > 0.8: Fear (Adrenaline)
SURPRISE_THRESHOLD_CURIOSITY = 0.2
SURPRISE_THRESHOLD_FEAR = 0.8

# 色変化の閾値 (正規化後0-1で比較するUI用)
COLOR_THRESHOLD_HIGH = 0.6  # > 60% for color change
COLOR_THRESHOLD_MEDIUM = 0.5
COLOR_THRESHOLD_PAIN = 0.5  # Cortisol > 50% shows pain color
COLOR_THRESHOLD_DYING = 0.8 # Cortisol > 80% dying color

# ホルモン変動量 (Deltas)
DELTA_POKE = 20.0           # つつかれた時のアドレナリン上昇
DELTA_PET = 10.0            # 撫でられた時のドーパミン上昇
DELTA_FEED_GLUCOSE = 30.0   # 食事時のグルコース上昇
DELTA_FEED_DOPAMINE = 10.0  # 食事時のドーパミン上昇
DELTA_PAIN_CORTISOL = 50.0  # エラー時のコルチゾール上昇
DELTA_PAIN_SEROTONIN = -30.0 # エラー時のセロトニン減少

# ==========================================
# 👁️ Retina Settings
# ==========================================
RETINA_FPS = 5         
RETINA_INTERVAL = 0.2  
RETINA_GRID_SIZE = 30  
RETINA_MOTION_GRID_ROWS = 3
RETINA_MOTION_GRID_COLS = 3

# ==========================================
# 👻 Body & UI Settings
# ==========================================
# 👻 Body & UI Settings
# ==========================================
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 300
GHOST_SIZE = 80
DEFAULT_X = 1000
DEFAULT_Y = 500

# Shape
BODY_ORB_RADIUS = 75 # Main body size (Diameter 150)
BODY_AURA_WIDTH = 2

# Optimization (Phase 11)
UI_QUEUE_BATCH_SIZE = 10 # Max UI updates per frame

# Colors (RGB)
COLOR_NEUTRAL = (100, 200, 150)
COLOR_JOY = (255, 215, 80)
COLOR_ANGER = (255, 140, 60)
COLOR_SADNESS = (80, 80, 100)
COLOR_RELAX = (80, 220, 180)
COLOR_LOVE = (255, 150, 200)
COLOR_SLEEP = (30, 30, 50)
COLOR_INTELLECT = (50, 150, 255) 

# ==========================================
# 🔊 Voice Settings
# ==========================================
USE_VOICE_GENERATION = True # Set to False for Low Memory Mode (Disables MeloTTS)
TTS_SPEED_DEFAULT = 1.0

# Ollama Settings (Phase 5)
OLLAMA_ENABLED = True
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"
VOICE_SPEED_NORMAL = 1.0
VOICE_SPEED_JOY = 1.3
VOICE_SPEED_SLEEP = 0.7

THROAT_GEO_BIAS_THRESHOLD = 0.3 # For voice effects

# ==========================================
# 🧱 Minecraft Interaction Settings (Phase 11)
# ==========================================
MC_BOREDOM_THRESHOLD = 15.0       # 退屈して何かしたくなる閾値
MC_CREATIVE_THRESHOLD = 40.0      # 創造的衝動 (Place) を生むドーパミン閾値
MC_DESTRUCTIVE_THRESHOLD = 20.0   # 破壊衝動 (Dig) を生むドーパミン閾値 (これ以下)

# Combat (FEP)
MC_COMBAT_CORTISOL_THRESHOLD = 30.0 # 脅威を感じて行動バイアスがかかる閾値
MC_COMBAT_URGENCY_BASE = 20.0       # 焦り始めるCortisol値
MC_COMBAT_URGENCY_SCALE = 80.0      # Urgency正規化用スケール (20~100)
MC_ATTACK_FACTOR = 2.0              # 攻撃バイアスの係数
MC_FLEE_FACTOR = 2.0                # 逃走バイアスの係数
MC_PANIC_DISTANCE = 3.0             # パニックになる敵との距離

# ==========================================
# 🔥 Agni (Mentor) Settings (Phase 15.5)
# ==========================================
EDUCATION_MODE = True
AGNI_HYPNOPEDIA = True # Sleep Learning Mode (Hypnopedia)
AGNI_SURPRISE_THRESHOLD = 0.3 # Gatekeeper: Ignore inputs with surprise < 0.3
# 環境変数から読み込む。設定方法: $env:GEMINI_API_KEY = "your-key-here"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# Gemma 3 27B IT (Instruction Tuned) - Google AI Studio経由
GEMINI_MODEL = "gemma-3-27b-it"
GEMINI_EMBEDDING_MODEL = "models/text-embedding-004" # Phase 2 Metamorphism
GEMINI_RATE_LIMIT = 30 # RPM (Requests Per Minute) - Gemma 3 無料枠最大
GRADUATION_VOCAB_SIZE = 5000
MEMORY_COMPRESSION_RATIO = 0.1

# Persona Rotation for Synthetic Socialization
AGNI_PERSONA_ROTATION = ["Teacher", "Friend", "Rival", "Child"]
# 最適化計算: RPD (Requests Per Day) = 14,400
# 1日24時間稼働の場合: 14400 / (24 * 60 * 60) = 0.16 req/sec
# interval = 1 / 0.16 = 6.0秒
MENTOR_AUTO_LOOP_INTERVAL = 6 # Seconds (RPD制限に基づく最適値)
MENTOR_AUTO_TEACH = True # 自動教育ON

# Source Tags
SOURCE_USER = "User"
SOURCE_AGNI = "Agni"


# ==========================================
# 💾 User Config Overlay (Persistence)
# ==========================================
import json
USER_CONFIG_PATH = os.path.join(BASE_DIR, "user_config.json")

def load_user_config():
    """ Load override values from JSON """
    if os.path.exists(USER_CONFIG_PATH):
        try:
            with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
                updates = json.load(f)
                
            # Apply updates to globals
            g = globals()
            for k, v in updates.items():
                if k in g:
                    g[k] = v
                    
            print(f"💾 Loaded User Config: {len(updates)} items.")
        except Exception as e:
            print(f"⚠️ Failed to load user_config.json: {e}")

load_user_config()

