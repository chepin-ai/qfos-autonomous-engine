"""
Collision Avoidance Module
Hazard detection and autonomous avoidance maneuver planning.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
try:
    from .orbital_mechanics import OrbitalBody, estimate_moid, hohmann_transfer_delta_v
except ImportError:
    from orbital_mechanics import OrbitalBody, estimate_moid, hohmann_transfer_delta_v


@dataclass
class HazardAssessment:
    """Result of collision risk assessment."""
    target_name: str
    moid_au: float
    risk_level: str  # LOW, MODERATE, HIGH, CRITICAL
    impact_probability: float
    recommended_action: str
    estimated_dv_kms: float


class CollisionAvoidanceSystem:
    """
    Autonomous collision avoidance system.
    Evaluates collision risks and plans avoidance maneuvers.
    """
    
    # Risk thresholds in AU
    CRITICAL_THRESHOLD = 0.01   # ~1.5 million km
    HIGH_THRESHOLD = 0.05       # ~7.5 million km
    MODERATE_THRESHOLD = 0.1    # ~15 million km
    
    def __init__(self, spacecraft_orbit: OrbitalBody):
        self.spacecraft = spacecraft_orbit
        self.hazard_log: List[HazardAssessment] = []
    
    def assess_target(self, target: OrbitalBody) -> HazardAssessment:
        """Assess collision risk with a target body."""
        moid = estimate_moid(self.spacecraft, target)
        
        # Simplified impact probability model
        period_ratio = (target.semi_major_axis_au / self.spacecraft.semi_major_axis_au) ** 1.5
        resonance = 1.0 / abs(period_ratio - round(period_ratio) + 0.1)
        impact_prob = min(1.0, 0.1 / (moid ** 2 + 0.001) * resonance / 1000)
        
        # Risk classification
        if moid < self.CRITICAL_THRESHOLD:
            risk = "CRITICAL"
            action = "IMMEDIATE EVASIVE MANEUVER REQUIRED"
        elif moid < self.HIGH_THRESHOLD:
            risk = "HIGH"
            action = "PLAN AVOIDANCE MANEUVER"
        elif moid < self.MODERATE_THRESHOLD:
            risk = "MODERATE"
            action = "CONTINUE MONITORING"
        else:
            risk = "LOW"
            action = "NO ACTION REQUIRED"
        
        # Estimate delta-v for avoidance (simplified)
        dv = hohmann_transfer_delta_v(
            self.spacecraft.semi_major_axis_au,
            target.semi_major_axis_au
        ) if moid < self.MODERATE_THRESHOLD else 0.0
        
        assessment = HazardAssessment(
            target_name=target.name,
            moid_au=round(moid, 6),
            risk_level=risk,
            impact_probability=round(impact_prob, 6),
            recommended_action=action,
            estimated_dv_kms=round(dv, 3)
        )
        self.hazard_log.append(assessment)
        return assessment
    
    def scan_field(self, targets: List[OrbitalBody]) -> List[HazardAssessment]:
        """Scan multiple targets and return sorted by risk."""
        results = []
        for target in targets:
            assessment = self.assess_target(target)
            results.append(assessment)
        
        # Sort by risk level (CRITICAL first)
        risk_order = {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3}
        results.sort(key=lambda x: risk_order.get(x.risk_level, 99))
        return results
    
    def get_critical_hazards(self) -> List[HazardAssessment]:
        """Return only critical and high risk hazards."""
        return [h for h in self.hazard_log 
                if h.risk_level in ("CRITICAL", "HIGH")]
