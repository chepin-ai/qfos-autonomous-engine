"""
Magnetic Flux Leakage Module
MFL sensor modeling, leakage field calculation, defect sizing,
and pipe wall loss estimation for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MFLSensor:
    """MFL sensor config."""
    lift_off_mm: float
    sensitivity_mV_mT: float
    bandwidth_Hz: float


class LeakageFieldCalculator:
    """
    Calculate magnetic flux leakage fields.
    """
    
    def __init__(self, magnetization_A_m: float = 1.0e6):
        """
        Args:
            magnetization_A_m: Material magnetization
        """
        self.M = magnetization_A_m
    
    def field_from_defect(self, defect_depth_mm: float,
                         defect_width_mm: float,
                         sensor_lift_off_mm: float) -> float:
        """
        Compute leakage field from defect.
        
        Args:
            defect_depth_mm: Defect depth
            defect_width_mm: Defect width
            sensor_lift_off_mm: Sensor lift-off
        
        Returns:
            Leakage flux density in mT
        """
        # Simplified dipole model
        depth_m = defect_depth_mm * 1e-3
        width_m = defect_width_mm * 1e-3
        lift_m = sensor_lift_off_mm * 1e-3
        
        # Dipole moment proportional to defect volume
        moment = self.M * depth_m * width_m * width_m
        
        # Field at distance
        distance = math.sqrt(depth_m**2 + lift_m**2)
        if distance < 1e-10:
            distance = 1e-10
        
        field_T = moment / (4.0 * math.pi * distance**3)
        return field_T * 1000.0  # Convert to mT
    
    def radial_component(self, defect_depth_mm: float,
                        defect_width_mm: float,
                        sensor_lift_off_mm: float,
                        lateral_offset_mm: float = 0.0) -> float:
        """
        Compute radial field component.
        
        Args:
            defect_depth_mm: Depth
            defect_width_mm: Width
            sensor_lift_off_mm: Lift-off
            lateral_offset_mm: Lateral offset
        
        Returns:
            Radial field in mT
        """
        depth_m = defect_depth_mm * 1e-3
        lift_m = sensor_lift_off_mm * 1e-3
        offset_m = lateral_offset_mm * 1e-3
        
        distance = math.sqrt(depth_m**2 + lift_m**2 + offset_m**2)
        if distance < 1e-10:
            distance = 1e-10
        
        field = self.field_from_defect(defect_depth_mm, defect_width_mm, sensor_lift_off_mm)
        
        # Radial component (along lift-off direction)
        cos_theta = lift_m / distance
        return field * cos_theta
    
    def axial_component(self, defect_depth_mm: float,
                       defect_width_mm: float,
                       sensor_lift_off_mm: float,
                       axial_offset_mm: float = 0.0) -> float:
        """
        Compute axial field component.
        
        Args:
            defect_depth_mm: Depth
            defect_width_mm: Width
            sensor_lift_off_mm: Lift-off
            axial_offset_mm: Axial offset
        
        Returns:
            Axial field in mT
        """
        depth_m = defect_depth_mm * 1e-3
        lift_m = sensor_lift_off_mm * 1e-3
        offset_m = axial_offset_mm * 1e-3
        
        distance = math.sqrt(depth_m**2 + lift_m**2 + offset_m**2)
        if distance < 1e-10:
            distance = 1e-10
        
        field = self.field_from_defect(defect_depth_mm, defect_width_mm, sensor_lift_off_mm)
        
        # Axial component
        sin_theta = offset_m / distance
        return field * sin_theta


class DefectSizer:
    """
    Size defects from MFL signals.
    """
    
    def __init__(self):
        self.calibration_factor = 1.0
    
    def depth_from_signal(self, peak_signal_mT: float,
                         wall_thickness_mm: float,
                         saturation_field_mT: float = 1.5) -> float:
        """
        Estimate defect depth from signal.
        
        Args:
            peak_signal_mT: Peak signal
            wall_thickness_mm: Wall thickness
            saturation_field_mT: Saturation field
        
        Returns:
            Estimated depth
        """
        if saturation_field_mT <= 0:
            return 0.0
        
        ratio = peak_signal_mT / saturation_field_mT
        depth = ratio * wall_thickness_mm * self.calibration_factor
        return min(depth, wall_thickness_mm)
    
    def length_from_signal(self, signal_width_mm: float,
                          sensor_speed_mm_s: float = 1000.0) -> float:
        """
        Estimate defect length from signal width.
        
        Args:
            signal_width_mm: Signal spatial width
            sensor_speed_mm_s: Scan speed
        
        Returns:
            Estimated length
        """
        return signal_width_mm
    
    def volume_loss(self, depth_mm: float,
                   length_mm: float,
                   width_mm: float) -> float:
        """
        Compute volume loss.
        
        Args:
            depth_mm: Depth
            length_mm: Length
            width_mm: Width
        
        Returns:
            Volume in mm^3
        """
        return depth_mm * length_mm * width_mm


class PipeWallLossEstimator:
    """
    Estimate pipe wall loss from MFL data.
    """
    
    def __init__(self, nominal_thickness_mm: float = 10.0):
        """
        Args:
            nominal_thickness_mm: Nominal thickness
        """
        self.nominal = nominal_thickness_mm
        self.readings: List[float] = []
    
    def add_reading(self, signal_mT: float):
        """
        Add reading.
        
        Args:
            signal_mT: Signal
        """
        self.readings.append(signal_mT)
    
    def remaining_thickness(self, sizer: DefectSizer,
                           saturation_field_mT: float = 1.5) -> float:
        """
        Estimate remaining thickness.
        
        Args:
            sizer: Defect sizer
            saturation_field_mT: Saturation field
        
        Returns:
            Remaining thickness
        """
        if not self.readings:
            return self.nominal
        
        max_signal = max(self.readings)
        depth = sizer.depth_from_signal(max_signal, self.nominal, saturation_field_mT)
        
        return max(0.0, self.nominal - depth)
    
    def wall_loss_percentage(self, sizer: DefectSizer,
                            saturation_field_mT: float = 1.5) -> float:
        """
        Compute wall loss percentage.
        
        Args:
            sizer: Defect sizer
            saturation_field_mT: Saturation field
        
        Returns:
            Percentage
        """
        remaining = self.remaining_thickness(sizer, saturation_field_mT)
        if self.nominal <= 0:
            return 0.0
        return (self.nominal - remaining) / self.nominal * 100.0


class MagneticFluxLeakage:
    """
    Unified MFL controller.
    """
    
    def __init__(self):
        self.sensor = MFLSensor(2.0, 10.0, 1000.0)
        self.calculator = LeakageFieldCalculator()
        self.sizer = DefectSizer()
        self.estimator = PipeWallLossEstimator()
        self.signals: List[float] = []
        self.positions: List[float] = []
    
    def scan(self, positions: List[float],
            defect_depths: List[float],
            defect_widths: List[float]):
        """
        Simulate scan.
        
        Args:
            positions: Positions
            defect_depths: Defect depths
            defect_widths: Defect widths
        """
        self.positions = positions
        self.signals = []
        
        for pos, depth, width in zip(positions, defect_depths, defect_widths):
            field = self.calculator.field_from_defect(
                depth, width, self.sensor.lift_off_mm
            )
            self.signals.append(field)
            self.estimator.add_reading(field)
    
    def find_defects(self, threshold_mT: float = 0.1) -> List[Dict]:
        """
        Find defects from signals.
        
        Args:
            threshold_mT: Threshold
        
        Returns:
            Defects
        """
        defects = []
        for i, signal in enumerate(self.signals):
            if signal > threshold_mT:
                depth = self.sizer.depth_from_signal(
                    signal, self.estimator.nominal
                )
                defects.append({
                    "position_mm": self.positions[i],
                    "signal_mT": signal,
                    "depth_mm": depth
                })
        return defects
    
    def mfl_summary(self) -> Dict:
        """Get summary."""
        return {
            "readings": len(self.signals),
            "lift_off_mm": self.sensor.lift_off_mm,
            "wall_loss_pct": self.estimator.wall_loss_percentage(self.sizer)
        }
