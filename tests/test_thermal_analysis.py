"""
Unit tests for thermal analysis module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from thermal_analysis import (ThermalPoint, HeatConduction,
                              TransientHeat,
                              ThermalExpansion,
                              SpecificHeatAnalysis,
                              ThermalAnalysis)


class TestHeatConduction(unittest.TestCase):
    """Test conduction."""
    
    def setUp(self):
        self.hc = HeatConduction(200.0)
    
    def test_heat_flux(self):
        """Should compute heat flux."""
        q = self.hc.heat_flux(1.0, 0.01, 100.0)
        self.assertEqual(q, 2_000_000.0)
        print(f"  [PASS] Q: {q:.0f} W")
    
    def test_thermal_resistance(self):
        """Should compute R_th."""
        r = self.hc.thermal_resistance(0.01, 1.0)
        self.assertEqual(r, 0.00005)
        print(f"  [PASS] R: {r}")
    
    def test_temp_distribution(self):
        """Should compute distribution."""
        d = self.hc.temperature_distribution(1.0, 300.0, 400.0, 5)
        self.assertEqual(len(d), 5)
        self.assertEqual(d[0].temperature_K, 300.0)
        self.assertEqual(d[-1].temperature_K, 400.0)
        print(f"  [PASS] Dist: {len(d)} pts")


class TestTransientHeat(unittest.TestCase):
    """Test transient."""
    
    def setUp(self):
        self.th = TransientHeat(1e-5)
    
    def test_biot(self):
        """Should compute Biot."""
        b = self.th.biot_number(10.0, 0.01, 200.0)
        self.assertEqual(b, 0.0005)
        print(f"  [PASS] Bi: {b}")


class TestThermalExpansion(unittest.TestCase):
    """Test expansion."""
    
    def setUp(self):
        self.te = ThermalExpansion(1.2e-5)
    
    def test_delta_length(self):
        """Should compute dL."""
        dl = self.te.delta_length(1.0, 100.0)
        self.assertAlmostEqual(dl, 0.0012, places=5)
        print(f"  [PASS] dL: {dl:.5f}")
    
    def test_delta_volume(self):
        """Should compute dV."""
        dv = self.te.delta_volume(1.0, 100.0)
        self.assertAlmostEqual(dv, 0.0036, places=5)
        print(f"  [PASS] dV: {dv:.5f}")
    
    def test_thermal_stress(self):
        """Should compute stress."""
        s = self.te.thermal_stress(200.0, 100.0)
        self.assertAlmostEqual(s, 240.0, delta=1.0)
        print(f"  [PASS] Sth: {s:.1f} MPa")


class TestSpecificHeatAnalysis(unittest.TestCase):
    """Test specific heat."""
    
    def setUp(self):
        self.sha = SpecificHeatAnalysis()
    
    def test_heat_capacity(self):
        """Should compute C."""
        c = self.sha.heat_capacity(1.0, 1000.0)
        self.assertEqual(c, 1000.0)
        print(f"  [PASS] C: {c}")
    
    def test_energy(self):
        """Should compute Q."""
        q = self.sha.energy_required(1.0, 1000.0, 10.0)
        self.assertEqual(q, 10000.0)
        print(f"  [PASS] Q: {q}")


class TestThermalAnalysis(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ta = ThermalAnalysis()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ta.ta_summary()
        self.assertIn("analyses", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
