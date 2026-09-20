"""
Magnetic Field Control Module
Field generation, coil control, and shielding assessment
for autonomous system magnetic management.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class CoilType(Enum):
    """Electromagnetic coil type."""
    SOLENOID = "solenoid"
    HELMHOLTZ = "helmholtz"
    TOROIDAL = "toroidal"
    DIPOLE = "dipole"


class FieldDirection(Enum):
    """Field direction."""
    X = "x"
    Y = "y"
    Z = "z"
    AXIAL = "axial"
    RADIAL = "radial"


@dataclass
class FieldVector:
    """Magnetic field vector."""
    bx: float  # Tesla
    by: float
    bz: float
    
    def magnitude(self) -> float:
        """Get field magnitude."""
        return math.sqrt(self.bx**2 + self.by**2 + self.bz**2)
    
    def direction(self) -> Tuple[float, float, float]:
        """Get unit direction."""
        mag = self.magnitude()
        if mag < 1e-15:
            return (0.0, 0.0, 1.0)
        return (self.bx/mag, self.by/mag, self.bz/mag)


class CoilController:
    """
    Control electromagnetic coil systems.
    """
    
    def __init__(self, coil_type: CoilType,
                 turns: int = 100,
                 radius_m: float = 0.1,
                 max_current_A: float = 10.0):
        """
        Args:
            coil_type: Type of coil
            turns: Number of turns
            radius_m: Coil radius
            max_current_A: Maximum current
        """
        self.coil_type = coil_type
        self.turns = turns
        self.radius = radius_m
        self.max_current = max_current_A
        self.current = 0.0
        self.mu0 = 4 * math.pi * 1e-7  # Permeability of free space
    
    def field_on_axis(self, distance_m: float) -> float:
        """
        Compute magnetic field on coil axis.
        
        Args:
            distance_m: Distance from coil center
        
        Returns:
            Field strength (Tesla)
        """
        if self.coil_type == CoilType.SOLENOID:
            # Solenoid: B = mu0 * N * I / (2 * R) * (1 + (z/R)^2)^(-3/2)
            b_center = self.mu0 * self.turns * self.current / (2 * self.radius)
            factor = (1 + (distance_m / self.radius)**2) ** (-1.5)
            return b_center * factor
        
        elif self.coil_type == CoilType.HELMHOLTZ:
            # Helmholtz pair: approximately uniform field between coils
            # B = (4/5)^(3/2) * mu0 * N * I / R
            if abs(distance_m) <= self.radius:
                return (4/5)**1.5 * self.mu0 * self.turns * self.current / self.radius
            return 0.0
        
        elif self.coil_type == CoilType.DIPOLE:
            # Dipole field: B = mu0 * N * I * R^2 / (2 * (R^2 + z^2)^(3/2))
            return (self.mu0 * self.turns * self.current * self.radius**2 /
                   (2 * (self.radius**2 + distance_m**2)**1.5))
        
        return 0.0
    
    def field_at_center(self) -> float:
        """Get field at coil center."""
        if self.coil_type == CoilType.SOLENOID:
            return self.mu0 * self.turns * self.current / (2 * self.radius)
        elif self.coil_type == CoilType.HELMHOLTZ:
            return (4/5)**1.5 * self.mu0 * self.turns * self.current / self.radius
        elif self.coil_type == CoilType.TOROIDAL:
            # Toroidal: B = mu0 * N * I / (2 * pi * R)
            return self.mu0 * self.turns * self.current / (2 * math.pi * self.radius)
        return 0.0
    
    def set_current(self, current_A: float) -> bool:
        """
        Set coil current.
        
        Args:
            current_A: Target current
        
        Returns:
            True if within limits
        """
        if abs(current_A) > self.max_current:
            return False
        self.current = current_A
        return True
    
    def power_dissipation(self, resistance_ohm: float = 1.0) -> float:
        """
        Compute power dissipation.
        
        Args:
            resistance_ohm: Coil resistance
        
        Returns:
            Power (W)
        """
        return self.current**2 * resistance_ohm


class FieldGenerator:
    """
    Generate controlled magnetic fields.
    """
    
    def __init__(self):
        self.coils: Dict[str, CoilController] = {}
        self.target_field: FieldVector = FieldVector(0.0, 0.0, 0.0)
    
    def add_coil(self, name: str, coil: CoilController):
        """Add coil to generator."""
        self.coils[name] = coil
    
    def set_target_field(self, bx_T: float, by_T: float, bz_T: float):
        """Set target field."""
        self.target_field = FieldVector(bx_T, by_T, bz_T)
    
    def compute_field(self, position_m: Tuple[float, float, float] = (0, 0, 0)
                     ) -> FieldVector:
        """
        Compute total field at position.
        
        Args:
            position_m: Position (x, y, z)
        
        Returns:
            Total field vector
        """
        bx, by, bz = 0.0, 0.0, 0.0
        
        for coil in self.coils.values():
            # Simplified: assume all coils aligned with z-axis
            b = coil.field_on_axis(position_m[2])
            bz += b
        
        return FieldVector(bx, by, bz)
    
    def field_error(self) -> float:
        """
        Compute field error from target.
        
        Returns:
            Error magnitude (Tesla)
        """
        actual = self.compute_field()
        err_bx = actual.bx - self.target_field.bx
        err_by = actual.by - self.target_field.by
        err_bz = actual.bz - self.target_field.bz
        return math.sqrt(err_bx**2 + err_by**2 + err_bz**2)
    
    def total_power(self, resistance_ohm: float = 1.0) -> float:
        """Get total power dissipation."""
        return sum(c.power_dissipation(resistance_ohm) for c in self.coils.values())


class ShieldingAssessor:
    """
    Assess magnetic shielding effectiveness.
    """
    
    def __init__(self, shield_thickness_m: float = 0.001,
                 material_permeability: float = 5000.0):
        """
        Args:
            shield_thickness_m: Shield thickness
            material_permeability: Relative permeability
        """
        self.thickness = shield_thickness_m
        self.permeability = material_permeability
    
    def shielding_factor(self, shield_radius_m: float) -> float:
        """
        Compute shielding factor.
        
        Args:
            shield_radius_m: Shield radius
        
        Returns:
            Shielding factor (>1 means shielding)
        """
        if shield_radius_m <= 0:
            return 1.0
        
        # Simplified spherical shield formula
        # SF = 1 + (2/9) * mu_r * (1 - (r_inner/r_outer)^3)
        r_outer = shield_radius_m + self.thickness
        ratio = shield_radius_m / r_outer
        
        return 1.0 + (2.0/9.0) * self.permeability * (1.0 - ratio**3)
    
    def attenuation_db(self, shield_radius_m: float) -> float:
        """
        Compute attenuation in dB.
        
        Args:
            shield_radius_m: Shield radius
        
        Returns:
            Attenuation (dB)
        """
        sf = self.shielding_factor(shield_radius_m)
        if sf <= 0:
            return 0.0
        return 20.0 * math.log10(sf)
    
    def field_inside(self, external_field_T: float,
                    shield_radius_m: float) -> float:
        """
        Compute field inside shield.
        
        Args:
            external_field_T: External field
            shield_radius_m: Shield radius
        
        Returns:
            Internal field (Tesla)
        """
        sf = self.shielding_factor(shield_radius_m)
        return external_field_T / sf


class MagneticFieldControl:
    """
    Unified magnetic field control system.
    """
    
    def __init__(self):
        self.generator = FieldGenerator()
        self.shielding = ShieldingAssessor()
        self.measurements: List[FieldVector] = []
    
    def add_coil(self, name: str, coil_type: CoilType,
                turns: int = 100, radius_m: float = 0.1,
                max_current_A: float = 10.0):
        """Add coil to system."""
        coil = CoilController(coil_type, turns, radius_m, max_current_A)
        self.generator.add_coil(name, coil)
    
    def set_coil_current(self, name: str, current_A: float) -> bool:
        """Set coil current."""
        coil = self.generator.coils.get(name)
        if coil:
            return coil.set_current(current_A)
        return False
    
    def measure_field(self, position: Tuple[float, float, float] = (0, 0, 0)):
        """Measure field at position."""
        field = self.generator.compute_field(position)
        self.measurements.append(field)
    
    def assess_shielding(self, external_field_T: float,
                        shield_radius_m: float) -> Dict:
        """
        Assess shielding effectiveness.
        
        Args:
            external_field_T: External field
            shield_radius_m: Shield radius
        
        Returns:
            Shielding assessment
        """
        sf = self.shielding.shielding_factor(shield_radius_m)
        atten = self.shielding.attenuation_db(shield_radius_m)
        internal = self.shielding.field_inside(external_field_T, shield_radius_m)
        
        return {
            "shielding_factor": sf,
            "attenuation_db": atten,
            "external_field_uT": external_field_T * 1e6,
            "internal_field_uT": internal * 1e6,
            "effective": sf > 10
        }
    
    def control_summary(self) -> Dict:
        """Get control summary."""
        return {
            "coils": len(self.generator.coils),
            "target_field_T": self.generator.target_field.magnitude(),
            "field_error_T": self.generator.field_error(),
            "measurements": len(self.measurements),
            "shielding_permeability": self.shielding.permeability
        }
