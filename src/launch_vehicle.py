"""
Launch Vehicle Module
Model launch vehicle performance, payload capacity,
and mission design for orbital insertion.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class OrbitCapability:
    """Launch vehicle capability to a specific orbit."""
    orbit_type: str
    altitude_km: float
    inclination_deg: float
    payload_mass_kg: float
    delta_v_reserve_ms: float = 0.0


class LaunchVehicle:
    """
    Launch vehicle performance model.
    
    Provides payload mass to orbit for various
    target orbits and mission parameters.
    """
    
    # Reference parameters for delta-V scaling
    LEO_REF_ALT_KM = 200.0
    LEO_REF_INC_DEG = 28.5
    
    def __init__(self, name: str, leo_payload_kg: float,
                 gto_payload_kg: float = 0.0,
                 geo_payload_kg: float = 0.0,
                 tli_payload_kg: float = 0.0,
                 launch_site_lat_deg: float = 28.5):
        """
        Args:
            name: Vehicle name
            leo_payload_kg: LEO reference payload
            gto_payload_kg: GTO payload
            geo_payload_kg: Direct GEO payload
            tli_payload_kg: Trans-lunar injection payload
            launch_site_lat_deg: Launch site latitude
        """
        self.name = name
        self.leo_payload_kg = leo_payload_kg
        self.gto_payload_kg = gto_payload_kg
        self.geo_payload_kg = geo_payload_kg
        self.tli_payload_kg = tli_payload_kg
        self.launch_site_lat_deg = launch_site_lat_deg
    
    def _delta_v_penalty(self, target_altitude_km: float,
                         target_inclination_deg: float) -> float:
        """
        Compute delta-V penalty for non-reference orbit.
        
        Args:
            target_altitude_km: Target altitude
            target_inclination_deg: Target inclination
        
        Returns:
            Delta-V penalty in m/s
        """
        penalty = 0.0
        
        # Inclination change penalty
        d_inc = abs(target_inclination_deg - self.launch_site_lat_deg)
        if d_inc > 0.0:
            # Approximate: plane change at LEO velocity
            v_leo = 7780.0  # m/s
            penalty += 2.0 * v_leo * math.sin(math.radians(d_inc) / 2.0)
        
        # Altitude penalty (circularization)
        if target_altitude_km > self.LEO_REF_ALT_KM:
            # Hohmann-like delta-V to raise orbit
            from orbital_mechanics import hohmann_transfer_delta_v
            r1 = (6378.0 + self.LEO_REF_ALT_KM)
            r2 = (6378.0 + target_altitude_km)
            dv, _ = hohmann_transfer_delta_v(r1, r2)
            penalty += dv * 1000.0  # Convert to m/s
        
        return penalty
    
    def payload_to_leo(self, altitude_km: float = 200.0,
                       inclination_deg: float = 28.5) -> float:
        """
        Compute LEO payload capacity.
        
        Args:
            altitude_km: Target altitude
            inclination_deg: Target inclination
        
        Returns:
            Payload mass in kg
        """
        if inclination_deg == self.launch_site_lat_deg and altitude_km == self.LEO_REF_ALT_KM:
            return self.leo_payload_kg
        
        # Scale with delta-V penalty
        penalty = self._delta_v_penalty(altitude_km, inclination_deg)
        
        # Simple exponential scaling
        # Typical penalty: ~1500 m/s for SSO from Cape Canaveral
        # Payload loss: ~50% for 1500 m/s penalty
        scale_factor = math.exp(-penalty / 3000.0)
        
        return self.leo_payload_kg * scale_factor
    
    def payload_to_gto(self, apogee_km: float = 35786.0,
                       inclination_deg: float = 27.0) -> float:
        """
        Compute GTO payload capacity.
        
        Args:
            apogee_km: Apogee altitude
            inclination_deg: Inclination
        
        Returns:
            Payload mass in kg
        """
        if self.gto_payload_kg > 0.0:
            base = self.gto_payload_kg
        else:
            # Estimate from LEO: GTO is ~1/3 of LEO
            base = self.leo_payload_kg / 3.0
        
        # Adjust for apogee
        ref_apogee = 35786.0
        if apogee_km != ref_apogee:
            # Higher apogee = less payload
            base *= math.sqrt(ref_apogee / apogee_km)
        
        return base
    
    def payload_to_geo(self) -> float:
        """Direct GEO payload."""
        if self.geo_payload_kg > 0.0:
            return self.geo_payload_kg
        # Estimate: ~1/2 of GTO
        return self.payload_to_gto() / 2.0
    
    def payload_to_sso(self, altitude_km: float = 600.0) -> float:
        """
        SSO payload (typically from Vandenberg).
        
        Args:
            altitude_km: SSO altitude
        
        Returns:
            Payload mass in kg
        """
        # SSO from ~34.6N (Vandenberg) or ~5N (equatorial)
        sso_inclination = 98.0  # Typical SSO
        return self.payload_to_leo(altitude_km, sso_inclination)
    
    def mission_analysis(self, target_mass_kg: float,
                         target_altitude_km: float,
                         target_inclination_deg: float) -> Dict:
        """
        Analyze mission feasibility.
        
        Args:
            target_mass_kg: Required payload mass
            target_altitude_km: Target altitude
            target_inclination_deg: Target inclination
        
        Returns:
            Analysis result
        """
        capacity = self.payload_to_leo(target_altitude_km, target_inclination_deg)
        margin = capacity - target_mass_kg
        
        penalty = self._delta_v_penalty(target_altitude_km, target_inclination_deg)
        
        return {
            "vehicle": self.name,
            "target_mass_kg": target_mass_kg,
            "capacity_kg": round(capacity, 1),
            "margin_kg": round(margin, 1),
            "margin_percent": round(margin / capacity * 100.0, 1) if capacity > 0 else 0.0,
            "feasible": margin >= 0.0,
            "delta_v_penalty_ms": round(penalty, 1),
            "target_altitude_km": target_altitude_km,
            "target_inclination_deg": target_inclination_deg,
            "launch_site_latitude_deg": self.launch_site_lat_deg
        }
    
    @staticmethod
    def falcon_9() -> 'LaunchVehicle':
        """SpaceX Falcon 9 performance."""
        return LaunchVehicle(
            name="Falcon 9",
            leo_payload_kg=22800.0,
            gto_payload_kg=8300.0,
            geo_payload_kg=0.0,
            tli_payload_kg=4000.0,
            launch_site_lat_deg=28.5
        )
    
    @staticmethod
    def falcon_heavy() -> 'LaunchVehicle':
        """SpaceX Falcon Heavy performance."""
        return LaunchVehicle(
            name="Falcon Heavy",
            leo_payload_kg=63800.0,
            gto_payload_kg=26700.0,
            geo_payload_kg=0.0,
            tli_payload_kg=16000.0,
            launch_site_lat_deg=28.5
        )
    
    @staticmethod
    def ariane_64() -> 'LaunchVehicle':
        """Ariane 64 performance."""
        return LaunchVehicle(
            name="Ariane 64",
            leo_payload_kg=21650.0,
            gto_payload_kg=11500.0,
            geo_payload_kg=0.0,
            launch_site_lat_deg=5.2
        )
    
    @staticmethod
    def compare_vehicles(vehicles: List['LaunchVehicle'],
                         target_altitude_km: float,
                         target_inclination_deg: float) -> List[Dict]:
        """
        Compare multiple launch vehicles.
        
        Args:
            vehicles: List of LaunchVehicle
            target_altitude_km: Target altitude
            target_inclination_deg: Target inclination
        
        Returns:
            Sorted comparison results
        """
        results = []
        for vehicle in vehicles:
            capacity = vehicle.payload_to_leo(target_altitude_km, target_inclination_deg)
            results.append({
                "name": vehicle.name,
                "capacity_kg": round(capacity, 1),
                "leo_capacity_kg": vehicle.leo_payload_kg,
                "launch_site_lat_deg": vehicle.launch_site_lat_deg
            })
        
        results.sort(key=lambda x: x["capacity_kg"], reverse=True)
        return results
