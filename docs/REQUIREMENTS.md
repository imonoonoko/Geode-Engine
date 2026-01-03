# Kaname システム要件定義書 (Requirements Specification)

## 1. システム概要
Kanameは、Echo State Network (ESN) と自由エネルギー原理 (FEP) を組み合わせた、自律成長型の人工知能エージェントです。外部データからの概念学習、感情シミュレーション、および自己保存本能を有します。

## 2. 動作環境 (Environment)

### ハードウェア要件 (Recommended)
| コンポーネント | 要件 | 備考 |
|---|---|---|
| **CPU** | 4コア以上 | マルチスレッド処理 (推論・学習・感情) のため推奨 |
| **Memory (RAM)** | 8GB 以上 | リザーバ計算、大規模テキスト処理、概念グラフの保持に必要 |
| **Storage** | SSD 推奨 | 頻繁なSQLiteアクセスとログ書き込みが発生するため |
| **Network** | インターネット接続 | 青空文庫からの自動データ収集に必要 |

### ソフトウェア要件
- **OS**: Windows 10/11, macOS, Linux
- **Python**: Version 3.10 以上

### 依存ライブラリ (Python Dependencies)
- `numpy`: 行列演算、ESN計算
- `networkx`: 概念グラフの構築・操作
- `matplotlib`: 状態の可視化 (任意)
- `requests`: Webデータ取得 (青空文庫)
- `typing`: 型ヒント
- `sqlite3`: (標準ライブラリ) 長期記憶データベース

---

## 3. 機能要件 (Functional Requirements)

### 3.1 脳幹・身体システム (Body & Brain Stem)
- **ホルモン調節**: ドーパミン、コルチゾール等の分泌と半減期シミュレーション。
- **恒常性維持**: エネルギー(Glucose)と覚醒度(Arousal)のバランス維持。
- **データ摂取 (Feeder)**: ローカルファイルおよびWebからのテキストデータ取得。

### 3.2 大脳皮質システム (Cortex)
- **予測エンジン (PredictionEngine)**: ESNを用いた時系列データの予測と、予測誤差(Surprise)の算出。
- **概念学習 (ConceptLearner)**: テキストからのキーワード抽出と、意味的結合の形成。
- **人格系 (PersonalityField)**: 現在の内部状態のスナップショット取得と、状態分岐(Bifurcation)の検出。
- **記憶システム (Hippocampus)**: 短期記憶から長期記憶への転送と、SQLデータベースへの永続化。

### 3.3 自律性 (Autonomy)
- **退屈トリガー**: 退屈度が閾値を超えた際、ユーザーの介在なしに自ら情報を探索・取得する機能。
- **睡眠サイクル**: 定期的なスリープモード移行によるメモリ整理と学習パラメータの最適化。

---

## 4. 非機能要件 (Non-Functional Requirements)

- **安定性 (Stability)**: リザーバ計算のスペクトル半径を制御し、感情値の発散を防ぐ (Lyapunov安定性の確保)。
- **拡張性 (Extensibility)**: 新しい感覚モジュールや出力モジュールを追加しやすいモジュラー設計。
- **永続性 (Persistence)**: プロセス終了後も学習内容と人格状態が保持されること。

---

## 5. ディレクトリ構成
```text
project_root/
├── src/
│   ├── brain_stem/   # 脳幹・統合制御
│   ├── body/         # 身体・入出力・ホルモン
│   └── cortex/       # 皮質・推論・記憶・人格
├── docs/             # ドキュメント
├── food/             # 食料入力フォルダ
├── memory_data/      # 記憶データ (SQLite, Logs)
└── start_kaname.bat  # 起動スクリプト
```
