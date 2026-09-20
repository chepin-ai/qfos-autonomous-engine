"""
Unit tests for hardness testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hardness_testing import (Indentation, BrinellHardness,
                              RockwellHardness,
                              VickersHardness,
                              KnoopHardness,
                              ShoreHardness,
                              HardnessConverter,
                              HardnessTesting)


class TestBrinellHardness(unittest.TestCase):
    """Test Brinell."""
    
    def setUp(self):
        self.bh = BrinellHardness(10.0)
    
    def test_hardness(self):
        """Should compute HBW."""
        h = self.bh.hardness(29420.0, 4.0)
        self.assertGreater(h, 0)
        print(f"  [PASS] HBW: {h:.1f}")
    
    def test_diameter(self):
        """Should compute diameter."""
        d = self.bh.indentation_diameter(29420.0, 200.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Diam: {d:.3f} mm")


class TestRockwellHardness(unittest.TestCase):
    """Test Rockwell."""
    
    def setUp(self):
        self.rh = RockwellHardness()
    
    def test_c(self):
        """Should compute HRC."""
        h = self.rh.c_scale_hardness(0.1)
        self.assertEqual(h, 50.0)
        print(f"  [PASS] HRC: {h}")
    
    def test_b(self):
        """Should compute HRB."""
        h = self.rh.b_scale_hardness(0.1)
        self.assertEqual(h, 80.0)
        print(f"  [PASS] HRB: {h}")
    
    def test_depth(self):
        """Should compute depth."""
        d = self.rh.depth_from_hrc(50.0)
        self.assertEqual(d, 0.1)
        print(f"  [PASS] Dep: {d}")


class TestVickersHardness(unittest.TestCase):
    """Test Vickers."""
    
    def setUp(self):
        self.vh = VickersHardness()
    
    def test_hardness(self):
        """Should compute HV."""
        h = self.vh.hardness(490.3, 0.5)
        self.assertGreater(h, 0)
        print(f"  [PASS] HV: {h:.1f}")
    
    def test_diagonal(self):
        """Should compute diagonal."""
        d = self.vh.diagonal_from_hv(490.3, 200.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Diag: {d:.4f} mm")
    
    def test_depth(self):
        """Should compute depth."""
        dep = self.vh.indentation_depth(0.5)
        self.assertGreater(dep, 0)
        print(f"  [PASS] Dep: {dep:.4f} mm")


class TestKnoopHardness(unittest.TestCase):
    """Test Knoop."""
    
    def setUp(self):
        self.kh = KnoopHardness()
    
    def test_hardness(self):
        """Should compute HK."""
        h = self.kh.hardness(490.3, 0.7)
        self.assertGreater(h, 0)
        print(f"  [PASS] HK: {h:.1f}")


class TestShoreHardness(unittest.TestCase):
    """Test Shore."""
    
    def setUp(self):
        self.sh = ShoreHardness("A")
    
    def test_hardness(self):
        """Should compute Shore."""
        h = self.sh.hardness(1.27)
        self.assertEqual(h, 50.0)
        print(f"  [PASS] Shore: {h}")


class TestHardnessConverter(unittest.TestCase):
    """Test converter."""
    
    def setUp(self):
        self.hc = HardnessConverter()
    
    def test_hrc_hv(self):
        """Should convert HRC to HV."""
        hv = self.hc.hrc_to_hv(50.0)
        self.assertEqual(hv, 500.0)
        print(f"  [PASS] HV: {hv}")
    
    def test_hv_hrc(self):
        """Should convert HV to HRC."""
        hrc = self.hc.hv_to_hrc(500.0)
        self.assertEqual(hrc, 50.0)
        print(f"  [PASS] HRC: {hrc}")
    
    def test_hbw_hv(self):
        """Should convert HBW to HV."""
        hv = self.hc.hbw_to_hv(200.0)
        self.assertEqual(hv, 210.0)
        print(f"  [PASS] HV: {hv}")


class TestHardnessTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ht = HardnessTesting()
    
    def test_all(self):
        """Should test all."""
        r = self.ht.test_all(Indentation(4.0, 0.1, 29420.0))
        self.assertIn("brinell_HBW", r)
        print(f"  [PASS] All: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.ht.ht_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
