"""
Eddy Current Array Module
ECA probe arrays, impedance plane analysis, C-scan imaging,
and defect mapping for autonomous NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ProbeOrientation(Enum):
    """ECA probe orientations."""
    LINEAR = "linear"
    CIRCULAR = "circular"
    MATRIX = "matrix"


@dataclass
class ECAReading:
    """Single ECA probe reading."""
    probe_id: int
    x_mm: float
    y_mm: float
    real_mV: float
    imag_mV: float
    lift_off_mm: float = 0.0


class ECAProbe:
    """
    Single ECA probe element.
    """
    
    def __init__(self, probe_id: int, position_mm: Tuple[float, float],
                 frequency_Hz: float = 100000.0):
        """
        Args:
            probe_id: Probe ID
            position_mm: (x, y) position
            frequency_Hz: Excitation frequency
        """
        self.probe_id = probe_id
        self.position = position_mm
        self.frequency = frequency_Hz
        self.coil_diameter_mm = 3.0
    
    def impedance(self, conductivity_MS_m: float = 1.0,
                 lift_off_mm: float = 0.0) -> complex:
        """
        Compute probe impedance.
        
        Args:
            conductivity_MS_m: Material conductivity
            lift_off_mm: Lift-off
        
        Returns:
            Complex impedance
        """
        # Simplified: impedance decreases with lift-off
        R = 10.0 + 5.0 * conductivity_MS_m
        X = 2.0 * math.pi * self.frequency * 1e-6
        
        lift_factor = math.exp(-lift_off_mm / self.coil_diameter_mm)
        return complex(R * lift_factor, X * lift_factor)
    
    def voltage(self, reference_impedance: complex,
               measured_impedance: complex,
               excitation_V: float = 1.0) -> complex:
        """
        Compute bridge voltage.
        
        Args:
            reference_impedance: Reference
            measured_impedance: Measured
            excitation_V: Excitation
        
        Returns:
            Voltage
        """
        delta = measured_impedance - reference_impedance
        return delta * excitation_V / reference_impedance


class ECAArray:
    """
    Eddy current array controller.
    """
    
    def __init__(self, num_probes: int = 16,
                 spacing_mm: float = 2.0):
        """
        Args:
            num_probes: Number of probes
            spacing_mm: Probe spacing
        """
        self.num_probes = num_probes
        self.spacing = spacing_mm
        self.probes: List[ECAProbe] = []
        self._build_array()
    
    def _build_array(self):
        """Initialize probe array."""
        for i in range(self.num_probes):
            pos = (i * self.spacing, 0.0)
            self.probes.append(ECAProbe(i, pos))
    
    def scan_line(self, conductivities: List[float],
                 lift_offs: List[float]) -> List[ECAReading]:
        """
        Simulate linear scan.
        
        Args:
            conductivities: Conductivity per probe
            lift_offs: Lift-off per probe
        
        Returns:
            Readings
        """
        readings = []
        ref = self.probes[0].impedance(1.0, 0.0)
        
        for i, probe in enumerate(self.probes):
            cond = conductivities[i] if i < len(conductivities) else 1.0
            lo = lift_offs[i] if i < len(lift_offs) else 0.0
            
            z = probe.impedance(cond, lo)
            v = probe.voltage(ref, z)
            
            readings.append(ECAReading(
                probe_id=probe.probe_id,
                x_mm=probe.position[0],
                y_mm=probe.position[1],
                real_mV=v.real * 1000.0,
                imag_mV=v.imag * 1000.0,
                lift_off_mm=lo
            ))
        
        return readings
    
    def coverage_width_mm(self) -> float:
        """
        Compute scan coverage.
        
        Returns:
            Width in mm
        """
        return (self.num_probes - 1) * self.spacing


class CScanImager:
    """
    C-scan image generation from ECA data.
    """
    
    def __init__(self, array: ECAArray):
        """
        Args:
            array: ECA array
        """
        self.array = array
        self.scan_data: List[List[ECAReading]] = []
    
    def add_scan_line(self, readings: List[ECAReading]):
        """
        Add scan line.
        
        Args:
            readings: Line readings
        """
        self.scan_data.append(readings)
    
    def amplitude_map(self) -> List[List[float]]:
        """
        Generate amplitude C-scan.
        
        Returns:
            2D amplitude map
        """
        if not self.scan_data:
            return []
        
        h = len(self.scan_data)
        w = self.array.num_probes
        
        amplitude = []
        for y in range(h):
            row = []
            for x in range(w):
                if x < len(self.scan_data[y]):
                    r = self.scan_data[y][x]
                    row.append(math.sqrt(r.real_mV**2 + r.imag_mV**2))
                else:
                    row.append(0.0)
            amplitude.append(row)
        
        return amplitude
    
    def phase_map(self) -> List[List[float]]:
        """
        Generate phase C-scan.
        
        Returns:
            2D phase map
        """
        if not self.scan_data:
            return []
        
        h = len(self.scan_data)
        w = self.array.num_probes
        
        phase = []
        for y in range(h):
            row = []
            for x in range(w):
                if x < len(self.scan_data[y]):
                    r = self.scan_data[y][x]
                    row.append(math.atan2(r.imag_mV, r.real_mV))
                else:
                    row.append(0.0)
            phase.append(row)
        
        return phase
    
    def defect_map(self, threshold_mV: float = 10.0) -> List[List[bool]]:
        """
        Generate defect map.
        
        Args:
            threshold_mV: Detection threshold
        
        Returns:
            Defect boolean map
        """
        amp = self.amplitude_map()
        return [[val > threshold_mV for val in row] for row in amp]


class ECADefectMapper:
    """
    Defect characterization from ECA data.
    """
    
    def defect_depth_estimate(self, amplitude_mV: float,
                           reference_amplitude_mV: float = 50.0,
                           skin_depth_mm: float = 1.0) -> float:
        """
        Estimate defect depth from amplitude.
        
        Args:
            amplitude_mV: Signal amplitude
            reference_amplitude_mV: Reference
            skin_depth_mm: Skin depth
        
        Returns:
            Depth in mm
        """
        if reference_amplitude_mV <= 0 or amplitude_mV <= 0:
            return 0.0
        ratio = amplitude_mV / reference_amplitude_mV
        if ratio >= 1.0:
            return 0.0
        return -skin_depth_mm * math.log(ratio)
    
    def defect_length_estimate(self, defect_pixels: int,
                              pixel_size_mm: float = 2.0) -> float:
        """
        Estimate defect length.
        
        Args:
            defect_pixels: Pixel count
            pixel_size_mm: Pixel size
        
        Returns:
            Length in mm
        """
        return defect_pixels * pixel_size_mm
    
    def severity_index(self, amplitude_mV: float,
                      depth_mm: float,
                      length_mm: float) -> float:
        """
        Compute severity index.
        
        Args:
            amplitude_mV: Amplitude
            depth_mm: Depth
            length_mm: Length
        
        Returns:
            Severity (0-1)
        """
        amp_norm = min(1.0, amplitude_mV / 100.0)
        depth_norm = min(1.0, depth_mm / 5.0)
        length_norm = min(1.0, length_mm / 20.0)
        return (amp_norm + depth_norm + length_norm) / 3.0


class EddyCurrentArray:
    """
    Unified eddy current array controller.
    """
    
    def __init__(self, num_probes: int = 16):
        """
        Args:
            num_probes: Number of probes
        """
        self.array = ECAArray(num_probes)
        self.imager = CScanImager(self.array)
        self.mapper = ECADefectMapper()
        self.defects: List[Dict] = []
    
    def scan(self, conductivity_profile: List[List[float]],
            lift_off_profile: List[List[float]]):
        """
        Run full scan.
        
        Args:
            conductivity_profile: 2D conductivity map
            lift_off_profile: 2D lift-off map
        """
        for y in range(len(conductivity_profile)):
            conds = conductivity_profile[y]
            los = lift_off_profile[y] if y < len(lift_off_profile) else [0.0] * self.array.num_probes
            readings = self.array.scan_line(conds, los)
            self.imager.add_scan_line(readings)
    
    def analyze_defects(self, threshold_mV: float = 10.0) -> List[Dict]:
        """
        Analyze defects.
        
        Args:
            threshold_mV: Threshold
        
        Returns:
            Defect list
        """
        defect_map = self.imager.defect_map(threshold_mV)
        amp_map = self.imager.amplitude_map()
        
        for y, row in enumerate(defect_map):
            for x, is_defect in enumerate(row):
                if is_defect:
                    amp = amp_map[y][x] if y < len(amp_map) and x < len(amp_map[y]) else 0.0
                    depth = self.mapper.defect_depth_estimate(amp)
                    severity = self.mapper.severity_index(amp, depth, self.array.spacing)
                    self.defects.append({
                        "x_mm": x * self.array.spacing,
                        "y_mm": y * self.array.spacing,
                        "amplitude_mV": amp,
                        "depth_mm": depth,
                        "severity": severity
                    })
        
        return self.defects
    
    def cscan_summary(self) -> Dict:
        """Get C-scan summary."""
        amp_map = self.imager.amplitude_map()
        if not amp_map:
            return {"status": "no_data"}
        
        max_amp = max(max(row) for row in amp_map)
        return {
            "scan_lines": len(self.imager.scan_data),
            "coverage_mm": self.array.coverage_width_mm(),
            "max_amplitude_mV": max_amp,
            "defects": len(self.defects)
        }
