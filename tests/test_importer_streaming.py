import unittest
import os
import shutil
from src.cortex.knowledge_graph import KnowledgeGraph
from src.cortex.knowledge_importer import KnowledgeImporter

class TestStreamingImporter(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_data_streaming"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        self.graph = KnowledgeGraph(save_dir=self.test_dir)
        self.importer = KnowledgeImporter(self.graph)
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_import_jsonl(self):
        # Create dummy JSONL
        jsonl_path = os.path.join(self.test_dir, "test.jsonl")
        with open(jsonl_path, "w", encoding="utf-8") as f:
            f.write('{"start": "Cat", "end": "Animal", "rel": "IsA", "weight": 2.0}\n')
            f.write('{"start": "Dog", "end": "Animal", "rel": "IsA", "weight": 2.0}\n')
            f.write('{"start": "Cat", "end": "Water", "rel": "Dislikes", "weight": 0.5}\n') # Low weight
            f.write('{"start": "Bird", "end": "Fly", "rel": "CapableOf", "weight": 1.5}\n')

        # Test Import with Filter (weight >= 1.0)
        count = self.importer.import_from_jsonl(jsonl_path, min_weight=1.0)
        
        # Expected: 3 edges (Cat-Animal, Dog-Animal, Bird-Fly). Cat-Water excluded (0.5 < 1.0)
        self.assertEqual(count, 3)
        
        # Verify Graph Content
        self.assertTrue(self.graph.G.has_node("Cat"))
        self.assertTrue(self.graph.G.has_node("Animal"))
        
        # Check if edge exists
        found_animal = self.graph.G.has_edge("Cat", "Animal")
        found_water = self.graph.G.has_edge("Cat", "Water")
                
        self.assertTrue(found_animal, "Cat should be IsA Animal")
        self.assertFalse(found_water, "Cat Dislikes Water should be filtered out")

if __name__ == '__main__':
    unittest.main()
