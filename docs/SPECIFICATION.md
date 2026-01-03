# M.A.I.A. Core (Kaname) 仕様書 v2.0 (Anatomical)

## 概要
生物学的構造（解剖学的アーキテクチャ）を持つ自律型AI生命体「カナメ」。
従来の「コマンド応答型」ではなく、**「代謝」「循環」「成長」**といった生命活動を通じて、ユーザーと長期的な関係を築くことを主眼とする。

---

## アーキテクチャ (Anatomical Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                 M.A.I.A. Anatomical Core                   │
│         (Mind Augmentation Interface Architect)             │
├─────────┬──────────────┬───────────────────┬────────────────┤
│ 🧬 DNA  │ 🧠 BrainStem │ 🏛️ Cortex         │ 🦾 Body       │
│ Config  │ Life Support │ Memory & Logic    │ Metabolism     │
└────┬────┴───────┬──────┴─────────┬─────────┴────────┬───────┘
     │            │                │                  │
     │      ┌─────▼─────┐    ┌─────▼─────┐      ┌─────▼─────┐
     └─────>│ 👁️ Senses │<──┤ 🦠 Cells  ├──>   │ 🛠️ Tools  │
            │ Input/YOLO│    │ Neuron    │      │ Atlas/Tele│
            └───────────┘    └───────────┘      └───────────┘
```

---

## 1. 脳幹・生理機能 (Brain Stem & DNA)
システムの生命維持装置。

### 1.1 DNA (`src/dna/config.py`)
- 全システムの設定、パス、定数を一元管理。
- **遺伝子定義**: ホルモンの半減期、性格パラメータ、色の定義など。

### 1.2 脳幹 (`src/brain_stem/`)
- **Main Loop (`main.py`)**: 覚醒・睡眠サイクル、スレッド管理、エラーハンドリング。
- **Brain (`brain.py`)**: 各臓器（モジュール）のオーケストレーション。自律思考サイクルの実行。
- **Attention (`attention_manager.py`)**: 視覚・聴覚情報の優先順位付けとフィルタリング。

---

## 2. 大脳皮質・記憶 (Cortex)
高度な認知機能と長期記憶。

### 2.1 地質学的記憶 (`src/cortex/memory.py`)
- **GeologicalMemory**: 1024x1024 の感情地形マップ。
- **感情テラフォーミング**: 感情の強度が「標高」となり、記憶の重要度を物理的に表現する。

### 2.2 堆積言語野 (`src/cortex/sedimentary.py`)
- **SedimentaryCortex**: 記憶を地層として積み重ねる。
- **化石化**: 古い記憶は圧縮され、抽象的な「信念」へと変化する。

### 2.3 海馬・意味記憶 (`src/cortex/hippocampus.py`)
- **SentenceTransformers**: テキストをベクトル化し、意味的な類似度で検索。
- **役割**: 文脈に応じた過去の記憶の想起（RAG）。

### 2.4 概念学習 (`src/cortex/concept_learner.py`)
- 未知の物体（YOLOタグ）とユーザーの言葉を結びつけ、新しい概念を学習する。

---

## 3. 感覚・知覚 (Senses)
外界情報の入力処理。

### 3.1 視覚野 (`src/senses/visual_bridge.py`)
- **Retina**: 画面全体のキャプチャと周辺視野（低解像度）/中心視野（高解像度）の処理。
- **VisualMemoryBridge**: YOLOv8を用いて物体を認識し、それを言語タグ（例: "cup" -> "コップ"）に変換して記憶・学習系に送る。

### 3.2 視床 (`src/senses/kaname_senses.py`)
- インプット情報の統合ハブ。

---

## 4. 身体・代謝 (Body)
物理的な実体と内部状態。

### 4.1 運動野 (`src/body/kaname_body.py`)
- **Ghost UI**: 透過ウィンドウによるキャラクター表示。
- **物理演算**: バネ・ダンパモデルによる滑らかな移動。

### 4.2 自律神経 (`src/body/biorhythm.py`)
- **ホルモン分泌**: ドーパミン、セロトニン、コルチゾール等の分泌と半減期シミュレーション。
- **概日リズム**: 時間帯によるテンションの変化。

### 4.3 免疫系 (`src/body/immune.py`)
- エラーが発生してもシステム全体をクラッシュさせず、局所的に回復させる。

### 4.4 声帯 (`src/body/throat.py`)
- **MeloTTS**: 高品質な日本語音声合成。

---

## 5. ツール (Tools)
- **Atlas Generator (`src/tools/generate_atlas.py`)**: ソースコードから `docs/FUNCTION_ATLAS.md` を自動生成。
- **Telemetry (`src/tools/telemetry_server.py`)**: WebSocketによる内部状態の可視化サーバー。

---

## 6. 起動方法

```bash
python -m src.brain_stem.main
```
または
```bash
##_start.bat
```

---

## 7. ディレクトリ構造

| ディレクトリ | 役割 |
| :--- | :--- |
| `src/dna` | 設定・定数 |
| `src/brain_stem` | コアロジック・メインループ |
| `src/cortex` | 記憶・推論・学習 |
| `src/senses` | 入力・認識 (YOLO) |
| `src/body` | 出力・UI・代謝 |
| `src/cells` | 基本データ構造 (Neuron) |
| `src/tools` | 補助ツール |
| `models/` | AIモデルファイル (yolov8n.pt) |
| `docs/` | ドキュメント群 |
| `memory_data/` | 永続化された記憶データ |
