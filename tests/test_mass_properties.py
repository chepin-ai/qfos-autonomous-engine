"""
Unit tests for mass properties module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mass_properties import MassProperties, PointMass, InertiaTensor


class TestInertiaTensor(unittest.TestCase):
    """Test inertia tensor."""
    
    def test_principal_moments(self):
        """Should compute principal moments."""
        I = InertiaTensor(Ixx=10.0, Iyy=5.0, Izz=3.0)
        p = I.principal_moments()
        self.assertEqual(p, (10.0, 5.0, 3.0))
        print("  [PASS] Principal moments: (10, 5, 3)")
    
    def test_as_matrix(self):
        """Should return matrix."""
        I = InertiaTensor(Ixx=1.0, Iyy=2.0, Izz=3.0, Ixy=0.5)
        m = I.as_matrix()
        self.assertEqual(len(m), 3)
        self.assertEqual(m[0][1], -0.5)
        print("  [PASS] Matrix: 3x3 with off-diagonal")


class TestMassProperties(unittest.TestCase):
    """Test mass properties."""
    
    def test_total_mass(self):
        """Should compute total mass."""
        sc = MassProperties()
        sc.add_component(PointMass("a", 10.0))
        sc.add_component(PointMass("b", 20.0))
        self.assertEqual(sc.total_mass_kg(), 30.0)
        print("  [PASS] Total mass: 30 kg")
    
    def test_center_of_mass(self):
        """Should compute CM."""
        sc = MassProperties()
        sc.add_component(PointMass("a", 10.0, x_m=0.0))
        sc.add_component(PointMass("b", 10.0, x_m=2.0))
        cm = sc.center_of_mass()
        self.assertAlmostEqual(cm[0], 1.0, delta=0.01)
        print(f"  [PASS] CM: ({cm[0]:.2f}, {cm[1]:.2f}, {cm[2]:.2f})")
    
    def test_inertia_tensor(self):
        """Should compute inertia tensor."""
        sc = MassProperties()
        sc.add_component(PointMass("a", 10.0, y_m=1.0, z_m=0.0))
        sc.add_component(PointMass("b", 10.0, y_m=-1.0, z_m=0.0))
        I = sc.inertia_tensor()
        self.assertGreater(I.Ixx, 0.0)
        print(f"  [PASS] Ixx={I.Ixx:.2f}, Iyy={I.Iyy:.2f}, Izz={I.Izz:.2f}")
    
    def test_radius_of_gyration(self):
        """Should compute radius of gyration."""
        sc = MassProperties()
        sc.add_component(PointMass("a", 100.0, y_m=1.0))
        sc.add_component(PointMass("b", 100.0, y_m=-1.0))
        rg = sc.radius_of_gyration_m()
        self.assertGreater(rg[0], 0.0)
        print(f"  [PASS] RG: kx={rg[0]:.3f}, ky={rg[1]:.3f}, kz={rg[2]:.3f}")
    
    def test_shift_component(self):
        """Should shift component."""
        sc = MassProperties()
        sc.add_component(PointMass("a", 10.0, x_m=0.0))
        sc.shift_component("a", 1.0, 0.0, 0.0)
        cm = sc.center_of_mass()
        self.assertAlmostEqual(cm[0], 1.0, delta=0.01)
        print("  [PASS] Shift: CM moved to x=1.0")
    
    def test_remove_component(self):
        """Should remove component."""
        sc = MassProperties()
        sc.add_component(PointMass("a", 10.0))
        sc.add_component(PointMass("b", 20.0))
        sc.remove_component("a")
        self.assertEqual(sc.total_mass_kg(), 20.0)
        print("  [PASS] Remove: mass=20 kg")
    
    def test_mass_budget(self):
        """Should provide mass budget."""
        sc = MassProperties.create_simple_spacecraft()
        budget = sc.mass_budget_summary()
        self.assertIn("total_mass_kg", budget)
        self.assertIn("inertia_tensor_kg_m2", budget)
        self.assertIn("components", budget)
        print(f"  [PASS] Budget: {budget['total_mass_kg']:.1f} kg")
    
    def test_slosh_effect(self):
        """Should estimate slosh."""
        sc = MassProperties.create_simple_spacecraft()
        slosh = sc.propellant_slosh_effect(
            propellant_mass_kg=100.0,
            tank_dimensions_m=(1.0, 0.5, 0.5),
            fill_level_percent=50.0
        )
        self.assertIn("cm_shift_m", slosh)
        print(f"  [PASS] Slosh: CM shift={slosh['cm_shift_m']:.6f} m")
    
    def test_create_simple(self):
        """Should create simple spacecraft."""
        sc = MassProperties.create_simple_spacecraft()
        self.assertGreater(len(sc.components), 3)
        print(f"  [PASS] Simple SC: {len(sc.components)} components")


if __name__ == '__main__':
    unittest.main(verbosity=2)
