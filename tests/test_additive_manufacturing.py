"""
Unit tests for additive manufacturing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from additive_manufacturing import (ProcessParameters, ProcessParameterOptimization,
                                    MeltPoolThermalModeling,
                                    ResidualStressPrediction,
                                    SupportStructureDesign,
                                    AdditiveManufacturing)


class TestProcessParameterOptimization(unittest.TestCase):
    """Test process."""
    
    def setUp(self):
        self.ppo = ProcessParameterOptimization()
        self.params = ProcessParameters(200.0, 1000.0, 0.1, 0.03)
    
    def test_energy(self):
        """Should compute energy density."""
        e = self.ppo.energy_density(self.params)
        self.assertGreater(e, 0)
        print(f"  [PASS] EVD: {e:.2f}")
    
    def test_linear(self):
        """Should compute linear energy."""
        l = self.ppo.linear_energy_density(self.params)
        self.assertEqual(l, 0.2)
        print(f"  [PASS] LED: {l:.3f}")
    
    def test_optimal(self):
        """Should compute optimal power."""
        p = self.ppo.optimal_power(100.0, 1000.0, 0.1, 0.03)
        self.assertEqual(p, 300.0)
        print(f"  [PASS] P: {p:.1f}")


class TestMeltPoolThermalModeling(unittest.TestCase):
    """Test melt pool."""
    
    def setUp(self):
        self.mptm = MeltPoolThermalModeling()
    
    def test_depth(self):
        """Should compute depth."""
        d = self.mptm.melt_pool_depth(200.0, 1000.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] D: {d:.4f}")
    
    def test_width(self):
        """Should compute width."""
        w = self.mptm.melt_pool_width(200.0, 1000.0)
        self.assertGreater(w, 0)
        print(f"  [PASS] W: {w:.4f}")
    
    def test_cooling(self):
        """Should compute cooling rate."""
        c = self.mptm.cooling_rate(1000.0)
        self.assertGreater(c, 0)
        print(f"  [PASS] CR: {c:.2e}")


class TestResidualStressPrediction(unittest.TestCase):
    """Test stress."""
    
    def setUp(self):
        self.rsp = ResidualStressPrediction()
    
    def test_strain(self):
        """Should compute strain."""
        e = self.rsp.thermal_strain(1000.0)
        self.assertEqual(e, 0.01)
        print(f"  [PASS] Eps: {e:.4f}")
    
    def test_stress(self):
        """Should compute stress."""
        s = self.rsp.residual_stress(200.0, 0.01)
        self.assertGreater(s, 0)
        print(f"  [PASS] Sig: {s:.2f}")
    
    def test_distortion(self):
        """Should compute distortion."""
        d = self.rsp.distortion(100.0, 200.0, 100.0, 10.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Dist: {d:.4f}")


class TestSupportStructureDesign(unittest.TestCase):
    """Test support."""
    
    def setUp(self):
        self.ssd = SupportStructureDesign()
    
    def test_angle(self):
        """Should compute angle."""
        a = self.ssd.overhang_angle(10.0, 10.0)
        self.assertEqual(a, 45.0)
        print(f"  [PASS] A: {a:.1f}")
    
    def test_needs(self):
        """Should check support."""
        n = self.ssd.needs_support(30.0)
        self.assertTrue(n)
        print(f"  [PASS] Sup: {n}")
    
    def test_volume(self):
        """Should compute volume."""
        v = self.ssd.support_volume(100.0, 10.0)
        self.assertEqual(v, 300.0)
        print(f"  [PASS] Vol: {v:.1f}")


class TestAdditiveManufacturing(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.am = AdditiveManufacturing()
    
    def test_summary(self):
        """Should summarize."""
        s = self.am.am_summary()
        self.assertIn("modules", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
