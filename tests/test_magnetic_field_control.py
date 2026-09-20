"""
Unit tests for magnetic field control module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from magnetic_field_control import (CoilType, FieldDirection, FieldVector,
                                    CoilController, FieldGenerator,
                                    ShieldingAssessor, MagneticFieldControl)


class TestFieldVector(unittest.TestCase):
    """Test field vector."""
    
    def test_magnitude(self):
        """Should compute magnitude."""
        v = FieldVector(1e-5, 0.0, 0.0)
        self.assertAlmostEqual(v.magnitude(), 1e-5)
        print(f"  [PASS] Magnitude: {v.magnitude()}")
    
    def test_direction(self):
        """Should compute direction."""
        v = FieldVector(1e-5, 0.0, 0.0)
        d = v.direction()
        self.assertAlmostEqual(d[0], 1.0)
        print(f"  [PASS] Direction: ({d[0]:.1f}, {d[1]:.1f}, {d[2]:.1f})")


class TestCoilController(unittest.TestCase):
    """Test coil controller."""
    
    def setUp(self):
        self.coil = CoilController(CoilType.SOLENOID, turns=100,
                                   radius_m=0.1, max_current_A=10.0)
    
    def test_field_center_zero(self):
        """Should have zero field with no current."""
        b = self.coil.field_at_center()
        self.assertEqual(b, 0.0)
        print("  [PASS] Zero current: 0 T")
    
    def test_field_center(self):
        """Should compute field at center."""
        self.coil.set_current(1.0)
        b = self.coil.field_at_center()
        self.assertGreater(b, 0)
        print(f"  [PASS] Field: {b:.6f} T")
    
    def test_field_on_axis(self):
        """Should compute field on axis."""
        self.coil.set_current(1.0)
        b = self.coil.field_on_axis(0.05)
        self.assertGreater(b, 0)
        print(f"  [PASS] Axis: {b:.6f} T")
    
    def test_set_current_limit(self):
        """Should enforce current limit."""
        ok = self.coil.set_current(15.0)
        self.assertFalse(ok)
        print("  [PASS] Limit: rejected")
    
    def test_power(self):
        """Should compute power."""
        self.coil.set_current(2.0)
        p = self.coil.power_dissipation(resistance_ohm=0.5)
        self.assertEqual(p, 4.0 * 0.5)
        print(f"  [PASS] Power: {p} W")


class TestFieldGenerator(unittest.TestCase):
    """Test field generator."""
    
    def setUp(self):
        self.fg = FieldGenerator()
        self.fg.add_coil("X", CoilController(CoilType.SOLENOID, 100, 0.1, 10.0))
        self.fg.add_coil("Y", CoilController(CoilType.SOLENOID, 100, 0.1, 10.0))
    
    def test_compute_field(self):
        """Should compute total field."""
        self.fg.coils["X"].set_current(1.0)
        field = self.fg.compute_field()
        self.assertGreater(field.magnitude(), 0)
        print(f"  [PASS] Field: {field.magnitude():.6f} T")
    
    def test_field_error(self):
        """Should compute field error."""
        self.fg.set_target_field(0.0, 0.0, 1e-4)
        error = self.fg.field_error()
        self.assertGreaterEqual(error, 0)
        print(f"  [PASS] Error: {error:.6f} T")
    
    def test_total_power(self):
        """Should compute total power."""
        self.fg.coils["X"].set_current(1.0)
        self.fg.coils["Y"].set_current(2.0)
        p = self.fg.total_power(resistance_ohm=1.0)
        self.assertEqual(p, 1.0 + 4.0)
        print(f"  [PASS] Total power: {p} W")


class TestShieldingAssessor(unittest.TestCase):
    """Test shielding assessor."""
    
    def setUp(self):
        self.sa = ShieldingAssessor(shield_thickness_m=0.001,
                                    material_permeability=5000.0)
    
    def test_shielding_factor(self):
        """Should compute shielding factor."""
        sf = self.sa.shielding_factor(0.1)
        self.assertGreater(sf, 1.0)
        print(f"  [PASS] SF: {sf:.1f}")
    
    def test_attenuation(self):
        """Should compute attenuation."""
        db = self.sa.attenuation_db(0.1)
        self.assertGreater(db, 0)
        print(f"  [PASS] Attenuation: {db:.1f} dB")
    
    def test_field_inside(self):
        """Should compute internal field."""
        b_in = self.sa.field_inside(1e-4, 0.1)
        self.assertLess(b_in, 1e-4)
        print(f"  [PASS] Inside: {b_in:.8f} T")


class TestMagneticFieldControl(unittest.TestCase):
    """Test unified magnetic field control."""
    
    def setUp(self):
        self.mfc = MagneticFieldControl()
        self.mfc.add_coil("main", CoilType.SOLENOID, 200, 0.15, 5.0)
    
    def test_add_coil(self):
        """Should add coil."""
        self.assertIn("main", self.mfc.generator.coils)
        print("  [PASS] Add: main coil")
    
    def test_set_current(self):
        """Should set current."""
        ok = self.mfc.set_coil_current("main", 2.0)
        self.assertTrue(ok)
        self.assertEqual(self.mfc.generator.coils["main"].current, 2.0)
        print("  [PASS] Current: 2.0 A")
    
    def test_measure(self):
        """Should measure field."""
        self.mfc.set_coil_current("main", 1.0)
        self.mfc.measure_field()
        self.assertEqual(len(self.mfc.measurements), 1)
        print("  [PASS] Measure: 1 reading")
    
    def test_assess_shielding(self):
        """Should assess shielding."""
        result = self.mfc.assess_shielding(1e-4, 0.1)
        self.assertIn("shielding_factor", result)
        self.assertIn("effective", result)
        print(f"  [PASS] Shield: SF={result['shielding_factor']:.1f}")
    
    def test_summary(self):
        """Should provide summary."""
        self.mfc.set_coil_current("main", 1.0)
        summary = self.mfc.control_summary()
        self.assertEqual(summary["coils"], 1)
        print(f"  [PASS] Summary: {summary['coils']} coils")


if __name__ == '__main__':
    unittest.main(verbosity=2)
