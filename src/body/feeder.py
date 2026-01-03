# feeder.py
# 「食べさせる」システム - テキストファイルをRNNに食べさせて消化（削除）する

import os
import glob
import time
import json
import re
import random
from datetime import datetime

class DataFeeder:
    def __init__(self, food_folder="food", brain_ref=None):
        """
        food_folder: テキストファイルを置くフォルダ
        brain_ref: Phase 30 - 退屈トリガー用
        """
        self.food_folder = food_folder
        self.brain_ref = brain_ref
        self.log_path = os.path.join("memory_data", "digestion_log.json")
        os.makedirs(self.food_folder, exist_ok=True)
        os.makedirs("memory_data", exist_ok=True)
        
        # Load existing log
        self.log = self._load_log()
        print(f"🍽️ Feeder Ready. Total digested: {self.log.get('total_chars', 0):,} chars across {self.log.get('total_files', 0)} files.")

    def _load_log(self):
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"total_chars": 0, "total_files": 0, "history": []}

    def _save_log(self):
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump(self.log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Log save error: {e}")

    def _clean_text(self, text):
        """ Clean Aozora Bunko and Markdown format """
        # 1. Aozora Bunko Cleaning
        text = re.split(r'\-{5,}', text)[-1] # Remove Header
        text = re.split(r'底本：', text)[0]   # Remove Footer
        text = re.sub(r'《.*?》', '', text)    # Remove Ruby
        text = re.sub(r'［.*?］', '', text)    # Remove Annotations
        text = re.sub(r'｜', '', text)         # Remove Ruby Marker
        
        # 2. Markdown Cleaning
        text = re.sub(r'\[\[(.*?)\]\]', r'\1', text) # [[WikiLink]] -> WikiLink
        text = re.sub(r'#+\s', '', text)              # Remove Headers
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)   # Remove Images
        
        return text.strip()

    def check_food(self):
        """
        フォルダ内のテキストファイルをチェック
        Returns: List of file paths
        """
        extensions = ["*.txt", "*.md"]
        files = []
        for ext in extensions:
            files.extend(glob.glob(os.path.join(self.food_folder, ext)))
        return files

    def eat(self):
        """
        Read, Clean, Shuffle, and Digest format.
        """
        files = self.check_food()
        if not files: return None
        
        all_lines = []
        digested_count = 0
        session_chars = 0
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    raw_text = f.read()
                
                # Cleaning
                cleaned_text = self._clean_text(raw_text)
                lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
                all_lines.extend(lines)
                
                # Stats calculation (based on cleaned text)
                char_count = len(cleaned_text)
                session_chars += char_count
                
                # Delete original file
                os.remove(file_path)
                digested_count += 1
                
                # Log
                self.log["history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "filename": os.path.basename(file_path),
                    "chars": char_count
                })
                
                print(f"🍴 Digested: {os.path.basename(file_path)} ({char_count:,} chars)")
                
            except Exception as e:
                print(f"⚠️ Failed to digest {file_path}: {e}")
        
        if digested_count > 0:
            # Shuffle lines for context blending
            random.shuffle(all_lines)
            final_text = "\n".join(all_lines)
            
            # Log updates
            self.log["total_chars"] = self.log.get("total_chars", 0) + session_chars
            self.log["total_files"] = self.log.get("total_files", 0) + digested_count
            self.log["history"] = self.log["history"][-100:]
            self._save_log()
            
            print(f"✨ Session: {digested_count} files, {session_chars:,} chars. (Shuffled)")
            return final_text
        
        return None

    def eat_file(self, file_path_or_content, is_direct_text=False):
        """
        Feed single file or direct text.
        """
        raw_text = ""
        filename = "direct_input"
        
        if is_direct_text:
            raw_text = file_path_or_content
            filename = f"direct_{datetime.now().strftime('%H%M%S')}.txt"
        else:
            if not os.path.exists(file_path_or_content): return None
            try:
                with open(file_path_or_content, 'r', encoding='utf-8', errors='ignore') as f:
                    raw_text = f.read()
                filename = os.path.basename(file_path_or_content)
            except Exception as e:
                print(f"⚠️ Read error: {e}")
                return None
        
        try:
            cleaned_text = self._clean_text(raw_text)
            lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
            random.shuffle(lines)
            final_text = "\n".join(lines)
            
            char_count = len(cleaned_text)
            
            # Log
            self.log["history"].append({
                "timestamp": datetime.now().isoformat(),
                "filename": filename,
                "chars": char_count
            })
            self.log["total_chars"] = self.log.get("total_chars", 0) + char_count
            self.log["total_files"] = self.log.get("total_files", 0) + 1
            self.log["history"] = self.log["history"][-100:]
            self._save_log()
            
            if not is_direct_text:
                try:
                    if os.path.exists(file_path_or_content):
                        os.remove(file_path_or_content)
                except Exception as e:
                    print(f"⚠️ Delete error: {e}")
            
            print(f"🍴 Direct Feed (Cleaned & Shuffled): {filename} ({char_count:,} chars)")
            
            return final_text
        except Exception as e:
            print(f"⚠️ Direct feed error: {e}")
            return None

    def has_food(self):
        """
        食べ物があるかチェック
        """
        return len(self.check_food()) > 0
    
    def get_stats(self):
        """
        統計情報を取得
        """
        return {
            "total_chars": self.log.get("total_chars", 0),
            "total_files": self.log.get("total_files", 0),
            "recent": self.log.get("history", [])[-5:]
        }

    def hungry_check(self) -> bool:
        """
        Phase 30: 退屈トリガーによる自動収集
        退屈度が高い時に食料があれば食べる
        
        Returns: True if food was consumed
        """
        if not self.brain_ref:
            return False
        
        try:
            from src.body.hormones import Hormone
            boredom = self.brain_ref.hormones.get(Hormone.BOREDOM)
            glucose = self.brain_ref.hormones.get(Hormone.GLUCOSE)
            
            # 退屈かつ空腹 → 食料を探す
            if boredom > 70 or glucose < 30:
                if self.has_food():
                    print(f"🍴 [AUTO-FEED] Boredom={boredom:.1f}, Glucose={glucose:.1f} → Eating...")
                    text = self.eat()
                    if text:
                        # 食べたら胃袋に送る
                        if hasattr(self.brain_ref, 'cortex') and hasattr(self.brain_ref.cortex, 'stomach'):
                            self.brain_ref.cortex.stomach.eat(text)
                        
                        # ホルモン更新
                        self.brain_ref.hormones.update(Hormone.BOREDOM, -30.0)
                        self.brain_ref.hormones.update(Hormone.GLUCOSE, 20.0)
                        self.brain_ref.hormones.update(Hormone.DOPAMINE, 15.0)
                        return True
        except Exception as e:
            print(f"⚠️ hungry_check error: {e}")
        
        return False
