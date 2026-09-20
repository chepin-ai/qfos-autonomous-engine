"""
Corrosion Monitor Module
Corrosion rate, electrochemical monitoring, and pitting
detection for autonomous system structural health.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class CorrosionType(Enum):
    """Type of corrosion."""
    UNIFORM = "uniform"
    PITTING = "pitting"
    GALVANIC = "galvanic"
    CREVICE = "crevice"
    STRESS = "stress"


@dataclass
class CorrosionReading:
    """A corrosion sensor reading."""
    sensor_id: str
    potential_mV: float
    current_density_uA_cm2: float
    temperature_C: float
    humidity_percent: float
    timestamp: float = 0.0


class CorrosionRateCalculator:
    """
    Calculate corrosion rates from electrochemical data.
    """
    
    def __init__(self, equivalent_weight_g: float = 27.92,
                 density_g_cm3: float = 7.87):
        """
        Args:
            equivalent_weight_g: Metal equivalent weight
            density_g_cm3: Metal density
        """
        self.equiv_weight = equivalent_weight_g
        self.density = density_g_cm3
    
    def from_polarization_resistance(self, rp_ohm_cm2: float,
                                     beta_a_mV: float = 120.0,
                                     beta_c_mV: float = 120.0) -> float:
        """
        Calculate corrosion rate from polarization resistance.
        
        Args:
            rp_ohm_cm2: Polarization resistance
            beta_a_mV: Anodic Tafel slope
            beta_c_mV: Cathodic Tafel slope
        
        Returns:
            Corrosion current density (uA/cm^2)
        """
        if rp_ohm_cm2 <= 0:
            return 0.0
        
        # Stern-Geary: i_corr = B / Rp
        B = (beta_a_mV * beta_c_mV) / (2.303 * (beta_a_mV + beta_c_mV))
        icorr = B / rp_ohm_cm2  # mV / ohm.cm2 = uA/cm2
        
        return abs(icorr)
    
    def from_weight_loss(self, weight_loss_mg: float,
                        area_cm2: float,
                        time_hours: float) -> float:
        """
        Calculate corrosion rate from weight loss.
        
        Args:
            weight_loss_mg: Weight loss in mg
            area_cm2: Exposed area
            time_hours: Exposure time
        
        Returns:
            Corrosion rate (mm/year)
        """
        if area_cm2 <= 0 or time_hours <= 0:
            return 0.0
        
        # CR = 87.6 * W / (D * A * T)
        cr = 87.6 * weight_loss_mg / (self.density * area_cm2 * time_hours)
        return cr
    
    def to_penetration_rate(self, icorr_uA_cm2: float) -> float:
        """
        Convert current density to penetration rate.
        
        Args:
            icorr_uA_cm2: Corrosion current density
        
        Returns:
            Penetration rate (mm/year)
        """
        # 0.00327 * i_corr * EW / D
        return 0.00327 * icorr_uA_cm2 * self.equiv_weight / self.density


class ElectrochemicalMonitor:
    """
    Monitor electrochemical corrosion parameters.
    """
    
    def __init__(self):
        self.readings: List[CorrosionReading] = []
        self.calculator = CorrosionRateCalculator()
    
    def add_reading(self, reading: CorrosionReading):
        """Add sensor reading."""
        self.readings.append(reading)
    
    def corrosion_potential(self, n: int = 5) -> float:
        """
        Compute average corrosion potential.
        
        Args:
            n: Number of recent readings
        
        Returns:
            Average E_corr (mV)
        """
        if not self.readings:
            return 0.0
        recent = self.readings[-n:]
        return sum(r.potential_mV for r in recent) / len(recent)
    
    def corrosion_current(self, n: int = 5) -> float:
        """
        Compute average corrosion current density.
        
        Args:
            n: Number of recent readings
        
        Returns:
            Average i_corr (uA/cm^2)
        """
        if not self.readings:
            return 0.0
        recent = self.readings[-n:]
        return sum(r.current_density_uA_cm2 for r in recent) / len(recent)
    
    def trend(self, n: int = 10) -> str:
        """
        Determine corrosion trend.
        
        Args:
            n: Number of readings to analyze
        
        Returns:
            Trend description
        """
        if len(self.readings) < 2:
            return "insufficient_data"
        
        recent = self.readings[-n:]
        first = sum(r.current_density_uA_cm2 for r in recent[:len(recent)//2])
        second = sum(r.current_density_uA_cm2 for r in recent[len(recent)//2:])
        
        if first == 0:
            return "stable"
        
        ratio = second / first
        if ratio > 1.5:
            return "accelerating"
        elif ratio < 0.7:
            return "decelerating"
        return "stable"


class PittingDetector:
    """
    Detect pitting corrosion from sensor data.
    """
    
    def __init__(self, threshold_current_uA_cm2: float = 10.0,
                 potential_threshold_mV: float = -200.0):
        """
        Args:
            threshold_current_uA_cm2: Current threshold for pitting
            potential_threshold_mV: Potential threshold
        """
        self.threshold_current = threshold_current_uA_cm2
        self.threshold_potential = potential_threshold_mV
    
    def detect(self, reading: CorrosionReading) -> bool:
        """
        Detect pitting from single reading.
        
        Args:
            reading: Sensor reading
        
        Returns:
            True if pitting detected
        """
        # High current density + negative potential indicates pitting
        if reading.current_density_uA_cm2 > self.threshold_current:
            if reading.potential_mV < self.threshold_potential:
                return True
        return False
    
    def pitting_index(self, readings: List[CorrosionReading]) -> float:
        """
        Compute pitting severity index.
        
        Args:
            readings: Sensor readings
        
        Returns:
            Pitting index (0-1)
        """
        if not readings:
            return 0.0
        
        pits = sum(1 for r in readings if self.detect(r))
        return pits / len(readings)
    
    def pitting_rate(self, depth_readings_um: List[float],
                    time_hours: float) -> float:
        """
        Estimate pitting rate.
        
        Args:
            depth_readings_um: Pit depth measurements
            time_hours: Time interval
        
        Returns:
            Pitting rate (um/hour)
        """
        if not depth_readings_um or time_hours <= 0:
            return 0.0
        
        max_depth = max(depth_readings_um)
        return max_depth / time_hours


class CorrosionRiskAssessor:
    """
    Assess overall corrosion risk.
    """
    
    def __init__(self):
        self.levels = {
            "low": (0, 2),
            "moderate": (2, 5),
            "high": (5, 10),
            "severe": (10, float('inf'))
        }
    
    def risk_level(self, corrosion_rate_mm_yr: float) -> str:
        """
        Determine risk level.
        
        Args:
            corrosion_rate_mm_yr: Corrosion rate
        
        Returns:
            Risk level string
        """
        for level, (low, high) in self.levels.items():
            if low <= corrosion_rate_mm_yr < high:
                return level
        return "severe"
    
    def remaining_life(self, corrosion_rate_mm_yr: float,
                      thickness_mm: float) -> float:
        """
        Estimate remaining life.
        
        Args:
            corrosion_rate_mm_yr: Corrosion rate
            thickness_mm: Remaining thickness
        
        Returns:
            Estimated years
        """
        if corrosion_rate_mm_yr <= 0:
            return float('inf')
        return thickness_mm / corrosion_rate_mm_yr


class CorrosionMonitor:
    """
    Unified corrosion monitoring system.
    """
    
    def __init__(self):
        self.electro = ElectrochemicalMonitor()
        self.pitting = PittingDetector()
        self.risk = CorrosionRiskAssessor()
        self.sensors: Dict[str, List[CorrosionReading]] = {}
    
    def add_sensor(self, sensor_id: str):
        """Register sensor."""
        self.sensors[sensor_id] = []
    
    def record(self, sensor_id: str, reading: CorrosionReading):
        """Record reading from sensor."""
        if sensor_id not in self.sensors:
            self.add_sensor(sensor_id)
        self.sensors[sensor_id].append(reading)
        self.electro.add_reading(reading)
    
    def health_assessment(self, sensor_id: str) -> Dict:
        """
        Get corrosion health for sensor.
        
        Args:
            sensor_id: Sensor ID
        
        Returns:
            Health summary
        """
        readings = self.sensors.get(sensor_id, [])
        if not readings:
            return {"status": "no_data"}
        
        latest = readings[-1]
        
        # Estimate corrosion rate from current density
        icorr = latest.current_density_uA_cm2
        cr = self.electro.calculator.to_penetration_rate(icorr)
        
        pitting = self.pitting.detect(latest)
        risk = self.risk.risk_level(cr)
        
        return {
            "sensor": sensor_id,
            "corrosion_rate_mm_yr": cr,
            "risk_level": risk,
            "pitting_detected": pitting,
            "potential_mV": latest.potential_mV,
            "current_density_uA_cm2": icorr,
            "trend": self.electro.trend()
        }
    
    def system_summary(self) -> Dict:
        """Get system-wide summary."""
        return {
            "sensors": len(self.sensors),
            "total_readings": sum(len(r) for r in self.sensors.values()),
            "trend": self.electro.trend()
        }
