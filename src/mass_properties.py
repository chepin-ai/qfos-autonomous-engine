"""
Mass Properties Module
Compute spacecraft mass properties: center of mass,
moments of inertia, products of inertia, and mass distribution.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PointMass:
    """A point mass component."""
    name: str
    mass_kg: float
    x_m: float = 0.0
    y_m: float = 0.0
    z_m: float = 0.0
    
    def moment_contribution(self, axis: str) -> Dict[str, float]:
        """Compute inertia contribution about axis."""
        if axis == 'x':
            r2 = self.y_m**2 + self.z_m**2
        elif axis == 'y':
            r2 = self.x_m**2 + self.z_m**2
        else:
            r2 = self.x_m**2 + self.y_m**2
        return {
            "I": self.mass_kg * r2,
            "mxy": self.mass_kg * self.x_m * self.y_m,
            "mxz": self.mass_kg * self.x_m * self.z_m,
            "myz": self.mass_kg * self.y_m * self.z_m
        }


@dataclass
class InertiaTensor:
    """3x3 inertia tensor."""
    Ixx: float
    Iyy: float
    Izz: float
    Ixy: float = 0.0
    Ixz: float = 0.0
    Iyz: float = 0.0
    
    def as_matrix(self) -> List[List[float]]:
        """Return as 3x3 matrix."""
        return [
            [self.Ixx, -self.Ixy, -self.Ixz],
            [-self.Ixy, self.Iyy, -self.Iyz],
            [-self.Ixz, -self.Iyz, self.Izz]
        ]
    
    def principal_moments(self) -> Tuple[float, float, float]:
        """
        Compute principal moments of inertia.
        
        Returns:
            (I1, I2, I3) sorted descending
        """
        # For simplicity, return diagonal if off-diagonal small
        if (abs(self.Ixy) + abs(self.Ixz) + abs(self.Iyz)) < 1e-6:
            moments = sorted([self.Ixx, self.Iyy, self.Izz], reverse=True)
            return tuple(moments)
        
        # Approximate: ignore products for now
        moments = sorted([self.Ixx, self.Iyy, self.Izz], reverse=True)
        return tuple(moments)
    
    def mean_axis_moment(self) -> float:
        """Mean moment of inertia."""
        return (self.Ixx + self.Iyy + self.Izz) / 3.0


class MassProperties:
    """
    Spacecraft mass properties calculator.
    
    Aggregates component masses and computes
    composite mass properties.
    """
    
    def __init__(self):
        self.components: List[PointMass] = []
    
    def add_component(self, component: PointMass):
        """Add a mass component."""
        self.components.append(component)
    
    def total_mass_kg(self) -> float:
        """Total spacecraft mass."""
        return sum(c.mass_kg for c in self.components)
    
    def center_of_mass(self) -> Tuple[float, float, float]:
        """
        Compute center of mass.
        
        Returns:
            (x, y, z) in meters
        """
        total_mass = self.total_mass_kg()
        if total_mass <= 0.0:
            return (0.0, 0.0, 0.0)
        
        x_cm = sum(c.mass_kg * c.x_m for c in self.components) / total_mass
        y_cm = sum(c.mass_kg * c.y_m for c in self.components) / total_mass
        z_cm = sum(c.mass_kg * c.z_m for c in self.components) / total_mass
        
        return (x_cm, y_cm, z_cm)
    
    def inertia_tensor(self, about_origin: bool = False) -> InertiaTensor:
        """
        Compute inertia tensor.
        
        Args:
            about_origin: If False, compute about center of mass
        
        Returns:
            InertiaTensor
        """
        if not about_origin:
            cm = self.center_of_mass()
        else:
            cm = (0.0, 0.0, 0.0)
        
        Ixx = sum(c.mass_kg * ((c.y_m - cm[1])**2 + (c.z_m - cm[2])**2)
                  for c in self.components)
        Iyy = sum(c.mass_kg * ((c.x_m - cm[0])**2 + (c.z_m - cm[2])**2)
                  for c in self.components)
        Izz = sum(c.mass_kg * ((c.x_m - cm[0])**2 + (c.y_m - cm[1])**2)
                  for c in self.components)
        
        Ixy = sum(c.mass_kg * (c.x_m - cm[0]) * (c.y_m - cm[1])
                  for c in self.components)
        Ixz = sum(c.mass_kg * (c.x_m - cm[0]) * (c.z_m - cm[2])
                  for c in self.components)
        Iyz = sum(c.mass_kg * (c.y_m - cm[1]) * (c.z_m - cm[2])
                  for c in self.components)
        
        return InertiaTensor(Ixx=Ixx, Iyy=Iyy, Izz=Izz,
                             Ixy=Ixy, Ixz=Ixz, Iyz=Iyz)
    
    def radius_of_gyration_m(self) -> Tuple[float, float, float]:
        """
        Compute radii of gyration.
        
        Returns:
            (kx, ky, kz) in meters
        """
        mass = self.total_mass_kg()
        if mass <= 0.0:
            return (0.0, 0.0, 0.0)
        
        I = self.inertia_tensor()
        kx = math.sqrt(I.Ixx / mass)
        ky = math.sqrt(I.Iyy / mass)
        kz = math.sqrt(I.Izz / mass)
        
        return (kx, ky, kz)
    
    def shift_component(self, name: str,
                        new_x_m: float, new_y_m: float, new_z_m: float):
        """
        Move a component to new location.
        
        Args:
            name: Component name
            new_x_m, new_y_m, new_z_m: New position
        """
        for c in self.components:
            if c.name == name:
                c.x_m = new_x_m
                c.y_m = new_y_m
                c.z_m = new_z_m
                break
    
    def remove_component(self, name: str):
        """Remove a component."""
        self.components = [c for c in self.components if c.name != name]
    
    def mass_budget_summary(self) -> Dict:
        """Get mass budget summary."""
        total = self.total_mass_kg()
        cm = self.center_of_mass()
        I = self.inertia_tensor()
        rg = self.radius_of_gyration_m()
        
        return {
            "total_mass_kg": round(total, 3),
            "center_of_mass_m": [round(cm[0], 4), round(cm[1], 4), round(cm[2], 4)],
            "inertia_tensor_kg_m2": {
                "Ixx": round(I.Ixx, 3),
                "Iyy": round(I.Iyy, 3),
                "Izz": round(I.Izz, 3),
                "Ixy": round(I.Ixy, 3),
                "Ixz": round(I.Ixz, 3),
                "Iyz": round(I.Iyz, 3)
            },
            "principal_moments_kg_m2": [round(m, 3) for m in I.principal_moments()],
            "radius_of_gyration_m": [round(r, 4) for r in rg],
            "components": [
                {
                    "name": c.name,
                    "mass_kg": c.mass_kg,
                    "position_m": [round(c.x_m, 3), round(c.y_m, 3), round(c.z_m, 3)],
                    "mass_fraction": round(c.mass_kg / total, 4) if total > 0 else 0.0
                }
                for c in self.components
            ]
        }
    
    def propellant_slosh_effect(self, propellant_mass_kg: float,
                                 tank_dimensions_m: Tuple[float, float, float],
                                 fill_level_percent: float = 50.0) -> Dict:
        """
        Estimate propellant slosh effect on CM.
        
        Args:
            propellant_mass_kg: Propellant mass
            tank_dimensions_m: (length, width, height)
            fill_level_percent: Tank fill level
        
        Returns:
            Slosh effect estimate
        """
        length, width, height = tank_dimensions_m
        fill = fill_level_percent / 100.0
        
        # Propellant CM (assumes bottom of tank at origin)
        prop_cm_z = height * fill / 2.0
        
        # Slosh amplitude estimate
        slosh_amplitude_m = 0.05 * height * (1.0 - fill) * fill
        
        # CM shift
        cm_shift_m = propellant_mass_kg * slosh_amplitude_m / self.total_mass_kg() if self.total_mass_kg() > 0 else 0.0
        
        return {
            "propellant_mass_kg": propellant_mass_kg,
            "fill_level": fill,
            "propellant_cm_z_m": round(prop_cm_z, 4),
            "slosh_amplitude_m": round(slosh_amplitude_m, 4),
            "cm_shift_m": round(cm_shift_m, 6)
        }
    
    @staticmethod
    def create_simple_spacecraft() -> 'MassProperties':
        """Create a simple spacecraft model."""
        sc = MassProperties()
        sc.add_component(PointMass("bus", 500.0, 0.0, 0.0, 0.0))
        sc.add_component(PointMass("payload", 150.0, 0.0, 0.0, 1.0))
        sc.add_component(PointMass("propellant", 300.0, 0.0, 0.0, -0.5))
        sc.add_component(PointMass("solar_panel_l", 25.0, -1.5, 0.0, 0.0))
        sc.add_component(PointMass("solar_panel_r", 25.0, 1.5, 0.0, 0.0))
        return sc
