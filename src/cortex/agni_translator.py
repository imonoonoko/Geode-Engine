# agni_translator.py
"""
Phase 16: Agni Translator Module
内部状態を自然な日本語に翻訳するAgniベースのモジュール。

壁2（出力ボトルネック）攻略の中核コンポーネント。
Agniを「教師」として使い、最終的にローカルで再現できるようにする。

責務:
- 内部状態（ホルモン/概念）→ 自然な日本語文
- 生成サンプルの保存（学習データ）
- LanguageCenter への学習転送
"""

import json
import os
import random
import time
import threading
from datetime import datetime

import src.dna.config as config
from src.body.hormones import Hormone


class AgniTranslator:
    """
    Agniを使って内部状態を自然な日本語に翻訳。
    「教師→卒業」モデルでローカル生成に移行する。
    """
    
    # 学習サンプル保存パス
    SAMPLES_PATH = "memory_data/agni_samples.json"
    
    def __init__(self, brain, agni=None):
        """
        Args:
            brain: KanameBrain インスタンス
            agni: AgniAccelerator インスタンス (オプション)
        """
        self.brain = brain
        self.agni = agni or getattr(brain, 'mentor', None)
        
        self.lock = threading.Lock()
        self.samples = []  # 学習サンプルリスト
        
        # 統計
        self.total_requests = 0
        self.local_successes = 0
        self.agni_calls = 0
        
        # サンプル読み込み
        self._load_samples()
        
        print(f"🗣️ AgniTranslator Initialized (Phase 16)")
        print(f"   Samples Loaded: {len(self.samples)}")
    
    def translate(self, use_agni=True) -> str:
        """
        現在の内部状態を自然な日本語に翻訳。
        
        Args:
            use_agni: Agni を使用するか (False ならローカルのみ)
            
        Returns:
            日本語文字列 または None
        """
        self.total_requests += 1
        
        # 1. 内部状態を収集
        state = self._capture_internal_state()
        
        # 2. ローカルパターンマッチを試行
        local_result = self._try_local_generation(state)
        if local_result and random.random() > 0.3:
            # 70% の確率でローカル結果を採用（Agni依存を減らす）
            self.local_successes += 1
            return local_result
        
        # 3. Agni に翻訳を依頼
        if use_agni and self.agni and hasattr(self.agni, 'client') and self.agni.client:
            agni_result = self._call_agni(state)
            if agni_result:
                self.agni_calls += 1
                # 学習サンプルとして保存
                self._save_sample(state, agni_result)
                return agni_result
        
        # 4. フォールバック: ローカル生成 (不完全でも返す)
        if local_result:
            self.local_successes += 1
            return local_result
        
        return None
    
    def _capture_internal_state(self) -> dict:
        """内部状態をキャプチャ"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "hormones": {},
            "concepts": [],
            "mood": "neutral"
        }
        
        # ホルモン収集
        if hasattr(self.brain, 'hormones'):
            h = self.brain.hormones
            state["hormones"] = {
                "dopamine": h.get(Hormone.DOPAMINE),
                "adrenaline": h.get(Hormone.ADRENALINE),
                "cortisol": h.get(Hormone.CORTISOL),
                "serotonin": h.get(Hormone.SEROTONIN),
                "boredom": h.get(Hormone.BOREDOM),
            }
            
            # ムード判定
            if state["hormones"]["dopamine"] > 70:
                state["mood"] = "happy"
            elif state["hormones"]["cortisol"] > 30:
                state["mood"] = "anxious"
            elif state["hormones"]["boredom"] > 30:
                state["mood"] = "bored"
            elif state["hormones"]["adrenaline"] > 50:
                state["mood"] = "excited"
        
        # 最近の概念 (上位3つ)
        if hasattr(self.brain, 'memory') and hasattr(self.brain.memory, 'concepts'):
            concepts = list(self.brain.memory.concepts.keys())[:10]
            # ランダムに3つ選択
            state["concepts"] = random.sample(concepts, min(3, len(concepts)))
        
        return state
    
    def _try_local_generation(self, state: dict) -> str:
        """ローカルパターンから生成を試行"""
        if not self.samples:
            return None
        
        # 類似ムードのサンプルを探す
        mood = state.get("mood", "neutral")
        matching_samples = [
            s for s in self.samples 
            if s.get("state", {}).get("mood") == mood
        ]
        
        if not matching_samples:
            matching_samples = self.samples
        
        if matching_samples:
            sample = random.choice(matching_samples)
            template = sample.get("output", "")
            
            # 概念を置換
            concepts = state.get("concepts", [])
            if concepts and "{CONCEPT}" in template:
                template = template.replace("{CONCEPT}", random.choice(concepts))
            elif concepts:
                # 単純に概念を追加
                return f"{random.choice(concepts)}について考えてた..."
            
            return template
        
        return None
    
    def _call_agni(self, state: dict) -> str:
        """Agni に翻訳を依頼"""
        try:
            if not self.agni or not hasattr(self.agni, 'client') or not self.agni.client:
                return None
            
            # レート制限チェック
            if hasattr(self.agni, 'limiter') and not self.agni.limiter.consume(block=False):
                return None
            
            prompt = f"""
