import numpy as np
import threading
import time
import os
import random
import math
import collections
import winsound
from pydub import AudioSegment
from pydub.generators import Sine
import src.dna.config as config
import queue # Added for Phase 2 fix

# 一時ファイルディレクトリ
TEMP_DIR = os.path.join(os.environ.get("TEMP", "."), "maia_resonance")
os.makedirs(TEMP_DIR, exist_ok=True)

class GeologicalResonance:
    def __init__(self, memory_ref, synapse_ref):
        print("💎 Initializing Geological Resonance (The Soul)...")
        self.memory = memory_ref
        self.synapse = synapse_ref
        
        # 現在震えている記憶 {word: amplitude}
        self.active_resonances = {} 
        self.lock = threading.Lock()
        
        # 音響生成用パラメータ
        self.base_freq = 110.0 # A2 (Low)
        self.max_depth = 2 # 共鳴の深さ
        
        # 再生スレッド管理
        self.is_active = True
        self.sound_queue = collections.deque(maxlen=5) # 再生待ち行列
        self.play_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.play_thread.start() # CRITICAL: This was missing! No sounds were playing.
        
        # Start cleanup worker (Single Thread)
        self.cleanup_queue = queue.Queue()
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()

    def stop(self):
        """ Graceful shutdown of resonance threads """
        self.is_active = False

    def _cleanup_worker(self):
        """ Dedicated thread for deleting temp files (prevents thread leak) """
        while self.is_active:
            try:
                # Wait for file to clean
                path = self.cleanup_queue.get(timeout=1.0)
                
                # Check exist
                if os.path.exists(path):
                    # Retry with small delay if locked by OS
                    for _ in range(5):
                        try: 
                            os.remove(path)
                            break
                        except PermissionError:
                            time.sleep(0.5) # Wait for sound to finish logic
                        except:
                            break
                    
                self.cleanup_queue.task_done()
                time.sleep(0.1) # Brief pause to yield CPU
            except queue.Empty:
                pass

    def impact(self, word, force=1.0):
        """ 1. 衝撃: 言葉の結晶を叩く """
        with self.lock:
            # 既存の振動に加算（共振）
            current = self.active_resonances.get(word, 0.0)
            self.active_resonances[word] = min(current + force, 2.0)
            
        # 波及効果 (非同期で行うべきだが、計算軽いのでここでやる)
        self._propagate_vibration(word, force, depth=0)
        
        # 音響生成リクエスト
        self._queue_sound_generation()

    def drift_impact(self, word):
        """ 自律思考用の微弱な共鳴 """
        # Force is very low (0.1 ~ 0.2)
        self.impact(word, force=0.15)

    def _propagate_vibration(self, start_node, force, depth):
        """ 2. 伝達: シナプス（弦）を伝って振動を広げる """
        if depth >= self.max_depth: return
        
        if start_node not in self.synapse.brain_graph:
            return

        neighbors = self.synapse.brain_graph[start_node]
        
        for neighbor, data in neighbors.items():
            weight = data.get('weight', 0.1)
            
            # 減衰係数: 結合が強いほどよく伝わる (Weight 1.0 -> Decay 0.9, Weight 0.1 -> Decay 0.1)
            # Weight is usually 0.5 to 3.0 in this system
            transmission = min(0.9, weight * 0.3)
            
            transmitted_force = force * transmission
            
            if transmitted_force > 0.1:
                with self.lock:
                    current = self.active_resonances.get(neighbor, 0.0)
                    self.active_resonances[neighbor] = min(current + transmitted_force, 1.5)
                
                # 再帰
                self._propagate_vibration(neighbor, transmitted_force, depth + 1)

    def _queue_sound_generation(self):
        """ 現在の共鳴状態から音を生成してキューに入れる """
        # 頻繁に呼びすぎないようにスロットリングが必要だが、
        # ここでは簡易的に「キューが空なら入れる」戦略で
        if len(self.sound_queue) < 2:
            self.sound_queue.append("GENERATE")

    def _playback_loop(self):
        """ 音響生成と再生を行うループ """
        while self.is_active:
            if not self.sound_queue:
                time.sleep(0.1)
                continue
            
            task = self.sound_queue.popleft()
            if task == "GENERATE":
                self._synthesize_and_play()
            
            time.sleep(0.05)

    def _synthesize_and_play(self):
        """ 3. 音響合成: クリスタルサウンドの生成 """
        # スナップショット作成
        with self.lock:
            if not self.active_resonances: return
            snapshot = self.active_resonances.copy()
            
            # 減衰処理 (Resonance Tail)
            to_remove = []
            for w in self.active_resonances:
                # Get Altitude for Decay Calculation
                altitude = 0.5
                if w in self.memory.concepts:
                    # Look up Y coord
                    cy = int(self.memory.concepts[w][1])
                    cx = int(self.memory.concepts[w][0])
                    try: altitude = float(self.memory.terrain[cy][cx])
                    except: pass
                
                # Variable Decay Rate
                # High Altitude (Happy) -> 0.96 (Long Sustain)
                # Low Altitude (Sad) -> 0.6 (Short Decay)
                # Map 0.0-1.0 to 0.6-0.96
                decay_rate = 0.6 + (altitude * 0.36)
                
                self.active_resonances[w] *= decay_rate
                
                if self.active_resonances[w] < 0.05:
                    to_remove.append(w)
            for w in to_remove:
                del self.active_resonances[w]

        # 合成 (pydub)
        # 2秒の無音ベース
        duration_ms = 1500
        mixed = AudioSegment.silent(duration=duration_ms)
        
        count = 0
        for word, amp in snapshot.items():
            if amp < 0.1: continue
            
            # ピッチ決定
            if word in self.memory.concepts:
                coords = self.memory.concepts[word] # [x, y, t] or [x, y]
                # altitude は memory.terrain から取るのが正確だが、簡易的に 'y' 座標を高度とみなすか？
                # いや、memory.terrainへのアクセスが必要
                # ここでは重いので、conceptsにはないが、memoryのterrain配列にアクセスする
                # int coords
                cx, cy = int(coords[0]), int(coords[1])
                try:
                    altitude = float(self.memory.terrain[cy][cx])
                except:
                    altitude = 0.5
            else:
                altitude = 0.5

            # クリスタル周波数計算: Formula from User
            # Freq = 110 * (2 ** (altitude * 3)) -> 110 ~ 880Hz
            freq = 110.0 * (2 ** (altitude * 3.0))
            
            # サイン波生成 (-20dB start)
            # 音量は amp に比例
            vol_db = -30.0 + (10.0 * amp) # -30dB ~ -10dB
            
            tone = Sine(freq).to_audio_segment(duration=duration_ms, volume=vol_db)
            
            # フェードイン・アウト (ベルのようなエンベロープ)
            tone = tone.fade_in(50).fade_out(duration_ms - 50)
            
            mixed = mixed.overlay(tone)
            count += 1
            if count > 5: break # ポリフォニー制限 (重くなりすぎないように)

        if count > 0:
            # 保存と再生
            try:
                # Use monotonic time to ensure uniqueness without uuid imports
                filename = os.path.join(TEMP_DIR, f"crystal_{int(time.time()*1000)}.wav")
                
                # Export
                mixed.export(filename, format="wav")
                
                # Play Async (Windows)
                winsound.PlaySound(filename, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT | winsound.SND_PURGE)
                
                # クリーンアップは遅延させるか、次回のループで古いものを消す
                # Fixed Phase 2: Use Queue to prevent thread leak
                self.cleanup_queue.put(filename)
                
            except Exception as e:
                print(f"Resonance Error: {e}")


