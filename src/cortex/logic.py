import random
import time
from src.cortex.knowledge_graph import KnowledgeGraph

class LogicEngine:
    """
    Kaname's Reasoning Core.
    Traverses the KnowledgeGraph to simulate thought processes.
    """
    def __init__(self, brain):
        self.brain = brain
        # Initialize Graph and Importer
        self.graph = KnowledgeGraph()
        
        # We need to import data on startup? 
        # Ideally, we load the saved graph. KnowledgeGraph already does that in __init__.
        # But for first run, we might want to trigger import if graph is empty?
        # Leaving that to manual trigger or auto_learn for now.
        
    def ponder(self, input_text: str, depth: int = 2) -> dict:
        """
        Think about the input.
        Returns a 'Thought Object' containing the path and decision.
        """
        # 1. Entity Extraction (Simple Match)
        # Find concepts in the graph that appear in input_text
        start_nodes = []
        with self.graph.lock:
            for node in self.graph.G.nodes():
                # Simple substring match. 
                # Optimization: In real world, use Janome/MeCab or Aho-Corasick
                if node in input_text:
                    start_nodes.append(node)
        
        # Sort by length (Longer match = more specific, usually better)
        start_nodes.sort(key=len, reverse=True)
        
        if not start_nodes:
            return {"decision": None, "reason": "No known concepts found."}
        
        # Use the longest match as the anchor
        anchor = start_nodes[0]
        
        # 2. Reasoning Loop (Breadth-First Search with Emotional Evaluation)
        # For now, we just find neighbors and evaluate them.
        candidates = self.graph.get_related(anchor, top_k=5)
        
        best_candidate = None
        best_score = -999.0
        
        thought_log = []
        
        for cand in candidates:
            # Simulate: What if I focus on this concept?
            # We use PredictionEngine to predict "Surprise" or "Mood"
            # Since we don't have text for the concept, we use its name.
            
            # Predict Mood/Surprise
            sim_surprise = 0.5
            if hasattr(self.brain, 'prediction_engine'):
                sim_surprise = self.brain.prediction_engine.simulate(cand['name'], 12) # 12=noon (dummy time)
            
            # Score Algorithm:
            # Score = (Relevance * 0.7) + (Resonance * 0.3)
            # Relevance = Edge Weight
            # Resonance = 1.0 - Surprise (if Strategy=RESONATE)
            
            relevance = cand['weight'] # Typically 0.0 to 1.0 (uncapped in KG but usually small?)
            # KnowledgeGraph associate caps at 5.0, but default is 1.0. 
            # Normalize? Let's treat 1.0 as standard.
            
            # Define strategy (Restored)
            strategy = "RESONATE"
            if hasattr(self.brain, 'current_action_strategy'):
                strategy = self.brain.current_action_strategy

            resonance = 0.0
            if strategy == "RESONATE":
                resonance = 1.0 - sim_surprise 
            else: # PROBE
                resonance = sim_surprise 
                
            score = (relevance * 0.7) + (resonance * 0.3)
            
            thought_log.append({
                "concept": cand['name'],
                "relation": cand['relation'],
                "sim_surprise": sim_surprise,
                "score": score,
                "weight": relevance
            })
            
            if score > best_score:
                best_score = score
                best_candidate = cand
        
        # 3. Formulate Conclusion
        result = {
            "anchor": anchor,
            "candidates": thought_log,
            "decision": best_candidate,
            "strategy": strategy,
            "depth": depth
        }
        
        return result

    def get_context_prompt(self, thought_result: dict) -> str:
        """ Generate a prompt snippet for AgniTranslator based on thought """
        if not thought_result or not thought_result['decision']:
            return ""
            
        anchor = thought_result['anchor']
        dec = thought_result['decision']
        
        # Emoji selection based on score/strategy
        icon = "💡"
        if thought_result['strategy'] == "PROBE":
            icon = "❓"
            
        return f"""
[Thinking Process]
Input triggered concept: '{anchor}'
{icon} Association: '{dec['name']}' ({dec['relation']})
   - Logic Score: {thought_result.get('decision', {}).get('weight', 0):.2f}
   - Strategy: {thought_result['strategy']}
"""
