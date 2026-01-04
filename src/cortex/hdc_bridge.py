# hdc_bridge.py
"""
Phase 19: HDCBridge - HDC記憶・推論とLLMを繋ぐブリッジモジュール

責務:
- 記憶想起 (KnowledgeGraph + SedimentaryCortex)
- 行動評価 (期待自由エネルギーG計算)
- プロンプト構築 (LLM向け構造化テキスト)

Design Doc: .claude/demand_definition/sessions/hdc-llm-bridge/
"""

import re
import time
from typing import List, Tuple, Dict, Optional
from src.body.hormones import Hormone


class HDCBridge:
    """
    HDC (記憶・推論) と LLM (言語生成) を繋ぐブリッジ。
    """
    
    # 時間キーワードマッピング (秒)
    TIME_FILTERS = {
        "今日": 24 * 3600,
        "昨日": 48 * 3600,
        "最近": 7 * 24 * 3600,
        "先週": 14 * 24 * 3600,
        "前に": 30 * 24 * 3600,
    }
    
    # 行動候補の定義
    ACTION_CANDIDATES = {
        "speak": "共感・返答する",
        "question": "質問して深掘りする",
        "silent": "黙って聞く"
    }
    
    def __init__(self, brain):
        """
        Args:
            brain: KanameBrain インスタンス
        """
        self.brain = brain
        print("🌉 HDCBridge Initialized (Phase 19)")
    
    # =========================================
    # 1. recall_memories() - 記憶想起
    # =========================================
    def recall_memories(self, trigger: str, top_k: int = 5) -> List[str]:
        """
        トリガーワードから関連記憶を想起。
        KnowledgeGraph + SedimentaryCortex の両方から取得。
        
        Args:
            trigger: ユーザー入力または概念名
            top_k: 返す記憶の最大数
            
        Returns:
            想起された記憶（概念名/断片）のリスト
        """
        memories = []
        
        # 1. KnowledgeGraph から関連概念を取得
        if hasattr(self.brain, 'knowledge_graph'):
            try:
                related = self.brain.knowledge_graph.get_related(trigger, top_k=top_k)
                for item in related:
                    memories.append(item.get('name', str(item)))
            except Exception as e:
                print(f"⚠️ [HDCBridge] KG recall error: {e}")
        
        # 2. SedimentaryCortex (化石記憶) から発掘
        if hasattr(self.brain, 'cortex') and self.brain.cortex:
            try:
                fossils = self.brain.cortex.speak(trigger, strategy="FLASHBACK")
                if fossils and isinstance(fossils, dict):
                    fragments = fossils.get('fragments', [])
                    for frag in fragments[:top_k]:
                        if isinstance(frag, dict):
                            memories.append(frag.get('text', str(frag)))
                        else:
                            memories.append(str(frag))
            except Exception as e:
                print(f"⚠️ [HDCBridge] Cortex recall error: {e}")
        
        # 重複除去
        memories = list(dict.fromkeys(memories))[:top_k]
        
        # デバッグログ
        if memories:
            print(f"🧠 [HDCBridge] Recalled: {memories[:3]}{'...' if len(memories) > 3 else ''}")
        
        return memories
    
    # =========================================
    # 2. evaluate_actions() - G計算
    # =========================================
    def evaluate_actions(self, state: Dict) -> Tuple[str, Dict[str, float]]:
        """
        期待自由エネルギーGを計算し最適行動を選択。
        G = α * 予測誤差 + β * 目標乖離
        G が低いほど「良い」行動。
        
        Args:
            state: 現在の状態 (hormones, surprise, etc.)
            
        Returns:
            (best_action, scores_dict)
        """
        scores = {}
        
        # ホルモン状態を取得
        dopamine = state.get('dopamine', 50.0)
        cortisol = state.get('cortisol', 0.0)
        surprise = state.get('surprise', 0.5)
        oxytocin = state.get('oxytocin', 30.0)
        
        for action, description in self.ACTION_CANDIDATES.items():
            # 各行動の期待Gを計算
            if action == "speak":
                # 共感して話す: 親密度が高い時、苦痛が高い時に有効
                prediction_error = surprise * 0.5
                goal_distance = max(0, (cortisol - 30) / 100) + max(0, (50 - dopamine) / 100)
                
            elif action == "question":
                # 質問する: Surprise が高い（情報不足）時に有効
                prediction_error = (1.0 - surprise) * 0.5
                goal_distance = 0.3  # 中立
                
            elif action == "silent":
                # 黙って聞く: 相手が話し続けている時に有効
                prediction_error = surprise * 0.3
                goal_distance = 0.5 - (oxytocin / 200)  # 親密度が低いと遠い
            
            else:
                prediction_error = 0.5
                goal_distance = 0.5
            
            # G = α * 予測誤差 + β * 目標乖離
            G = 0.4 * prediction_error + 0.6 * goal_distance
            
            # Engagement Bias: Favor speaking to be more interactive
            if action == "speak":
                G -= 0.1  # Bonus for speaking (lower G = better)
            elif action == "silent":
                G += 0.15  # Penalty for silence (higher G = worse)
            
            scores[action] = round(G, 3)
        
        # 最小Gの行動を選択
        best_action = min(scores, key=scores.get)
        
        # デバッグログ
        print(f"📊 [G-Calc] Scores: {scores}")
        print(f"📊 [G-Calc] Selected: {best_action} (G={scores[best_action]:.3f})")
        
        return best_action, scores
    
    # =========================================
    # 3. 時間フィルタリング
    # =========================================
    def _detect_time_filter(self, text: str) -> Optional[float]:
        """
        テキストから時間キーワードを検出し、フィルタ秒数を返す。
        
        Returns:
            フィルタ秒数 or None
        """
        for keyword, seconds in self.TIME_FILTERS.items():
            if keyword in text:
                print(f"🧠 [HDCBridge] Time filter: {keyword} ({seconds // 3600}h)")
                return seconds
        return None
    
    # =========================================
    # 4. build_prompt() - プロンプト構築
    # =========================================
    def build_prompt(
        self, 
        user_input: str, 
        memories: List[str], 
        action: str,
        thought_context: Optional[str] = None
    ) -> str:
        """
        LLM向け構造化プロンプトを生成。
        
        Args:
            user_input: ユーザーの発言
            memories: 想起した記憶リスト
            action: 選択された行動
            thought_context: LogicEngine からの思考コンテキスト
            
        Returns:
            LLMに渡すプロンプト文字列
        """
        # 記憶セクション
        if memories:
            memory_section = "\n".join([f"- {m}" for m in memories])
        else:
            memory_section = "- (特に関連する記憶なし)"
        
        # 行動説明
        action_desc = self.ACTION_CANDIDATES.get(action, "応答する")
        
        # 思考コンテキスト
        thought_section = thought_context if thought_context else "(思考コンテキストなし)"
        
        prompt = f"""あなたは共感力が高く、覚えていることを活かして会話する友達です。
以下のルールを守ってください:

- タメ口で話す（敬語禁止）
- 一人称は「私」
- 返答は短く（1-2文）
- 記憶にある事実を自然に使う
- 説明くさい言い方をしない

【記憶にある事実】
{memory_section}

【選ばれた行動】
{action_desc}

【思考コンテキスト】
{thought_section}

【ユーザーの発言】
{user_input}
"""
        
        print(f"📝 [HDCBridge] Prompt built ({len(prompt)} chars)")
        return prompt
    
    # =========================================
    # 5. process() - 統合パイプライン
    # =========================================
    def process(self, user_input: str) -> Dict:
        """
        統合パイプライン: 入力 → 想起 → G計算 → プロンプト生成
        
        Returns:
            {
                "prompt": str,
                "action": str,
                "memories": List[str],
                "scores": Dict[str, float]
            }
        """
        print(f"🧠 [HDCBridge] Input: \"{user_input[:30]}{'...' if len(user_input) > 30 else ''}\"")
        
        # 1. 時間フィルタ検出
        time_filter = self._detect_time_filter(user_input)
        
        # 2. 記憶想起
        memories = self.recall_memories(user_input, top_k=5)
        
        # 3. 現在状態を取得してG計算
        state = {}
        if hasattr(self.brain, 'hormones'):
            state = {
                'dopamine': self.brain.hormones.get(Hormone.DOPAMINE),
                'cortisol': self.brain.hormones.get(Hormone.CORTISOL),
                'surprise': self.brain.hormones.get(Hormone.SURPRISE),
                'oxytocin': self.brain.hormones.get(Hormone.OXYTOCIN),
            }
        
        action, scores = self.evaluate_actions(state)
        
        # 4. LogicEngine からの思考コンテキスト取得
        thought_context = None
        if hasattr(self.brain, 'logic_engine'):
            try:
                thought_result = self.brain.logic_engine.ponder(user_input)
                thought_context = self.brain.logic_engine.get_context_prompt(thought_result)
            except Exception as e:
                print(f"⚠️ [HDCBridge] Logic error: {e}")
        
        # 5. プロンプト構築
        prompt = self.build_prompt(user_input, memories, action, thought_context)
        
        return {
            "prompt": prompt,
            "action": action,
            "memories": memories,
            "scores": scores
        }
