"""
Resource Assessment Module
Evaluate in-situ resources: subsurface ice, regolith composition,
water content, and extractable materials for ISRU planning.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SubsurfaceReading:
    """A subsurface sensor reading."""
    lat_deg: float
    lon_deg: float
    depth_m: float
    dielectric_constant: float
    attenuation_db_m: float
    temperature_k: float


@dataclass
class ResourceDeposit:
    """Identified resource deposit."""
    name: str
    lat_deg: float
    lon_deg: float
    depth_range_m: Tuple[float, float]
    estimated_volume_m3: float
    purity_percent: float
    resource_type: str  # water_ice, regolith_minerals, etc.
    confidence: float  # 0.0-1.0


class GroundPenetratingRadar:
    """
    Ground-penetrating radar for subsurface ice detection.
    """
    
    # Dielectric constants
    EPSILON_DRY_REGOLITH = 2.5
    EPSILON_WATER_ICE = 3.2
    EPSILON_LIQUID_WATER = 80.0
    
    def __init__(self, frequency_mhz: float = 20.0,
                 antenna_gain_db: float = 10.0,
                 transmit_power_w: float = 50.0):
        """
        Args:
            frequency_mhz: Operating frequency
            antenna_gain_db: Antenna gain
            transmit_power_w: Transmit power
        """
        self.frequency_mhz = frequency_mhz
        self.antenna_gain = antenna_gain_db
        self.transmit_power = transmit_power_w
        self.wavelength_m = 300.0 / frequency_mhz
    
    def simulate_reading(self, lat_deg: float, lon_deg: float,
                         ice_purity: float = 0.0,
                         depth_ice_m: float = 0.0) -> SubsurfaceReading:
        """
        Simulate GPR reading at location.
        
        Args:
            lat_deg, lon_deg: Position
            ice_purity: Ice fraction (0.0-1.0)
            depth_ice_m: Ice layer depth
        
        Returns:
            Subsurface reading
        """
        # Dielectric constant varies with ice content
        epsilon = (self.EPSILON_DRY_REGOLITH * (1.0 - ice_purity) +
                   self.EPSILON_WATER_ICE * ice_purity)
        
        # Attenuation increases with depth and ice
        attenuation = 0.1 + depth_ice_m * 0.05 + ice_purity * 0.3
        
        # Temperature
        temp = 210.0 - ice_purity * 30.0  # K
        
        return SubsurfaceReading(
            lat_deg=lat_deg, lon_deg=lon_deg,
            depth_m=depth_ice_m,
            dielectric_constant=round(epsilon, 2),
            attenuation_db_m=round(attenuation, 3),
            temperature_k=round(temp, 1)
        )
    
    def detect_ice(self, reading: SubsurfaceReading,
                   threshold_epsilon: float = 3.0) -> Dict:
        """
        Detect ice from reading.
        
        Args:
            reading: GPR reading
            threshold_epsilon: Dielectric threshold for ice
        
        Returns:
            Detection result
        """
        detected = reading.dielectric_constant > threshold_epsilon
        # Confidence from dielectric constant: dry=2.5, pure ice=3.2
        confidence = min(1.0, max(0.0, (reading.dielectric_constant - 2.5) / 0.7))
        
        return {
            "ice_detected": detected,
            "confidence": round(confidence, 3),
            "estimated_depth_m": reading.depth_m,
            "dielectric_constant": reading.dielectric_constant
        }


class RegolithAnalyzer:
    """
    Analyze regolith composition and extractable resources.
    """
    
    # Mars regolith typical composition (% by mass)
    TYPICAL_MARS_REGOLITH = {
        "SiO2": 44.0,
        "Fe2O3": 18.0,
        "Al2O3": 10.0,
        "MgO": 7.0,
        "CaO": 6.0,
        "SO3": 7.0,
        "H2O": 2.0,
        "other": 6.0
    }
    
    def __init__(self):
        self.samples: List[Dict] = []
    
    def analyze_sample(self, sample_mass_kg: float,
                       water_content_percent: float = 2.0,
                       location: Optional[Tuple[float, float]] = None) -> Dict:
        """
        Analyze regolith sample.
        
        Args:
            sample_mass_kg: Sample mass
            water_content_percent: Water ice content
            location: (lat, lon)
        
        Returns:
            Analysis results
        """
        # Scale typical composition by sample mass
        composition = {}
        for compound, percent in self.TYPICAL_MARS_REGOLITH.items():
            if compound == "H2O":
                composition[compound] = round(sample_mass_kg * water_content_percent / 100.0, 4)
            else:
                composition[compound] = round(sample_mass_kg * percent / 100.0, 4)
        
        # Extractable resources
        water_extractable_kg = composition["H2O"] * 0.9  # 90% extraction efficiency
        oxygen_from_water = water_extractable_kg * 8.0 / 9.0  # H2O -> H2 + 1/2 O2
        
        # Iron extraction
        iron_from_oxide = composition["Fe2O3"] * 2.0 * 55.845 / 159.69  # Fe2O3 -> 2Fe
        
        # Aluminium
        aluminium_from_oxide = composition["Al2O3"] * 2.0 * 26.98 / 101.96
        
        result = {
            "sample_mass_kg": sample_mass_kg,
            "location": location,
            "composition_kg": composition,
            "extractable_water_kg": round(water_extractable_kg, 4),
            "extractable_oxygen_kg": round(oxygen_from_water, 4),
            "extractable_iron_kg": round(iron_from_oxide, 4),
            "extractable_aluminium_kg": round(aluminium_from_oxide, 4),
            "regolith_bulk_density_kg_m3": 1500.0
        }
        
        self.samples.append(result)
        return result
    
    def water_extraction_rate(self, regolith_mass_rate_kg_s: float,
                              water_content_percent: float = 2.0,
                              extraction_efficiency: float = 0.9) -> float:
        """
        Compute water extraction rate.
        
        Args:
            regolith_mass_rate_kg_s: Regolith processing rate
            water_content_percent: Water content
            extraction_efficiency: Extraction efficiency
        
        Returns:
            Water extraction rate kg/s
        """
        return regolith_mass_rate_kg_s * (water_content_percent / 100.0) * extraction_efficiency


class ResourceMapper:
    """
    Map resources over an area from multiple readings.
    """
    
    def __init__(self, gpr: GroundPenetratingRadar,
                 analyzer: RegolithAnalyzer):
        self.gpr = gpr
        self.analyzer = analyzer
        self.readings: List[SubsurfaceReading] = []
        self.deposits: List[ResourceDeposit] = []
    
    def add_reading(self, reading: SubsurfaceReading):
        """Add a GPR reading."""
        self.readings.append(reading)
    
    def identify_deposits(self, min_confidence: float = 0.5) -> List[ResourceDeposit]:
        """
        Identify resource deposits from readings.
        
        Args:
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of deposits
        """
        self.deposits = []
        
        for reading in self.readings:
            detection = self.gpr.detect_ice(reading)
            
            if detection["ice_detected"] and detection["confidence"] >= min_confidence:
                # Estimate volume from signal strength
                volume = 1000.0 * detection["confidence"]  # m3
                
                deposit = ResourceDeposit(
                    name=f"Deposit_{len(self.deposits)+1}",
                    lat_deg=reading.lat_deg,
                    lon_deg=reading.lon_deg,
                    depth_range_m=(reading.depth_m, reading.depth_m + 2.0),
                    estimated_volume_m3=round(volume, 1),
                    purity_percent=round(detection["confidence"] * 100.0, 1),
                    resource_type="water_ice",
                    confidence=round(detection["confidence"], 3)
                )
                
                self.deposits.append(deposit)
        
        return self.deposits
    
    def resource_summary(self) -> Dict:
        """Get summary of mapped resources."""
        total_volume = sum(d.estimated_volume_m3 for d in self.deposits)
        total_water = total_volume * 0.9 * 917.0 / 1000.0  # kg, assuming 90% ice, 917 kg/m3
        
        return {
            "num_deposits": len(self.deposits),
            "total_estimated_volume_m3": round(total_volume, 1),
            "total_extractable_water_kg": round(total_water, 1),
            "readings_processed": len(self.readings),
            "avg_confidence": round(sum(d.confidence for d in self.deposits) / len(self.deposits), 3) if self.deposits else 0.0
        }
