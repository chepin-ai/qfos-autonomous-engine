"""
Unit tests for thermal barrier coatings module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from thermal_barrier_coatings import (CoatingLayer, ThermalGradient,
                                      BondCoatOxidation,
                                      ThermalCycling,
                                      CoatingDurability,
                                      ThermalBarrierCoatings)


class TestThermalGradient(unittest.TestCase):
    """Test gradient."""
    
    def setUp(self):
        self.tg = ThermalGradient()
    
    def test_drop(self):
        """Should compute drop."""
        d = self.tg.temperature_drop(1.0, 0.001, 1.0)
        self.assertEqual(d, 1000.0)
        print(f"  [PASS] Drop: {d:.1f} K")
    
    def test_interface(self):
        """Should compute temps."""
        t = self.tg.interface_temperature(1500.0, [100.0, 200.0])
        self.assertEqual(t, [1500.0, 1400.0, 1200.0])
        print(f"  [PASS] T: {t}")


class TestBondCoatOxidation(unittest.TestCase):
    """Test oxidation."""
    
    def setUp(self):
        self.bo = BondCoatOxidation()
    
    def test_parabolic(self):
        """Should compute TGO."""
        t = self.bo.parabolic_growth(100.0, 0.01)
        self.assertEqual(t, 1.0)
        print(f"  [PASS] TGO: {t:.2f} um")
    
    def test_rate(self):
        """Should compute rate."""
        k = self.bo.growth_rate_constant(1300.0)
        self.assertGreater(k, 0)
        print(f"  [PASS] kp: {k:.6f}")


class TestThermalCycling(unittest.TestCase):
    """Test cycling."""
    
    def setUp(self):
        self.tc = ThermalCycling()
    
    def test_strain(self):
        """Should compute strain."""
        e = self.tc.thermal_strain(1000.0, 12.0)
        self.assertEqual(e, 0.012)
        print(f"  [PASS] Strain: {e:.4f}")
    
    def test_stress(self):
        """Should compute stress."""
        s = self.tc.stress_from_strain(0.01, 200.0)
        self.assertEqual(s, 2000.0)
        print(f"  [PASS] Stress: {s:.1f} MPa")
    
    def test_cycles(self):
        """Should compute cycles."""
        c = self.tc.cycles_to_failure(200.0)
        self.assertGreater(c, 0)
        print(f"  [PASS] Cycles: {c:.1f}")


class TestCoatingDurability(unittest.TestCase):
    """Test durability."""
    
    def setUp(self):
        self.cd = CoatingDurability()
    
    def test_shock(self):
        """Should compute shock param."""
        p = self.cd.thermal_shock_parameter(2.0, 1.5, 200.0, 12.0)
        self.assertGreater(p, 0)
        print(f"  [PASS] Shock: {p:.4f}")
    
    def test_spallation(self):
        """Should compute life."""
        l = self.cd.spallation_life(100.0)
        self.assertEqual(l, 0.5)
        print(f"  [PASS] Life: {l:.2f}")


class TestThermalBarrierCoatings(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.tbc = ThermalBarrierCoatings()
    
    def test_summary(self):
        """Should summarize."""
        s = self.tbc.tbc_summary()
        self.assertIn("layers", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
