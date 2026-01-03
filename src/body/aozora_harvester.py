# aozora_harvester.py
# 青空文庫から自動的にテキストを収穫する

import requests
import random
import re
import os
import time
from typing import Optional

class AozoraHarvester:
    """
    青空文庫から自動的に作品を取得
    退屈時に Kaname が自分で食料を探しに行く
    
    50+ 作品から選択可能
    """
    
    # 作品リスト (AuthorID, WorkID, Title)
    # これによりカードページ(card{WorkID}.html)から最新のファイルURLを取得する
    WORKS = [
        # 宮沢賢治 (81)
        (81, 456, "銀河鉄道の夜"),
        (81, 43754, "注文の多い料理店"),
        (81, 470, "セロ弾きのゴーシュ"),
        (81, 462, "風の又三郎"),
        (81, 46605, "やまなし"),
        (81, 45630, "雨ニモマケズ"),
        # 太宰治 (35)
        (35, 1567, "走れメロス"),
        (35, 301, "人間失格"),
        (35, 1565, "斜陽"),
        (35, 2253, "ヴィヨンの妻"),
        (35, 307, "お伽草紙"),
        (35, 275, "女生徒"),
        # 芥川龍之介 (879)
        (879, 127, "羅生門"),
        (879, 92, "蜘蛛の糸"),
        (879, 42, "鼻"),
        (879, 179, "藪の中"),
        (879, 60, "地獄変"),
        (879, 43016, "トロッコ"),
        # 夏目漱石 (148)
        (148, 789, "吾輩は猫である"),
        (148, 773, "こころ"),
        (148, 752, "坊つちやん"),
        (148, 799, "夢十夜"),
        (148, 776, "草枕"),
        # 寺田寅彦 (42)
        (42, 2362, "茶碗の湯"),
        (42, 1684, "柿の種"),
        # 中島敦 (119)
        (119, 624, "山月記"),
        (119, 1737, "李陵"),
        (119, 621, "弟子"),
        # 梶井基次郎 (74)
        (74, 424, "檸檬"),
        (74, 427, "桜の樹の下には"),
        # 新美南吉 (121)
        (121, 628, "ごん狐"),
        (121, 637, "手袋を買いに"),
        # 坂口安吾 (1095)
        (1095, 42620, "堕落論"),
        (1095, 42618, "桜の森の満開の下"),
        # 森鷗外 (129)
        (129, 2078, "舞姫"),
        (129, 691, "高瀬舟"),
    ]
    
    BASE_URL = "https://www.aozora.gr.jp"
    
    def __init__(self, brain_ref=None, cache_dir: str = "food"):
        self.brain_ref = brain_ref
        self.cache_dir = cache_dir
        self.harvested_count = 0
        self.last_harvest = 0.0
        self.cooldown = 300.0
        self.harvested_ids = set()  # (AuthorID, WorkID) で管理
        
        os.makedirs(cache_dir, exist_ok=True)
        print("🌾 Aozora Harvester Initialized.")

    def _get_random_work(self) -> Optional[tuple]:
        """ランダムな作品を取得"""
        available = [w for w in self.WORKS if (w[0], w[1]) not in self.harvested_ids]
        if not available:
            available = self.WORKS
            self.harvested_ids.clear()
        return random.choice(available)
    
    def _resolve_file_url(self, author_id: int, work_id: int) -> Optional[str]:
        """カードページからHTMLファイルのURLを解決する"""
        card_url = f"{self.BASE_URL}/cards/{author_id:06d}/card{work_id}.html"
        try:
            response = requests.get(card_url, timeout=10)
            response.encoding = 'utf-8' # カードページはUTF-8またはShift_JISだがrequestsが判定してくれるはず。明示するならtextアクセス前に。
            
            # HTMLリンクを探す
            # 例: <a href="./files/456_15050.html">いますぐXHTML版で読む</a>
            matches = re.findall(r'<a href=\"([^\"]+)\"[^>]*>いますぐ[X]?HTML版で読む</a>', response.text)
            if matches:
                # 相対パスを絶対パスに変換
                rel_path = matches[0]
                # ./files/... -> files/...
                if rel_path.startswith('./'):
                    rel_path = rel_path[2:]
                return f"{self.BASE_URL}/cards/{author_id:06d}/{rel_path}"
                
            return None
        except Exception as e:
            print(f"⚠️ Resolve URL Error: {e}")
            return None
    
    def _download_text(self, url: str) -> Optional[str]:
        """テキストをダウンロード"""
        try:
            response = requests.get(url, timeout=15)
            # 青空文庫は基本的にShift_JIS
            response.encoding = 'shift_jis'
            text = response.text
            
            # 本文抽出: main_text div を探す (正規表現で属性のバリエーションに対応)
            match = re.search(r'<div[^>]*class=["\']?main_text["\']?[^>]*>', text)
            
            if match:
                start = match.end()
                # 終了位置を探す: 書誌情報の開始 または bodyの終了
                # 1. 書誌情報の前まで
                end_match = re.search(r'<div[^>]*class=["\']?bibliographical_information["\']?[^>]*>', text[start:])
                if end_match:
                    end = start + end_match.start()
                else:
                    # 2. 書誌情報がない場合、メインテキストの終了コメントを探す
                    end_comment = text.find('</div><!--/main_text-->', start)
                    if end_comment != -1:
                        end = end_comment
                    else:
                        # 3. bodyの終了まで
                        body_end = text.rfind('</body>')
                        if body_end != -1:
                            end = body_end
                        else:
                            end = len(text)
                            
                main_text = text[start:end]
            
            else:
                # main_text がない場合 (古い形式など)、body全体から抽出を試みる
                body_start = re.search(r'<body[^>]*>', text)
                if body_start:
                    start = body_start.end()
                    body_end = text.rfind('</body>')
                    end = body_end if body_end != -1 else len(text)
                    main_text = text[start:end]
                else:
                    return None
            
            if not main_text or len(main_text) < 100:
                # デバッグ情報を出す
                print(f"⚠️ Content too short ({len(main_text) if 'main_text' in locals() else 0} chars)")
                return None
            
            # HTMLタグを除去
            main_text = re.sub(r'<[^>]+>', '', main_text)
            # ルビ注記を除去
            main_text = re.sub(r'《[^》]+》', '', main_text)
            main_text = re.sub(r'［[^］]+］', '', main_text)
            main_text = re.sub(r'｜', '', main_text)
            # 連続空白を整理
            main_text = re.sub(r'\s+', ' ', main_text)
            
            return main_text.strip()
            
        except Exception as e:
            print(f"⚠️ Aozora Download Error: {e}")
            return None
    
    def harvest(self) -> Optional[str]:
        """
        青空文庫から1作品を収穫
        
        Returns: 作品テキスト（成功時）、None（失敗時）
        """
        # クールダウンチェック
        if time.time() - self.last_harvest < self.cooldown:
            return None
        
        print("🌾 [Aozora] Harvesting...")
        
        work = self._get_random_work()
        if not work:
            print("⚠️ [Aozora] No work found.")
            return None
        
        author_id, work_id, title = work
        print(f"📚 作品ID:{work_id}『{title}』のURLを解決中...")
        
        # カードページからファイルURLを解決
        url = self._resolve_file_url(author_id, work_id)
        if not url:
            print(f"⚠️ [Aozora] Failed to resolve URL for {title}")
            return None
            
        text = self._download_text(url)
        if not text or len(text) < 100:
            print("⚠️ [Aozora] Text too short or empty.")
            return None
        
        self.harvested_count += 1
        self.last_harvest = time.time()
        self.harvested_ids.add((author_id, work_id))
        
        # キャッシュに保存
        # IDベースの名前に変更して衝突回避
        filename = f"aozora_{author_id}_{work_id}_{int(time.time())}.txt"
        filepath = os.path.join(self.cache_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"🌾 [Aozora] Harvested: 『{title}』({len(text):,} chars)")
        
        return text
    
    def hungry_harvest(self) -> bool:
        """
        退屈時に自動で収穫
        brain_ref が必要
        
        Returns: True if harvested
        """
        if not self.brain_ref:
            return False
        
        try:
            from src.body.hormones import Hormone
            boredom = self.brain_ref.hormones.get(Hormone.BOREDOM)
            stimulation = self.brain_ref.hormones.get(Hormone.STIMULATION)
            
            # 退屈かつ刺激不足 → 収穫に出る
            if boredom > 60 and stimulation < 30:
                text = self.harvest()
                if text:
                    # 直接胃袋に送り込む
                    if hasattr(self.brain_ref, 'cortex') and hasattr(self.brain_ref.cortex, 'stomach'):
                        self.brain_ref.cortex.stomach.eat(text)
                    
                    # ホルモン更新
                    self.brain_ref.hormones.update(Hormone.BOREDOM, -20.0)
                    self.brain_ref.hormones.update(Hormone.STIMULATION, 30.0)
                    self.brain_ref.hormones.update(Hormone.DOPAMINE, 10.0)
                    
                    print("🌾 [Aozora] Fed to stomach!")
                    return True
        except Exception as e:
            print(f"⚠️ hungry_harvest error: {e}")
        
        return False
