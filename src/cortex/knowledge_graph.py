import networkx as nx
import threading
import json
import os
import time

from src.cortex.knowledge_base import KnowledgeBase

class KnowledgeGraph:
    """
    Kaname's Common Sense Map (Wrapper for NetworkX).
    Stores concepts as Nodes and relationships as Edges.
    Implements Tiered Memory (RAM + SQLite).
    """
    def __init__(self, save_dir="memory_data"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
        self.graph_path = os.path.join(self.save_dir, "knowledge_graph.gml")
        
        self.lock = threading.RLock()
        self.G = nx.DiGraph() # Directed Graph
        
        # Tiered Memory: LTM (SQLite)
        self.ltm = KnowledgeBase()
        
        # Load existing graph
        self._load()
        
    def _load(self):
        """ Load graph from disk """
        if os.path.exists(self.graph_path):
            try:
                self.G = nx.read_gml(self.graph_path)
                print(f"🕸️ KnowledgeGraph Loaded: {self.G.number_of_nodes()} concepts, {self.G.number_of_edges()} links.")
            except Exception as e:
                print(f"⚠️ Graph Load Error: {e}")
                self.G = nx.DiGraph()
        else:
            print("🕸️ New KnowledgeGraph Created.")

    def save(self):
        """ Save graph to disk (Async recommended, but sync for now) """
        try:
            with self.lock:
                nx.write_gml(self.G, self.graph_path)
        except Exception as e:
            print(f"⚠️ Graph Save Error: {e}")

    def add_concept(self, name: str, attributes: dict = None):
        """ Add or update a concept node """
        with self.lock:
            if not self.G.has_node(name):
                # Check LTM first (Lazy Load)
                if self.lazy_load(name):
                    return # Loaded from disk
                
                self.G.add_node(name, created_at=time.time(), last_accessed=time.time())
            else:
                self.G.nodes[name]['last_accessed'] = time.time()
            
            if attributes:
                for k, v in attributes.items():
                    if isinstance(v, (list, dict)):
                        v = json.dumps(v, ensure_ascii=False)
                    self.G.nodes[name][k] = v
                
                # Async save to LTM
                try:
                    self.ltm.save_concept(name, attributes)
                except: pass

    def associate(self, source: str, target: str, relation: str = "related_to", weight: float = 1.0):
        """ Connect two concepts """
        with self.lock:
            # Lookups will trigger lazy_load if needed
            self.add_concept(source)
            self.add_concept(target)
            
            if self.G.has_edge(source, target):
                old_weight = self.G[source][target].get('weight', 0.0)
                new_weight = old_weight + (weight * 0.1) 
                self.G[source][target]['weight'] = min(5.0, new_weight)
            else:
                self.G.add_edge(source, target, relation=relation, weight=weight)
            
            # Async save to LTM
            try:
                self.ltm.save_edge(source, target, relation, self.G[source][target]['weight'])
            except: pass

    def get_related(self, concept: str, top_k: int = 5, min_weight: float = 0.5) -> list:
        """ Get connected concepts (Outgoing edges) """
        with self.lock:
            if not self.G.has_node(concept):
                if not self.lazy_load(concept):
                    return []
            
            # Update Access Time
            self.G.nodes[concept]['last_accessed'] = time.time()
            
            # Get neighbors with edge data
            neighbors = []
            for nbr in self.G.successors(concept):
                data = self.G[concept][nbr]
                if data.get('weight', 0) >= min_weight:
                    neighbors.append({
                        "name": nbr,
                        "relation": data.get('relation', 'related'),
                        "weight": data.get('weight', 0.0)
                    })
            
            neighbors.sort(key=lambda x: x['weight'], reverse=True)
            return neighbors[:top_k]

    def find_path(self, start: str, end: str, max_depth: int = 3) -> list:
        """ Find shortest path between two concepts """
        with self.lock:
            try:
                # Ensure nodes are loaded
                if not self.G.has_node(start): self.lazy_load(start)
                if not self.G.has_node(end): self.lazy_load(end)
                
                if not self.G.has_node(start) or not self.G.has_node(end):
                    return []
                
                path = nx.shortest_path(self.G, source=start, target=end)
                if len(path) > max_depth + 1:
                    return []
                return path
            except nx.NetworkXNoPath:
                return []
            except Exception as e:
                # print(f"⚠️ Path Find Error: {e}")
                return []

    def get_subgraph_text(self, center_node: str, depth: int = 1) -> str:
        """ format subgraph as text for debug/LLM context """
        with self.lock:
            self.add_concept(center_node) # Enhance: Try to load
            
            if not self.G.has_node(center_node):
                return ""
            
            lines = [f"Origin: {center_node}"]
            neighbors = self.get_related(center_node, top_k=10)
            for n in neighbors:
                lines.append(f"  --[{n['relation']}]--> {n['name']} (w={n['weight']:.2f})")
                if depth > 1:
                    sub_neighbors = self.get_related(n['name'], top_k=3)
                    for sn in sub_neighbors:
                        lines.append(f"      --[{sn['relation']}]--> {sn['name']}")
                        
            return "\n".join(lines)

    # --- Tiered Memory Methods ---

    def lazy_load(self, concept: str) -> bool:
        """ Fetch concept and its immediate neighbors from LTM (SQLite) """
        # 1. Fetch Concept
        attrs = self.ltm.get_concept(concept)
        # Note: If concept not in concepts table but exists in edges, we might miss it.
        # But import usually creates both.
        
        # 2. Fetch Edges
        edges = self.ltm.get_edges(concept)
        if not attrs and not edges:
            return False # Not in LTM
            
        # Add to Graph
        self.G.add_node(concept, created_at=time.time(), last_accessed=time.time())
        if attrs:
            for k, v in attrs.items():
                self.G.nodes[concept][k] = v
        
        # Add Neighbors
        for target, relation, weight in edges:
            self.G.add_node(target, created_at=time.time(), last_accessed=time.time())
            self.G.add_edge(concept, target, relation=relation, weight=weight)
            
        print(f"📖 Recall: Loaded '{concept}' + {len(edges)} links from LTM.")
        return True

    def prune(self, limit: int = 10000):
        """ Forget old memories if capacity exceeded """
        with self.lock:
            current_size = self.G.number_of_nodes()
            if current_size <= limit:
                return
            
            remove_count = current_size - limit
            print(f"🧹 Pruning {remove_count} old memories...")
            
            # Sort by last_accessed (Smallest = Oldest)
            # Default to 0 if missing
            nodes_sorted = sorted(
                self.G.nodes(data=True), 
                key=lambda x: x[1].get('last_accessed', 0)
            )
            
            for i in range(remove_count):
                node_name = nodes_sorted[i][0]
                self.G.remove_node(node_name)

