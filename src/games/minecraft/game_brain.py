import random
import math
import src.dna.config as config

class MinecraftBrain:
    """
    🎮 Game Brain (Minecraft Cortex)
    
    役割:
    - GeodeBrain (本体) から「ホルモン」「記憶」「意図」を受け取る。
    - Minecraft固有の環境情報 (State) を分析する。
    - 具体的な行動 (DIG, PLACE, ATTACK, MOVE) を決定する。
    
    Design:
    - 本体 (GeodeBrain) は汎用的な生命維持装置。
    - このGameBrainは「Minecraftの身体を動かすための小脳/運動野」。
    - 記憶は本体の `brain.memory` を共有・更新する。
    """
    
    def __init__(self, brain_core):
        self.brain = brain_core # Reference to GeodeBrain
        print("🎮 Minecraft Brain Connected to Core.")

    def decide_intent(self, state):
        """
        Minecraft環境における次の行動意図を決定する。
        """
        # 0. 基本欲求の参照 (本体から)
        # BrainのHormoneManagerに直接アクセスせず、Getterを使うのが理想だが、
        # Python的には直接参照で高速化する。
        
        # import cyclic reference回避のため、型チェックは緩くする
        hormones = self.brain.hormones
        
        # 文字列キーで取得する (Hormone Enumへの依存は最小限に)
        # (ただしHormoneクラスはEnumなので、brain.pyと同じ定数を使うべき)
        from src.body.hormones import Hormone
        
        dopamine = hormones.get(Hormone.DOPAMINE)
        boredom = hormones.get(Hormone.BOREDOM)
        cortisol = hormones.get(Hormone.CORTISOL)
        
        # 1. 状態チェック (掘削中など)
        if state and state.get("isDigging"):
            return "WAIT"

        # 2. 行動確率分布 (Action Probability Distribution)
        # デフォルト重み
        action_weights = {
            "MOVE_FORWARD": 1.0,
            "TURN_LEFT": 0.5,
            "TURN_RIGHT": 0.5,
            "JUMP": 0.2, # Phase 15.6 Jump Logic
            "DIG": 0.0,
            "PLACE": 0.0, # Phase 11.2
            "ATTACK": 0.0,
            "WAIT": 0.1
        }
        
        # --- Bias Injection (Game Logic) ---
        
        # 退屈 (Boredom) triggers Creativity or Destruction
        if boredom > 15.0:
            # 創造的衝動 (Dopamine > 40) -> PLACE
            if dopamine > 40.0:
                action_weights["PLACE"] += (boredom - 15.0) * 0.1
                action_weights["WAIT"] += 0.2 # じっくり考える
            # 破壊的衝動 (Dopamine Low) -> DIG
            else:
                 action_weights["DIG"] += (boredom - 15.0) * 0.1
                 action_weights["TURN_LEFT"] += 0.2
                 action_weights["TURN_RIGHT"] += 0.2
            
        # 恐怖 (Cortisol) -> 攻撃/逃走 (Fight or Flight)
        # Phase 11.3: FEP-based Combat Logic
        # 予測誤差(痛み=Cortisol)を最小化するための能動的推論
        
        nearest_mob = state.get("nearestMob")
        
        if nearest_mob and nearest_mob.get("isEnemy"):
            mob_name = nearest_mob.get("name")
            dist = nearest_mob.get("distance", 100)
            
            # Memory Lookup: 過去の勝率
            # self.brain.memory が GeologicalMemory のインスタンスであると仮定
            if hasattr(self.brain, "memory") and hasattr(self.brain.memory, "get_combat_win_rate"):
                win_rate = self.brain.memory.get_combat_win_rate(mob_name)
            else:
                win_rate = 0.5 # Default prior
            
            # Cortisolによる強迫度 (Pain Signal)
            # 痛みが強いほど、現状維持(WAIT/IGNORE)は許されない -> Action Bias増大
            urgency = max(0, (cortisol - config.MC_COMBAT_URGENCY_BASE) / config.MC_COMBAT_URGENCY_SCALE)
            
            # Action Selection:
            # 1. ATTACK: 脅威を排除する (Expectation: Pain stops)
            #    勝率が高いほど選ばれやすい。
            # 2. MOVE_AWAY: 脅威から離れる (Expectation: Pain stops)
            #    勝率が低い、または距離が近すぎて危険な場合。
            
            attack_bias = win_rate * config.MC_ATTACK_FACTOR
            flee_bias = (1.0 - win_rate) * config.MC_FLEE_FACTOR
            
            # 距離補正: 近すぎるとパニック(Cortisol高)で攻撃か逃走が暴発
            if dist < config.MC_PANIC_DISTANCE:
                action_weights["ATTACK"] += attack_bias * urgency * 5.0
                # 逃げ場がないなら戦うしかない、あるいは後ろに下がる
                action_weights["MOVE_FORWARD"] += flee_bias * urgency * 5.0 # 本来はMOVE_BACKだが簡易的に
            else:
                 # まだ距離がある
                 action_weights["ATTACK"] += attack_bias * urgency * 2.0
                 action_weights["MOVE_FORWARD"] += flee_bias * urgency * 2.0 # 逃げる
            
            # 敵を見たら少し足を止める（慎重さ）
            if urgency < 0.2:
                 action_weights["WAIT"] += 0.5

        elif cortisol > config.MC_COMBAT_CORTISOL_THRESHOLD:
             # 敵は見えないが怖い -> 逃げる (Unseen Threat prediction)
             action_weights["MOVE_FORWARD"] += 0.5 # ランダムに逃げる

        # 視界情報によるバイアス
        cursor = state.get("cursor") if state else None
        if cursor and cursor.get("name") != "air":
            # 目の前にブロックがある = DIG or PLACE(on it)
            
            # DIG: 木や土なら掘る
            if "log" in cursor["name"] or "dirt" in cursor["name"]:
                 if boredom > 10.0 and dopamine <= 40.0:
                    action_weights["DIG"] += 0.5
            
            # PLACE: 何かブロックがあれば、その上に置くチャンス
            if "air" not in cursor["name"]:
                 if boredom > 15.0 and dopamine > 40.0:
                      action_weights["PLACE"] += 0.6
                      
            # 硬すぎるものは掘らない
            if "obsidian" in cursor["name"] or "bedrock" in cursor["name"]:
                action_weights["DIG"] = 0.0

        # 確率的選択
        actions = list(action_weights.keys())
        weights = list(action_weights.values())
        
        final_intent = random.choices(actions, weights=weights, k=1)[0]
        
        # ログは確率で出す (GameBrain独自の思考ログ)
        if random.random() < 0.05:
            print(f"🎮 [GameBrain] Intent: {final_intent} (B:{boredom:.1f} C:{cortisol:.1f})")

        # 移動系が選ばれたなら、勾配に従って具体的アクションを決定 (Brainの記憶を使用)
        if final_intent in ["MOVE_FORWARD", "TURN_LEFT", "TURN_RIGHT"]:
            return self._decide_movement_from_memory(state)
            
        return final_intent

    def _decide_movement_from_memory(self, state):
        """本体の記憶(Memory)を参照して移動方向を決める"""
        pos = state.get("position", {})
        if not pos:
            return random.choice(["MOVE_FORWARD", "TURN_RIGHT", "TURN_LEFT"])
            
        # Phase 15.1: Use MotorCortex for movement calculation
        if hasattr(self.brain, 'motor_cortex') and self.brain.motor_cortex:
            return self.brain.motor_cortex.calculate_gradient_action(pos)
        
        return "MOVE_FORWARD"  # Fallback

