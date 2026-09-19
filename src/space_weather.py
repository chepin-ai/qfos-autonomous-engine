"""
Space Weather Module
Models space environment effects on spacecraft operations.
Includes radiation environment, geomagnetic activity indices,
and spacecraft charging risk assessment.
"""

import math
from typing import Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class RadiationRiskLevel(Enum):
    """Radiation risk classification."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class GeomagneticIndices:
    """Geomagnetic activity indices."""
    kp: float  # 0-9 planetary K index
    ap: float  # 0-400 planetary A index
    dst_nt: float  # Disturbance storm time in nT
    
    def storm_level(self) -> str:
        """Classify geomagnetic storm level."""
        if self.dst_nt > -30:
            return "quiet"
        elif self.dst_nt > -50:
            return "weak"
        elif self.dst_nt > -100:
            return "moderate"
        elif self.dst_nt > -200:
            return "strong"
        else:
            return "severe"


@dataclass
class RadiationEnvironment:
    """Radiation environment at a given orbit."""
    proton_flux_cm2_s: float  # >10 MeV proton flux
    electron_flux_cm2_s: float  # >1 MeV electron flux
    total_dose_rad_day: float  # Total ionizing dose per day
    dose_rate_rad_hr: float  # Dose rate


class SpaceWeatherModel:
    """
    Space weather environment model for mission planning.
    
    Provides radiation environment estimates, geomagnetic storm
    impact assessment, and spacecraft charging risk analysis.
    """
    
    # Earth's radiation belt boundaries (approximate)
    INNER_BELT_L = 1.2  # Earth radii
    OUTER_BELT_L = 3.0  # Earth radii
    
    # Solar cycle parameters
    SOLAR_CYCLE_YEARS = 11.0
    
    def __init__(self):
        self.current_kp = 2.0
        self.current_ap = 5.0
        self.current_dst = -10.0
    
    def update_indices(self, kp: float, ap: float, dst_nt: float):
        """Update geomagnetic indices."""
        self.current_kp = kp
        self.current_ap = ap
        self.current_dst = dst_nt
    
    def get_indices(self) -> GeomagneticIndices:
        """Get current geomagnetic indices."""
        return GeomagneticIndices(
            kp=self.current_kp,
            ap=self.current_ap,
            dst_nt=self.current_dst
        )
    
    def radiation_at_altitude(self, altitude_km: float,
                               latitude_deg: float = 0.0,
                               solar_activity: str = "moderate") -> RadiationEnvironment:
        """
        Estimate radiation environment at given altitude.
        
        Args:
            altitude_km: Altitude above Earth's surface
            latitude_deg: Latitude in degrees
            solar_activity: "low", "moderate", "high"
        
        Returns:
            RadiationEnvironment estimate
        """
        re_km = 6378.0
        r = (re_km + altitude_km) / re_km  # L-shell approximation
        
        # Base fluxes
        if r < self.INNER_BELT_L:
            # Inner belt (high proton flux)
            proton_flux = 1.0e4
            electron_flux = 1.0e6
        elif r < self.OUTER_BELT_L:
            # Slot region
            proton_flux = 1.0e2
            electron_flux = 1.0e4
        elif r < 6.0:
            # Outer belt (high electron flux)
            proton_flux = 1.0e1
            electron_flux = 1.0e8
        else:
            # Beyond belts
            proton_flux = 1.0e0
            electron_flux = 1.0e3
        
        # Solar activity scaling
        solar_factor = {"low": 0.5, "moderate": 1.0, "high": 3.0}.get(solar_activity, 1.0)
        
        proton_flux *= solar_factor
        electron_flux *= solar_factor
        
        # Latitude effect (South Atlantic Anomaly)
        if -40.0 < latitude_deg < 0.0:
            proton_flux *= 5.0
            electron_flux *= 3.0
        
        # Dose estimates (simplified)
        total_dose = proton_flux * 1.0e-5 + electron_flux * 1.0e-7
        dose_rate = total_dose / 24.0
        
        return RadiationEnvironment(
            proton_flux_cm2_s=round(proton_flux, 2),
            electron_flux_cm2_s=round(electron_flux, 2),
            total_dose_rad_day=round(total_dose, 6),
            dose_rate_rad_hr=round(dose_rate, 8)
        )
    
    def charging_risk(self, spacecraft_potential_v: float = 0.0) -> Dict:
        """
        Assess spacecraft charging risk.
        
        Args:
            spacecraft_potential_v: Measured spacecraft potential
        
        Returns:
            Risk assessment dictionary
        """
        # High Kp increases charging risk
        kp_factor = self.current_kp / 9.0
        
        # Charging risk thresholds
        if spacecraft_potential_v < -1000:
            risk_level = "critical"
            risk_color = "red"
        elif spacecraft_potential_v < -500:
            risk_level = "high"
            risk_color = "orange"
        elif spacecraft_potential_v < -200:
            risk_level = "moderate"
            risk_color = "yellow"
        else:
            risk_level = "low"
            risk_color = "green"
        
        # Kp enhancement
        if self.current_kp >= 7:
            if risk_level == "low":
                risk_level = "moderate"
            elif risk_level == "moderate":
                risk_level = "high"
        
        return {
            "spacecraft_potential_v": spacecraft_potential_v,
            "kp": self.current_kp,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "kp_enhancement": kp_factor > 0.6,
            "recommendation": self._charging_recommendation(risk_level)
        }
    
    def _charging_recommendation(self, risk_level: str) -> str:
        """Get recommendation for charging risk level."""
        recommendations = {
            "low": "Normal operations. Monitor potential.",
            "moderate": "Increase monitoring. Verify grounding.",
            "high": "Consider safing. Check for discharges.",
            "critical": "IMMEDIATE SAFE MODE. Risk of discharge damage."
        }
        return recommendations.get(risk_level, "Monitor")
    
    def atmospheric_expansion_factor(self) -> float:
        """
        Compute atmospheric density enhancement factor from geomagnetic activity.
        
        High Kp causes thermospheric expansion, increasing drag.
        """
        # Simplified model: density increases with Ap
        base_factor = 1.0
        if self.current_ap > 50:
            base_factor += (self.current_ap - 50) / 100.0
        return round(base_factor, 3)
    
    def solar_panel_degradation_factor(self, years_in_orbit: float,
                                        shielding_mm: float = 1.0) -> float:
        """
        Estimate solar panel power degradation from radiation.
        
        Args:
            years_in_orbit: Mission duration
            shielding_mm: Coverglass thickness
        
        Returns:
            Remaining power fraction (0.0-1.0)
        """
        # Base degradation: ~3% per year for 1mm shielding in LEO
        annual_deg = 0.03 * (1.0 / max(shielding_mm, 0.1))
        
        # Solar cycle enhancement
        cycle_phase = (years_in_orbit % self.SOLAR_CYCLE_YEARS) / self.SOLAR_CYCLE_YEARS
        cycle_factor = 1.0 + 0.5 * math.sin(2.0 * math.pi * cycle_phase)
        
        total_deg = annual_deg * cycle_factor * years_in_orbit
        remaining = max(0.5, 1.0 - total_deg)
        
        return round(remaining, 4)
    
    def mission_risk_assessment(self, altitude_km: float,
                                 mission_duration_years: float,
                                 shielding_mm: float = 1.0) -> Dict:
        """
        Comprehensive mission risk assessment.
        
        Args:
            altitude_km: Orbit altitude
            mission_duration_years: Planned mission duration
            shielding_mm: Shielding thickness
        
        Returns:
            Risk assessment summary
        """
        rad_env = self.radiation_at_altitude(altitude_km)
        
        # Total mission dose
        total_mission_dose = rad_env.total_dose_rad_day * 365.25 * mission_duration_years
        
        # Solar panel degradation
        panel_remaining = self.solar_panel_degradation_factor(
            mission_duration_years, shielding_mm
        )
        
        # Risk classification
        if total_mission_dose > 100000:
            radiation_risk = RadiationRiskLevel.EXTREME
        elif total_mission_dose > 50000:
            radiation_risk = RadiationRiskLevel.HIGH
        elif total_mission_dose > 10000:
            radiation_risk = RadiationRiskLevel.MODERATE
        else:
            radiation_risk = RadiationRiskLevel.LOW
        
        return {
            "altitude_km": altitude_km,
            "mission_duration_years": mission_duration_years,
            "daily_dose_rad": rad_env.total_dose_rad_day,
            "total_mission_dose_rad": round(total_mission_dose, 2),
            "radiation_risk": radiation_risk.value,
            "panel_remaining_fraction": panel_remaining,
            "geomagnetic_storm_level": self.get_indices().storm_level(),
            "kp": self.current_kp,
            "atmospheric_expansion": self.atmospheric_expansion_factor()
        }
