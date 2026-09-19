"""
Knowledge Graph Module
Mission entity relationships, semantic reasoning,
and inference over spacecraft domain knowledge.
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field


@dataclass
class Entity:
    """A node in the knowledge graph."""
    id: str
    entity_type: str
    attributes: Dict[str, any] = field(default_factory=dict)


@dataclass
class Relation:
    """An edge in the knowledge graph."""
    source: str
    target: str
    relation_type: str
    weight: float = 1.0
    bidirectional: bool = False


class KnowledgeGraph:
    """
    Semantic knowledge graph for mission domain.
    
    Stores entities and relations, supports traversal
    and simple inference.
    """
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        self.index: Dict[str, List[Relation]] = {}  # source -> relations
        self.type_index: Dict[str, List[str]] = {}  # type -> entity ids
    
    def add_entity(self, entity: Entity):
        """Add an entity."""
        self.entities[entity.id] = entity
        if entity.entity_type not in self.type_index:
            self.type_index[entity.entity_type] = []
        self.type_index[entity.entity_type].append(entity.id)
    
    def add_relation(self, relation: Relation):
        """Add a relation."""
        self.relations.append(relation)
        
        if relation.source not in self.index:
            self.index[relation.source] = []
        self.index[relation.source].append(relation)
        
        if relation.bidirectional:
            rev = Relation(relation.target, relation.source,
                          relation.relation_type, relation.weight, False)
            if relation.target not in self.index:
                self.index[relation.target] = []
            self.index[relation.target].append(rev)
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        return self.entities.get(entity_id)
    
    def get_related(self, entity_id: str,
                    relation_type: Optional[str] = None) -> List[Tuple[str, str, float]]:
        """
        Get entities related to given entity.
        
        Args:
            entity_id: Source entity
            relation_type: Filter by relation type
        
        Returns:
            List of (target_id, relation_type, weight)
        """
        results = []
        for rel in self.index.get(entity_id, []):
            if relation_type is None or rel.relation_type == relation_type:
                results.append((rel.target, rel.relation_type, rel.weight))
        return results
    
    def find_path(self, source: str, target: str,
                  max_depth: int = 5) -> Optional[List[str]]:
        """
        Find path between entities using BFS.
        
        Args:
            source: Start entity
            target: Goal entity
            max_depth: Maximum search depth
        
        Returns:
            Path as list of entity IDs or None
        """
        if source not in self.entities or target not in self.entities:
            return None
        
        visited = {source}
        queue = [(source, [source])]
        
        while queue:
            current, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            for rel in self.index.get(current, []):
                if rel.target == target:
                    return path + [target]
                
                if rel.target not in visited:
                    visited.add(rel.target)
                    queue.append((rel.target, path + [rel.target]))
        
        return None
    
    def infer_type(self, entity_id: str) -> Optional[str]:
        """Infer entity type from relations."""
        entity = self.entities.get(entity_id)
        if entity:
            return entity.entity_type
        
        # Check if it's a target of "is_a" relations
        for rel in self.relations:
            if rel.target == entity_id and rel.relation_type == "is_a":
                return "subtype"
        
        return None
    
    def query(self, entity_type: Optional[str] = None,
              attribute_filter: Optional[Dict[str, any]] = None) -> List[Entity]:
        """
        Query entities by type and attributes.
        
        Args:
            entity_type: Filter by type
            attribute_filter: Filter by attributes
        
        Returns:
            Matching entities
        """
        candidates = []
        
        if entity_type:
            candidates = [self.entities[eid] for eid in self.type_index.get(entity_type, [])]
        else:
            candidates = list(self.entities.values())
        
        if attribute_filter:
            results = []
            for entity in candidates:
                match = True
                for key, value in attribute_filter.items():
                    if entity.attributes.get(key) != value:
                        match = False
                        break
                if match:
                    results.append(entity)
            candidates = results
        
        return candidates
    
    def subgraph(self, center: str, depth: int = 2) -> Dict:
        """
        Extract subgraph around center entity.
        
        Args:
            center: Center entity ID
            depth: Neighborhood depth
        
        Returns:
            Subgraph dict
        """
        nodes = {center}
        edges = []
        frontier = {center}
        
        for _ in range(depth):
            new_frontier = set()
            for node in frontier:
                for rel in self.index.get(node, []):
                    edges.append(rel)
                    new_frontier.add(rel.target)
                    nodes.add(rel.target)
            frontier = new_frontier
        
        return {
            "nodes": [self.entities[n].__dict__ for n in nodes if n in self.entities],
            "edges": [(e.source, e.relation_type, e.target) for e in edges]
        }
    
    def graph_stats(self) -> Dict:
        """Get graph statistics."""
        return {
            "entities": len(self.entities),
            "relations": len(self.relations),
            "entity_types": len(self.type_index),
            "avg_degree": round(len(self.relations) * 2 / max(1, len(self.entities)), 2)
        }
    
    @staticmethod
    def create_mission_graph() -> "KnowledgeGraph":
        """Create a sample mission knowledge graph."""
        kg = KnowledgeGraph()
        
        # Spacecraft entities
        kg.add_entity(Entity("sc_main", "spacecraft", {"mass_kg": 5000, "status": "operational"}))
        kg.add_entity(Entity("sc_lander", "spacecraft", {"mass_kg": 800, "status": "standby"}))
        kg.add_entity(Entity("sc_relay", "spacecraft", {"mass_kg": 300, "status": "operational"}))
        
        # Subsystems
        kg.add_entity(Entity("prop_main", "subsystem", {"type": "propulsion", "fuel_kg": 2000}))
        kg.add_entity(Entity("power_main", "subsystem", {"type": "power", "capacity_w": 5000}))
        kg.add_entity(Entity("comm_main", "subsystem", {"type": "communication", "band": "X"}))
        kg.add_entity(Entity("nav_main", "subsystem", {"type": "navigation"}))
        
        # Celestial bodies
        kg.add_entity(Entity("earth", "planet", {"gravity": 9.81}))
        kg.add_entity(Entity("mars", "planet", {"gravity": 3.71}))
        kg.add_entity(Entity("moon", "moon", {"gravity": 1.62}))
        
        # Relations
        kg.add_relation(Relation("sc_main", "prop_main", "has_subsystem"))
        kg.add_relation(Relation("sc_main", "power_main", "has_subsystem"))
        kg.add_relation(Relation("sc_main", "comm_main", "has_subsystem"))
        kg.add_relation(Relation("sc_main", "nav_main", "has_subsystem"))
        kg.add_relation(Relation("sc_main", "earth", "departed_from"))
        kg.add_relation(Relation("sc_main", "mars", "heading_to"))
        kg.add_relation(Relation("sc_lander", "mars", "targets"))
        kg.add_relation(Relation("sc_relay", "mars", "orbits"))
        kg.add_relation(Relation("prop_main", "sc_main", "belongs_to", bidirectional=True))
        
        return kg
