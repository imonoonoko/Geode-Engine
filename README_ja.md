# 🪨 Geode-Engine（ジオード・エンジン）

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**地質学的記憶AI** — 脳科学と地質学にインスパイアされた実験的人工生命シミュレーション

> [!WARNING]
> **現在開発中**: このプロジェクトは初期段階の実験プロトタイプであり、最終的な目標（完全な自律的デジタル生命）にはまだ程遠い状態です。多くの機能が未完成であり、破壊的な変更が頻繁に行われる可能性があります。

[English README](README.md)

---

## 🌟 概要

Geode-Engineは、**地質学的メタファー**を用いて認知をモデル化するユニークなAIアーキテクチャです：

| コンセプト | 生物学的類似物 | 実装 |
|:---|:---|:---|
| **地質学的記憶** | 長期記憶 | 概念が堆積層のように蓄積 |
| **ホルモンシステム** | 神経調節物質 | ドーパミン、コルチゾール、セロトニンが意思決定に影響 |
| **予測符号化** | 能動的推論 | 自由エネルギー原理による知覚 |
| **夢による統合** | 睡眠 | アイドル時間中の記憶圧縮 |

---

## 🧠 アーキテクチャ

```
Geode-Engine/
├── src/
│   ├── brain_stem/      # 脳幹（コア機能）
│   │   ├── brain.py     # メインのGeodeBrainクラス
│   │   ├── motor_cortex.py
│   │   ├── sensory_cortex.py
│   │   └── dream_engine.py
│   ├── cortex/          # 記憶と認知
│   │   ├── memory.py         # 地質学的記憶 (HDC)
│   │   ├── sedimentary.py    # 長期記憶 (SQLite)
│   │   ├── knowledge_graph.py # 階層化記憶システム
│   │   ├── hdc_bridge.py     # **Phase 19: HDC-LLM Bridge**
│   │   ├── agni_translator.py # LLM統合
│   │   └── logic.py          # 推論エンジン
│   ├── body/            # ホルモンと代謝
│   │   ├── hormones.py       # 神経調節物質システム
│   │   └── metabolism.py     # 概日リズム
│   ├── senses/          # 知覚
│   │   ├── visual_bridge.py  # 視覚記憶
│   │   └── mentor.py         # Agniアクセラレータ (Gemini)
│   └── games/           # Minecraft統合
│       └── minecraft/
├── docs/                # ドキュメント
├── tests/               # ユニットテスト
└── README.md
```

---

## 🚀 クイックスタート

### 前提条件

**必須:**
- Python 3.10以上（3.11推奨）
- 8GB以上のRAM（最適なパフォーマンスには16GB推奨）
- Windows 10/11、Linux、またはmacOS

**オプション（拡張機能用）:**
- **Ollama**（ローカルLLM推論用）
  - ダウンロード: https://ollama.ai
  - 推奨モデル: `gemma2:2b` または `phi3:mini`
- **Google Gemini APIキー**（Agniアクセラレータ用）
  - 無料枠あり: https://ai.google.dev
- **Node.js 18以上**（Minecraft統合用）
  - ダウンロード: https://nodejs.org

### インストール

```bash
# 1. リポジトリをクローン
git clone https://github.com/imonoonoko/Geode-Engine.git
cd Geode-Engine

# 2. 仮想環境を作成
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. 依存関係をインストール
pip install -r requirements.txt

# 4. 環境設定
cp .env.example .env
# .env を編集して GEMINI_API_KEY を設定（オプション）

# 5. 実行
python src/brain_stem/main.py
# または起動スクリプトを使用（Windows）:
# start_geode.bat
```

---

## 🔑 主な機能

### 1. 超次元計算（HDC）
- SimHashベースの概念エンコーディング（768→1024ビット）
- KD-Treeによる効率的な類似検索

### 2. HDC-LLMブリッジ（Phase 19）🆕
- **記憶想起**: KnowledgeGraphとSedimentaryCortexから関連記憶を取得
- **G計算**: 期待自由エネルギー最小化による行動選択
- **動的プロンプト注入**: 想起した記憶でLLMプロンプトを強化
- 内部知識に基づいた文脈を考慮した会話を実現

### 3. アグニ・アクセラレータ
- Gemini APIによる知識注入
- 「教師→卒業」パラダイム（一時的な依存）

### 4. モジュール式脳アーキテクチャ
- **MotorCortex（運動野）**: 運動制御
- **SensoryCortex（感覚野）**: 視覚知覚
- **DreamEngine（夢エンジン）**: 自律思考
- **MetabolismManager（代謝管理）**: エネルギーと概日リズム

### 4. Minecraft統合
- Mineflayerベースの身体化
- 空間記憶マッピング
- 感情駆動行動

---

## 📊 設定

`src/dna/config.py` の主な設定：

| 変数 | デフォルト | 説明 |
|:---|:---|:---|
| `EDUCATION_MODE` | `False` | アグニのバックグラウンド教育を有効化 |
| `THRESHOLD_LOW` | `30.0` | 低ホルモン閾値 |
| `THRESHOLD_HIGH` | `70.0` | 高ホルモン閾値 |
| `MEMORY_SAVE_INTERVAL` | `300` | 自動保存間隔（秒） |

---

## ⚙️ 機能のオン / オフ設定

`src/dna/config.py` で各種AI機能の動作をカスタマイズできます：

| 機能 | 設定変数 | デフォルト | 説明 |
|:---|:---|:---:|:---|
| **知識注入（教育）** | `EDUCATION_MODE` | `False` | アグニ（Gemini）による知識学習の有効化 |
| **睡眠時学習** | `AGNI_HYPNOPEDIA` | `False` | 「睡眠」中も学習を継続するかどうか |
| **自動Web学習** | `MENTOR_AUTO_TEACH` | `False` | Webソース（青空文庫等）から自動で知識を収集 |
| **音声出力** | `USE_VOICE_GENERATION` | `True` | MeloTTSによる音声合成の有効化 |
| **Minecraft連携** | `self.minecraft` | `None` | (内部) Mineflayerエージェントとの通信 |

---

---

## 🧪 テスト

```bash
# 全テスト実行
python run_tests.py

# 特定のテスト
python -m pytest tests/test_motor_cortex.py -v
```

---

## 🤝 コントリビューション

コントリビューションを歓迎します！

1. リポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m '素晴らしい機能を追加'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

---

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**🧠 Geode-Engine Team 製作**
