# knowledge_harvesters.py
# 知識ハーベスター: 複数の情報ソースから知識を収集
# 青空文庫 + Wikipedia + NHK News + 名言 + 天気 + RSS

import time
import random
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import urllib.request
import urllib.parse
import json
import re


class SourceType(Enum):
    """情報ソースの種類"""
    AOZORA = auto()      # 青空文庫（既存）
    WIKIPEDIA = auto()   # Wikipedia
    NHK_NEWS = auto()    # NHK やさしい日本語ニュース
    QUOTES = auto()      # 名言・格言
    WEATHER = auto()     # 天気情報
    RSS = auto()         # RSSフィード


@dataclass
class HarvestedContent:
    """収集したコンテンツ"""
    source: SourceType
    title: str
    content: str
    url: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)


class WikipediaHarvester:
    """
    Wikipedia 日本語版からランダムな記事を取得
    """
    
    def __init__(self):
        self.api_url = "https://ja.wikipedia.org/api/rest_v1"
        print("📖 Wikipedia Harvester Initialized.")
    
    def get_random_article(self) -> Optional[HarvestedContent]:
        """ランダムな記事を取得"""
        try:
            # ランダムページのタイトルを取得
            random_url = "https://ja.wikipedia.org/wiki/Special:Random"
            req = urllib.request.Request(random_url, headers={'User-Agent': 'Kaname/1.0'})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                final_url = response.geturl()
                title = urllib.parse.unquote(final_url.split("/wiki/")[-1])
            
            # 記事の要約を取得
            summary_url = f"{self.api_url}/page/summary/{urllib.parse.quote(title)}"
            req = urllib.request.Request(summary_url, headers={'User-Agent': 'Kaname/1.0'})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            extract = data.get("extract", "")
            if not extract:
                return None
            
            return HarvestedContent(
                source=SourceType.WIKIPEDIA,
                title=data.get("title", title),
                content=extract[:500],  # 最大500文字
                url=final_url,
                metadata={"type": "encyclopedia"}
            )
        except Exception as e:
            print(f"⚠️ Wikipedia harvest failed: {e}")
            return None


