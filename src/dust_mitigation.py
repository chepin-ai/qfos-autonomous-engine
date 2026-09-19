"""
Dust Mitigation Module
Dust detection, electrostatic removal, and surface
protection for autonomous systems operating in dusty environments.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class DustLevel(Enum):
    """Dust contamination level."""
    CLEAN = "clean"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    SEVERE = "severe"


class MitigationMethod(Enum):
    """Dust mitigation method."""
    ELECTROSTATIC = "electrostatic"
    PNEUMATIC = "pneumatic"
    BRUSH = "brush"
    VIBRATION = "vibration"
    COATING = "coating"


@dataclass
class DustReading:
    """A dust sensor reading."""
    sensor_id: str
    particle_count_per_cc: float
    particle_size_um: float
    opacity_percent: float
    timestamp: float = 0.0


class DustDetector:
    """
    Detect and quantify dust contamination.
    """
    
    def __init__(self, threshold_clean: float = 10.0,
                 threshold_light: float = 50.0,
                 threshold_moderate: float = 200.0,
                 threshold_heavy: float = 500.0):
        """
        Args:
            threshold_clean: Clean threshold (particles/cc)
            threshold_light: Light threshold
            threshold_moderate: Moderate threshold
            threshold_heavy: Heavy threshold
        """
        self.thresholds = {
            DustLevel.CLEAN: threshold_clean,
            DustLevel.LIGHT: threshold_light,
            DustLevel.MODERATE: threshold_moderate,
            DustLevel.HEAVY: threshold_heavy,
        }
        self.readings: List[DustReading] = []
    
    def add_reading(self, reading: DustReading):
        """Add sensor reading."""
        self.readings.append(reading)
    
    def assess_level(self, reading: DustReading) -> DustLevel:
        """
        Assess dust level from reading.
        
        Args:
            reading: Dust reading
        
        Returns:
            Dust level
        """
        count = reading.particle_count_per_cc
        
        if count <= self.thresholds[DustLevel.CLEAN]:
            return DustLevel.CLEAN
        elif count <= self.thresholds[DustLevel.LIGHT]:
            return DustLevel.LIGHT
        elif count <= self.thresholds[DustLevel.MODERATE]:
            return DustLevel.MODERATE
        elif count <= self.thresholds[DustLevel.HEAVY]:
            return DustLevel.HEAVY
        else:
            return DustLevel.SEVERE
    
    def average_opacity(self) -> float:
        """Get average opacity from readings."""
        if not self.readings:
            return 0.0
        return sum(r.opacity_percent for r in self.readings) / len(self.readings)
    
    def peak_particle_count(self) -> float:
        """Get peak particle count."""
        if not self.readings:
            return 0.0
        return max(r.particle_count_per_cc for r in self.readings)
    
    def clear_readings(self):
        """Clear all readings."""
        self.readings.clear()


class ElectrostaticRemover:
    """
    Electrostatic dust removal system.
    """
    
    def __init__(self, max_field_kV_m: float = 50.0,
                 coverage_area_m2: float = 2.0):
        """
        Args:
            max_field_kV_m: Maximum electric field
            coverage_area_m2: Coverage area
        """
        self.max_field = max_field_kV_m
        self.coverage = coverage_area_m2
        self.active = False
        self.current_field = 0.0
    
    def activate(self, target_field_kV_m: Optional[float] = None):
        """
        Activate electrostatic removal.
        
        Args:
            target_field_kV_m: Target field strength
        """
        self.active = True
        if target_field_kV_m is not None:
            self.current_field = min(target_field_kV_m, self.max_field)
        else:
            self.current_field = self.max_field * 0.8
    
    def deactivate(self):
        """Deactivate system."""
        self.active = False
        self.current_field = 0.0
    
    def removal_efficiency(self, particle_size_um: float) -> float:
        """
        Compute removal efficiency for particle size.
        
        Args:
            particle_size_um: Particle diameter
        
        Returns:
            Efficiency (0-1)
        """
        if not self.active:
            return 0.0
        
        # Efficiency increases with field and particle size
        field_factor = self.current_field / self.max_field
        size_factor = min(1.0, particle_size_um / 50.0)
        
        return field_factor * size_factor * 0.95
    
    def power_consumption_W(self) -> float:
        """Get power consumption."""
        if not self.active:
            return 0.0
        # Power proportional to field squared
        return 100.0 * (self.current_field / self.max_field) ** 2


class SurfaceProtection:
    """
    Surface coating and protection system.
    """
    
    def __init__(self, coating_thickness_um: float = 100.0):
        """
        Args:
            coating_thickness_um: Coating thickness
        """
        self.coating_thickness = coating_thickness_um
        self.coating_integrity = 1.0
        self.dust_accumulated_g = 0.0
    
    def apply_coating(self, thickness_um: float):
        """Apply or refresh coating."""
        self.coating_thickness = thickness_um
        self.coating_integrity = 1.0
    
    def accumulate_dust(self, mass_g: float):
        """Accumulate dust mass."""
        self.dust_accumulated_g += mass_g
        # Degrade coating with dust accumulation
        self.coating_integrity = max(0.0, 1.0 - self.dust_accumulated_g / 100.0)
    
    def clean_surface(self, removal_efficiency: float = 0.9):
        """
        Clean surface.
        
        Args:
            removal_efficiency: Cleaning efficiency
        """
        removed = self.dust_accumulated_g * removal_efficiency
        self.dust_accumulated_g -= removed
        self.coating_integrity = min(1.0, self.coating_integrity + 0.05)
    
    def protection_factor(self) -> float:
        """Get current protection factor."""
        return self.coating_integrity * min(1.0, self.coating_thickness / 100.0)


class DustMitigationController:
    """
    Unified dust mitigation controller.
    """
    
    def __init__(self):
        self.detector = DustDetector()
        self.es_remover = ElectrostaticRemover()
        self.protection = SurfaceProtection()
        self.active_methods: List[MitigationMethod] = []
    
    def add_reading(self, sensor_id: str, count_per_cc: float,
                   size_um: float, opacity: float):
        """Add dust reading."""
        reading = DustReading(sensor_id, count_per_cc, size_um, opacity)
        self.detector.add_reading(reading)
    
    def assess_situation(self) -> DustLevel:
        """Assess overall dust level."""
        if not self.detector.readings:
            return DustLevel.CLEAN
        
        # Use worst reading
        worst = DustLevel.CLEAN
        for reading in self.detector.readings:
            level = self.detector.assess_level(reading)
            if list(DustLevel).index(level) > list(DustLevel).index(worst):
                worst = level
        return worst
    
    def activate_mitigation(self, method: MitigationMethod):
        """Activate a mitigation method."""
        if method not in self.active_methods:
            self.active_methods.append(method)
        
        if method == MitigationMethod.ELECTROSTATIC:
            self.es_remover.activate()
    
    def deactivate_mitigation(self, method: MitigationMethod):
        """Deactivate a mitigation method."""
        if method in self.active_methods:
            self.active_methods.remove(method)
        
        if method == MitigationMethod.ELECTROSTATIC:
            self.es_remover.deactivate()
    
    def run_mitigation_cycle(self) -> Dict:
        """
        Run one mitigation cycle.
        
        Returns:
            Cycle results
        """
        level = self.assess_situation()
        
        # Auto-activate based on level
        if level in (DustLevel.HEAVY, DustLevel.SEVERE):
            self.activate_mitigation(MitigationMethod.ELECTROSTATIC)
        elif level == DustLevel.CLEAN:
            self.deactivate_mitigation(MitigationMethod.ELECTROSTATIC)
        
        # Calculate removal if active
        removed_mass = 0.0
        if MitigationMethod.ELECTROSTATIC in self.active_methods and \
           self.detector.readings:
            avg_size = sum(r.particle_size_um for r in self.detector.readings) / len(self.detector.readings)
            eff = self.es_remover.removal_efficiency(avg_size)
            removed_mass = self.protection.dust_accumulated_g * eff * 0.1
            self.protection.clean_surface(eff)
        
        return {
            "dust_level": level.value,
            "active_methods": [m.value for m in self.active_methods],
            "power_consumption_W": self.es_remover.power_consumption_W(),
            "removed_mass_g": removed_mass,
            "protection_factor": self.protection.protection_factor()
        }
    
    def mitigation_summary(self) -> Dict:
        """Get mitigation summary."""
        return {
            "dust_level": self.assess_situation().value,
            "avg_opacity": self.detector.average_opacity(),
            "peak_count": self.detector.peak_particle_count(),
            "active_methods": len(self.active_methods),
            "coating_integrity": self.protection.coating_integrity,
            "dust_accumulated_g": self.protection.dust_accumulated_g
        }
