"""
Materials Simulator Module
Material property modeling, thermal analysis, and stress
analysis for spacecraft structural components.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Material:
    """A material with physical properties."""
    name: str
    density: float  # kg/m^3
    thermal_conductivity: float  # W/(m·K)
    specific_heat: float  # J/(kg·K)
    youngs_modulus: float  # Pa
    yield_strength: float  # Pa
    thermal_expansion: float  # 1/K
    emissivity: float = 0.5


@dataclass
class ThermalProfile:
    """Thermal analysis result."""
    temperatures: List[float] = field(default_factory=list)
    heat_flux: float = 0.0
    max_temp: float = 0.0
    min_temp: float = 0.0
    avg_temp: float = 0.0


@dataclass
class StressResult:
    """Stress analysis result."""
    von_mises: float = 0.0
    principal_stress: float = 0.0
    safety_factor: float = 0.0
    deformed: bool = False
    max_strain: float = 0.0


class ThermalAnalyzer:
    """
    Steady-state thermal analysis.
    """
    
    def __init__(self, material: Material):
        """
        Args:
            material: Material properties
        """
        self.material = material
    
    def analyze(self, heat_input: float,  # W
               area: float,  # m^2
               thickness: float,  # m
               ambient_temp: float = 273.15,  # K
               convection_coeff: float = 10.0  # W/(m^2·K)
               ) -> ThermalProfile:
        """
        Steady-state thermal analysis.
        
        Args:
            heat_input: Heat input power
            area: Surface area
            thickness: Material thickness
            ambient_temp: Ambient temperature
            convection_coeff: Convection coefficient
        
        Returns:
            ThermalProfile
        """
        # Conduction resistance
        r_cond = thickness / (self.material.thermal_conductivity * area)
        
        # Convection resistance
        r_conv = 1.0 / (convection_coeff * area)
        
        # Total resistance
        r_total = r_cond + r_conv
        
        # Temperature rise
        delta_t = heat_input * r_total
        
        # Hot side temperature
        hot_temp = ambient_temp + delta_t
        
        # Temperature gradient through thickness
        temp_gradient = delta_t / thickness if thickness > 0 else 0
        
        # Discretize temperature profile
        n_points = 10
        temperatures = []
        for i in range(n_points + 1):
            x = i / n_points * thickness
            temp = ambient_temp + heat_input * (x / (self.material.thermal_conductivity * area) + r_conv)
            temperatures.append(temp)
        
        return ThermalProfile(
            temperatures=temperatures,
            heat_flux=heat_input / area,
            max_temp=hot_temp,
            min_temp=ambient_temp,
            avg_temp=(hot_temp + ambient_temp) / 2
        )
    
    def thermal_shock_check(self, temp_change: float,  # K
                           time_duration: float  # s
                           ) -> bool:
        """
        Check thermal shock resistance.
        
        Args:
            temp_change: Temperature change
            time_duration: Duration of change
        
        Returns:
            True if material can withstand
        """
        # Simplified: check if rate of change is reasonable
        rate = abs(temp_change) / time_duration if time_duration > 0 else float('inf')
        
        # Typical ceramic threshold: 100 K/s
        return rate < 100.0


class StressAnalyzer:
    """
    Linear elastic stress analysis.
    """
    
    def __init__(self, material: Material):
        """
        Args:
            material: Material properties
        """
        self.material = material
    
    def analyze_tensile(self, force: float,  # N
                       cross_section: float  # m^2
                       ) -> StressResult:
        """
        Tensile stress analysis.
        
        Args:
            force: Applied force
            cross_section: Cross-sectional area
        
        Returns:
            StressResult
        """
        if cross_section <= 0:
            return StressResult(deformed=True)
        
        stress = force / cross_section
        strain = stress / self.material.youngs_modulus
        safety_factor = self.material.yield_strength / stress if stress > 0 else float('inf')
        
        return StressResult(
            von_mises=abs(stress),
            principal_stress=stress,
            safety_factor=safety_factor,
            deformed=stress > self.material.yield_strength,
            max_strain=strain
        )
    
    def analyze_bending(self, moment: float,  # N·m
                       width: float,  # m
                       height: float  # m
                       ) -> StressResult:
        """
        Bending stress analysis (rectangular beam).
        
        Args:
            moment: Bending moment
            width: Beam width
            height: Beam height
        
        Returns:
            StressResult
        """
        if width <= 0 or height <= 0:
            return StressResult(deformed=True)
        
        # Section modulus for rectangle
        section_modulus = width * height ** 2 / 6.0
        
        stress = moment / section_modulus
        strain = stress / self.material.youngs_modulus
        safety_factor = self.material.yield_strength / abs(stress) if stress != 0 else float('inf')
        
        return StressResult(
            von_mises=abs(stress),
            principal_stress=stress,
            safety_factor=safety_factor,
            deformed=abs(stress) > self.material.yield_strength,
            max_strain=strain
        )
    
    def thermal_stress(self, temp_change: float,  # K
                      constrained: bool = True
                      ) -> float:
        """
        Thermal stress calculation.
        
        Args:
            temp_change: Temperature change
            constrained: Whether expansion is constrained
        
        Returns:
            Thermal stress (Pa)
        """
        if not constrained:
            return 0.0
        
        strain = self.material.thermal_expansion * temp_change
        stress = self.material.youngs_modulus * strain
        return stress


class MaterialsSimulator:
    """
    Unified materials simulation engine.
    """
    
    def __init__(self):
        self.materials: Dict[str, Material] = {}
        self.thermal_analyzers: Dict[str, ThermalAnalyzer] = {}
        self.stress_analyzers: Dict[str, StressAnalyzer] = {}
    
    def add_material(self, material: Material):
        """Add material to library."""
        self.materials[material.name] = material
        self.thermal_analyzers[material.name] = ThermalAnalyzer(material)
        self.stress_analyzers[material.name] = StressAnalyzer(material)
    
    def get_material(self, name: str) -> Optional[Material]:
        """Get material by name."""
        return self.materials.get(name)
    
    def thermal_analysis(self, material_name: str,
                        heat_input: float,
                        area: float,
                        thickness: float,
                        ambient_temp: float = 273.15
                        ) -> Optional[ThermalProfile]:
        """
        Run thermal analysis.
        
        Args:
            material_name: Material name
            heat_input: Heat input (W)
            area: Area (m^2)
            thickness: Thickness (m)
            ambient_temp: Ambient temperature (K)
        
        Returns:
            ThermalProfile or None
        """
        analyzer = self.thermal_analyzers.get(material_name)
        if analyzer is None:
            return None
        return analyzer.analyze(heat_input, area, thickness, ambient_temp)
    
    def stress_analysis(self, material_name: str,
                       load_type: str,
                       **kwargs
                       ) -> Optional[StressResult]:
        """
        Run stress analysis.
        
        Args:
            material_name: Material name
            load_type: "tensile" or "bending"
            **kwargs: Load parameters
        
        Returns:
            StressResult or None
        """
        analyzer = self.stress_analyzers.get(material_name)
        if analyzer is None:
            return None
        
        if load_type == "tensile":
            return analyzer.analyze_tensile(kwargs["force"], kwargs["cross_section"])
        elif load_type == "bending":
            return analyzer.analyze_bending(kwargs["moment"], kwargs["width"], kwargs["height"])
        else:
            return None
    
    def check_component(self, material_name: str,
                       requirements: Dict[str, float]
                       ) -> Dict[str, bool]:
        """
        Check if material meets requirements.
        
        Args:
            material_name: Material name
            requirements: Dict of property -> min_value
        
        Returns:
            Dict of property -> passes
        """
        material = self.materials.get(material_name)
        if material is None:
            return {}
        
        results = {}
        for prop, min_val in requirements.items():
            actual = getattr(material, prop, None)
            if actual is not None:
                results[prop] = actual >= min_val
            else:
                results[prop] = False
        
        return results
    
    def simulator_summary(self) -> Dict:
        """Get simulator summary."""
        return {
            "materials": len(self.materials),
            "available": list(self.materials.keys())
        }
