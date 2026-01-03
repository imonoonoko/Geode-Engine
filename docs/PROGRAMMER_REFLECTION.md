# PROGRAMMER_REFLECTION.md
M.A.I.A. 開発における反省点と教訓

---

## [2026-01-01] Demon Audit 反省録

### 🔴 Issue 1: ファイル編集の自己破壊
- **発生**: `brain.py` の `VisualMemoryBridge` クラスを編集してメソッドを追加した際。
- **症状**: 正しいインデントやクラス構造を維持できず、ファイル全体が破損した。
- **原因**: 長大なファイルを `replace_file_content` で部分編集する際、コンテキストを見失った。
- **✅ Lesson**: 編集前には必ず `view_file` で行番号を確認し、**小さな単位**で編集する。

### 🔴 Issue 2: パス依存とインポートエラー
- **発生**: `tests/test_kaname_vision.py` 作成時。
- **症状**: `ModuleNotFoundError: No module named 'src'` が発生。
- **原因**: `src` 構成のプロジェクトでは `PYTHONPATH` が必須。
- **✅ Lesson**: 新しいスクリプトを作る際は、**パス依存と実行ディレクトリ**を常に意識する。

## [2026-01-03] Phase 6 Sleep & Consolidation

### 🔴 Issue 3: Missing Synergy (Synaptic-Geological Disconnect)
- **発生**: Phase 6 設計段階
- **症状**: 「経験」を司るシナプス結合と、「世界観」を司る地質学的記憶が連携しておらず、人格形成が不十分だった。
- **原因**: 独立したモジュールとして作ることに集中しすぎて、**有機的な結合**（特に睡眠時の同期プロセス）を見落としていた。
- **✅ Lesson**: 脳科学的なアーキテクチャでは、**睡眠時処理（Offline Processing）** こそがシステムの統合（Consolidation）の主役であると認識する。

## [2026-01-03] Phase 11 Demon Audit
### 🔴 Issue 4: Magic Numbers in GameBrain
- **発生**: MinecraftBrain (`game_brain.py`) 実装時。
- **症状**: 多数の閾値 (`20.0`, `15.0`) や距離定数がコード内に散乱していた。
- **原因**: 急速なプロトタイピング優先で、設定ファイルへの抽出を後回しにした。
- **✅ Lesson**: AIの行動パラメータは **チューニングの要** であるため、最初から `config.py` に定義すべき。 (`MC_BOREDOM_THRESHOLD` 等へリファクタリング済み)

## [2026-01-04] Demon Audit (Phase 2)
### 🔴 Issue 5: Stubbed Safety Logic (Mock Hazard)
- **発生**: `SedimentaryCortex` の `Metamorphic Compression` 追加時。
- **症状**: `_get_fragment_valence` が常に `0.0` を返しており、**Valence Safeguard (感情保護)** が機能していなかった。
- **原因**: 急ピッチな実装時に「後で作る」としてプレースホルダ(`return 0.0`)を残したまま忘れていた。
- **✅ Lesson**: 安全装置(Safeguard)に関わるメソッドには、スタブ状態であっても**明示的な警告ログ**か**TODOコメント**を埋め込み、Demon Auditで必ず回収する。

### 🔴 Issue 6: Async Speech Logic Bug
- **発生**: `Chimera Language Engine` (Phase 5) 統合後、`brain.py` の非同期発話スレッドにて。
- **症状**: `soliloquy` が生成したテキスト (`impulse_ir["text"]`) があるにも関わらず、`_async_speak_task` がそれを無視して、断片 (`fragments`) から再構築しようとしていた（結果、空文字や意図しない発話になる可能性）。
- **原因**: `impulse_ir` のキー優先順位のロジック不備。`text` キーが存在する場合の処理が抜けていた。
- **✅ Lesson**: データの受け渡し構造 (`impulse_ir` dict) を変更した際は、**受信側の全ロジック** (`_async_speak_task`) を必ずトレースして整合性を確認する。

### 🔴 Issue 7: Stray Markup in Code
- **発生**: `src/body/body_interface.py` の修正時。
- **症状**: ファイル末尾に Markdown のコードブロック終了記号 (```) が混入し、`SyntaxError` を引き起こした。
- **原因**: `replace_file_content` 使用時に、エージェントが提示したコードブロックの枠を誤ってコンテンツに含めてしまった。または、前のツール出力のコピペミス。
- **✅ Lesson**: コード編集後は必ず `py_compile` (構文チェック) を走らせ、単純な記号混入がないか機械的に保証する。ツール任せにせず、自分の目で一度 `view_file` で確認する癖をつける。

### 🔴 Issue 8: NumPy Deprecation (np.float_)
- **発生**: `maya_synapse.py` の `mypy` チェック時。
- **症状**: `Module has no attribute "float_"` エラー。
- **原因**: NumPy 1.24以降で `np.float_` エイリアスが削除されたため。
- **✅ Lesson**: Pythonの型ヒントには `float` または `np.float64` を明示的に使用し、古いエイリアスに依存しない。

### 🔴 Issue 9: Type Hint Inconsistency
- **発生**: `body_interface.py` の `mypy` チェック時。
- **症状**: `Incompatible default for argument "body_impl"`。
- **原因**: 引数のデフォルト値が `None` なのに、型ヒントが `Optional` になっていなかった。
- **✅ Lesson**: `None` をデフォルトにする場合は必ず `Optional[Type] = None` と書く。

### 🔴 Issue 10: Test Port Conflict
- **発生**: `run_tests.py` 実行時（バックグラウンドで `node bot.js` が稼働中）。
- **症状**: ポート8080-8084が埋まっており、テスト用サーバーが立ち上がらずテスト失敗。
- **原因**: テストコードが本番と同じ固定ポートを使おうとした。
- **✅ Lesson**: 統合テストでは、**動的ポート割り当て**を行うか、**ネットワーク層をモック**して、稼働中の環境と衝突しないようにする。

### 🔴 Issue 11: NameError (h_term)
- **発生**: `test_phase12_personality.py` 実行時。
- **症状**: `NameError: name 'h_term' is not defined`.
- **原因**: リファクタリング時に古い変数の参照行を削除し忘れた。
- **✅ Lesson**: 変更後は `py_compile` に加えて、必ず**影響範囲の最小テスト**を実行してからコミットする。

### 🔴 Issue 12: Mypy Errors (BodyHAL & ActionController)
- **発生**: `mypy` スキャン時。
- **症状**: `BodyHAL` attribute missing, `Optional` types mismatch.
- **原因**: 動的言語の柔軟さに頼り、初期化(`__init__`)を疎かにしていた。
- **✅ Lesson**: クラス属性は**必ず** `__init__` で定義する。デフォルト引数 `None` には `Optional` をつける。

### 🔴 Issue 13: KanameBody Float/Int Mismatch
- **発生**: `mypy` スキャン時。
- **症状**: `Incompatible types in assignment (float -> int)`.
- **原因**: 変数 `max_move` を `0` (int) で初期化したが、実際は `float` が代入された。
- **✅ Lesson**: 数値変数の初期化時は型を意識する (`0.0` vs `0`)。

## [2026-01-04] Phase 16 Demon Audit

### 🔴 Issue 12: Test Assertion Mismatch
- **発生**: `tests/test_vision.py` 実行時。
- **症状**: `assert_any_call(Hormone.DOPAMINE, 10.0)` が失敗 (actual: 30)。
- **原因**: `MC_INNATE_EMOTIONS` の値がコード更新時にテストに反映されていなかった。
- **✅ Lesson**: 定数値を変更したら、**関連テストも同時に更新**する。grep で `assert.*Hormone` を確認。
