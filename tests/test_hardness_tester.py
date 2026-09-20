"""
Unit tests for hardness tester module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hardness_tester import (HardnessScale, Indentation,
                             BrinellHardness, RockwellHardness,
                             VickersHardness, KnoopHardness,
                             HardnessConverter, HardnessTester)


class TestBrinellHardness(unittest.TestCase):
    """Test Brinell hardness."""
    
    def setUp(self):
        self.bh = BrinellHardness()
    
    def test_compute(self):
        """Should compute HBW."""
        hbw = self.bh.compute(29420.0, 5.0)  # 3000 kgf
        self.assertGreater(hbw, 0)
        print(f"  [PASS] HBW: {hbw:.1f}")
    
    def test_estimate_diameter(self):
        """Should estimate diameter."""
        d = self.bh.estimate_diameter(29420.0, 200.0)
        self.assertGreater(d, 0)
        self.assertLess(d, 10.0)
        print(f"  [PASS] Diam: {d:.3f}")
    
    def test_invalid(self):
        """Should reject invalid."""
        hbw = self.bh.compute(29420.0, 15.0)
        self.assertEqual(hbw, 0.0)
        print("  [PASS] Invalid")


class TestRockwellHardness(unittest.TestCase):
    """Test Rockwell hardness."""
    
    def setUp(self):
        self.rh = RockwellHardness()
    
    def test_hrc(self):
        """Should compute HRC."""
        hrc = self.rh.hrc(0.1)
        self.assertAlmostEqual(hrc, 50.0)
        print(f"  [PASS] HRC: {hrc}")
    
    def test_hrb(self):
        """Should compute HRB."""
        hrb = self.rh.hrb(0.1)
        self.assertAlmostEqual(hrb, 80.0)
        print(f"  [PASS] HRB: {hrb}")
    
    def test_depth_from_hrc(self):
        """Should invert HRC."""
        d = self.rh.depth_from_hrc(60.0)
        self.assertAlmostEqual(d, 0.08)
        print(f"  [PASS] Depth: {d}")


class TestVickersHardness(unittest.TestCase):
    """Test Vickers hardness."""
    
    def setUp(self):
        self.vh = VickersHardness()
    
    def test_compute(self):
        """Should compute HV."""
        hv = self.vh.compute(98.07, 0.5)
        self.assertGreater(hv, 0)
        print(f"  [PASS] HV: {hv:.1f}")
    
    def test_diagonal(self):
        """Should estimate diagonal."""
        d = self.vh.diagonal_from_hv(98.07, 200.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Diag: {d:.4f}")


class TestKnoopHardness(unittest.TestCase):
    """Test Knoop hardness."""
    
    def setUp(self):
        self.kh = KnoopHardness()
    
    def test_compute(self):
        """Should compute HK."""
        hk = self.kh.compute(9.807, 0.2)
        self.assertGreater(hk, 0)
        print(f"  [PASS] HK: {hk:.1f}")


class TestHardnessConverter(unittest.TestCase):
    """Test hardness converter."""
    
    def test_hrc_to_hv(self):
        """Should convert HRC to HV."""
        hv = HardnessConverter.hrc_to_hv(50.0)
        self.assertGreater(hv, 0)
        print(f"  [PASS] HRC->HV: {hv:.1f}")
    
    def test_hv_to_hrc(self):
        """Should convert HV to HRC."""
        hrc = HardnessConverter.hv_to_hrc(220.0)
        self.assertGreater(hrc, 0)
        print(f"  [PASS] HV->HRC: {hrc:.1f}")
    
    def test_roundtrip(self):
        """Should approximate roundtrip."""
        hrc = 50.0
        hv = HardnessConverter.hrc_to_hv(hrc)
        hrc_back = HardnessConverter.hv_to_hrc(hv)
        self.assertAlmostEqual(hrc, hrc_back, places=0)
        print(f"  [PASS] Round: {hrc_back:.1f}")


class TestHardnessTester(unittest.TestCase):
    """Test unified hardness tester."""
    
    def setUp(self):
        self.ht = HardnessTester()
    
    def test_measure_brinell(self):
        """Should measure Brinell."""
        r = self.ht.measure_brinell(29420.0, 5.0)
        self.assertIn("value", r)
        print(f"  [PASS] Brinell: {r['value']:.1f}")
    
    def test_measure_vickers(self):
        """Should measure Vickers."""
        r = self.ht.measure_vickers(98.07, 0.5)
        self.assertIn("value", r)
        print(f"  [PASS] Vickers: {r['value']:.1f}")
    
    def test_report(self):
        """Should generate report."""
        self.ht.measure_vickers(98.07, 0.5)
        rep = self.ht.hardness_report()
        self.assertIn("avg_hardness", rep)
        print(f"  [PASS] Report: avg={rep['avg_hardness']:.1f}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
