"""
Unit tests for knowledge graph module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from knowledge_graph import KnowledgeGraph, Entity, Relation


class TestKnowledgeGraph(unittest.TestCase):
    """Test knowledge graph."""
    
    def setUp(self):
        self.kg = KnowledgeGraph()
        self.kg.add_entity(Entity("sc", "spacecraft", {"mass": 1000}))
        self.kg.add_entity(Entity("prop", "subsystem", {"type": "propulsion"}))
        self.kg.add_entity(Entity("mars", "planet", {"gravity": 3.71}))
        self.kg.add_relation(Relation("sc", "prop", "has_subsystem"))
        self.kg.add_relation(Relation("sc", "mars", "orbits"))
    
    def test_add_entity(self):
        """Should add entity."""
        self.assertEqual(len(self.kg.entities), 3)
        print("  [PASS] Entities: 3 added")
    
    def test_add_relation(self):
        """Should add relation."""
        self.assertEqual(len(self.kg.relations), 2)
        print("  [PASS] Relations: 2 added")
    
    def test_get_entity(self):
        """Should get entity."""
        e = self.kg.get_entity("sc")
        self.assertIsNotNone(e)
        self.assertEqual(e.entity_type, "spacecraft")
        print("  [PASS] Get: sc is spacecraft")
    
    def test_get_related(self):
        """Should get related entities."""
        related = self.kg.get_related("sc")
        self.assertEqual(len(related), 2)
        print(f"  [PASS] Related: {len(related)} entities")
    
    def test_get_related_filtered(self):
        """Should filter by relation type."""
        related = self.kg.get_related("sc", "has_subsystem")
        self.assertEqual(len(related), 1)
        self.assertEqual(related[0][0], "prop")
        print("  [PASS] Filtered: prop")
    
    def test_find_path(self):
        """Should find path."""
        # Add chain
        self.kg.add_entity(Entity("engine", "component"))
        self.kg.add_relation(Relation("prop", "engine", "contains"))
        
        path = self.kg.find_path("sc", "engine")
        self.assertIsNotNone(path)
        self.assertEqual(path, ["sc", "prop", "engine"])
        print(f"  [PASS] Path: {'->'.join(path)}")
    
    def test_find_path_none(self):
        """Should return None if no path."""
        self.kg.add_entity(Entity("unconnected", "test"))
        path = self.kg.find_path("sc", "unconnected")
        self.assertIsNone(path)
        print("  [PASS] No path: None")
    
    def test_query(self):
        """Should query by type."""
        results = self.kg.query(entity_type="planet")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "mars")
        print(f"  [PASS] Query: {len(results)} planet(s)")
    
    def test_query_attribute(self):
        """Should query by attribute."""
        results = self.kg.query(attribute_filter={"type": "propulsion"})
        self.assertEqual(len(results), 1)
        print("  [PASS] Query attr: propulsion")
    
    def test_subgraph(self):
        """Should extract subgraph."""
        sg = self.kg.subgraph("sc", depth=1)
        self.assertGreater(len(sg["nodes"]), 0)
        print(f"  [PASS] Subgraph: {len(sg['nodes'])} nodes")
    
    def test_graph_stats(self):
        """Should provide stats."""
        stats = self.kg.graph_stats()
        self.assertEqual(stats["entities"], 3)
        print(f"  [PASS] Stats: {stats['entities']} entities")
    
    def test_mission_graph(self):
        """Should create mission graph."""
        kg = KnowledgeGraph.create_mission_graph()
        self.assertGreater(len(kg.entities), 5)
        print(f"  [PASS] Mission graph: {len(kg.entities)} entities")


if __name__ == '__main__':
    unittest.main(verbosity=2)
