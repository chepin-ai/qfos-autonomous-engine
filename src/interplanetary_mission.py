"""
Interplanetary Mission Planner Module
Top-level mission planning using NASA SBDB data for asteroid/comet targets.
Integrates all spacecraft subsystems for end-to-end mission design.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    from .orbital_mechanics import OrbitalBody, hohmann_transfer_delta_v, AU, MU_SUN
    from .gravity_assist import optimal_flyby_planet
    from .data_connector import SBDBConnector
except ImportError:
    from orbital_mechanics import OrbitalBody, hohmann_transfer_delta_v, AU, MU_SUN
    from gravity_assist import optimal_flyby_planet
    from data_connector import SBDBConnector


class MissionPhase(Enum):
    LAUNCH = "launch"
    CRUISE = "cruise"
    ENCOUNTER = "encounter"
    EXTENDED = "extended"


@dataclass
class MissionObjective:
    """A mission objective for an interplanetary target."""
    target_designation: str
    objective_type: str  # 'flyby', 'orbit', 'rendezvous', 'sample_return'
    arrival_date: Optional[str] = None
    min_distance_km: float = 1000.0
    science_instruments: List[str] = field(default_factory=list)


@dataclass
class MissionProfile:
    """Complete interplanetary mission profile."""
    mission_name: str
    launch_vehicle: str
    launch_date: Optional[str] = None
    total_delta_v_kms: float = 0.0
    total_duration_days: float = 0.0
    phases: List[Dict] = field(default_factory=list)
    objectives: List[MissionObjective] = field(default_factory=list)
    constraints: Dict = field(default_factory=dict)


class InterplanetaryMissionPlanner:
    """
    Plan interplanetary missions to small bodies using real SBDB data.
    
    Integrates trajectory, gravity assist, propulsion, and subsystem analysis.
    """
    
    # Fallback data for common targets when SBDB is unavailable
    KNOWN_BODIES = {
        "1 Ceres": OrbitalBody(
            name="1 Ceres", spkid="2000001", a_au=2.769, e=0.076,
            i_deg=10.59, omega_deg=73.6, Omega_deg=80.3, epoch="J2000"
        ),
        "4 Vesta": OrbitalBody(
            name="4 Vesta", spkid="2000004", a_au=2.362, e=0.089,
            i_deg=7.14, omega_deg=150.7, Omega_deg=103.8, epoch="J2000"
        ),
        "99942 Apophis": OrbitalBody(
            name="99942 Apophis", spkid="2099942", a_au=0.922, e=0.191,
            i_deg=3.33, omega_deg=126.4, Omega_deg=204.4, epoch="J2000"
        ),
        "433 Eros": OrbitalBody(
            name="433 Eros", spkid="2000433", a_au=1.458, e=0.223,
            i_deg=10.83, omega_deg=178.8, Omega_deg=304.3, epoch="J2000"
        ),
    }
    
    def __init__(self, data_connector: Optional[SBDBConnector] = None):
        self.connector = data_connector or SBDBConnector()
    
    def analyze_target(self, designation: str) -> Optional[Dict]:
        """
        Analyze a small body target from SBDB.
        
        Args:
            designation: Target designation (e.g., '1 Ceres', '99942 Apophis')
        
        Returns:
            Target analysis or None if not found
        """
        body = None
        try:
            body = self.connector.get_body(designation)
            # Validate: reject bodies with zero semi-major axis
            if body and body.semi_major_axis_au <= 0:
                body = None
        except Exception:
            pass
        
        # Fallback to known bodies
        if not body:
            body = self.KNOWN_BODIES.get(designation)
        
        if not body:
            return None
        
        return {
            "designation": designation,
            "object_type": getattr(body, 'object_type', 'unknown'),
            "semi_major_axis_au": round(body.semi_major_axis_au, 4),
            "eccentricity": round(body.e, 4),
            "inclination_deg": round(body.inclination_deg, 2),
            "orbital_period_yr": round(body.period_years, 2),
            "moid_au": None,
            "diameter_km": getattr(body, 'diameter_km', None),
            "accessible": body.semi_major_axis_au < 3.5  # Inner solar system
        }
    
    def design_transfer(self, target_designation: str,
                        launch_window_start: str = None,
                        launch_window_end: str = None) -> Dict:
        """
        Design a transfer trajectory to a target.
        
        Args:
            target_designation: Target small body
            launch_window_start: Earliest launch date (YYYY-MM-DD)
            launch_window_end: Latest launch date (YYYY-MM-DD)
        
        Returns:
            Transfer design
        """
        # Get target orbital elements (SBDB or fallback)
        target = None
        try:
            target = self.connector.get_body(target_designation)
        except Exception:
            pass
        if not target:
            target = self.KNOWN_BODIES.get(target_designation)
        
        if not target:
            return {"error": f"Target {target_designation} not found"}
        
        # Earth reference
        earth = OrbitalBody(
            name="Earth", spkid="399", a_au=1.0, e=0.0167,
            i_deg=0.0, omega_deg=0.0, Omega_deg=0.0, epoch="J2000"
        )
        
        # Direct Hohmann transfer
        dv, time_days = hohmann_transfer_delta_v(earth, target)
        
        # Check for gravity assist opportunities
        a_target = target.semi_major_axis_au
        best_ga = None
        if a_target > 2.0:
            ga_results = optimal_flyby_planet(
                v_inf_required=5000.0,
                available_planets=["Venus", "Earth", "Mars", "Jupiter"]
            )
            if ga_results:
                best_ga = ga_results[0]
        
        # Build transfer profile
        phases = [
            {
                "phase": "departure",
                "from": "Earth",
                "delta_v_kms": round(dv / 2, 3),
                "action": "Earth escape burn"
            },
            {
                "phase": "cruise",
                "duration_days": round(time_days, 1),
                "distance_au": round(abs(a_target - 1.0), 3)
            }
        ]
        
        if best_ga:
            phases.insert(1, {
                "phase": "gravity_assist",
                "planet": best_ga["planet"],
                "turn_angle_deg": round(best_ga["turn_angle_deg"], 1),
                "potential_dv_savings_kms": round(best_ga["max_delta_v_ms"] / 1000.0, 3)
            })
        
        phases.append({
            "phase": "arrival",
            "to": target_designation,
            "delta_v_kms": round(dv / 2, 3),
            "action": "Target capture/encounter"
        })
        
        return {
            "target": target_designation,
            "transfer_type": "Hohmann" if not best_ga else "Gravity-assisted",
            "total_delta_v_kms": round(dv, 3),
            "transfer_time_days": round(time_days, 1),
            "transfer_time_years": round(time_days / 365.25, 2),
            "phases": phases,
            "gravity_assist": best_ga
        }
    
    def design_mission(self, name: str, objectives: List[MissionObjective],
                       launch_vehicle: str = "Falcon 9",
                       c3_limit_km2_s2: float = 100.0) -> MissionProfile:
        """
        Design a complete interplanetary mission.
        
        Args:
            name: Mission name
            objectives: List of mission objectives
            launch_vehicle: Launch vehicle name
            c3_limit_km2_s2: Maximum launch energy
        
        Returns:
            MissionProfile
        """
        profile = MissionProfile(
            mission_name=name,
            launch_vehicle=launch_vehicle,
            objectives=objectives,
            constraints={"c3_limit_km2_s2": c3_limit_km2_s2}
        )
        
        total_dv = 0.0
        total_time = 0.0
        phases = []
        
        for obj in objectives:
            transfer = self.design_transfer(obj.target_designation)
            
            if "error" in transfer:
                phases.append({
                    "objective": obj.objective_type,
                    "target": obj.target_designation,
                    "status": "FAILED",
                    "reason": transfer["error"]
                })
                continue
            
            total_dv += transfer["total_delta_v_kms"]
            total_time += transfer["transfer_time_days"]
            
            phases.append({
                "objective": obj.objective_type,
                "target": obj.target_designation,
                "delta_v_kms": transfer["total_delta_v_kms"],
                "duration_days": transfer["transfer_time_days"],
                "transfer": transfer
            })
        
        profile.total_delta_v_kms = round(total_dv, 3)
        profile.total_duration_days = round(total_time, 1)
        profile.phases = phases
        
        return profile
    
    def assess_mission_feasibility(self, profile: MissionProfile) -> Dict:
        """
        Assess mission feasibility against constraints.
        
        Returns:
            Feasibility assessment
        """
        c3_limit = profile.constraints.get("c3_limit_km2_s2", 100.0)
        
        # Convert total dV to approximate C3
        # C3 ≈ v_inf^2 where v_inf ≈ dv_escape
        # For Earth escape: dv ≈ sqrt(C3) - v_circular
        v_circ_earth = 29.78  # km/s
        v_inf = profile.total_delta_v_kms  # Simplified
        c3_required = v_inf**2
        
        # Launch mass estimate (simplified Tsiolkovsky)
        # Assume Isp=320s (hydrazine), dry mass=500kg
        isp_s = 320.0
        g0 = 9.81e-3  # km/s^2
        ve = isp_s * g0
        mass_ratio = math.exp(profile.total_delta_v_kms / ve)
        
        return {
            "mission": profile.mission_name,
            "feasible": c3_required <= c3_limit,
            "c3_required_km2_s2": round(c3_required, 1),
            "c3_limit_km2_s2": c3_limit,
            "total_delta_v_kms": profile.total_delta_v_kms,
            "total_duration_years": round(profile.total_duration_days / 365.25, 2),
            "estimated_mass_ratio": round(mass_ratio, 2),
            "launch_vehicle": profile.launch_vehicle,
            "objectives_count": len(profile.objectives),
            "bottleneck": "delta_v" if c3_required > c3_limit else None
        }
    
    def compare_targets(self, designations: List[str]) -> List[Dict]:
        """
        Compare multiple targets for mission planning.
        
        Returns:
            Ranked list of target assessments
        """
        results = []
        
        for desig in designations:
            analysis = self.analyze_target(desig)
            if analysis:
                transfer = self.design_transfer(desig)
                analysis["transfer_delta_v_kms"] = transfer.get("total_delta_v_kms", 0)
                analysis["transfer_time_yr"] = transfer.get("transfer_time_years", 0)
                
                # Accessibility score (lower is better)
                score = (
                    analysis["transfer_delta_v_kms"] * 0.5 +
                    analysis["transfer_time_yr"] * 2.0 +
                    (1.0 / analysis["moid_au"] if analysis["moid_au"] else 10.0) * 0.1
                )
                analysis["mission_score"] = round(score, 2)
                results.append(analysis)
        
        # Sort by score ascending
        results.sort(key=lambda x: x["mission_score"])
        return results
    
    def generate_mission_report(self, profile: MissionProfile) -> str:
        """Generate a human-readable mission report."""
        lines = [
            f"# Mission Report: {profile.mission_name}",
            f"**Launch Vehicle:** {profile.launch_vehicle}",
            f"**Total Delta-V:** {profile.total_delta_v_kms} km/s",
            f"**Total Duration:** {profile.total_duration_days / 365.25:.2f} years",
            "",
            "## Objectives",
        ]
        
        for i, obj in enumerate(profile.objectives, 1):
            lines.append(f"{i}. **{obj.objective_type.upper()}** {obj.target_designation}")
            if obj.science_instruments:
                lines.append(f"   Instruments: {', '.join(obj.science_instruments)}")
        
        lines.extend(["", "## Transfer Phases"])
        for phase in profile.phases:
            if "target" in phase:
                lines.append(f"- **{phase['target']}**: {phase.get('delta_v_kms', 0)} km/s, {phase.get('duration_days', 0)} days")
        
        return "\n".join(lines)
