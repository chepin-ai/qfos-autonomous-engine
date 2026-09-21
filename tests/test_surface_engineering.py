"""
Unit tests for surface engineering module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from surface_engineering import (SurfaceProperties, SurfaceHardening,
                                 CoatingDeposition,
                                 SurfaceTexturing,
                                 Tribology,
                                 SurfaceEngineering)


class TestSurfaceHardening(unittest.TestCase):
    """Test hardening."""
    
    def setUp(self):
        self.sh = SurfaceHardening()
    
    def test_case_depth(self):
        """Should compute case depth."""
        d = self.sh.case_depth(10.0, 1200.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Depth: {d:.3f} mm")
    
    def test_hardness_profile(self):
        """Should compute hardness."""
        h = self.sh.hardness_profile(800.0, 200.0, 1.0, 0.5)
        self.assertEqual(h, 500.0)
        print(f"  [PASS] HV: {h:.0f}")


class TestCoatingDeposition(unittest.TestCase):
    """Test coating."""
    
    def setUp(self):
        self.cd = CoatingDeposition()
    
    def test_rate(self):
        """Should compute rate."""
        r = self.cd.deposition_rate(5.0, 60.0)
        self.assertAlmostEqual(r, 0.0833, delta=0.01)
        print(f"  [PASS] Rate: {r:.4f}")
    
    def test_adhesion(self):
        """Should compute adhesion."""
        a = self.cd.adhesion_strength(50.0)
        self.assertGreater(a, 0)
        print(f"  [PASS] Adh: {a:.1f}")


class TestSurfaceTexturing(unittest.TestCase):
    """Test texturing."""
    
    def setUp(self):
        self.st = SurfaceTexturing()
    
    def test_density(self):
        """Should compute density."""
        d = self.st.dimple_density(100, 10.0)
        self.assertEqual(d, 10.0)
        print(f"  [PASS] Den: {d:.1f}")
    
    def test_aspect(self):
        """Should compute aspect ratio."""
        a = self.st.aspect_ratio(10.0, 50.0)
        self.assertEqual(a, 0.2)
        print(f"  [PASS] AR: {a:.2f}")


class TestTribology(unittest.TestCase):
    """Test tribology."""
    
    def setUp(self):
        self.tr = Tribology()
    
    def test_friction(self):
        """Should compute mu."""
        m = self.tr.friction_coefficient(10.0, 50.0)
        self.assertEqual(m, 0.2)
        print(f"  [PASS] Mu: {m:.2f}")
    
    def test_wear(self):
        """Should compute wear rate."""
        w = self.tr.wear_rate(1.0, 100.0, 10.0)
        self.assertEqual(w, 0.001)
        print(f"  [PASS] Wear: {w:.4f}")
    
    def test_stribeck(self):
        """Should identify regime."""
        r = self.tr.stribeck_curve(0.5)
        self.assertEqual(r, "mixed")
        print(f"  [PASS] Reg: {r}")


class TestSurfaceEngineering(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.se = SurfaceEngineering()
    
    def test_summary(self):
        """Should summarize."""
        s = self.se.surface_summary()
        self.assertIn("processes", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
