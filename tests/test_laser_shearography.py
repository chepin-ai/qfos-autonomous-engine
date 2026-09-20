"""
Unit tests for laser shearography module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from laser_shearography import (ShearDirection, Shearogram,
                                 ShearographyOptics, FringeAnalyzer,
                                 StrainMapper, LaserShearography)


class TestShearographyOptics(unittest.TestCase):
    """Test optics."""
    
    def setUp(self):
        self.optics = ShearographyOptics()
    
    def test_opd(self):
        """Should compute OPD."""
        opd = self.optics.optical_path_difference(1e-6, 0.0)
        self.assertAlmostEqual(opd, 2e-6, places=10)
        print(f"  [PASS] OPD: {opd:.2e}")
    
    def test_phase(self):
        """Should compute phase."""
        phase = self.optics.phase_shift(1e-9)
        self.assertGreater(phase, 0)
        print(f"  [PASS] Phase: {phase:.4f}")
    
    def test_fringe_order(self):
        """Should compute fringe order."""
        order = self.optics.fringe_order(math.pi)
        self.assertEqual(order, 0)
        print(f"  [PASS] Order: {order}")


class TestFringeAnalyzer(unittest.TestCase):
    """Test fringe analyzer."""
    
    def setUp(self):
        self.fa = FringeAnalyzer()
    
    def test_contrast(self):
        """Should compute contrast."""
        pattern = [[0.0, 1.0], [0.0, 1.0]]
        c = self.fa.fringe_contrast(pattern)
        self.assertEqual(c, 1.0)
        print(f"  [PASS] Contrast: {c}")
    
    def test_defect(self):
        """Should detect defects."""
        pattern = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]]
        d = self.fa.defect_indicator(pattern, 0.1)
        self.assertGreater(len(d), 0)
        print(f"  [PASS] Defects: {len(d)}")
    
    def test_unwrap(self):
        """Should unwrap phase."""
        wrapped = [[0.0, math.pi], [0.0, math.pi]]
        u = self.fa.wrap_phase(wrapped)
        self.assertEqual(len(u), 2)
        print("  [PASS] Unwrap")


class TestStrainMapper(unittest.TestCase):
    """Test strain mapper."""
    
    def setUp(self):
        self.sm = StrainMapper()
    
    def test_strain(self):
        """Should compute strain."""
        phase = [[0.0, 0.1, 0.2], [0.0, 0.1, 0.2]]
        s = self.sm.out_of_plane_strain(phase, 1.0)
        self.assertEqual(len(s), 2)
        print("  [PASS] Strain")
    
    def test_max_strain(self):
        """Should find max strain."""
        strain = [[0.0, 100.0], [0.0, 50.0]]
        m = self.sm.max_strain(strain)
        self.assertEqual(m, 100.0)
        print(f"  [PASS] Max: {m}")


class TestLaserShearography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ls = LaserShearography()
    
    def test_inspect(self):
        """Should inspect."""
        disp = [[0.0] * 5 for _ in range(5)]
        disp[2][2] = 1e-6
        r = self.ls.inspect(disp)
        self.assertIn("contrast", r)
        print(f"  [PASS] Insp: {r}")
    
    def test_summary(self):
        """Should summarize."""
        disp = [[0.0] * 5 for _ in range(5)]
        self.ls.inspect(disp)
        s = self.ls.shearography_summary()
        self.assertIn("inspections", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
