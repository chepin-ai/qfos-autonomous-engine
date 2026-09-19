"""
Radiation Monitor Module
Radiation detection, dose calculation, and shielding assessment
for space environment monitoring.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class RadiationType(Enum):
    """Types of ionizing radiation."""
    GAMMA = "gamma"
    XRAY = "xray"
    PROTON = "proton"
    ELECTRON = "electron"
    NEUTRON = "neutron"
    HEAVY_ION = "heavy_ion"


@dataclass
class RadiationEvent:
    """A detected radiation event."""
    timestamp: float
    radiation_type: RadiationType
    energy_mev: float
    count: int = 1


class DoseCalculator:
    """
    Calculate radiation dose and equivalent dose.
    """
    
    # Quality factors for different radiation types
    QF = {
        RadiationType.GAMMA: 1.0,
        RadiationType.XRAY: 1.0,
        RadiationType.PROTON: 2.0,
        RadiationType.ELECTRON: 1.0,
        RadiationType.NEUTRON: 10.0,
        RadiationType.HEAVY_ION: 20.0,
    }
    
    def __init__(self):
        self.total_dose_gray = 0.0
        self.total_dose_sievert = 0.0
        self.dose_history: List[Tuple[float, float, float]] = []
        # (timestamp, gray, sievert)
    
    def add_measurement(self, timestamp: float,
                       flux_cm2s: float,
                       energy_mev: float,
                       rad_type: RadiationType,
                       exposure_time_s: float = 1.0):
        """
        Add radiation measurement.
        
        Args:
            timestamp: Time
            flux_cm2s: Particle flux (particles/cm^2/s)
            energy_mev: Energy per particle (MeV)
            rad_type: Radiation type
            exposure_time_s: Exposure duration
        """
        # Convert flux to dose rate (simplified)
        # Dose rate in Gy/s ≈ flux * energy * conversion
        # 1 MeV/g = 1.602e-13 J/g = 1.602e-10 Gy (for 1 g mass)
        # Simplified: dose_rate_Gy = flux * energy_MeV * 1.6e-13 * 10000 / density
        dose_rate = flux_cm2s * energy_mev * 1.6e-13 * 10000  # Gy/s for 1 g/cm^3
        
        dose_gray = dose_rate * exposure_time_s
        qf = self.QF.get(rad_type, 1.0)
        dose_sv = dose_gray * qf
        
        self.total_dose_gray += dose_gray
        self.total_dose_sievert += dose_sv
        self.dose_history.append((timestamp, dose_gray, dose_sv))
    
    def dose_rate(self, window_s: float = 60.0) -> float:
        """
        Compute average dose rate over window.
        
        Args:
            window_s: Time window (seconds)
        
        Returns:
            Dose rate (Gy/s)
        """
        if not self.dose_history:
            return 0.0
        
        now = self.dose_history[-1][0]
        recent = [h for h in self.dose_history if now - h[0] <= window_s]
        if not recent:
            return 0.0
        
        total_gray = sum(h[1] for h in recent)
        return total_gray / window_s
    
    def annual_equivalent(self, extrapolate: bool = True) -> float:
        """
        Estimate annual equivalent dose.
        
        Args:
            extrapolate: Whether to extrapolate from history
        
        Returns:
            Annual dose (Sv/year)
        """
        if not self.dose_history:
            return 0.0
        
        total_time = self.dose_history[-1][0] - self.dose_history[0][0]
        if total_time <= 0:
            return self.total_dose_sievert * 3.154e7  # annualize single point
        
        rate = self.total_dose_sievert / total_time
        return rate * 3.154e7  # seconds per year


class ShieldingAssessor:
    """
    Assess shielding effectiveness.
    """
    
    # Half-value layers (cm) for aluminum at 1 MeV
    HVL = {
        RadiationType.GAMMA: 1.5,
        RadiationType.XRAY: 0.5,
        RadiationType.PROTON: 2.0,
        RadiationType.ELECTRON: 0.3,
        RadiationType.NEUTRON: 5.0,
        RadiationType.HEAVY_ION: 0.1,
    }
    
    def transmission(self, thickness_cm: float,
                    rad_type: RadiationType) -> float:
        """
        Compute radiation transmission through shielding.
        
        Args:
            thickness_cm: Shield thickness (cm)
            rad_type: Radiation type
        
        Returns:
            Transmission fraction (0-1)
        """
        hvl = self.HVL.get(rad_type, 1.0)
        if hvl <= 0:
            return 0.0
        return 0.5 ** (thickness_cm / hvl)
    
    def required_thickness(self, desired_transmission: float,
                          rad_type: RadiationType) -> float:
        """
        Compute required shield thickness.
        
        Args:
            desired_transmission: Desired transmission (0-1)
            rad_type: Radiation type
        
        Returns:
            Required thickness (cm)
        """
        if desired_transmission <= 0:
            return float('inf')
        if desired_transmission >= 1:
            return 0.0
        hvl = self.HVL.get(rad_type, 1.0)
        return hvl * math.log(desired_transmission) / math.log(0.5)
    
    def assess_protection(self, shield_thickness_cm: float,
                         events: List[RadiationEvent]) -> float:
        """
        Assess overall protection level.
        
        Args:
            shield_thickness_cm: Shield thickness
            events: Radiation events
        
        Returns:
            Protection score (0-1)
        """
        if not events:
            return 1.0
        
        total_count = sum(e.count for e in events)
        transmitted = sum(
            e.count * self.transmission(shield_thickness_cm, e.radiation_type)
            for e in events
        )
        
        if total_count <= 0:
            return 1.0
        
        return 1.0 - (transmitted / total_count)


class RadiationDetector:
    """
    Simulate radiation detector behavior.
    """
    
    def __init__(self, efficiency: float = 0.8,
                 energy_threshold_mev: float = 0.01):
        """
        Args:
            efficiency: Detection efficiency (0-1)
            energy_threshold_mev: Minimum detectable energy
        """
        self.efficiency = efficiency
        self.threshold = energy_threshold_mev
        self.event_count = 0
        self.total_counts = 0
    
    def detect(self, event: RadiationEvent) -> bool:
        """
        Detect a radiation event.
        
        Args:
            event: Radiation event
        
        Returns:
            True if detected
        """
        if event.energy_mev < self.threshold:
            return False
        
        import random
        if random.random() < self.efficiency:
            self.event_count += 1
            self.total_counts += event.count
            return True
        return False
    
    def count_rate(self, time_window_s: float) -> float:
        """
        Compute count rate.
        
        Args:
            time_window_s: Time window
        
        Returns:
            Counts per second
        """
        if time_window_s <= 0:
            return 0.0
        return self.total_counts / time_window_s


class RadiationMonitor:
    """
    Unified radiation monitoring controller.
    """
    
    def __init__(self):
        self.dose_calc = DoseCalculator()
        self.shielding = ShieldingAssessor()
        self.detector = RadiationDetector()
        self.events: List[RadiationEvent] = []
        self.shield_thickness_cm = 0.5
    
    def record_event(self, event: RadiationEvent,
                    flux_cm2s: float = 1.0,
                    exposure_time_s: float = 1.0):
        """
        Record radiation event.
        
        Args:
            event: Radiation event
            flux_cm2s: Particle flux
            exposure_time_s: Exposure time
        """
        self.events.append(event)
        self.dose_calc.add_measurement(
            event.timestamp, flux_cm2s, event.energy_mev,
            event.radiation_type, exposure_time_s
        )
        self.detector.detect(event)
    
    def set_shielding(self, thickness_cm: float):
        """Set shielding thickness."""
        self.shield_thickness_cm = thickness_cm
    
    def get_dose(self) -> Dict[str, float]:
        """Get current dose readings."""
        return {
            "total_gray": self.dose_calc.total_dose_gray,
            "total_sievert": self.dose_calc.total_dose_sievert,
            "dose_rate_Gy_per_s": self.dose_calc.dose_rate(),
            "annual_equivalent_Sv": self.dose_calc.annual_equivalent()
        }
    
    def get_protection(self) -> float:
        """Get protection score."""
        return self.shielding.assess_protection(self.shield_thickness_cm, self.events)
    
    def is_safe(self, limit_sv: float = 0.05) -> bool:
        """
        Check if radiation level is safe.
        
        Args:
            limit_sv: Dose limit (Sv)
        
        Returns:
            True if safe
        """
        return self.dose_calc.total_dose_sievert < limit_sv
    
    def monitor_summary(self) -> Dict:
        """Get monitor summary."""
        return {
            "events_recorded": len(self.events),
            "total_counts": self.detector.total_counts,
            "shield_thickness_cm": self.shield_thickness_cm,
            "protection_score": self.get_protection(),
            **self.get_dose()
        }
