# sensory_cortex.py
"""
Phase 15.2: Sensory Cortex Module
感覚処理の責務を担う。brain.py から分離された感覚関連ロジック。

責務:
- 視覚情報 (Minecraft Raycast) の処理
- 空間記憶 (座標) の処理
- 外部感覚データの受信と分類

設計原則:
- 依存性注入（DI）
- オブジェクト属性の変更のみ（再代入を避ける）
"""

import random
import threading
import time

from src.body.hormones import Hormone


# Phase 14: Block/Entity Translation Constants
MC_BLOCK_TO_JP = {
    # Blocks
    "stone": "石", "cobblestone": "丸石", "dirt": "土", "grass block": "草ブロック",
    "oak log": "オークの原木", "birch log": "白樺の原木", "spruce log": "トウヒの原木",
    "oak planks": "オークの板材", "diamond ore": "ダイヤ鉱石", "gold ore": "金鉱石",
    "iron ore": "鉄鉱石", "coal ore": "石炭鉱石", "lapis ore": "ラピス鉱石",
    "redstone ore": "レッドストーン鉱石", "emerald ore": "エメラルド鉱石",
    "water": "水", "lava": "溶岩", "sand": "砂", "gravel": "砂利",
    "obsidian": "黒曜石", "bedrock": "岩盤", "crafting table": "作業台",
    "furnace": "かまど", "chest": "チェスト", "torch": "たいまつ",
    # Entities
    "zombie": "ゾンビ", "skeleton": "スケルトン", "spider": "クモ",
    "creeper": "クリーパー", "enderman": "エンダーマン", "witch": "ウィッチ",
    "pig": "ブタ", "cow": "ウシ", "sheep": "ヒツジ", "chicken": "ニワトリ",
    "wolf": "オオカミ", "cat": "ネコ", "horse": "ウマ", "villager": "村人",
}

# Phase 14: Innate Emotion Responses
MC_INNATE_EMOTIONS = {
    # Danger
    "lava": {"cortisol": 15, "adrenaline": 10, "log": "🔥 DANGER: 溶岩!"},
    "zombie": {"cortisol": 20, "adrenaline": 25, "log": "👹 THREAT: ゾンビ!"},
    "skeleton": {"cortisol": 25, "adrenaline": 20, "log": "💀 THREAT: スケルトン!"},
    "creeper": {"cortisol": 40, "adrenaline": 30, "log": "💥 EXTREME DANGER: クリーパー!"},
    "spider": {"cortisol": 15, "adrenaline": 15, "log": "🕷️ THREAT: クモ!"},
    "enderman": {"cortisol": 30, "adrenaline": 20, "log": "👁️ THREAT: エンダーマン!"},
    # Joy
    "diamond ore": {"dopamine": 30, "log": "💎 TREASURE: ダイヤ発見!"},
    "gold ore": {"dopamine": 20, "log": "🥇 TREASURE: 金発見!"},
    "emerald ore": {"dopamine": 25, "log": "💚 TREASURE: エメラルド発見!"},
    # Comfort
    "pig": {"oxytocin": 10, "log": "🐷 FRIENDLY: ブタ発見!"},
    "cow": {"oxytocin": 10, "log": "🐄 FRIENDLY: ウシ発見!"},
    "sheep": {"oxytocin": 10, "log": "🐑 FRIENDLY: ヒツジ発見!"},
    "cat": {"oxytocin": 15, "log": "🐱 FRIENDLY: ネコ発見!"},
    "wolf": {"oxytocin": 8, "log": "🐺 FRIENDLY: オオカミ発見!"},
    # Safety
    "torch": {"serotonin": 5, "log": None},
    "crafting table": {"serotonin": 3, "log": None},
    "water": {"serotonin": 2, "log": None},
}


