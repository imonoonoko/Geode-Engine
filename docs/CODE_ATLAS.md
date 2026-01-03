# CODE_ATLAS.md

## 🗺️ プロジェクト・マップ

### 🧠 Brain / Docs
- `PROJECT_MANIFEST.md`: プロジェクトの憲法と概要。
- `ANALYSIS_REPORT.md`: 統合AIの現状分析レポート (Deep Dive & Resonance Integrated)。
- `DEPENDENCY_MAP.md`: モジュール間の依存関係。
- `SYNERGY_DESIGN.md`: 付加価値と最適化の設計。
- `VERIFICATION_PLAN.md`: 品質保証とテスト計画。
- `ROADMAP.md`: 実装ロードマップと撤退基準。
- `PROGRAMMER_REFLECTION.md`: 開発中の教訓と自己省察の記録。
- `HUMANIZATION_ROADMAP.md`: 人間化フェーズの詳細計画。
- `EMOTIONAL_DIGESTION_PLAN.md`: 感情消化（記憶＝栄養）の実装計画。

### 📦 Source Code (Anatomical Architecture)
**Source Root**: `src/`

#### 🧬 `src/dna` (Genetics & Config)
- `config.py`: **[設定]** 全システムの定数、パス、パラメータ管理。

#### 🧠 `src/brain_stem` (Core Life Support)
- `main.py`: **[オーケストレーター]** システム起動、ループ制御、スレッド管理。
- `brain.py`: **[中枢統合]** `KanameBrain`。各器官の調整、思考ループの実行。
- `attention_manager.py`: **[注意制御]** 入力情報のフィルタリングと優先順位付け。

#### 🏛️ `src/cortex` (Memory & Logic)
- `memory.py`: **[海馬]** `GeologicalMemory`。地質学的記憶システム、長期記憶の保存と検索。
- `sedimentary.py`: **[堆積岩皮質]** `SedimentaryCortex`。発話生成と記憶発掘。
- `soliloquy.py`: **[うわ言]** `SoliloquyManager`。能動的推論ベースの自律発話システム (Phase 24: 言語化強制)。
- `inference.py`: **[前頭葉]** `PredictionEngine`。能動的推論、未来予測、驚きの最小化。
- `concept_learner.py`: **[学習中枢]** `ConceptLearner`。未知の概念の学習と獲得。
- `hippocampus.py`: **[意味記憶]** `Hippocampus`。ベクトル検索による関連記憶の想起。
- `translator.py`: **[翻訳]** 言語間の意味変換。
- `personality_field.py`: **[人格場]** 人格スナップショットと分岐検出。
- `ethics.py`: **[Phase 11: 倫理層]** `EthicsLayer`。行動制約を C(a,s) ∈ {0,1} として定義。
- `meta_learner.py`: **[Phase 13: メタ学習]** `MetaLearner`。学習率と探索率の動的調整。
- `world_model.py`: **[Phase 14: 世界モデル]** `WorldModel`。状態遷移予測と予測誤差学習。
- `identity_monitor.py`: **[Phase 15: 自己同一性]** `IdentityMonitor`。自己予測と分岐検出。
- `goal_system.py`: **[Phase 16: 目的再定義]** `GoalSystem`。目的が状態から創発。
- `memory_distortion.py`: **[Phase 17: 記憶歪み]** `MemoryDistorter`。ネガティブバイアスと記憶再構成。
- `word_binding.py`: **[Phase 18: 言葉結合]** `WordStateBindingSystem`。言葉と状態の三項結合。
- `dreaming.py`: **[Phase 19: 夢]** `DreamProcessor`。睡眠中の記憶圧縮。
- `personality_system.py`: **[Phase 20: 人格系]** `PersonalitySystem`。複数人格の共存・競合。
- `meaning_generator.py`: **[Phase 21: 意味生成]** `MeaningGenerator`。内部整合性から意味を導出。
- `conserved_quantities.py`: **[Phase 22: 保存量]** `ConservedQuantities`。意味生成能力、自己参照密度、多様性。
- `release_monitor.py`: **[Phase 23: 手離し判定]** `ReleaseMonitor`。設計者介入の必要性判定。

#### 👁️ `src/senses` (Sensory Input)
- `kaname_senses.py`: **[視床]** `KanameSenses`。全感覚情報の統合とルーティング。
- `visual_bridge.py`: **[視覚野]** `VisualMemoryBridge`。視覚情報（YOLO）の言語化と記憶への接続。