class NHKNewsHarvester:
    """
    NHK NEWS WEB EASY (やさしい日本語ニュース) からニュースを取得
    """
    
    def __init__(self):
        self.api_url = "https://www3.nhk.or.jp/news/easy/news-list.json"
        print("📰 NHK News Harvester Initialized.")
    
    def get_random_news(self) -> Optional[HarvestedContent]:
        """ランダムなニュースを取得"""
        try:
            req = urllib.request.Request(
                self.api_url,
                headers={'User-Agent': 'Kaname/1.0'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                raw = response.read().decode('utf-8')
                # BOMを除去
                if raw.startswith('\ufeff'):
                    raw = raw[1:]
                data = json.loads(raw)
            
            # 日付ごとにニュースがグループ化されている
            all_news = []
            for date_key, news_list in data[0].items():
                if isinstance(news_list, list):
                    all_news.extend(news_list)
            
            if not all_news:
                return None
            
            news = random.choice(all_news)
            
            return HarvestedContent(
                source=SourceType.NHK_NEWS,
                title=news.get("title", ""),
                content=news.get("title", ""),  # 本文は別途取得が必要
                url=f"https://www3.nhk.or.jp/news/easy/{news.get('news_id', '')}/{news.get('news_id', '')}.html",
                metadata={"date": news.get("news_prearranged_time", "")}
            )
        except Exception as e:
            print(f"⚠️ NHK News harvest failed: {e}")
            return None


class QuotesHarvester:
    """
    名言・格言を提供（ローカルデータベース）
    """
    
    def __init__(self):
        self.quotes = [
            {"text": "人生は短い。だからこそ、今を大切に生きなければならない。", "author": "セネカ"},
            {"text": "失敗は成功のもと。", "author": "日本のことわざ"},
            {"text": "知識は力なり。", "author": "フランシス・ベーコン"},
            {"text": "今日できることを明日に延ばすな。", "author": "ベンジャミン・フランクリン"},
            {"text": "継続は力なり。", "author": "日本のことわざ"},
            {"text": "学びて時にこれを習う、また説ばしからずや。", "author": "孔子"},
            {"text": "己の欲せざる所は人に施すこと勿れ。", "author": "孔子"},
            {"text": "人を見て法を説け。", "author": "釈迦"},
            {"text": "七転び八起き。", "author": "日本のことわざ"},
            {"text": "初心忘るべからず。", "author": "世阿弥"},
            {"text": "われ思う、ゆえにわれあり。", "author": "デカルト"},
            {"text": "人間は考える葦である。", "author": "パスカル"},
            {"text": "万物は流転する。", "author": "ヘラクレイトス"},
            {"text": "無知の知。", "author": "ソクラテス"},
            {"text": "人間万事塞翁が馬。", "author": "中国のことわざ"},
            {"text": "雨垂れ石を穿つ。", "author": "日本のことわざ"},
            {"text": "虎穴に入らずんば虎子を得ず。", "author": "中国のことわざ"},
            {"text": "生きるとは呼吸することではない。行動することだ。", "author": "ルソー"},
            {"text": "人は城、人は石垣、人は堀。", "author": "武田信玄"},
            {"text": "敵を知り己を知れば百戦危うからず。", "author": "孫子"},
        ]
        print("💬 Quotes Harvester Initialized.")
    
    def get_random_quote(self) -> HarvestedContent:
        """ランダムな名言を取得"""
        quote = random.choice(self.quotes)
        return HarvestedContent(
            source=SourceType.QUOTES,
            title=quote["author"],
            content=quote["text"],
            metadata={"type": "quote"}
        )


class WeatherHarvester:
    """
    天気情報を取得（OpenWeatherMap または wttr.in）
    """
    
    def __init__(self, city: str = "Tokyo"):
        self.city = city
        self.api_url = f"https://wttr.in/{city}?format=j1"
        print(f"🌤️ Weather Harvester Initialized ({city}).")
    
    def get_weather(self) -> Optional[HarvestedContent]:
        """現在の天気を取得"""
        try:
            req = urllib.request.Request(
                self.api_url,
                headers={'User-Agent': 'Kaname/1.0'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            current = data.get("current_condition", [{}])[0]
            
            temp = current.get("temp_C", "?")
            humidity = current.get("humidity", "?")
            desc = current.get("weatherDesc", [{}])[0].get("value", "")
            
            content = f"現在の{self.city}の天気: {desc}, 気温{temp}°C, 湿度{humidity}%"
            
            return HarvestedContent(
                source=SourceType.WEATHER,
                title=f"{self.city}の天気",
                content=content,
                metadata={
                    "temp": temp,
                    "humidity": humidity,
                    "desc": desc
                }
            )
        except Exception as e:
            print(f"⚠️ Weather harvest failed: {e}")
            return None


class RSSHarvester:
    """
    RSSフィードから記事を取得
    """
    
    def __init__(self):
        self.feeds = [
            ("はてなブックマーク", "https://b.hatena.ne.jp/hotentry/it.rss"),
            ("ITmedia", "https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml"),
        ]
        print("📡 RSS Harvester Initialized.")
    
    def get_random_article(self) -> Optional[HarvestedContent]:
        """ランダムなRSS記事を取得"""
        try:
            feed_name, feed_url = random.choice(self.feeds)
            
            req = urllib.request.Request(
                feed_url,
                headers={'User-Agent': 'Kaname/1.0'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8')
            
            # 簡易的なXMLパース（titleタグを抽出）
            titles = re.findall(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', content)
            links = re.findall(r'<link>(.*?)</link>', content)
            
            if len(titles) < 2:
                return None
            
            # 最初のtitleはフィードタイトルなのでスキップ
            idx = random.randint(1, min(10, len(titles) - 1))
            
            return HarvestedContent(
                source=SourceType.RSS,
                title=titles[idx] if idx < len(titles) else "",
                content=titles[idx] if idx < len(titles) else "",
                url=links[idx] if idx < len(links) else "",
                metadata={"feed": feed_name}
            )
        except Exception as e:
            print(f"⚠️ RSS harvest failed: {e}")
            return None


class KnowledgeHarvesterManager:
    """
    全ハーベスターを統合管理
    """
    
    def __init__(self):
        self.lock = threading.Lock()
        
        # 各ハーベスターを初期化
        self.wikipedia = WikipediaHarvester()
        self.nhk = NHKNewsHarvester()
        self.quotes = QuotesHarvester()
        self.weather = WeatherHarvester()
        self.rss = RSSHarvester()
        
        # 収集履歴
        self.history: List[HarvestedContent] = []
        
        print("🌐 Knowledge Harvester Manager Ready.")
    
    def harvest_random(self) -> Optional[HarvestedContent]:
        """
        ランダムなソースから知識を収集
        """
        sources = [
            (SourceType.WIKIPEDIA, lambda: self.wikipedia.get_random_article()),
            (SourceType.NHK_NEWS, lambda: self.nhk.get_random_news()),
            (SourceType.QUOTES, lambda: self.quotes.get_random_quote()),
            (SourceType.WEATHER, lambda: self.weather.get_weather()),
            (SourceType.RSS, lambda: self.rss.get_random_article()),
        ]
        
        # ランダムに選択
        source_type, harvester = random.choice(sources)
        
        try:
            content = harvester()
            if content:
                with self.lock:
                    self.history.append(content)
                    # 最大100件
                    if len(self.history) > 100:
                        self.history = self.history[-100:]
                
                print(f"📚 Harvested from {source_type.name}: {content.title[:30]}...")
            return content
        except Exception as e:
            print(f"⚠️ Harvest failed: {e}")
            return None
    
    def harvest_from(self, source: SourceType) -> Optional[HarvestedContent]:
        """
        指定ソースから知識を収集
        """
        harvesters = {
            SourceType.WIKIPEDIA: lambda: self.wikipedia.get_random_article(),
            SourceType.NHK_NEWS: lambda: self.nhk.get_random_news(),
            SourceType.QUOTES: lambda: self.quotes.get_random_quote(),
            SourceType.WEATHER: lambda: self.weather.get_weather(),
            SourceType.RSS: lambda: self.rss.get_random_article(),
        }
        
        if source not in harvesters:
            return None
        
        return harvesters[source]()
    
    def get_recent(self, count: int = 10) -> List[HarvestedContent]:
        """最近の収集履歴を取得"""
        with self.lock:
            return list(self.history[-count:])
    
    def get_state(self) -> Dict[str, Any]:
        """状態を取得"""
        return {
            "history_count": len(self.history),
            "sources": [s.name for s in SourceType]
        }
