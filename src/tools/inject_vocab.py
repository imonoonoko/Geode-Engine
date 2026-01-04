
import sys
import os
import time

# Setup Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from src.brain_stem.brain import KanameBrain
import src.dna.config as config

# 100 Basic Japanese Words (JlPT N5/N4 + Poetic/Abstract)
VOCAB_LIST = [
    # 自然 (Nature)
    "空", "海", "山", "川", "森", "花", "雨", "風", "雪", "雲",
    "太陽", "月", "星", "光", "影", "虹", "雷", "大地", "宇宙", "世界",
    
    # 感情 (Emotion)
    "楽しい", "悲しい", "嬉しい", "寂しい", "怒り", "恐れ", "驚き", "幸せ", "苦しみ", "安らぎ",
    "好き", "嫌い", "愛", "憎しみ", "希望", "絶望", "勇気", "不安", "憧れ", "後悔",

    # 行動 (Action)
    "歩く", "走る", "飛ぶ", "泳ぐ", "食べる", "寝る", "見る", "聞く", "話す", "歌う",
    "考える", "忘れる", "思い出す", "探す", "見つける", "作る", "壊す", "笑う", "泣く", "叫ぶ",

    # 抽象 (Abstract)
    "時間", "未来", "過去", "現在", "記憶", "夢", "現実", "幻", "運命", "自由",
    "孤独", "絆", "理由", "意味", "嘘", "真実", "平和", "戦い", "命", "死",

    # 日常 (Daily/Objects)
    "家", "窓", "扉", "道", "橋", "壁", "鏡", "時計", "本", "手紙",
    "言葉", "音楽", "色", "音", "匂い", "味", "熱", "冷たさ", "痛み", "力"
]

def inject():
    print(f"💉 Injecting {len(VOCAB_LIST)} words into Geological Memory...")
    
    # Initialize Brain (Headless)
    brain = KanameBrain()
    
    # Wait for initialization (Embeddings etc)
    time.sleep(2)
    
    count = 0
    for word in VOCAB_LIST:
        print(f"   📖 Learning: {word}")
        
        # 1. Reinforce in Memory (Create Concept)
        # Use activate_concept which handles creation/embedding
        brain.activate_concept(word, boost=0.5)
        
        # 2. Also Learn in Sedimentary Cortex (Context)
        if hasattr(brain, 'sedimentary_cortex'):
            brain.sedimentary_cortex.learn(word, "VOCAB_INJECT", surprise=0.1)
        elif hasattr(brain, 'cortex'):
             brain.cortex.learn(word, "VOCAB_INJECT", surprise=0.1)
        
        count += 1
        
    print(f"✅ Injection Complete. {count} words added.")

if __name__ == "__main__":
    inject()