class SensoryCortex:
    """
    感覚皮質: 外部入力を処理し、記憶と感情に変換する。
    """
    
    def __init__(self, hormones, memory, activate_concept_fn=None):
        """
        Args:
            hormones: HormoneManager インスタンス
            memory: GeologicalMemory インスタンス
            activate_concept_fn: 概念活性化関数 (Brain.activate_concept)
        """
        self.hormones = hormones
        self.memory = memory
        self.activate_concept = activate_concept_fn or (lambda name, boost=1.0: None)
        
        self.lock = threading.Lock()
        self.time_step = 0
        
        print("👁️ SensoryCortex Initialized (Phase 15.2)")
    
    def process_visual_input(self, cursor_data: dict):
        """
        Minecraft Raycast 視覚データを処理。
        
        Args:
            cursor_data: {"name": "minecraft:stone", "position": {...}}
        """
        try:
            if not cursor_data:
                return
            
            block_name = cursor_data.get("name")
            if not block_name:
                return
            
            # Normalize block name
            simple_name = block_name.replace('minecraft:', '').replace('_', ' ')
            jp_name = MC_BLOCK_TO_JP.get(simple_name, simple_name)
            
            # Apply innate emotion response
            emotion_key = simple_name.lower()
            if emotion_key in MC_INNATE_EMOTIONS:
                self._apply_emotion_response(MC_INNATE_EMOTIONS[emotion_key])
            
            # Memory reinforcement
            position = cursor_data.get("position")
            if position and jp_name:
                self.memory.reinforce(jp_name, 0.1)
                self.activate_concept(jp_name, boost=0.5)
            
            # Debug log (2% chance)
            if random.random() < 0.02:
                print(f"👁️ Saw: {jp_name}")
                
        except Exception as e:
            print(f"⚠️ [SensoryCortex] Visual Error: {e}")
    
    def process_spatial_input(self, pos_data: dict):
        """
        Minecraft 座標データを処理。
        
        Args:
            pos_data: {"x": float, "y": float, "z": float}
        """
        try:
            self.time_step += 1
            
            if not pos_data:
                return
            
            mx = pos_data.get('x')
            mz = pos_data.get('z')
            if mx is None or mz is None:
                return
            
            # Spatial hashing (16-block chunks)
            grid_x = int(mx) // 16
            grid_z = int(mz) // 16
            loc_key = f"LOC:{grid_x}:{grid_z}"
            
            # Memory access
            brain_coords = self.memory.get_coords(loc_key)
            
            # Emotion update based on familiarity
            with self.memory.lock:
                val = self.memory.concepts.get(loc_key)
                if val:
                    count = val[3] if len(val) >= 4 else 1
                    
                    if count <= 1:
                        # New discovery!
                        print(f"🗺️ New Location: {loc_key}")
                        self.hormones.update(Hormone.DOPAMINE, 10.0)
                        self.hormones.update(Hormone.STIMULATION, 20.0)
                    elif count < 10:
                        # Familiar place
                        self.hormones.update(Hormone.SEROTONIN, 0.5)
                    else:
                        # Boring place
                        self.hormones.update(Hormone.BOREDOM, 0.2)
            
            # Debug log (every 100 steps)
            if self.time_step % 100 == 0:
                print(f"📍 Mapped ({mx:.0f},{mz:.0f}) -> {loc_key}")
                
        except Exception as e:
            print(f"⚠️ [SensoryCortex] Spatial Error: {e}")
    
    def _apply_emotion_response(self, response: dict):
        """Apply innate emotion response to hormones."""
        if response.get("cortisol"):
            self.hormones.update(Hormone.CORTISOL, response["cortisol"])
        if response.get("adrenaline"):
            self.hormones.update(Hormone.ADRENALINE, response["adrenaline"])
        if response.get("dopamine"):
            self.hormones.update(Hormone.DOPAMINE, response["dopamine"])
        if response.get("oxytocin"):
            self.hormones.update(Hormone.OXYTOCIN, response["oxytocin"])
        if response.get("serotonin"):
            self.hormones.update(Hormone.SEROTONIN, response["serotonin"])
        if response.get("log"):
            print(f"👁️ [Vision] {response['log']}")
