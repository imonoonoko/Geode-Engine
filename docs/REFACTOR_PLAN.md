# 堅牢化と拡張性のためのリファクタリング計画 (Phase 8 Proposal)

Demon Audit の反省（マジックナンバー、分散管理、スケール不整合）に基づき、以下のアーキテクチャ変更を提案します。
これにより、バグが入り込む余地をシステム的に排除し、将来の機能追加を容易にします。

---

## 🛡️ Pillar 1: 状態管理のカプセル化 (The Iron Heart)

**現状の問題**:
`brain.chemicals["dopamine"] += 10.0` のように、辞書を直接操作しているため、バリデーション（0-100制限）が効かず、スペルミスもエラーにならない。

**改善案**:
`HormoneManager` クラスを導入し、アクセスをメソッド経由に限定する。

```python
# Before (Current)
self.chemicals["dopamine"] = min(100.0, self.chemicals["dopamine"] + 10.0)

# After (Proposed)
self.hormones.add(Hormone.DOPAMINE, 10.0) 
# -> 内部で自動的に clamp(0.0, 100.0) され、ログも残る
```

### 具体的な実装イメージ
1.  **`src/body/hormones.py` の新設**:
    - `Enum` 定義: `Hormone.DOPAMINE`, `Hormone.CORTISOL` ...
    - `HormoneSystem` クラス: 値の保持、更新、減衰、クランプを一元管理。

---

## 📏 Pillar 2: 構成の一元管理と型安全性 (Strict Config)

**現状の問題**:
`min(1.0, ...)` のような数値リテラルが散在。`config.py` はあるが、強制力がない。

**改善案**:
`config` を単なる定数ファイルから、意味のあるパラメータセットに昇華させる。また、文字列キーへの依存を排除する。

```python
# Before
if self.chemicals["adrenaline"] > 60.0: ...

# After
if self.hormones.get(Hormone.ADRENALINE) > config.Threshold.EXCITEMENT: ...
```

---

## 🔌 Pillar 3: インターフェースの明確化 (Body HAL 2.0)

**現状の問題**:
`brain` が `feeder` や `immune` の内部実装を知りすぎている（密結合）。
`feeder` が `brain` の詳細を知らずにホルモンを操作しようとしてバグる。

**改善案**:
**Event-Driven (Pub/Sub) パターン** の導入（または Observer パターン）。
各モジュールは「何が起きたか」を通知するだけで、それによるホルモン変動は `Brain` 側（あるいは `HormoneManager`）が決定する。

```python
# Example: Feeder
# Before: Feederが直接脳を書き換えようとして失敗
brain.chemicals["dopamine"] += ... 

# After: Feederはイベントを発火するだけ
self.events.emit(Event.ATE_FILE, file_size=1024)
# -> Brainがイベントを購読し、適切にホルモンを分泌
```

---

## 🧪 Pillar 4: 自動テストの導入 (Safety Net)

**現状の問題**:
「動かしてみないとわからない」。修正が別の場所を壊していないか保証できない。

**改善案**:
主要ロジック（特にホルモン計算、記憶形成）に対する **Unit Test** を整備する。
GitHub Actions 等は不要だが、ローカルで `python run_tests.py` 一発で論理破綻を検知できるようにする。

---

## 実行ロードマップ

このリファクタリングは大規模になるため、段階的に実施することを推奨します。

1.  **Step 1: Hormone Enum & Manager 導入** (最も効果が高い)
    - 文字列キー `"dopamine"` をすべて `Hormone.DOPAMINE` に置換。
2.  **Step 2: Config Refactoring**
    - マジックナンバーの全排除。
3.  **Step 3: Unit Tests**
    - ホルモン計算ロジックのテスト作成。

この計画に着手しますか？
