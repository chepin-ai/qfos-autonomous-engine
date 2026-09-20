"""
Magnetic Particle Inspection Module
Magnetization, particle suspension, UV indication detection,
and demagnetization for autonomous surface and near-surface NDT.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class MagnetizationType(Enum):
    """Types of magnetization."""
    CIRCUMFERENTIAL = "circumferential"
    LONGITUDINAL = "longitudinal"
    MULTI_DIRECTIONAL = "multi_directional"


class ParticleType(Enum):
    """Types of magnetic particles."""
    FLUORESCENT = "fluorescent"
    VISIBLE = "visible"


@dataclass
class MagneticIndication:
    """A detected magnetic particle indication."""
    x: float
    y: float
    length_mm: float
    width_mm: float
    intensity: float
    orientation_deg: float = 0.0


class Magnetizer:
    """
    Magnetize test object.
    """
    
    def __init__(self, magnetization_type: MagnetizationType = MagnetizationType.CIRCUMFERENTIAL):
        """
        Args:
            magnetization_type: Type of magnetization
        """
        self.mag_type = magnetization_type
        self.field_strength_A_m = 2000.0
    
    def set_field(self, strength_A_m: float):
        """
        Set magnetizing field strength.
        
        Args:
            strength_A_m: Field strength in A/m
        """
        self.field_strength_A_m = strength_A_m
    
    def required_current(self, diameter_mm: float,
                        turns: int = 3) -> float:
        """
        Compute required magnetizing current.
        
        Args:
            diameter_mm: Part diameter
            turns: Coil turns
        
        Returns:
            Current in amperes
        """
        if diameter_mm <= 0 or turns <= 0:
            return 0.0
        # I = H * pi * D / N
        return self.field_strength_A_m * math.pi * diameter_mm * 1e-3 / turns
    
    def magnetic_flux_density(self, material_permeability: float) -> float:
        """
        Compute magnetic flux density B = mu * H.
        
        Args:
            material_permeability: Relative permeability
        
        Returns:
            B in Tesla
        """
        mu0 = 4.0 * math.pi * 1e-7
        return mu0 * material_permeability * self.field_strength_A_m


class ParticleSuspension:
    """
    Magnetic particle suspension properties.
    """
    
    def __init__(self, particle_type: ParticleType = ParticleType.FLUORESCENT,
                 concentration_ml_L: float = 0.2):
        """
        Args:
            particle_type: Particle type
            concentration_ml_L: Concentration in ml/L
        """
        self.particle_type = particle_type
        self.concentration = concentration_ml_L
    
    def particle_density(self) -> float:
        """
        Compute particle density.
        
        Returns:
            Particles per ml
        """
        return self.concentration * 1e6  # Simplified
    
    def settling_time(self, particle_size_um: float = 5.0) -> float:
        """
        Estimate settling time.
        
        Args:
            particle_size_um: Particle size
        
        Returns:
            Time in minutes
        """
        if particle_size_um <= 0:
            return 0.0
        # Larger particles settle faster
        return 60.0 / (particle_size_um * self.concentration)
    
    def uv_response(self, magnetic_field_T: float) -> float:
        """
        Compute UV response.
        
        Args:
            magnetic_field_T: Magnetic field in Tesla
        
        Returns:
            Response intensity
        """
        if self.particle_type == ParticleType.FLUORESCENT:
            return min(1.0, magnetic_field_T * 10.0 * self.concentration)
        return min(1.0, magnetic_field_T * 5.0 * self.concentration)


class UVIndicationDetector:
    """
    Detect indications under UV light.
    """
    
    def __init__(self, intensity_threshold: float = 0.15):
        """
        Args:
            intensity_threshold: Detection threshold
        """
        self.threshold = intensity_threshold
    
    def detect(self, uv_image: List[float],
              positions: List[Tuple[float, float]]) -> List[MagneticIndication]:
        """
        Detect indications from UV image.
        
        Args:
            uv_image: Pixel intensities
            positions: Pixel positions
        
        Returns:
            Indications
        """
        indications = []
        i = 0
        while i < len(uv_image):
            if uv_image[i] > self.threshold:
                start = i
                max_int = uv_image[i]
                while i < len(uv_image) and uv_image[i] > self.threshold:
                    max_int = max(max_int, uv_image[i])
                    i += 1
                end = i
                
                xs = [positions[j][0] for j in range(start, end)]
                ys = [positions[j][1] for j in range(start, end)]
                cx = sum(xs) / len(xs) if xs else 0
                cy = sum(ys) / len(ys) if ys else 0
                length = max(xs) - min(xs) if xs else 0
                width = max(ys) - min(ys) if ys else 0
                
                # Orientation
                if length > 0:
                    dx = xs[-1] - xs[0] if len(xs) > 1 else 0
                    dy = ys[-1] - ys[0] if len(ys) > 1 else 0
                    orient = math.degrees(math.atan2(dy, dx))
                else:
                    orient = 0.0
                
                indications.append(MagneticIndication(
                    x=cx, y=cy, length_mm=length, width_mm=width,
                    intensity=max_int, orientation_deg=orient
                ))
            else:
                i += 1
        return indications
    
    def contrast_ratio(self, indication_intensity: float,
                      background: float) -> float:
        """
        Compute contrast ratio.
        
        Args:
            indication_intensity: Indication intensity
            background: Background
        
        Returns:
            Contrast ratio
        """
        if background <= 0:
            return float('inf')
        return indication_intensity / background


class Demagnetizer:
    """
    Demagnetize test object.
    """
    
    def __init__(self):
        self.decay_cycles = 5
    
    def decay_field(self, initial_field_A_m: float,
                   cycle: int) -> float:
        """
        Compute decayed field for cycle.
        
        Args:
            initial_field_A_m: Initial field
            cycle: Cycle number
        
        Returns:
            Field strength
        """
        if cycle <= 0:
            return initial_field_A_m
        return initial_field_A_m / (2.0 ** cycle)
    
    def alternating_decay(self, initial_field_A_m: float) -> List[float]:
        """
        Generate alternating decay sequence.
        
        Args:
            initial_field_A_m: Initial field
        
        Returns:
            Field sequence
        """
        sequence = []
        for cycle in range(1, self.decay_cycles + 1):
            field = self.decay_field(initial_field_A_m, cycle)
            sequence.append(field)
            sequence.append(-field)
        sequence.append(0.0)
        return sequence
    
    def residual_field(self, initial_field_A_m: float,
                      material_coercivity_A_m: float) -> float:
        """
        Estimate residual field.
        
        Args:
            initial_field_A_m: Initial field
            material_coercivity_A_m: Coercivity
        
        Returns:
            Residual field
        """
        if initial_field_A_m <= material_coercivity_A_m:
            return initial_field_A_m * 0.1
        return material_coercivity_A_m * 0.5


class MagneticParticleInspection:
    """
    Unified magnetic particle inspection controller.
    """
    
    def __init__(self):
        self.magnetizer = Magnetizer()
        self.suspension = ParticleSuspension()
        self.detector = UVIndicationDetector()
        self.demagnetizer = Demagnetizer()
        self.inspections: List[Dict] = []
    
    def inspect(self, uv_image: List[float],
               positions: List[Tuple[float, float]],
               diameter_mm: float = 50.0,
               material_permeability: float = 1000.0) -> Dict:
        """
        Run magnetic particle inspection.
        
        Args:
            uv_image: UV image intensities
            positions: Positions
            diameter_mm: Part diameter
            material_permeability: Permeability
        
        Returns:
            Inspection report
        """
        current = self.magnetizer.required_current(diameter_mm)
        B = self.magnetizer.magnetic_flux_density(material_permeability)
        
        indications = self.detector.detect(uv_image, positions)
        rejectable = [ind for ind in indications if ind.length_mm > 3.0]
        
        report = {
            "magnetizing_current_A": current,
            "flux_density_T": B,
            "indications": len(indications),
            "rejectable": len(rejectable),
            "pass": len(rejectable) == 0
        }
        self.inspections.append(report)
        return report
    
    def set_magnetization(self, mag_type: MagnetizationType):
        """
        Set magnetization type.
        
        Args:
            mag_type: Type
        """
        self.magnetizer = Magnetizer(mag_type)
    
    def inspection_summary(self) -> Dict:
        """Get inspection summary."""
        if not self.inspections:
            return {"status": "no_data"}
        
        return {
            "inspections": len(self.inspections),
            "pass_count": sum(1 for r in self.inspections if r["pass"]),
            "total_indications": sum(r["indications"] for r in self.inspections)
        }
