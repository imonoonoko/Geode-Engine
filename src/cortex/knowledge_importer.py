import json
import os
import glob
from src.cortex.knowledge_graph import KnowledgeGraph

class KnowledgeImporter:
    """
    Ingests data from JSON files and external sources into the Knowledge Graph.
    """
    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def import_from_directory(self, data_dir="data/learning"):
        """ Import all JSON files from the learning directory """
        json_files = glob.glob(os.path.join(data_dir, "*.json"))
        print(f"📥 Importing knowledge from {len(json_files)} files...")
        
        count = 0
        for file_path in json_files:
            if self.import_file(file_path):
                count += 1
        
        print(f"✅ Imported {count} files into Knowledge Graph.")
        self.graph.save()

    def import_file(self, file_path: str) -> bool:
        """ Import a single JSON file """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            subject = data.get("subject", "Unknown")
            concepts = data.get("concepts", [])
            texts = data.get("texts", [])
            
            # 1. Add Subject Node
            self.graph.add_concept(subject, {"type": "subject", "source": os.path.basename(file_path)})
            
            # 2. Add Concept Nodes & Link to Subject
            for concept in concepts:
                self.graph.add_concept(concept, {"type": "concept"})
                
                # Link: Subject -> Concept (IsRelatedTo)
                self.graph.associate(subject, concept, relation="related_to", weight=1.0)
                
                # Link: Concept -> Subject (Bidirectional for weak association)
                self.graph.associate(concept, subject, relation="related_to", weight=0.5)

            # 3. Text Co-occurrence (Clique)
            # If concepts appear in the same text list, they satisfy "Contextual Co-occurrence"
            # To avoid N^2 explosion, we just link them to the Subject strongly.
            # But let's try a simple sequential link for flow?
            # "A -> B -> C"
            # No, that assumes order.
            
            # Let's check co-occurrence in texts
            # Simple Heuristic: All concepts in this file are related.
            # We already linked them to Subject. that allows 2-hop jump: A -> Subject -> B.
            
            return True
        except Exception as e:
            print(f"⚠️ Import Failed ({file_path}): {e}")
            return False
    def import_from_jsonl(self, file_path: str, min_weight: float = 1.0, allowed_relations: list = None) -> int:
        """ 
        Import knowledge from a large JSONL file (ConceptNet style).
        Expected format per line:
        {"start": "conceptA", "end": "conceptB", "rel": "RelatedTo", "weight": 2.0}
        
        Args:
            file_path: Path to .jsonl file
            min_weight: Minimum weight to import (filter noise)
            allowed_relations: List of relation types to allow (e.g., ["IsA", "PartOf"])
        
        Returns:
            Number of edges imported
        """
        print(f"🌊 Streaming import from {file_path}...")
        count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        
                        # ConceptNet-like keys
                        start = record.get("start") or record.get("head")
                        end = record.get("end") or record.get("tail")
                        rel = record.get("rel") or record.get("relation")
                        weight = float(record.get("weight", 1.0))
                        
                        if not (start and end and rel):
                            continue
                            
                        # Filtering
                        if weight < min_weight:
                            continue
                        if allowed_relations and rel not in allowed_relations:
                            continue
                            
                        # Add Nodes
                        self.graph.add_concept(start)
                        self.graph.add_concept(end)
                        
                        # Add Edge
                        self.graph.associate(start, end, relation=rel, weight=weight)
                        count += 1
                        
                        if count % 1000 == 0:
                            print(f"   Imported {count} edges...", end='\r')
                            
                    except json.JSONDecodeError:
                        continue
                        
            print(f"\n✅ Stream complete. Imported {count} edges.")
            self.graph.save()
            return count
            
        except Exception as e:
            print(f"⚠️ Streaming Import Failed: {e}")

    def import_from_conceptnet_csv(self, file_path: str, min_weight: float = 1.0, limit: int = 0) -> int:
        """
        Import knowledge from ConceptNet CSV (gzipped or raw).
        Format: URI \t Relation \t Start \t End \t JSON_Metadata
        
        Args:
            limit: Max edges to import (0 = no limit)
        """
        import gzip
        import json
        
        print(f"🌊 Streaming import from {file_path} (Limit: {limit})...")
        
        opener = gzip.open if file_path.endswith(".gz") else open
        count = 0
        skipped = 0
        
        try:
            with opener(file_path, 'rt', encoding='utf-8') as f:
                for line in f:
                    try:
                        if limit > 0 and count >= limit:
                            print(f"\n🛑 Limit reached: {limit}")
                            break

                        parts = line.split('\t')
                        if len(parts) < 5:
                            continue
                            
                        # Extract
                        # 0: URI (ignore)
                        # 1: Relation (/r/RelatedTo)
                        rel_raw = parts[1]
                        start_raw = parts[2]
                        end_raw = parts[3]
                        meta_json = parts[4]
                        
                        # Filter by Language (Only JA and EN)
                        if "/c/ja/" not in start_raw and "/c/ja/" not in end_raw:
                            if "/c/en/" not in start_raw or "/c/en/" not in end_raw:
                                skipped += 1
                                continue
                                
                        # Parse Metadata
                        meta = json.loads(meta_json)
                        weight = meta.get("weight", 1.0)
                        
                        if weight < min_weight:
                            skipped += 1
                            continue
                            
                        # Clean IDs
                        # /c/en/cat -> cat
                        # /c/ja/猫 -> 猫
                        def clean_id(raw_id):
                            return raw_id.split('/')[-1]
                            
                        def clean_rel(raw_rel):
                            return raw_rel.split('/')[-1]

                        start = clean_id(start_raw)
                        end = clean_id(end_raw)
                        rel = clean_rel(rel_raw)
                        
                        # Add to Graph
                        self.graph.add_concept(start)
                        self.graph.add_concept(end)
                        self.graph.associate(start, end, relation=rel, weight=weight)
                        
                        count += 1
                        if count % 1000 == 0:
                            print(f"   Imported {count} edges (Skipped {skipped})...", end='\r')
                            
                    except Exception:
                        continue
                        
            print(f"\n✅ Import complete. {count} edges added.")
            self.graph.save()
            return count
            
        except Exception as e:
            print(f"⚠️ Import CSV Failed: {e}")
            return 0
