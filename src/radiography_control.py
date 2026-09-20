"""
Radiography Control Module
X-ray/RT exposure parameters, film processing,
optical density control, and penetrameter evaluation
for autonomous non-destructive testing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class RadiationSource(Enum):
    """Types of radiation sources."""
    X_RAY = "x-ray"
    GAMMA_RAY = "gamma-ray"
    ISOTOPE = "isotope"


class FilmType(Enum):
    """Film classification."""
    CLASS_1 = "class_1"  # High contrast
    CLASS_2 = "class_2"  # Medium contrast
    CLASS_3 = "class_3"  # High latitude


@dataclass
class ExposureParameters:
    """RT exposure parameters."""
    kVp: float = 200.0
    mA: float = 5.0
    exposure_time_s: float = 2.0
    focal_distance_mm: float = 700.0
    source_type: RadiationSource = RadiationSource.X_RAY


class ExposureCalculator:
    """
    Compute RT exposure parameters.
    """
    
    def __init__(self):
        self.base_HVL_mm_steel = 15.0  # Half-value layer
    
    def half_value_layer(self, kVp: float, material: str = "steel") -> float:
        """
        Compute HVL for given kVp.
        
        Args:
            kVp: Peak voltage
            material: Material
        
        Returns:
            HVL in mm
        """
        if kVp <= 0:
            return 0.0
        # HVL increases with kVp
        return self.base_HVL_mm_steel * (kVp / 200.0) ** 1.5
    
    def required_exposure(self, thickness_mm: float, kVp: float,
                         film_speed: float = 100.0) -> float:
        """
        Compute required exposure (mA * s).
        
        Args:
            thickness_mm: Material thickness
            kVp: Peak voltage
            film_speed: Film speed
        
        Returns:
            mA*s
        """
        if thickness_mm <= 0 or kVp <= 0:
            return 0.0
        
        hvl = self.half_value_layer(kVp)
        n_hvl = thickness_mm / hvl if hvl > 0 else 0
        # Exposure doubles per HVL
        return film_speed * (2.0 ** n_hvl) / 1000.0
    
    def geometric_unsharpness(self, focal_size_mm: float,
                              object_distance_mm: float,
                              film_distance_mm: float = 10.0) -> float:
        """
        Compute geometric unsharpness Ug.
        
        Args:
            focal_size_mm: Source size
            object_distance_mm: Object to film distance
            film_distance_mm: Film thickness
        
        Returns:
            Ug in mm
        """
        if object_distance_mm + film_distance_mm <= 0:
            return 0.0
        return focal_size_mm * film_distance_mm / (object_distance_mm + film_distance_mm)
    
    def exposure_time(self, required_mAs: float, mA: float) -> float:
        """
        Compute exposure time.
        
        Args:
            required_mAs: Required mA*s
            mA: Current
        
        Returns:
            Time in seconds
        """
        if mA <= 0:
            return 0.0
        return required_mAs / mA


class FilmProcessor:
    """
    Film processing control.
    """
    
    def __init__(self):
        self.developer_temp_C = 20.0
        self.developer_time_min = 5.0
    
    def optical_density(self, exposure_mAs: float,
                       film_gamma: float = 3.5,
                       base_fog: float = 0.2) -> float:
        """
        Estimate optical density.
        
        Args:
            exposure_mAs: Exposure
            film_gamma: Film gamma
            base_fog: Base+fog
        
        Returns:
            Density
        """
        if exposure_mAs <= 0:
            return base_fog
        logE = math.log10(exposure_mAs)
        return base_fog + film_gamma * logE
    
    def density_range(self, min_exposure: float,
                     max_exposure: float,
                     film_gamma: float = 3.5) -> Tuple[float, float]:
        """
        Compute usable density range.
        
        Args:
            min_exposure: Minimum
            max_exposure: Maximum
            film_gamma: Film gamma
        
        Returns:
            (min_density, max_density)
        """
        d_min = self.optical_density(min_exposure, film_gamma)
        d_max = self.optical_density(max_exposure, film_gamma)
        return (d_min, d_max)
    
    def process_deviation(self, actual_density: float,
                         target_density: float = 2.5) -> float:
        """
        Compute process deviation.
        
        Args:
            actual_density: Actual
            target_density: Target
        
        Returns:
            Deviation
        """
        return actual_density - target_density


class PenetrameterEvaluator:
    """
    Evaluate image quality using penetrameter.
    """
    
    def __init__(self):
        self.standard_wire_thicknesses_mm = [0.10, 0.125, 0.16, 0.20, 0.25,
                                             0.32, 0.40, 0.50, 0.63, 0.80,
                                             1.00, 1.25, 1.60, 2.00, 2.50]
    
    def required_sensitivity(self, thickness_mm: float,
                            class_level: str = "A") -> float:
        """
        Compute required sensitivity.
        
        Args:
            thickness_mm: Thickness
            class_level: Class A or B
        
        Returns:
            Required wire diameter mm
        """
        if class_level.upper() == "B":
            return thickness_mm / 100.0
        return thickness_mm / 50.0
    
    def visible_wires(self, thickness_mm: float,
                     visible_count: int) -> List[float]:
        """
        Get visible wire thicknesses.
        
        Args:
            thickness_mm: Thickness
            visible_count: Number visible
        
        Returns:
            Wire diameters
        """
        req = self.required_sensitivity(thickness_mm)
        wires = [w for w in self.standard_wire_thicknesses_mm if w >= req]
        return wires[:visible_count]
    
    def image_quality_indicator(self, thickness_mm: float,
                               visible_count: int) -> str:
        """
        Get IQI designation.
        
        Args:
            thickness_mm: Thickness
            visible_count: Visible wires
        
        Returns:
            IQI string
        """
        req = self.required_sensitivity(thickness_mm)
        if visible_count >= 2:
            return f"IQI-{req:.3f}mm ({visible_count} wires visible)"
        return "INSUFFICIENT"


class ScatterControl:
    """
    Scatter radiation control.
    """
    
    def scatter_factor(self, thickness_mm: float,
                      field_area_cm2: float = 100.0) -> float:
        """
        Estimate scatter buildup factor.
        
        Args:
            thickness_mm: Thickness
            field_area_cm2: Field area
        
        Returns:
            Scatter factor
        """
        if thickness_mm <= 0:
            return 1.0
        # Scatter increases with thickness and field area
        return 1.0 + 0.001 * thickness_mm * math.sqrt(field_area_cm2)
    
    def required_lead_screen(self, kVp: float,
                            thickness_mm: float) -> float:
        """
        Compute lead screen thickness.
        
        Args:
            kVp: Peak voltage
            thickness_mm: Thickness
        
        Returns:
            Lead thickness in mm
        """
        if kVp < 150:
            return 0.1
        elif kVp < 250:
            return 0.2
        return 0.5


class RadiographyControl:
    """
    Unified radiography controller.
    """
    
    def __init__(self):
        self.exposure = ExposureCalculator()
        self.film = FilmProcessor()
        self.penetrameter = PenetrameterEvaluator()
        self.scatter = ScatterControl()
        self.exposures: List[Dict] = []
    
    def plan_exposure(self, thickness_mm: float,
                     kVp: float = 200.0,
                     mA: float = 5.0,
                     film_speed: float = 100.0) -> ExposureParameters:
        """
        Plan exposure for given thickness.
        
        Args:
            thickness_mm: Material thickness
            kVp: Peak voltage
            mA: Current
            film_speed: Film speed
        
        Returns:
            Exposure parameters
        """
        mAs = self.exposure.required_exposure(thickness_mm, kVp, film_speed)
        t = self.exposure.exposure_time(mAs, mA)
        return ExposureParameters(kVp=kVp, mA=mA, exposure_time_s=t)
    
    def evaluate_density(self, exposure_params: ExposureParameters,
                        film_gamma: float = 3.5) -> Dict:
        """
        Evaluate expected film density.
        
        Args:
            exposure_params: Exposure
            film_gamma: Film gamma
        
        Returns:
            Density report
        """
        mAs = exposure_params.mA * exposure_params.exposure_time_s
        density = self.film.optical_density(mAs, film_gamma)
        deviation = self.film.process_deviation(density)
        
        return {
            "optical_density": density,
            "deviation_from_target": deviation,
            "acceptable": 1.8 <= density <= 4.0
        }
    
    def run_inspection(self, thickness_mm: float,
                      kVp: float = 200.0) -> Dict:
        """
        Run full radiography inspection.
        
        Args:
            thickness_mm: Thickness
            kVp: Peak voltage
        
        Returns:
            Inspection report
        """
        params = self.plan_exposure(thickness_mm, kVp)
        density_report = self.evaluate_density(params)
        req_sens = self.penetrameter.required_sensitivity(thickness_mm)
        lead = self.scatter.required_lead_screen(kVp, thickness_mm)
        
        report = {
            "exposure": {
                "kVp": params.kVp,
                "mA": params.mA,
                "time_s": params.exposure_time_s,
                "mAs": params.mA * params.exposure_time_s
            },
            "density": density_report,
            "required_sensitivity_mm": req_sens,
            "lead_screen_mm": lead,
            "pass": density_report["acceptable"]
        }
        self.exposures.append(report)
        return report
    
    def inspection_summary(self) -> Dict:
        """Get inspection summary."""
        if not self.exposures:
            return {"status": "no_data"}
        
        return {
            "inspections": len(self.exposures),
            "pass_count": sum(1 for r in self.exposures if r.get("pass", False)),
            "avg_density": sum(r["density"]["optical_density"] for r in self.exposures) / len(self.exposures)
        }
