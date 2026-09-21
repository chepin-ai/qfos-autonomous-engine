"""
Unit tests for microstructure characterization module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from microstructure_characterization import (GrainData, GrainSizeAnalysis,
                                             PhaseFraction,
                                             TextureAnalysis,
                                             Stereology,
                                             MicrostructureCharacterization)


class TestGrainSizeAnalysis(unittest.TestCase):
    """Test grain size."""
    
    def setUp(self):
        self.gsa = GrainSizeAnalysis()
    
    def test_diameter(self):
        """Should compute diameter."""
        d = self.gsa.equivalent_diameter(100.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] D: {d:.2f}")
    
    def test_aspect(self):
        """Should compute aspect ratio."""
        a = self.gsa.aspect_ratio(10.0, 5.0)
        self.assertEqual(a, 2.0)
        print(f"  [PASS] AR: {a:.1f}")
    
    def test_astm(self):
        """Should compute ASTM."""
        g = self.gsa.astm_grain_size(100.0)
        self.assertGreater(g, 0)
        print(f"  [PASS] G: {g:.1f}")
    
    def test_mean(self):
        """Should compute mean."""
        grains = [GrainData(100.0, 30.0, 10.0, 5.0), GrainData(200.0, 40.0, 15.0, 8.0)]
        m = self.gsa.mean_grain_size(grains)
        self.assertGreater(m, 0)
        print(f"  [PASS] Mean: {m:.2f}")


class TestPhaseFraction(unittest.TestCase):
    """Test phase."""
    
    def setUp(self):
        self.pf = PhaseFraction()
    
    def test_area(self):
        """Should compute area fraction."""
        f = self.pf.area_fraction(20.0, 100.0)
        self.assertEqual(f, 0.2)
        print(f"  [PASS] Af: {f:.2f}")
    
    def test_volume(self):
        """Should convert to volume."""
        f = self.pf.volume_fraction_from_area(0.3)
        self.assertEqual(f, 0.3)
        print(f"  [PASS] Vf: {f:.2f}")
    
    def test_line(self):
        """Should compute line fraction."""
        f = self.pf.line_fraction(5.0, 20.0)
        self.assertEqual(f, 0.25)
        print(f"  [PASS] Lf: {f:.2f}")


class TestTextureAnalysis(unittest.TestCase):
    """Test texture."""
    
    def setUp(self):
        self.ta = TextureAnalysis()
    
    def test_density(self):
        """Should compute density."""
        d = self.ta.orientation_density(10, 100)
        self.assertEqual(d, 10.0)
        print(f"  [PASS] OD: {d:.1f}")
    
    def test_index(self):
        """Should compute texture index."""
        t = self.ta.texture_index([0.5, 0.5, 0.5])
        self.assertEqual(t, 0.25)
        print(f"  [PASS] TI: {t:.2f}")


class TestStereology(unittest.TestCase):
    """Test stereology."""
    
    def setUp(self):
        self.st = Stereology()
    
    def test_intercept(self):
        """Should compute intercept."""
        l = self.st.mean_intercept_length(10.0, 20)
        self.assertEqual(l, 0.5)
        print(f"  [PASS] L: {l:.2f}")
    
    def test_size(self):
        """Should estimate grain size."""
        s = self.st.grain_size_from_intercept(10.0)
        self.assertEqual(s, 10.0)
        print(f"  [PASS] GS: {s:.1f}")


class TestMicrostructureCharacterization(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.mc = MicrostructureCharacterization()
    
    def test_summary(self):
        """Should summarize."""
        s = self.mc.microstructure_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
