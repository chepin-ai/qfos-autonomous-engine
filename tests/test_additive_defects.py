"""
Unit tests for additive manufacturing defects module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from additive_defects import (DefectRegion, PorosityDetection,
                              CrackDetection,
                              LayerMisalignment,
                              GeometricDeviation,
                              AdditiveDefects)


class TestPorosityDetection(unittest.TestCase):
    """Test porosity."""
    
    def setUp(self):
        self.pd = PorosityDetection()
    
    def test_fraction(self):
        """Should compute fraction."""
        f = self.pd.porosity_fraction(1.0, 10.0)
        self.assertEqual(f, 0.1)
        print(f"  [PASS] Por: {f:.2f}")
    
    def test_diameter(self):
        """Should compute diameter."""
        d = self.pd.pore_equivalent_diameter(1.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] D: {d:.3f} mm")
    
    def test_threshold(self):
        """Should compute threshold."""
        t = self.pd.critical_porosity_threshold()
        self.assertGreater(t, 0)
        print(f"  [PASS] Th: {t:.4f}")


class TestCrackDetection(unittest.TestCase):
    """Test crack."""
    
    def setUp(self):
        self.cd = CrackDetection()
    
    def test_severity(self):
        """Should classify severity."""
        s = self.cd.crack_severity(5.0, 0.1)
        self.assertEqual(s, "moderate")
        print(f"  [PASS] Sev: {s}")
    
    def test_ki(self):
        """Should compute KI."""
        k = self.cd.stress_intensity_factor(100.0, 1.0)
        self.assertGreater(k, 0)
        print(f"  [PASS] KI: {k:.3f}")


class TestLayerMisalignment(unittest.TestCase):
    """Test misalignment."""
    
    def setUp(self):
        self.lm = LayerMisalignment()
    
    def test_vector(self):
        """Should compute vector."""
        v = self.lm.misalignment_vector((0.0, 0.0), (0.1, 0.2))
        self.assertEqual(v, (0.1, 0.2))
        print(f"  [PASS] Vec: {v}")
    
    def test_cumulative(self):
        """Should compute cumulative."""
        c = self.lm.cumulative_misalignment([(0.1, 0.0), (0.0, 0.1)])
        self.assertAlmostEqual(c, 0.141, delta=0.01)
        print(f"  [PASS] Cum: {c:.3f}")


class TestGeometricDeviation(unittest.TestCase):
    """Test geometric."""
    
    def setUp(self):
        self.gd = GeometricDeviation()
    
    def test_deviation(self):
        """Should compute deviation."""
        d = self.gd.dimensional_deviation(10.1, 10.0)
        self.assertAlmostEqual(d, 0.1, delta=1e-10)
        print(f"  [PASS] Dev: {d:.2f}")
    
    def test_roughness(self):
        """Should compute roughness dev."""
        r = self.gd.surface_roughness_deviation(8.0, 5.0)
        self.assertEqual(r, 3.0)
        print(f"  [PASS] Ra: {r:.1f}")
    
    def test_tolerance(self):
        """Should check tolerance."""
        t = self.gd.is_within_tolerance(0.05)
        self.assertTrue(t)
        print("  [PASS] Tol")


class TestAdditiveDefects(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ad = AdditiveDefects()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ad.defects_summary()
        self.assertIn("defect_types", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