#### 🦾 `src/body` (Physical Manifestation)
- `kaname_body.py`: **[運動野]** `KanameBody`。UI制御、物理演算、ウィンドウ操作、**[DnD摂食 / Metamorphosis]**。
- `throat.py`: **[声帯]** `KanameThroat`。発話生成（TTS）。
- `immune.py`: **[免疫系]** `KanameImmuneSystem`。エラーハンドリングと異常検知。
- `biorhythm.py`: **[自律神経]** `BioRhythm`。ホルモン分泌、サーカディアンリズム、ホメオスタシス。
- `hormones.py`: **[内分泌系]** `HormoneManager`。ホルモン状態の管理とカプセル化（The Iron Heart）。
- `events.py`: **[神経伝達]** `EventBus`。Pub/Subパターンによるモジュール間疎結合化。
- `maya_resonance.py`: **[共鳴]** `GeologicalResonance`。感情の波及効果シミュレーション。
- `maya_synapse.py`: **[消化器]** `SynapticStomach`。情報の消化と吸収、**[Dream Rehearsal (夢の反芻)]**。
- `body_interface.py`: **[神経インターフェース]** 身体制御の抽象化レイヤー。
- `feeder.py`: **[摂食]** 外部データの取り込み。

#### 🎮 `src/games` (Game AI Integration)
- `game_interface.py`: **[統合インターフェース]** ゲーム環境の抽象化レイヤー。
- `game_player.py`: **[ゲームプレイヤー]** 汎用ゲーム実行エージェント。
- `action_controller.py`: **[アクション制御]** ゲーム操作の統一インターフェース。

##### `src/games/minecraft` (Minecraft Integration)
- `mineflayer_env.py`: **[Mineflayer環境]** Node.js Mineflayer Bot とのPython Bridge。HTTP API経由でボット制御。
- `java_env.py`: **[MineRL環境]** MineRL用Java環境ラッパー（未使用）。
- `bot/bot.js`: **[Node.jsボット]** Mineflayer本体。Minecraft Protocol実装。
- `bot/package.json`: **[依存関係]** Mineflayer, pathfinder等のnpm依存。
- `manager.py`: **[Bedrock管理]** Bedrock版WebSocket接続（旧実装）。
- `action.py`: **[Bedrockアクション]** pyautogui経由のキー入力（旧実装）。

#### 🧬 `src/dna` (Genetics & Config)
- `config.py`: **[設定]** 全システムの定数、パス、パラメータ管理。
- `hormone_presets.py`: **[ホルモンプリセット]** ゲームモード用ホルモン初期値定義。

#### 🦠 `src/cells` (Basic Units)
- `neuron.py`: **[ニューロン]** 基本的な神経細胞モデル。

#### 🛠️ `src/tools` (Surgical Tools)
- `generate_atlas.py`: **[解剖図生成]** `FUNCTION_ATLAS.md` を自動生成するツール。
- `telemetry_server.py`: **[テレメトリ]** 系统状態の外部モニタリングサーバー。
- `cortex_generator.py`: **[言語生成]** RNNによるテキスト生成モデル。

#### 🧪 `tests` (Automated Tests)
- `test_hormones.py`: HormoneManager テスト。
- `test_events.py`: EventBus テスト。
- `test_soliloquy.py`: SoliloquyManager テスト。
- `test_aozora.py`: AozoraHarvester テスト。
- `test_personality.py`: PersonalityField テスト。
- `test_ethics.py`: **[Phase 11]** EthicsLayer テスト。
- `test_meta_learner.py`: **[Phase 13]** MetaLearner テスト。
- `test_world_model.py`: **[Phase 14]** WorldModel テスト。
- `test_identity_monitor.py`: **[Phase 15]** IdentityMonitor テスト。
- `test_goal_system.py`: **[Phase 16]** GoalSystem テスト。
- `test_memory_distortion.py`: **[Phase 17]** MemoryDistorter テスト。
- `run_tests.py`: **[テストランナー]** 全51テストを実行。

#### 🧠 `models` (AI Models)
- `yolov8n.pt`: **[視覚野]** 物体認識用 YOLOv8 Nano モデル。

### 🎨 Visualization
- `dashboard.html`: 2Dパラメーターモニタリング画面。
- `dashboard_3d.html`: 3D地質学的記憶ビジュアライザー (Three.js)。

### 🛠️ Legacy / Prototypes
**Location**: `archived_prototypes/`
- `old_maya_core.py`: [旧統合コア]
- `maya_voice.py`: [旧音声合成試作]
- `Emotional_Terrarium.py`: [地形変形プロトタイプ]
- `Digital_Hormone_Creature.py`: [代謝プロトタイプ]
- `PC_Life_Monitor.py`: [バイタルプロトタイプ]
- `naming_ceremony.py`: [命名儀式スクリプト]
