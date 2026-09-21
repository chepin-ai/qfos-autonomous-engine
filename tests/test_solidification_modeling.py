"""
Unit tests for solidification modeling module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from solidification_modeling import (AlloyComposition, NucleationModeling,
                                     GrowthKinetics,
                                     ScheilEquation,
                                     Microsegregation,
                                     SolidificationModeling)


class TestNucleationModeling(unittest.TestCase):
    """Test nucleation."""
    
    def setUp(self):
        self.nm = NucleationModeling()
    
    def test_rate(self):
        """Should compute rate."""
        r = self.nm.homogeneous_nucleation_rate(100.0)
        self.assertGreaterEqual(r, 0)
        print(f"  [PASS] I: {r:.2e}")
    
    def test_radius(self):
        """Should compute radius."""
        rad = self.nm.critical_radius(100.0)
        self.assertGreater(rad, 0)
        print(f"  [PASS] R*: {rad:.2e}")


class TestGrowthKinetics(unittest.TestCase):
    """Test growth."""
    
    def setUp(self):
        self.gk = GrowthKinetics()
    
    def test_velocity(self):
        """Should compute velocity."""
        v = self.gk.dendrite_tip_velocity(50.0)
        self.assertGreater(v, 0)
        print(f"  [PASS] V: {v:.2e}")
    
    def test_sdas(self):
        """Should compute SDAS."""
        s = self.gk.secondary_dendrite_arm_spacing(100.0)
        self.assertGreater(s, 0)
        print(f"  [PASS] SDAS: {s:.2e}")


class TestScheilEquation(unittest.TestCase):
    """Test Scheil."""
    
    def setUp(self):
        self.se = ScheilEquation()
    
    def test_solid(self):
        """Should compute solid composition."""
        c = self.se.solid_composition(0.1, 0.5, 0.5)
        self.assertGreater(c, 0)
        print(f"  [PASS] Cs: {c:.4f}")
    
    def test_liquid(self):
        """Should compute liquid composition."""
        c = self.se.liquid_composition(0.1, 0.5, 0.5)
        self.assertGreater(c, 0)
        print(f"  [PASS] Cl: {c:.4f}")
    
    def test_eutectic(self):
        """Should compute eutectic fraction."""
        f = self.se.final_eutectic_fraction(0.1, 0.5, 0.5)
        self.assertGreaterEqual(f, 0)
        print(f"  [PASS] Fe: {f:.4f}")


class TestMicrosegregation(unittest.TestCase):
    """Test microsegregation."""
    
    def setUp(self):
        self.ms = Microsegregation()
    
    def test_lever(self):
        """Should compute lever rule."""
        c = self.ms.lever_rule_composition(0.1, 0.5, 0.5)
        self.assertGreater(c, 0)
        print(f"  [PASS] Clever: {c:.4f}")
    
    def test_ratio(self):
        """Should compute segregation ratio."""
        r = self.ms.segregation_ratio(0.2, 0.1)
        self.assertEqual(r, 2.0)
        print(f"  [PASS] SR: {r:.1f}")


class TestSolidificationModeling(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.sm = SolidificationModeling()
    
    def test_summary(self):
        """Should summarize."""
        s = self.sm.solidification_summary()
        self.assertIn("models", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