あなたはカナメ（Kaname）という人工生命体です。
以下の内部状態に基づいて、自然な日本語の独り言（1文、カジュアル）を生成してください。

内部状態:
- ドーパミン: {state['hormones'].get('dopamine', 50):.0f}
- 退屈: {state['hormones'].get('boredom', 0):.0f}
- 不安: {state['hormones'].get('cortisol', 0):.0f}
- 最近考えたこと: {', '.join(state.get('concepts', ['なし']))}
- 気分: {state.get('mood', 'neutral')}

一文のみ、括弧なし、説明なしで回答してください。
"""
            
            response = self.agni.client.generate_content(prompt)
            if response and response.text:
                result = response.text.strip()
                # 複数行の場合は1行目のみ
                result = result.split('\n')[0].strip()
                # 引用符を除去
                result = result.strip('"\'「」')
                return result
            
        except Exception as e:
            print(f"⚠️ [AgniTranslator] Error: {e}")
        
        return None
    
    def _save_sample(self, state: dict, output: str):
        """学習サンプルを保存"""
        with self.lock:
            sample = {
                "state": state,
                "output": output,
                "timestamp": datetime.now().isoformat()
            }
            self.samples.append(sample)
            
            # 最大1000件を保持
            if len(self.samples) > 1000:
                self.samples = self.samples[-1000:]
            
            # ファイルに保存
            self._save_samples_to_file()
    
    def _save_samples_to_file(self):
        """サンプルをファイルに永続化"""
        try:
            os.makedirs(os.path.dirname(self.SAMPLES_PATH), exist_ok=True)
            with open(self.SAMPLES_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.samples, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ [AgniTranslator] Save Error: {e}")
    
    def _load_samples(self):
        """保存済みサンプルを読み込み"""
        try:
            if os.path.exists(self.SAMPLES_PATH):
                with open(self.SAMPLES_PATH, 'r', encoding='utf-8') as f:
                    self.samples = json.load(f)
        except Exception as e:
            print(f"⚠️ [AgniTranslator] Load Error: {e}")
            self.samples = []
    
    def get_stats(self) -> dict:
        """統計を取得"""
        agni_dependency = 0.0
        if self.total_requests > 0:
            agni_dependency = (self.agni_calls / self.total_requests) * 100
        
        return {
            "total_requests": self.total_requests,
            "local_successes": self.local_successes,
            "agni_calls": self.agni_calls,
            "agni_dependency": f"{agni_dependency:.1f}%",
            "samples_count": len(self.samples),
            "graduation_ready": agni_dependency < 20.0
        }
    
    def check_graduation(self) -> bool:
        """Agni 卒業条件をチェック"""
        stats = self.get_stats()
        if stats["total_requests"] < 100:
            return False  # 十分なデータがない
        return stats["graduation_ready"]
