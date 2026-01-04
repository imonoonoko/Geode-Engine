# spatial.py
"""
Phase 9.2 & 31: Spatial Cortex & Minecraft Navigation logic.
Space is not just coordinates; it is a memory map.
"""

import random
from src.body.hormones import Hormone
import src.dna.config as config

class SpatialCortex:
    def __init__(self, brain):
        self.brain = brain
        self.memory = brain.memory
        self.hormones = brain.hormones
        
        # State: Vertical 'Depth' in the Geological Mind (0=Surface/North, 1000=Deep/South)
        self.current_geo_y = config.BRAIN_GEO_INITIAL
        
        self._last_env_resonance_concept = None

    def process_sense(self, sense_data):
        """
        Brain.receive_sense から委譲される MC_TRAVEL 処理
        """
        # DEBUG: 座標受信を記録
        # print(f"📍 [Spatial] Processing MC_TRAVEL sense...")
        
        # 1. Spatial Memory Mapping (The core logic)
        self.process_spatial_memory(sense_data)
        
        # 2. Rewards for Exploration
        self.hormones.update(Hormone.DOPAMINE, 0.5)
        self.hormones.update(Hormone.GLUCOSE, -0.2)
        self.hormones.update(Hormone.BOREDOM, -1.0)
        
        # 3. Epigenetic Reinforcement (Vision/Biome)
        if 'concept' in sense_data:
            target = sense_data.get('geo_target')
            gain = sense_data.get('photosynthesis_rate', 0)
            
            if target == 'Valley':
                self.memory.reinforce(target, -0.1) # 嫌な場所
            elif gain > 0:
                self.memory.reinforce(target, +0.05) 

            # Throttle: Only resonate if concept changed
            if target != self._last_env_resonance_concept:
                self.hormones.update(Hormone.STIMULATION, 20.0)
                self._last_env_resonance_concept = target
                
                # Affect Geo-Y
                if target == 'South':
                    self.current_geo_y = min(config.BRAIN_GEO_MAX, self.current_geo_y + 50)
                    self.brain.resonance.drift_impact("Hot")
                elif target == 'North':
                    self.current_geo_y = max(config.BRAIN_GEO_MIN, self.current_geo_y - 50)
                    self.brain.resonance.drift_impact("Cold")
                elif target == 'North_High':
                     self.current_geo_y = 200
                     self.brain.resonance.drift_impact("Intellect")
                elif target == 'Valley':
                     self.hormones.update(Hormone.SEROTONIN, -0.05)
                     self.brain.resonance.drift_impact("Fear")

    def process_spatial_memory(self, pos_data):
        """
        Minecraftの座標感覚を処理し、地質学的記憶にマッピングする。
        (Refactored from brain.py)
        """
        try:
            if not pos_data: return
            
            mx, my, mz = pos_data.get('x'), pos_data.get('y'), pos_data.get('z')
            if mx is None: return
            
            # 1. 座標の概念化 (Spatial Hashing)
            grid_x = int(mx) // 16
            grid_z = int(mz) // 16
            loc_key = f"LOC:{grid_x}:{grid_z}"
            
            # 2. 記憶へのアクセス・更新
            brain_coords = self.memory.get_coords(loc_key)
            
            # 3. 感情・ホルモン更新
            # Use memory lock if accessed directly, but get_coords handles it? 
            # Brain.py used explicit lock. Let's be safe.
            with self.memory.lock:
                val = self.memory.concepts.get(loc_key)
                if val:
                    count = val[3] if len(val) >= 4 else 1
                    
                    if count <= 1:
                        print(f"🗺️ New Location Discovered: {loc_key}")
                        self.hormones.update(Hormone.DOPAMINE, 10.0)
                        self.hormones.update(Hormone.STIMULATION, 20.0)
                        self.hormones.update(Hormone.GLUCOSE, -0.5)
                        
                    elif count < 10:
                        self.hormones.update(Hormone.SEROTONIN, 0.5)
                        
                    else:
                        self.hormones.update(Hormone.BOREDOM, 0.2)
            
            # DEBUG: Log occasionally
            if self.brain.time_step % 100 == 0:
                 print(f"📍 Mapped ({mx:.0f},{mz:.0f}) -> {loc_key} -> Brain{brain_coords}")

        except Exception as e:
            print(f"⚠️ [Spatial] Error: {e}")

    def decide_intent(self, state):
        """
        Determine Minecraft action based on spatial memory gradient.
        Returns: 'TURN_LEFT', 'TURN_RIGHT', 'MOVE_FORWARD', 'JUMP', or None
        """
        if not self.memory: return None
            
        # 1. Get Spatial Gradient
        pos = state.get("position", {})
        mx = pos.get("x")
        mz = pos.get("z")
        
        if mx is None or mz is None:
             return "MOVE_FORWARD"

        grid_x = int(mx) // 16
        grid_z = int(mz) // 16
        
        gradient = self.memory.get_spatial_gradient(grid_x, grid_z)
        if not gradient:
            return "MOVE_FORWARD" if random.random() < 0.1 else None 
            
        best_dir_name = max(gradient, key=gradient.get)
        
        # 2. Convert Direction to Target Yaw
        target_yaws = {
            "North": 3.14159, # PI
            "South": 0.0,
            "East": -1.5708, # -PI/2
            "West": 1.5708   # PI/2
        }
        target_yaw = target_yaws.get(best_dir_name, 0.0)
        
        # 3. Compare with Current Yaw
        current_yaw = 0.0
        if "position" in state and "yaw" in state["position"]:
            current_yaw = state["position"]["yaw"]
            
        diff = target_yaw - current_yaw
        
        # Normalize diff to -PI, PI
        while diff > 3.14159: diff -= 2*3.14159
        while diff < -3.14159: diff += 2*3.14159
        
        # Threshold for turning
        if abs(diff) > 0.5:
             # In brain.py logic was: return "TURN_LEFT" if diff > 0 else "TURN_RIGHT"
             # Wait, if target is Left (positive diff?), we turn left?
             # Minecraft Yaw increases clockwise? No, usually counter-clockwise or weird.
             # Keeping brain.py logic:
            return "TURN_LEFT" if diff > 0 else "TURN_RIGHT"
            
        # If facing correctly, move!
        # Check boredom for JUMP/TURN (Exploration)
        if self.hormones.get(Hormone.BOREDOM) > 60:
            rng = random.random()
            if rng < 0.3:
                return "JUMP"
            elif rng < 0.5:
                return "TURN_LEFT"
            elif rng < 0.7:
                return "TURN_RIGHT"
                
        return "MOVE_FORWARD"
