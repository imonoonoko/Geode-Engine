# M.A.I.A. 技術仕様書 v2.1 (Anatomical Structure)
**Mind Augmentation Interface Architect - Project Kaname**

> "プログラムではなく、同居人を作る"

---

## 1. プロジェクトの意図 (Philosophy)
(v2.0と同様)

---

## 2. アーキテクチャ概要

### 2.1 システム構成 (Directory Structure)
```
src/
 ├── dna/ (Config)
 ├── brain_stem/ (Core, Main Loop)
 ├── cortex/ (Memory, Logic, Inference)
 ├── senses/ (Input, YOLO, VisualBridge)
 ├── body/ (UI, Physics, Metabolism)
 └── cells/ (Neuron Model)
```

### 2.2 モジュール詳細
#### `src/brain_stem/brain.py` - 中枢神経系
*   **KanameBrain**: 全臓器のオーケストレーター。
*   **AttentionManager**: 興味に基づいた視覚・行動制御。

#### `src/cortex/sedimentary.py` - 堆積大脳皮質
*   **Sedimentation**: 地層としての記憶保存。
*   **SynapticStomach**: テキストの消化（グラフ化）と吸収。
    *   **Dream Rehearsal**: 睡眠時にランダムな結合強化を行い、忘却を防ぐ。

#### `src/cortex/inference.py` - 推論エンジン
*   **Active Inference**: 予測誤差（Surprise）の最小化による行動決定。

#### `src/senses/visual_bridge.py` - 視覚野
*   **YOLOv8**: 物体認識 (`models/yolov8n.pt`).
*   **Concept Activation**: 見た物体を言語タグとして記憶へ送る。

#### `src/body/kaname_body.py` - 身体 (Ghost UI)
*   **TkinterDnD**: ドラッグ＆ドロップによる「摂食」に対応。
*   **Digital Respiration**: ホルモン状態と同期した呼吸アニメーション。
*   **Metamorphosis**: 右クリックによるConfigホットリロード機能。

---

## 3. データフロー
(v2.0の概念を維持しつつ、パス結合を強化)

### 3.1 摂食フロー (Feeding)
1.  **Drag & Drop**: `kaname_body.py` がファイルを受け取る。
2.  **Eating**: `feeder` または `stomach` がテキストを分解。
3.  **Digestion**: 単語間の共起関係をグラフ（シナプス）として強化。
4.  **Metabolism**: 血糖値 (Glucose) 上昇、ドーパミン分泌。

---

## 4. 品質保証
**Anatomical Refactoring (Phase 6.5)** により、機能ごとのモジュール分割が完了。
`src/` 以下に整理され、循環参照リスクが低減された。

---

**Version**: 2.1 (Anatomical Structure Update)
**Updates**: Corrected file paths (`src/`), added YOLO/DnD details.
