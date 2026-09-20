"""
Surface Tension Measurement Module
Wilhelmy plate, pendant drop, capillary rise, du Noüy ring,
and interfacial tension measurement for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TensionReading:
    """Surface tension reading."""
    method: str
    value_mN_m: float
    temperature_C: float
    timestamp_ms: float


class WilhelmyPlate:
    """
    Wilhelmy plate method for surface tension.
    """
    
    def __init__(self, plate_width_mm: float = 19.9,
                 plate_thickness_mm: float = 0.2,
                 contact_angle_deg: float = 0.0):
        """
        Args:
            plate_width_mm: Plate width
            plate_thickness_mm: Plate thickness
            contact_angle_deg: Contact angle
        """
        self.width = plate_width_mm
        self.thickness = plate_thickness_mm
        self.contact_angle = math.radians(contact_angle_deg)
    
    def perimeter_mm(self) -> float:
        """
        Compute plate perimeter.
        
        Returns:
            Perimeter in mm
        """
        return 2.0 * (self.width + self.thickness)
    
    def surface_tension(self, force_mN: float) -> float:
        """
        Compute surface tension from force.
        
        Args:
            force_mN: Force in mN
        
        Returns:
            Surface tension in mN/m
        """
        p = self.perimeter_mm()
        if p <= 0 or math.cos(self.contact_angle) <= 0:
            return 0.0
        return force_mN / (p * math.cos(self.contact_angle))
    
    def force_from_tension(self, tension_mN_m: float) -> float:
        """
        Compute force from surface tension.
        
        Args:
            tension_mN_m: Surface tension
        
        Returns:
            Force in mN
        """
        p = self.perimeter_mm()
        return tension_mN_m * p * math.cos(self.contact_angle)


class PendantDropAnalyzer:
    """
    Analyze pendant drop for surface tension.
    """
    
    def __init__(self, density_g_cm3: float = 1.0):
        """
        Args:
            density_g_cm3: Liquid density
        """
        self.density = density_g_cm3  # g/cm3
    
    def bond_number(self, drop_diameter_mm: float,
                   apex_radius_mm: float) -> float:
        """
        Compute Bond number from drop shape.
        
        Args:
            drop_diameter_mm: Maximum diameter
            apex_radius_mm: Apex radius
        
        Returns:
            Bond number
        """
        if apex_radius_mm <= 0:
            return 0.0
        # Simplified: Bo = (rho * g * De^2) / gamma
        # Using shape factor S = De / (2 * apex_radius)
        return (drop_diameter_mm / (2.0 * apex_radius_mm)) ** 2
    
    def surface_tension_from_drop(self, drop_diameter_mm: float,
                                  apex_radius_mm: float) -> float:
        """
        Estimate surface tension from pendant drop.
        
        Args:
            drop_diameter_mm: Maximum diameter
            apex_radius_mm: Apex radius
        
        Returns:
            Surface tension in mN/m
        """
        if apex_radius_mm <= 0:
            return 0.0
        # Simplified calculation
        g_cm_s2 = 980.665  # cm/s2
        # Convert mm to cm
        de_cm = drop_diameter_mm / 10.0
        ra_cm = apex_radius_mm / 10.0
        
        # gamma = rho * g * de^2 / H where H depends on shape
        # Simplified approximation
        bond = self.bond_number(drop_diameter_mm, apex_radius_mm)
        if bond <= 0:
            return 0.0
        
        gamma = self.density * g_cm_s2 * (de_cm ** 2) / bond
        return gamma


class CapillaryRise:
    """
    Capillary rise method for surface tension.
    """
    
    def __init__(self, capillary_radius_mm: float = 0.5,
                 contact_angle_deg: float = 0.0):
        """
        Args:
            capillary_radius_mm: Tube radius
            contact_angle_deg: Contact angle
        """
        self.radius = capillary_radius_mm
        self.contact_angle = math.radians(contact_angle_deg)
    
    def surface_tension(self, rise_height_mm: float,
                       density_g_cm3: float = 1.0) -> float:
        """
        Compute surface tension from capillary rise.
        
        Args:
            rise_height_mm: Rise height
            density_g_cm3: Liquid density
        
        Returns:
            Surface tension in mN/m
        """
        if self.radius <= 0 or rise_height_mm <= 0:
            return 0.0
        
        g = 9.80665  # m/s2
        # h in m, r in m
        h = rise_height_mm / 1000.0
        r = self.radius / 1000.0
        rho = density_g_cm3 * 1000.0  # kg/m3
        
        cos_theta = math.cos(self.contact_angle)
        if cos_theta <= 0:
            return 0.0
        
        return (rho * g * h * r) / (2.0 * cos_theta)


class DuNouyRing:
    """
    Du Noüy ring method for surface tension.
    """
    
    def __init__(self, ring_radius_mm: float = 9.5,
                 wire_radius_mm: float = 0.185):
        """
        Args:
            ring_radius_mm: Ring radius
            wire_radius_mm: Wire radius
        """
        self.ring_radius = ring_radius_mm
        self.wire_radius = wire_radius_mm
    
    def ring_perimeter_mm(self) -> float:
        """
        Compute ring perimeter.
        
        Returns:
            Perimeter in mm
        """
        return 2.0 * math.pi * self.ring_radius
    
    def surface_tension(self, force_mN: float,
                       correction_factor: float = 1.0) -> float:
        """
        Compute surface tension from force.
        
        Args:
            force_mN: Force in mN
            correction_factor: Correction factor
        
        Returns:
            Surface tension in mN/m
        """
        p = self.ring_perimeter_mm()
        if p <= 0:
            return 0.0
        return force_mN / (p * correction_factor)


class InterfacialTension:
    """
    Measure interfacial tension between two liquids.
    """
    
    def __init__(self):
        self.readings: List[TensionReading] = []
    
    def measure(self, tension_mN_m: float,
               method: str = "pendant_drop",
               temperature_C: float = 20.0) -> TensionReading:
        """
        Record interfacial tension.
        
        Args:
            tension_mN_m: Tension
            method: Method
            temperature_C: Temperature
        
        Returns:
            Reading
        """
        import time as time_mod
        reading = TensionReading(method, tension_mN_m, temperature_C,
                                 time_mod.time() * 1000)
        self.readings.append(reading)
        return reading
    
    def average_tension(self) -> float:
        """
        Compute average tension.
        
        Returns:
            Average in mN/m
        """
        if not self.readings:
            return 0.0
        return sum(r.value_mN_m for r in self.readings) / len(self.readings)


class SurfaceTensionMeasurement:
    """
    Unified surface tension measurement controller.
    """
    
    def __init__(self):
        self.wilhelmy = WilhelmyPlate()
        self.pendant = PendantDropAnalyzer()
        self.capillary = CapillaryRise()
        self.ring = DuNouyRing()
        self.interfacial = InterfacialTension()
    
    def measure_all_methods(self, sample_params: Dict) -> Dict:
        """
        Measure using all methods.
        
        Args:
            sample_params: Parameters
        
        Returns:
            Results
        """
        results = {}
        
        if "force_mN" in sample_params:
            results["wilhelmy_mN_m"] = self.wilhelmy.surface_tension(
                sample_params["force_mN"])
        
        if "drop_diameter_mm" in sample_params:
            results["pendant_mN_m"] = self.pendant.surface_tension_from_drop(
                sample_params["drop_diameter_mm"],
                sample_params.get("apex_radius_mm", 1.0))
        
        if "rise_height_mm" in sample_params:
            results["capillary_mN_m"] = self.capillary.surface_tension(
                sample_params["rise_height_mm"],
                sample_params.get("density_g_cm3", 1.0))
        
        if "ring_force_mN" in sample_params:
            results["ring_mN_m"] = self.ring.surface_tension(
                sample_params["ring_force_mN"],
                sample_params.get("correction", 1.0))
        
        return results
    
    def stm_summary(self) -> Dict:
        """Get summary."""
        return {
            "methods": ["wilhelmy", "pendant", "capillary", "ring"],
            "interfacial_readings": len(self.interfacial.readings)
        }
