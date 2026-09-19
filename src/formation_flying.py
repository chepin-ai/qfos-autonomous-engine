"""
Formation Flying Module
Relative orbit keeping, coordinated control, and
formation maintenance for multi-spacecraft systems.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SpacecraftState:
    """Spacecraft orbital state."""
    position: Tuple[float, float, float]  # km (ECI)
    velocity: Tuple[float, float, float]  # km/s
    sc_id: str = ""


class RelativeOrbitalElements:
    """
    Compute relative orbital elements (ROE) for formation flying.
    """
    
    @staticmethod
    def compute_relative(state_chief: SpacecraftState,
                        state_deputy: SpacecraftState
                        ) -> Dict[str, float]:
        """
        Compute relative state.
        
        Args:
            state_chief: Chief spacecraft state
            state_deputy: Deputy spacecraft state
        
        Returns:
            Relative position and velocity
        """
        dr = tuple(d - c for c, d in zip(state_chief.position, state_deputy.position))
        dv = tuple(d - c for c, d in zip(state_chief.velocity, state_deputy.velocity))
        
        return {
            "dx_km": dr[0], "dy_km": dr[1], "dz_km": dr[2],
            "dvx_kms": dv[0], "dvy_kms": dv[1], "dvz_kms": dv[2],
            "range_km": math.sqrt(sum(c**2 for c in dr))
        }
    
    @staticmethod
    def hill_frame(state_chief: SpacecraftState,
                   state_deputy: SpacecraftState
                   ) -> Dict[str, float]:
        """
        Convert relative state to Hill (LVLH) frame.
        
        Args:
            state_chief: Chief state
            state_deputy: Deputy state
        
        Returns:
            Hill frame coordinates (radial, along-track, cross-track)
        """
        r = state_chief.position
        v = state_chief.velocity
        
        r_norm = math.sqrt(sum(c**2 for c in r))
        h = (
            r[1]*v[2] - r[2]*v[1],
            r[2]*v[0] - r[0]*v[2],
            r[0]*v[1] - r[1]*v[0]
        )
        h_norm = math.sqrt(sum(c**2 for c in h))
        
        # LVLH axes
        o_r = tuple(c / r_norm for c in r)  # radial
        o_h = tuple(c / h_norm for c in h)  # cross-track
        o_t = (
            o_h[1]*o_r[2] - o_h[2]*o_r[1],
            o_h[2]*o_r[0] - o_h[0]*o_r[2],
            o_h[0]*o_r[1] - o_h[1]*o_r[0]
        )  # along-track
        
        dr = tuple(d - c for c, d in zip(state_chief.position, state_deputy.position))
        
        return {
            "radial_km": sum(dr[i] * o_r[i] for i in range(3)),
            "along_track_km": sum(dr[i] * o_t[i] for i in range(3)),
            "cross_track_km": sum(dr[i] * o_h[i] for i in range(3))
        }


class FormationKeeping:
    """
    Formation-keeping control using impulsive maneuvers.
    """
    
    def __init__(self, mu: float = 398600.4418):
        """
        Args:
            mu: Gravitational parameter (km^3/s^2)
        """
        self.mu = mu
    
    def _orbit_rate(self, r: float) -> float:
        """Mean orbital rate (rad/s)."""
        return math.sqrt(self.mu / r**3)
    
    def station_keeping_delta_v(self, state_chief: SpacecraftState,
                                state_deputy: SpacecraftState,
                                desired_separation_km: float
                                ) -> Tuple[float, float, float]:
        """
        Compute station-keeping delta-v.
        
        Args:
            state_chief: Chief state
            state_deputy: Deputy state
            desired_separation_km: Desired separation
        
        Returns:
            Delta-v vector (km/s)
        """
        rel = RelativeOrbitalElements.compute_relative(state_chief, state_deputy)
        r = math.sqrt(sum(c**2 for c in state_chief.position))
        n = self._orbit_rate(r)
        
        # Simple proportional controller
        error = rel["range_km"] - desired_separation_km
        gain = n * 0.001  # small gain
        
        # Direct toward chief
        direction = tuple(
            (state_chief.position[i] - state_deputy.position[i]) / rel["range_km"]
            if rel["range_km"] > 1e-10 else 0.0
            for i in range(3)
        )
        
        dv = tuple(error * gain * d for d in direction)
        return dv
    
    def periodic_correction(self, state_chief: SpacecraftState,
                           state_deputy: SpacecraftState,
                           desired_hill: Dict[str, float]
                           ) -> Tuple[float, float, float]:
        """
        Compute periodic correction in Hill frame.
        
        Args:
            state_chief: Chief state
            state_deputy: Deputy state
            desired_hill: Desired Hill coordinates
        
        Returns:
            Correction delta-v (km/s)
        """
        hill = RelativeOrbitalElements.hill_frame(state_chief, state_deputy)
        r = math.sqrt(sum(c**2 for c in state_chief.position))
        n = self._orbit_rate(r)
        
        # Errors
        e_r = hill["radial_km"] - desired_hill.get("radial_km", 0)
        e_t = hill["along_track_km"] - desired_hill.get("along_track_km", 0)
        e_h = hill["cross_track_km"] - desired_hill.get("cross_track_km", 0)
        
        # Simple feedback
        dv_r = -n * e_t * 0.01
        dv_t = n * e_r * 0.01
        dv_h = -n * e_h * 0.01
        
        return (dv_r / 1000, dv_t / 1000, dv_h / 1000)  # convert to km/s


class CoordinatedControl:
    """
    Coordinated control for multiple spacecraft.
    """
    
    def __init__(self):
        self.spacecraft: Dict[str, SpacecraftState] = {}
        self.formation_geometry: Dict[str, Dict[str, float]] = {}
    
    def register(self, sc_id: str, state: SpacecraftState):
        """Register spacecraft."""
        state.sc_id = sc_id
        self.spacecraft[sc_id] = state
    
    def set_desired_geometry(self, sc_id: str, hill: Dict[str, float]):
        """Set desired Hill coordinates."""
        self.formation_geometry[sc_id] = hill
    
    def compute_corrections(self, chief_id: str
                           ) -> Dict[str, Tuple[float, float, float]]:
        """
        Compute corrections for all deputies.
        
        Args:
            chief_id: Chief spacecraft ID
        
        Returns:
            Map of sc_id -> delta-v
        """
        chief = self.spacecraft.get(chief_id)
        if not chief:
            return {}
        
        keeper = FormationKeeping()
        corrections = {}
        
        for sc_id, state in self.spacecraft.items():
            if sc_id == chief_id:
                continue
            desired = self.formation_geometry.get(sc_id, {"radial_km": 0, "along_track_km": 0.5, "cross_track_km": 0})
            dv = keeper.periodic_correction(chief, state, desired)
            corrections[sc_id] = dv
        
        return corrections
    
    def formation_error(self, chief_id: str) -> Dict[str, float]:
        """
        Compute formation errors.
        
        Args:
            chief_id: Chief ID
        
        Returns:
            Max errors per axis
        """
        chief = self.spacecraft.get(chief_id)
        if not chief:
            return {}
        
        max_err = {"radial": 0.0, "along_track": 0.0, "cross_track": 0.0, "range": 0.0}
        
        for sc_id, state in self.spacecraft.items():
            if sc_id == chief_id:
                continue
            hill = RelativeOrbitalElements.hill_frame(chief, state)
            desired = self.formation_geometry.get(sc_id, {})
            
            max_err["radial"] = max(max_err["radial"], abs(hill["radial_km"] - desired.get("radial_km", 0)))
            max_err["along_track"] = max(max_err["along_track"], abs(hill["along_track_km"] - desired.get("along_track_km", 0)))
            max_err["cross_track"] = max(max_err["cross_track"], abs(hill["cross_track_km"] - desired.get("cross_track_km", 0)))
            
            rel = RelativeOrbitalElements.compute_relative(chief, state)
            max_err["range"] = max(max_err["range"], rel["range_km"])
        
        return max_err


class FormationFlying:
    """
    Unified formation flying controller.
    """
    
    def __init__(self):
        self.coord = CoordinatedControl()
        self.keeper = FormationKeeping()
    
    def add_spacecraft(self, sc_id: str, position: Tuple[float, float, float],
                      velocity: Tuple[float, float, float]):
        """Add spacecraft to formation."""
        self.coord.register(sc_id, SpacecraftState(position, velocity, sc_id))
    
    def set_geometry(self, sc_id: str, radial: float = 0,
                    along_track: float = 0, cross_track: float = 0):
        """Set desired relative geometry."""
        self.coord.set_desired_geometry(sc_id, {
            "radial_km": radial,
            "along_track_km": along_track,
            "cross_track_km": cross_track
        })
    
    def compute_maneuvers(self, chief_id: str) -> Dict[str, Tuple[float, float, float]]:
        """Compute formation-keeping maneuvers."""
        return self.coord.compute_corrections(chief_id)
    
    def get_errors(self, chief_id: str) -> Dict[str, float]:
        """Get formation errors."""
        return self.coord.formation_error(chief_id)
    
    def get_relative_state(self, chief_id: str, deputy_id: str) -> Dict[str, float]:
        """Get relative state between two spacecraft."""
        chief = self.coord.spacecraft.get(chief_id)
        deputy = self.coord.spacecraft.get(deputy_id)
        if not chief or not deputy:
            return {}
        return RelativeOrbitalElements.compute_relative(chief, deputy)
    
    def flying_summary(self, chief_id: str) -> Dict:
        """Get formation summary."""
        errors = self.get_errors(chief_id)
        return {
            "spacecraft": len(self.coord.spacecraft),
            "max_range_km": errors.get("range", 0),
            "max_radial_err_km": errors.get("radial", 0),
            "max_along_err_km": errors.get("along_track", 0),
            "max_cross_err_km": errors.get("cross_track", 0)
        }
