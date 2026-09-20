"""
Unit tests for rheology module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rheology import (RheologyPoint, ViscosityCalculator,
                      ShearStressAnalyzer,
                      ModulusAnalyzer,
                      CreepCompliance,
                      Rheology)


class TestViscosityCalculator(unittest.TestCase):
    """Test viscosity."""
    
    def setUp(self):
        self.vc = ViscosityCalculator()
    
    def test_newtonian(self):
        """Should compute Newtonian."""
        v = self.vc.newtonian_viscosity(10.0, 5.0)
        self.assertEqual(v, 2.0)
        print(f"  [PASS] Newt: {v} Pa.s")
    
    def test_apparent(self):
        """Should compute apparent."""
        pts = [RheologyPoint(1.0, 10.0, 0.0), RheologyPoint(2.0, 20.0, 1.0)]
        v = self.vc.apparent_viscosity(pts)
        self.assertEqual(v, 10.0)
        print(f"  [PASS] App: {v} Pa.s")
    
    def test_power_law(self):
        """Should compute power-law."""
        v = self.vc.power_law_viscosity(1.0, 0.5, 10.0)
        self.assertGreater(v, 0)
        print(f"  [PASS] PL: {v:.4f} Pa.s")


class TestShearStressAnalyzer(unittest.TestCase):
    """Test shear."""
    
    def setUp(self):
        self.ssa = ShearStressAnalyzer()
    
    def test_yield(self):
        """Should estimate yield."""
        pts = [RheologyPoint(1.0, 5.0, 0.0), RheologyPoint(2.0, 10.0, 1.0)]
        y = self.ssa.yield_stress(pts)
        self.assertEqual(y, 5.0)
        print(f"  [PASS] Yield: {y} Pa")
    
    def test_bingham(self):
        """Should compute Bingham."""
        s = self.ssa.bingham_model(5.0, 2.0, 10.0)
        self.assertEqual(s, 25.0)
        print(f"  [PASS] Bing: {s} Pa")
    
    def test_casson(self):
        """Should compute Casson."""
        s = self.ssa.casson_model(4.0, 1.0, 16.0)
        self.assertGreater(s, 0)
        print(f"  [PASS] Cass: {s:.2f} Pa")


class TestModulusAnalyzer(unittest.TestCase):
    """Test modulus."""
    
    def setUp(self):
        self.ma = ModulusAnalyzer()
    
    def test_storage(self):
        """Should compute G'."""
        g = self.ma.storage_modulus(100.0, 0.1, 0.0)
        self.assertEqual(g, 1000.0)
        print(f"  [PASS] G': {g} Pa")
    
    def test_loss(self):
        """Should compute G''."""
        g = self.ma.loss_modulus(100.0, 0.1, 90.0)
        self.assertEqual(g, 1000.0)
        print(f"  [PASS] G'': {g} Pa")
    
    def test_tan_delta(self):
        """Should compute tan(delta)."""
        t = self.ma.tan_delta(100.0, 50.0)
        self.assertEqual(t, 0.5)
        print(f"  [PASS] Tan: {t}")
    
    def test_complex(self):
        """Should compute |G*|."""
        g = self.ma.complex_modulus(300.0, 400.0)
        self.assertEqual(g, 500.0)
        print(f"  [PASS] |G*|: {g} Pa")


class TestCreepCompliance(unittest.TestCase):
    """Test creep."""
    
    def setUp(self):
        self.cc = CreepCompliance()
    
    def test_compliance(self):
        """Should compute compliance."""
        c = self.cc.compliance(0.1, 1000.0)
        self.assertEqual(c, 1e-4)
        print(f"  [PASS] Comp: {c}")
    
    def test_maxwell(self):
        """Should compute Maxwell."""
        c = self.cc.maxwell_compliance(1.0, 1e6, 1e3)
        self.assertGreater(c, 0)
        print(f"  [PASS] Maxw: {c:.2e}")
    
    def test_kv(self):
        """Should compute K-V."""
        c = self.cc.kelvin_voigt_compliance(1.0, 1e6, 1e3, 1000.0)
        self.assertGreater(c, 0)
        print(f"  [PASS] KV: {c:.2e}")


class TestRheology(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.r = Rheology()
    
    def test_add(self):
        """Should add point."""
        self.r.add_point(RheologyPoint(1.0, 10.0, 0.0))
        self.assertEqual(len(self.r.points), 1)
        print("  [PASS] Add")
    
    def test_analyze(self):
        """Should analyze."""
        self.r.add_point(RheologyPoint(1.0, 10.0, 0.0))
        self.r.add_point(RheologyPoint(2.0, 20.0, 1.0))
        a = self.r.analyze()
        self.assertIn("apparent_viscosity_Pa_s", a)
        print(f"  [PASS] Anlz: {a}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.r.rheo_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
