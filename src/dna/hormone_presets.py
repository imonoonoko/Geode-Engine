# ゲームモード用ホルモンプリセット
# カナメがゲームをプレイする際の最適な精神状態を定義

from typing import Dict

class HormonePresets:
    """
    ゲームモード用のホルモン初期値プリセット。
    通常状態とは異なる精神状態でゲームに集中させる。
    """
    
    # ゲームモード: 高い報酬感度と集中力
    GAME_MODE = {
        "dopamine": 70.0,      # 高い報酬感度（行動を促進）
        "boredom": 10.0,       # 低い退屈（集中維持）
        "adrenaline": 50.0,    # 適度な興奮（反応速度）
        "glucose": 80.0,       # 高エネルギー
        "serotonin": 60.0,     # 安定した気分
        "cortisol": 20.0,      # 低ストレス
        "oxytocin": 30.0,      # 適度な社会性
        "surprise": 40.0,      # 適度な新規性への感度
    }
    
    # 探索モード: 好奇心と冒険心
    EXPLORATION_MODE = {
        "dopamine": 50.0,
        "boredom": 80.0,       # 高い好奇心（新しい場所を探す）
        "adrenaline": 30.0,
        "glucose": 70.0,
        "serotonin": 50.0,
        "cortisol": 15.0,
        "oxytocin": 20.0,
        "surprise": 70.0,      # 高い驚き感度（未知を求める）
    }
    
    # サバイバルモード: 警戒と生存本能
    SURVIVAL_MODE = {
        "dopamine": 40.0,
        "boredom": 20.0,
        "adrenaline": 70.0,    # 高い反応速度
        "glucose": 60.0,
        "serotonin": 40.0,
        "cortisol": 50.0,      # 警戒状態
        "oxytocin": 10.0,
        "surprise": 50.0,
    }
    
    # リラックスモード: 低ストレスでのんびり
    RELAX_MODE = {
        "dopamine": 60.0,
        "boredom": 30.0,
        "adrenaline": 10.0,
        "glucose": 50.0,
        "serotonin": 80.0,     # 高い安定感
        "cortisol": 5.0,       # 低ストレス
        "oxytocin": 60.0,
        "surprise": 20.0,
    }
    
    # 学習モード: 長期学習向け
    LEARNING_MODE = {
        "dopamine": 60.0,      # 適度な報酬感度
        "boredom": 50.0,       # バランスの良い好奇心
        "adrenaline": 20.0,    # 落ち着いた状態
        "glucose": 70.0,       # 十分なエネルギー
        "serotonin": 70.0,     # 安定
        "cortisol": 10.0,      # 低ストレス
        "oxytocin": 30.0,
        "surprise": 50.0,
    }
    
    @classmethod
    def get_preset(cls, name: str) -> Dict[str, float]:
        """名前でプリセットを取得"""
        presets = {
            "game": cls.GAME_MODE,
            "exploration": cls.EXPLORATION_MODE,
            "survival": cls.SURVIVAL_MODE,
            "relax": cls.RELAX_MODE,
            "learning": cls.LEARNING_MODE,
        }
        return presets.get(name.lower(), cls.GAME_MODE)
    
    @classmethod
    def apply_to_brain(cls, brain, preset_name: str):
        """ホルモンプリセットを脳に適用"""
        from src.body.hormones import Hormone
        
        preset = cls.get_preset(preset_name)
        
        # 各ホルモン値を設定
        hormone_map = {
            "dopamine": Hormone.DOPAMINE,
            "boredom": Hormone.BOREDOM,
            "adrenaline": Hormone.ADRENALINE,
            "glucose": Hormone.GLUCOSE,
            "serotonin": Hormone.SEROTONIN,
            "cortisol": Hormone.CORTISOL,
            "oxytocin": Hormone.OXYTOCIN,
            "surprise": Hormone.SURPRISE,
        }
        
        for key, value in preset.items():
            if key in hormone_map:
                # 現在値との差分を計算して更新
                current = brain.hormones.get(hormone_map[key])
                diff = value - current
                brain.hormones.update(hormone_map[key], diff)
        
        print(f"🧬 Applied hormone preset: {preset_name.upper()}")
        return True
