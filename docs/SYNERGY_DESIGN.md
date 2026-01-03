# 技術の壁 攻略計画 - シナジー設計

## Agni 活用戦略: 「教師→卒業」モデル

Agni (Gemini API) を「永続的な依存」ではなく「一時的な教師」として位置づける。

---

## 各壁における Agni シナジー

### 壁2: 出力ボトルネック (最優先)

**現状**: LanguageCenter がテンプレートベースで「ロボットっぽい」

**Agni シナジー**:
```python
# AgniTranslator (新規)
class AgniTranslator:
    def translate_internal_state(self, hormones, concepts):
        """
        Agni に内部状態を送り、自然な日本語を生成させる。
        同時に LanguageCenter への学習サンプルとして保存。
        """
        prompt = f"""
        Kanameの現在の状態:
        - ドーパミン: {hormones['dopamine']}
        - 退屈: {hormones['boredom']}
        - 最近見たもの: {concepts}
        
        この状態のKanameが「独り言」を言うとしたら、
        どのような日本語が自然ですか？（1文、カジュアルに）
        """
        return agni.call(prompt)
```

**卒業条件**: LanguageCenter が Agni 出力の類似文を生成できるようになったら

---

### 壁4: 文脈と注意 (2番目)

**現状**: AttentionManager が文脈を無視して連想暴走

**Agni シナジー**:
```python
# AgniContextClassifier (新規)
class AgniContextClassifier:
    CONTEXTS = ["探索", "食事", "危険回避", "休息", "社交"]
    
    def classify(self, recent_concepts, hormones):
        """
        現在の文脈をAgniに分類させる。
        結果をローカルの分類器のラベルデータとして保存。
        """
        prompt = f"""
        最近の概念: {recent_concepts}
        ホルモン: {hormones}
        
        以下のどの文脈に最も近いですか？
        {self.CONTEXTS}
        """
        return agni.call(prompt)
```

**卒業条件**: ローカル分類器が90%以上の一致率

---

### 壁1: 結合問題 (3番目)

**現状**: SimHash は単純な類似度のみ

**Agni シナジー**:
```python
# AgniBindingTutor (新規)
class AgniBindingTutor:
    def generate_binding_example(self, concept_a, concept_b):
        """
        「AとBを結合するとCになる」のパターンを取得。
        """
        prompt = f"""
        概念A: {concept_a}
        概念B: {concept_b}
        
        AとBを結合した新しい概念Cは何ですか？
        例: 赤 + リンゴ = 赤いリンゴ
        """
        return agni.call(prompt)
```

**卒業条件**: 結合演算器が既知パターンを再現できる

---

### 壁3: 可塑性/安定性 (4番目)

**現状**: DreamEngine が無差別に圧縮

**Agni シナジー**:
```python
# AgniImportanceRater (新規)
class AgniImportanceRater:
    def rate_memory(self, concept, context, frequency):
        """
        記憶の重要度 (0-1) をAgniに評価させる。
        """
        prompt = f"""
        概念: {concept}
        文脈: {context}
        出現頻度: {frequency}回
        
        この記憶の重要度は？ (0.0 = 忘れてよい, 1.0 = 絶対保持)
        """
        return float(agni.call(prompt))
```

**卒業条件**: ローカル重要度判定器が同等の判断を下せる

---

## 実装順序とシナジー効果

| 順序 | 壁 | Agni シナジー | 副次効果 |
|:---:|:---|:---|:---|
| 1 | 壁2 | 言語翻訳 | Chimera Engine 品質向上 |
| 2 | 壁4 | 文脈分類 | 連想暴走防止 |
| 3 | 壁1 | 結合教育 | 概念理解の深化 |
| 4 | 壁3 | 重要度判定 | 記憶効率向上 |

---

*Generated for 技術の壁 攻略計画*
