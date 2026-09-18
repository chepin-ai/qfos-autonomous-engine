"""
Autonomous Navigation Engine
Main engine coordinating orbital mechanics, data ingestion, and collision avoidance.
"""

import json
import math
from typing import Dict, List, Optional
try:
    from .orbital_mechanics import OrbitalBody, hohmann_transfer_delta_v
    from .data_connector import SBDBConnector
    from .collision_avoidance import CollisionAvoidanceSystem, HazardAssessment
except ImportError:
    from orbital_mechanics import OrbitalBody, hohmann_transfer_delta_v
    from data_connector import SBDBConnector
    from collision_avoidance import CollisionAvoidanceSystem, HazardAssessment


class AutonomousNavigationEngine:
    """
    QF-OS Autonomous Navigation Engine.
    Provides real-data-driven autonomous navigation capabilities.
    """
    
    def __init__(self, spacecraft_name: str = "QF-OS-SC1"):
        self.spacecraft_name = spacecraft_name
        self.data_connector = SBDBConnector()
        self.known_bodies: Dict[str, OrbitalBody] = {}
        self.collision_system: Optional[CollisionAvoidanceSystem] = None
        self.mission_log: List[Dict] = []
    
    def initialize_spacecraft(self, a_au: float = 1.0, e: float = 0.0167, 
                               i_deg: float = 0.0) -> OrbitalBody:
        """Initialize spacecraft orbit (default: Earth-like)."""
        sc = OrbitalBody(
            name=self.spacecraft_name,
            spkid="SC1",
            a_au=a_au,
            e=e,
            i_deg=i_deg
        )
        self.collision_system = CollisionAvoidanceSystem(sc)
        return sc
    
    def load_asteroid_database(self, designations: List[str]) -> int:
        """Load real asteroid data from NASA SBDB."""
        fetched = self.data_connector.fetch_multiple(designations)
        self.known_bodies.update(fetched)
        return len(fetched)
    
    def run_hazard_scan(self) -> List[HazardAssessment]:
        """Run full collision avoidance scan against loaded targets."""
        if not self.collision_system:
            raise RuntimeError("Spacecraft not initialized. Call initialize_spacecraft() first.")
        
        targets = list(self.known_bodies.values())
        if not targets:
            raise RuntimeError("No targets loaded. Call load_asteroid_database() first.")
        
        results = self.collision_system.scan_field(targets)
        
        # Log mission event
        self.mission_log.append({
            "event": "HAZARD_SCAN",
            "targets_scanned": len(targets),
            "critical_count": sum(1 for r in results if r.risk_level == "CRITICAL"),
            "high_count": sum(1 for r in results if r.risk_level == "HIGH"),
        })
        
        return results
    
    def compute_transfer_to(self, target_name: str) -> Dict:
        """Compute Hohmann transfer from current orbit to target."""
        if not self.collision_system:
            raise RuntimeError("Spacecraft not initialized.")
        
        target = self.known_bodies.get(target_name)
        if not target:
            raise ValueError(f"Target {target_name} not in database.")
        
        sc_a = self.collision_system.spacecraft.semi_major_axis_au
        target_a = target.semi_major_axis_au
        
        dv = hohmann_transfer_delta_v(sc_a, target_a)
        transfer_time_years = 3.14159 * math.sqrt(((sc_a + target_a) / 2.0) ** 3)
        
        return {
            "from": self.spacecraft_name,
            "to": target_name,
            "delta_v_kms": round(dv, 3),
            "transfer_time_years": round(transfer_time_years, 2),
            "origin_orbit_au": round(sc_a, 4),
            "target_orbit_au": round(target_a, 4)
        }
    
    def get_mission_report(self) -> Dict:
        """Generate comprehensive mission status report."""
        return {
            "spacecraft": self.spacecraft_name,
            "known_bodies": len(self.known_bodies),
            "mission_events": len(self.mission_log),
            "hazard_assessments": len(self.collision_system.hazard_log) if self.collision_system else 0,
            "targets": [b.name for b in self.known_bodies.values()]
        }
