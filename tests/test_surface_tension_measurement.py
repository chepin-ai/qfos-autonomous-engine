"""
Unit tests for surface tension measurement module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from surface_tension_measurement import (TensionReading, WilhelmyPlate,
                                         PendantDropAnalyzer,
                                         CapillaryRise,
                                         DuNouyRing,
                                         InterfacialTension,
                                         SurfaceTensionMeasurement)


class TestWilhelmyPlate(unittest.TestCase):
    """Test Wilhelmy."""
    
    def setUp(self):
        self.wp = WilhelmyPlate(19.9, 0.2, 0.0)
    
    def test_perimeter(self):
        """Should compute perimeter."""
        p = self.wp.perimeter_mm()
        self.assertAlmostEqual(p, 40.2, places=5)
        print(f"  [PASS] Perim: {p:.4f} mm")
    
    def test_tension(self):
        """Should compute tension."""
        t = self.wp.surface_tension(72.8)
        self.assertGreater(t, 0)
        print(f"  [PASS] Tens: {t:.4f} mN/m")
    
    def test_force(self):
        """Should compute force."""
        f = self.wp.force_from_tension(72.0)
        self.assertGreater(f, 0)
        print(f"  [PASS] Force: {f:.4f} mN")


class TestPendantDropAnalyzer(unittest.TestCase):
    """Test pendant drop."""
    
    def setUp(self):
        self.pda = PendantDropAnalyzer(1.0)
    
    def test_bond(self):
        """Should compute Bond."""
        b = self.pda.bond_number(4.0, 2.0)
        self.assertEqual(b, 1.0)
        print(f"  [PASS] Bond: {b}")
    
    def test_tension(self):
        """Should compute tension."""
        t = self.pda.surface_tension_from_drop(4.0, 2.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] PTens: {t:.4f} mN/m")


class TestCapillaryRise(unittest.TestCase):
    """Test capillary."""
    
    def setUp(self):
        self.cr = CapillaryRise(0.5, 0.0)
    
    def test_tension(self):
        """Should compute tension."""
        t = self.cr.surface_tension(14.8, 1.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] CTens: {t:.4f} mN/m")


class TestDuNouyRing(unittest.TestCase):
    """Test ring."""
    
    def setUp(self):
        self.dn = DuNouyRing(9.5, 0.185)
    
    def test_perimeter(self):
        """Should compute perimeter."""
        p = self.dn.ring_perimeter_mm()
        self.assertGreater(p, 0)
        print(f"  [PASS] RPerim: {p:.4f} mm")
    
    def test_tension(self):
        """Should compute tension."""
        t = self.dn.surface_tension(72.0, 1.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] RTens: {t:.4f} mN/m")


class TestInterfacialTension(unittest.TestCase):
    """Test interfacial."""
    
    def setUp(self):
        self.it = InterfacialTension()
    
    def test_measure(self):
        """Should record."""
        r = self.it.measure(50.0, "pendant", 25.0)
        self.assertEqual(r.value_mN_m, 50.0)
        print("  [PASS] Rec")
    
    def test_avg(self):
        """Should average."""
        self.it.measure(50.0)
        self.it.measure(52.0)
        a = self.it.average_tension()
        self.assertEqual(a, 51.0)
        print(f"  [PASS] Avg: {a}")


class TestSurfaceTensionMeasurement(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.stm = SurfaceTensionMeasurement()
    
    def test_all(self):
        """Should measure all."""
        r = self.stm.measure_all_methods({
            "force_mN": 72.0,
            "drop_diameter_mm": 4.0,
            "apex_radius_mm": 2.0,
            "rise_height_mm": 14.8,
            "density_g_cm3": 1.0,
            "ring_force_mN": 72.0,
            "correction": 1.0
        })
        self.assertIn("wilhelmy_mN_m", r)
        print(f"  [PASS] All: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.stm.stm_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
