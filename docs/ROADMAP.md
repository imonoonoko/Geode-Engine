# Roadmap: 究極の地質学的知性

## 🏁 Phase 1: Gatekeeper ✅
予測符号化フィルタでAgniからの洪水を制御。

## 🧠 Phase 2: Semantic Brain
### 2.1: Semantic Upgrade ✅
*   `PredictionEngine` を 768次元 Gemini Embedding 対応に改修。
*   検証済み: 犬-子犬 類似度 > 犬-車 類似度

### 2.2: Metamorphic Compression ⏳ (実装中)
*   堆積記憶の80%トリガーでクラスタリング＆圧縮。
*   Leader Algorithm (NumPy, 1パス)

### 2.3: Embedding Cache 📋 (計画)
*   **Gemini3助言**: APIレイテンシ対策。直近の埋め込みをキャッシュ（LRU 1000件）。

---

## 🔮 Phase 3: HDC (Holographic Bedrock)
*   SimHash でベクトルをバイナリ化 (768 float → 1024 bit)。
*   グリッド容量: 100万セル → 約128MB。

## 🌲 Phase 4: KD-Tree Spatial Index
*   **Gemini3助言**: `scipy.spatial.KDTree` で半径検索を O(log N) に高速化。
*   睡眠時にツリー構築、起動時はロード。

## 🗣️ Phase 5: Slot-Filling Language ✅
*   構文テンプレート＋ホルモン選択＋スロット埋めで、LLMなしで文法生成。
*   検証済み: 怒り/平静/好奇心のテンプレート切り替え。

## 🧬 Phase 12: Self-Reference (The Soul) ⏳
*   **12.1 Non-Linear Personality**:
    *   Lyapunov安定性を持つ感情自己参照ループ (`hormones.py`).
    *   個体固有の「性格（平衡点）」を定義。
*   **12.2 Grounded Language**:
    *   `LanguageCenter` と `Soliloquy` の統合。
    *   「今の気分」ではなく「性格バネの歪み」を言語化する。

## 👁️ Phase 14: Retina & Visual Attention (Minecraft Vision) 📋
*   **14.1 Mineflayer Integration**:
    *   Minecraft Java Edition に `mineflayer` ボットで接続。
    *   `prismarine-viewer` でボット視界をブラウザ表示。
*   **14.2 Block/Entity Perception**:
    *   前方ブロック/エンティティをスキャン → 日本語翻訳 → 記憶。
    *   ダイヤ発見 → Dopamine / 溶岩発見 → Cortisol の感情マッピング。
*   **14.3 Spatial Memory**:
    *   「どこに何があったか」を座標付きで記憶。

## 🧩 Phase 15: Brain Modularization (God Object分離) 📋
*   **15.1 MotorCortex 分離**:
    *   運動制御ロジックを `motor_cortex.py` に分離。
    *   依存性注入 (DI) で循環参照を回避。
*   **15.2 SensoryCortex 分離**:
    *   感覚処理を `sensory_cortex.py` に分離。
*   **15.3 DreamEngine 分離**:
    *   夢/自律思考を `dream_engine.py` に分離。
*   **15.4 MetabolismManager 分離**:
    *   代謝処理を `metabolism.py` に分離。

## 🗣️ Phase 16: 壁2 - 出力ボトルネック攻略 📋
*   **AgniTranslator**: 内部状態→自然文の翻訳
*   **LanguageCenter v2**: パターン学習で出力多様化
*   **卒業条件**: Agni依存率 < 20%

## 🎯 Phase 17: 壁4 - 文脈と注意攻略 📋
*   **ContextBuffer**: 直近N概念の保持
*   **ContextClassifier**: 文脈ラベル分類
*   **AssociationGate**: 連想暴走防止

## 🔗 Phase 18: 壁1 - 結合問題攻略 📋
*   **BindingOperator**: XOR + 置換行列
*   **AgniBindingTutor**: 結合パターン学習
*   **可逆結合**: A ⊕ B ⊕ B = A

## 💤 Phase 19: 壁3 - 可塑性/安定性攻略 📋
*   **ImportanceClassifier**: 記憶重要度判定
*   **SelectiveConsolidation**: 選択的記憶固定
*   **卒業条件**: 重要記憶残存率 > 80%

---

## 🚨 撤退基準 (Circuit Breaker)
| トリガー | アクション |
| :--- | :--- |
| API Error 連発 | Hash Fallback (実装済み) |
| RAM +200MB 超 | バイナリ化 (Phase 3) を前倒し |
| 実装工数 超過 | 該当フェーズを単純化 or 延期 |

