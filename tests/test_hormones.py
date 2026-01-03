# test_hormones.py
# Unit Tests for HormoneManager

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.body.hormones import Hormone, HormoneManager
import src.dna.config as config


def test_initialization():
    """初期値が Config に従って設定されているか"""
    hm = HormoneManager()
    
    assert hm.get(Hormone.DOPAMINE) == config.DOPAMINE_BASE, \
        f"Expected {config.DOPAMINE_BASE}, got {hm.get(Hormone.DOPAMINE)}"
    
    assert hm.get(Hormone.SEROTONIN) == config.SEROTONIN_BASE, \
        f"Expected {config.SEROTONIN_BASE}, got {hm.get(Hormone.SEROTONIN)}"
    
    assert hm.get(Hormone.GLUCOSE) == 50.0, \
        f"Expected 50.0, got {hm.get(Hormone.GLUCOSE)}"


def test_update_clamp():
    """Clamp が正しく機能するか (0-100)"""
    hm = HormoneManager()
    
    # Over max
    hm.set(Hormone.DOPAMINE, 50.0)
    hm.update(Hormone.DOPAMINE, 100000.0)
    assert hm.get(Hormone.DOPAMINE) == 100.0, \
        f"Expected 100.0 (clamped), got {hm.get(Hormone.DOPAMINE)}"
    
    # Under min
    hm.update(Hormone.DOPAMINE, -100000.0)
    assert hm.get(Hormone.DOPAMINE) == 0.0, \
        f"Expected 0.0 (clamped), got {hm.get(Hormone.DOPAMINE)}"


def test_set():
    """Absolute set が正しく機能するか"""
    hm = HormoneManager()
    
    hm.set(Hormone.ADRENALINE, 77.0)
    assert hm.get(Hormone.ADRENALINE) == 77.0, \
        f"Expected 77.0, got {hm.get(Hormone.ADRENALINE)}"
    
    # Clamp on set
    hm.set(Hormone.ADRENALINE, 999.0)
    assert hm.get(Hormone.ADRENALINE) == 100.0, \
        f"Expected 100.0 (clamped), got {hm.get(Hormone.ADRENALINE)}"


def test_decay():
    """Decay (減衰) が正しく機能するか"""
    hm = HormoneManager()
    
    hm.set(Hormone.CORTISOL, 100.0)
    hm.decay(Hormone.CORTISOL, 0.5)  # 50% decay
    
    assert hm.get(Hormone.CORTISOL) == 50.0, \
        f"Expected 50.0, got {hm.get(Hormone.CORTISOL)}"


def test_as_dict():
    """as_dict が string key を返すか"""
    hm = HormoneManager()
    d = hm.as_dict()
    
    assert "dopamine" in d, "Key 'dopamine' not found in dict"
    assert isinstance(d["dopamine"], float), f"Expected float, got {type(d['dopamine'])}"
    
    # All hormones should be present
    assert "serotonin" in d
    assert "adrenaline" in d
    assert "glucose" in d


def test_get_max_hormone():
    """最も高いホルモンを正しく返すか"""
    hm = HormoneManager()
    
    # Set adrenaline as highest
    hm.set(Hormone.ADRENALINE, 90.0)
    hm.set(Hormone.DOPAMINE, 10.0)
    
    hormone, value = hm.get_max_hormone()
    
    assert hormone == Hormone.ADRENALINE, f"Expected ADRENALINE, got {hormone}"
    assert value == 90.0, f"Expected 90.0, got {value}"
