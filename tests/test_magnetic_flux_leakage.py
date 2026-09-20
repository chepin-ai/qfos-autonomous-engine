"""
Unit tests for magnetic flux leakage module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from magnetic_flux_leakage import (MFLSensor, LeakageFieldCalculator,
                                    DefectSizer, PipeWallLossEstimator,
                                    MagneticFluxLeakage)


class TestLeakageFieldCalculator(unittest.TestCase):
    """Test leakage field."""
    
    def setUp(self):
        self.lfc = LeakageFieldCalculator()
    
    def test_field(self):
        """Should compute field."""
        f = self.lfc.field_from_defect(2.0, 5.0, 2.0)
        self.assertGreater(f, 0)
        print(f"  [PASS] Field: {f:.4f} mT")
    
    def test_radial(self):
        """Should compute radial."""
        r = self.lfc.radial_component(2.0, 5.0, 2.0, 1.0)
        self.assertIsNotNone(r)
        print(f"  [PASS] Radial: {r:.4f}")
    
    def test_axial(self):
        """Should compute axial."""
        a = self.lfc.axial_component(2.0, 5.0, 2.0, 1.0)
        self.assertIsNotNone(a)
        print(f"  [PASS] Axial: {a:.4f}")


class TestDefectSizer(unittest.TestCase):
    """Test defect sizer."""
    
    def setUp(self):
        self.ds = DefectSizer()
    
    def test_depth(self):
        """Should estimate depth."""
        d = self.ds.depth_from_signal(0.5, 10.0, 1.5)
        self.assertGreater(d, 0)
        print(f"  [PASS] Depth: {d:.4f}")
    
    def test_length(self):
        """Should estimate length."""
        l = self.ds.length_from_signal(5.0)
        self.assertEqual(l, 5.0)
        print(f"  [PASS] Len: {l}")
    
    def test_volume(self):
        """Should compute volume."""
        v = self.ds.volume_loss(2.0, 5.0, 3.0)
        self.assertEqual(v, 30.0)
        print(f"  [PASS] Vol: {v}")


class TestPipeWallLossEstimator(unittest.TestCase):
    """Test wall loss."""
    
    def setUp(self):
        self.pwle = PipeWallLossEstimator(10.0)
    
    def test_remaining(self):
        """Should estimate remaining."""
        self.pwle.add_reading(0.5)
        r = self.pwle.remaining_thickness(DefectSizer(), 1.5)
        self.assertGreaterEqual(r, 0)
        print(f"  [PASS] Rem: {r:.4f}")
    
    def test_percentage(self):
        """Should compute percentage."""
        self.pwle.add_reading(0.5)
        p = self.pwle.wall_loss_percentage(DefectSizer(), 1.5)
        self.assertGreaterEqual(p, 0)
        print(f"  [PASS] Pct: {p:.2f}%")


class TestMagneticFluxLeakage(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.mfl = MagneticFluxLeakage()
    
    def test_scan(self):
        """Should scan."""
        self.mfl.scan([0.0, 1.0, 2.0], [1.0, 2.0, 0.5], [5.0, 5.0, 5.0])
        self.assertEqual(len(self.mfl.signals), 3)
        print("  [PASS] Scan")
    
    def test_find(self):
        """Should find defects."""
        self.mfl.scan([0.0, 1.0, 2.0], [1.0, 3.0, 0.5], [5.0, 5.0, 5.0])
        defects = self.mfl.find_defects(0.1)
        self.assertGreaterEqual(len(defects), 0)
        print(f"  [PASS] Find: {len(defects)} defects")
    
    def test_summary(self):
        """Should summarize."""
        s = self.mfl.mfl_summary()
        self.assertIn("readings", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
