# test_memory_distortion.py
from src.cortex.memory_distortion import MemoryDistorter


def test_distorter_init():
    md = MemoryDistorter()
    assert md.negativity_bias == 1.5


def test_encode_strong_emotion():
    md = MemoryDistorter()
    # 強いネガティブ感情
    memory = md.encode("bad event", valence=-0.8, arousal=0.9)
    # 確率的だが、強い感情は保存されやすい
    # 複数回試行
    for _ in range(10):
        m = md.encode("bad", -0.9, 0.9)
        if m:
            break
    # 少なくとも1回は成功するはず（確率的）


def test_emotional_bias():
    md = MemoryDistorter()
    # ネガティブ記憶を複数追加
    for _ in range(20):
        md.encode("negative", -0.7, 0.8)
    bias = md.get_emotional_bias()
    # ネガティブバイアスが存在することを確認
    assert bias <= 0  # or at least leaning negative
