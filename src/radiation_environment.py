"""
Radiation Environment Module
Model spacecraft radiation environment: Van Allen belts,
solar particle events, galactic cosmic rays, shielding effects.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ParticleType(Enum):
    """Types of radiation particles."""
    ELECTRON = "electron"
    PROTON = "proton"
    GCR_HEAVY = "gcr_heavy"
    SOLAR_PROTON = "solar_proton"


@dataclass
class RadiationDose:
    """Radiation dose estimate."""
    total_dose_krad: float
    dose_rate_krad_day: float
    component_doses: Dict[str, float]
    shielding_thickness_mm: float
    material: str


class RadiationEnvironment:
    """
    Radiation environment model for spacecraft.
    
    Computes total ionizing dose (TID) and single-event
    effects from electrons, protons, and heavy ions.
    """
    
    # Nominal dose rates at 1mm Al shielding (krad/day)
    # Based on NASA AP8/AE8 models for average solar conditions
    BELT_DOSE_RATES = {
        "inner_proton": 5.0e-3,      # Inner belt protons
        "outer_electron": 2.0e-4,    # Outer belt electrons
        "solar_min_gcr": 1.0e-4,     # GCR at solar minimum
        "solar_max_gcr": 3.0e-5,     # GCR at solar maximum
    }
    
    # Shielding attenuation coefficient (per mm Al)
    ATTENUATION_PER_MM = {
        ParticleType.ELECTRON: 0.15,
        ParticleType.PROTON: 0.05,
        ParticleType.GCR_HEAVY: 0.02,
        ParticleType.SOLAR_PROTON: 0.03,
    }
    
    def __init__(self, altitude_km: float,
                 inclination_deg: float = 0.0,
                 shielding_mm_al: float = 1.0):
        """
        Args:
            altitude_km: Orbit altitude
            inclination_deg: Orbit inclination
            shielding_mm_al: Aluminum shielding thickness
        """
        self.altitude_km = altitude_km
        self.inclination_deg = inclination_deg
        self.shielding_mm = shielding_mm_al
    
    def _attenuation_factor(self, particle: ParticleType) -> float:
        """Compute shielding attenuation factor."""
        coeff = self.ATTENUATION_PER_MM.get(particle, 0.05)
        return math.exp(-coeff * self.shielding_mm)
    
    def _belt_dose_rate(self) -> float:
        """Compute trapped radiation dose rate."""
        h = self.altitude_km
        
        # Inner belt: ~1000-5000 km
        # Peak at ~3000 km
        if 500.0 <= h <= 7000.0:
            inner_belt_factor = math.exp(-((h - 3000.0) / 1500.0) ** 2)
        else:
            inner_belt_factor = 0.0
        
        # Outer belt: ~13000-25000 km
        # Peak at ~18000 km
        if 10000.0 <= h <= 30000.0:
            outer_belt_factor = math.exp(-((h - 18000.0) / 4000.0) ** 2)
        else:
            outer_belt_factor = 0.0
        
        # Electron attenuation stronger than proton
        electron_atten = self._attenuation_factor(ParticleType.ELECTRON)
        proton_atten = self._attenuation_factor(ParticleType.PROTON)
        
        proton_dose = self.BELT_DOSE_RATES["inner_proton"] * inner_belt_factor * proton_atten
        electron_dose = self.BELT_DOSE_RATES["outer_electron"] * outer_belt_factor * electron_atten
        
        return proton_dose + electron_dose
    
    def _gcr_dose_rate(self, solar_maximum: bool = False) -> float:
        """Compute GCR dose rate."""
        base_rate = (self.BELT_DOSE_RATES["solar_max_gcr"] if solar_maximum
                     else self.BELT_DOSE_RATES["solar_min_gcr"])
        attenuation = self._attenuation_factor(ParticleType.GCR_HEAVY)
        return base_rate * attenuation
    
    def total_dose_rate_krad_day(self, mission_days: float = 0.0,
                                  solar_maximum: bool = False) -> float:
        """
        Compute total dose rate.
        
        Args:
            mission_days: Days since mission start (for SPE decay)
            solar_maximum: Solar maximum conditions
        
        Returns:
            Dose rate in krad/day
        """
        belt = self._belt_dose_rate()
        gcr = self._gcr_dose_rate(solar_maximum)
        
        # Solar particle event contribution
        spe = self.solar_particle_event_dose(mission_days)
        
        return belt + gcr + spe
    
    def solar_particle_event_dose(self, mission_days: float) -> float:
        """
        Estimate SPE dose contribution.
        
        Args:
            mission_days: Mission elapsed time
        
        Returns:
            SPE dose rate in krad/day
        """
        # Simplified: ~1 major SPE per year during solar max
        # Average contribution ~1e-3 krad/day at 1mm Al
        base_spe = 1.0e-3
        attenuation = self._attenuation_factor(ParticleType.SOLAR_PROTON)
        
        # Modulate with solar cycle
        solar_phase = math.sin(2.0 * math.pi * mission_days / (11.0 * 365.25))
        modulation = 0.5 + 0.5 * solar_phase
        
        return base_spe * attenuation * modulation
    
    def mission_total_dose(self, mission_duration_days: float,
                           solar_maximum: bool = False) -> RadiationDose:
        """
        Compute total mission dose.
        
        Args:
            mission_duration_days: Mission duration
            solar_maximum: Solar maximum conditions
        
        Returns:
            RadiationDose estimate
        """
        # Average dose rate over mission
        avg_rate = self.total_dose_rate_krad_day(mission_duration_days / 2.0, solar_maximum)
        
        total_dose = avg_rate * mission_duration_days
        
        component_doses = {
            "trapped_radiation": round(self._belt_dose_rate() * mission_duration_days, 4),
            "galactic_cosmic_rays": round(self._gcr_dose_rate(solar_maximum) * mission_duration_days, 4),
            "solar_particle_events": round(
                self.solar_particle_event_dose(mission_duration_days / 2.0) * mission_duration_days, 4
            )
        }
        
        return RadiationDose(
            total_dose_krad=round(total_dose, 4),
            dose_rate_krad_day=round(avg_rate, 6),
            component_doses=component_doses,
            shielding_thickness_mm=self.shielding_mm,
            material="Aluminum"
        )
    
    def shielding_optimization(self, target_dose_krad: float,
                               mission_days: float,
                               max_thickness_mm: float = 10.0) -> Dict:
        """
        Find minimum shielding for target dose.
        
        Args:
            target_dose_krad: Maximum acceptable dose
            mission_days: Mission duration
            max_thickness_mm: Maximum shielding thickness
        
        Returns:
            Optimization result
        """
        original_shielding = self.shielding_mm
        
        best_thickness = max_thickness_mm
        best_dose = float('inf')
        
        for thickness in [0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0]:
            if thickness > max_thickness_mm:
                break
            
            self.shielding_mm = thickness
            dose = self.mission_total_dose(mission_days).total_dose_krad
            
            if dose <= target_dose_krad and thickness < best_thickness:
                best_thickness = thickness
                best_dose = dose
        
        self.shielding_mm = original_shielding
        
        return {
            "required_shielding_mm": best_thickness,
            "achieved_dose_krad": round(best_dose, 4),
            "target_dose_krad": target_dose_krad,
            "mission_days": mission_days,
            "feasible": best_dose <= target_dose_krad
        }
    
    def component_radiation_tolerance(self, component_type: str) -> float:
        """
        Get typical radiation tolerance for component type.
        
        Args:
            component_type: Component type string
        
        Returns:
            Typical tolerance in krad
        """
        tolerances = {
            "commercial_cmos": 5.0,
            "radiation_tolerant": 50.0,
            "radiation_hardened": 300.0,
            "power_mosfet": 100.0,
            "solar_cell_gaas": 1000.0,
            "solar_cell_si": 100.0,
            "optoelectronics": 10.0,
            "memory_sram": 50.0,
            "memory_dram": 20.0,
            "fpga": 30.0,
        }
        return tolerances.get(component_type.lower(), 50.0)
    
    def survivability_assessment(self, mission_days: float,
                                  components: List[Dict]) -> Dict:
        """
        Assess component survivability.
        
        Args:
            mission_days: Mission duration
            components: List of dicts with name, type, shielding_mm
        
        Returns:
            Assessment result
        """
        dose = self.mission_total_dose(mission_days)
        
        component_results = []
        all_survive = True
        
        for comp in components:
            name = comp.get("name", "Unknown")
            comp_type = comp.get("type", "radiation_tolerant")
            comp_shielding = comp.get("shielding_mm", self.shielding_mm)
            
            tolerance = self.component_radiation_tolerance(comp_type)
            
            # Adjust dose for component-specific shielding
            ratio = comp_shielding / self.shielding_mm if self.shielding_mm > 0 else 1.0
            adjusted_dose = dose.total_dose_krad * math.exp(-0.05 * (comp_shielding - self.shielding_mm))
            
            margin = tolerance / adjusted_dose if adjusted_dose > 0 else float('inf')
            survives = adjusted_dose < tolerance
            
            if not survives:
                all_survive = False
            
            component_results.append({
                "name": name,
                "type": comp_type,
                "tolerance_krad": tolerance,
                "projected_dose_krad": round(adjusted_dose, 4),
                "margin": round(margin, 2),
                "status": "OK" if survives else "MARGINAL" if margin > 0.5 else "FAIL"
            })
        
        return {
            "all_survive": all_survive,
            "mission_dose_krad": dose.total_dose_krad,
            "components": component_results
        }
