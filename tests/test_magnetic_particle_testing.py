"""
Unit tests for magnetic particle testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from magnetic_particle_testing import (Indication, Magnetizer,
                                       ParticleApplicator,
                                       IndicationDetector,
                                       DefectCharacterizer,
                                       MagneticParticleTesting)


class TestMagnetizer(unittest.TestCase):
    """Test magnetizer."""
    
    def setUp(self):
        self.mag = Magnetizer(2000.0)
    
    def test_longitudinal(self):
        """Should compute longitudinal."""
        i = self.mag.longitudinal_magnetization(100.0, 100.0)
        self.assertGreater(i, 0)
        print(f"  [PASS] Long: {i:.4f}")
    
    def test_circular(self):
        """Should compute circular."""
        i = self.mag.circular_magnetization(50.0, 100.0)
        self.assertGreater(i, 0)
        print(f"  [PASS] Circ: {i:.4f}")


class TestParticleApplicator(unittest.TestCase):
    """Test applicator."""
    
    def setUp(self):
        self.pa = ParticleApplicator(5.0)
    
    def test_concentration(self):
        """Should compute concentration."""
        c = self.pa.concentration(10.0, 1.0)
        self.assertEqual(c, 10.0)
        print(f"  [PASS] Conc: {c}")


class TestIndicationDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.det = IndicationDetector(1.0, 0.1)
    
    def test_detect(self):
        """Should detect indications."""
        img = [[0.0, 0.0, 0.0], [0.0, 0.5, 0.0], [0.0, 0.0, 0.0]]
        inds = self.det.detect(img, 1.0)
        self.assertEqual(len(inds), 1)
        print(f"  [PASS] Det: {len(inds)}")
    
    def test_classify(self):
        """Should classify."""
        ind = Indication(0.0, 0.0, 5.0, 1.0, 0.5, 0.0)
        c = self.det.classify(ind)
        self.assertEqual(c, "significant")
        print(f"  [PASS] Cls: {c}")


class TestDefectCharacterizer(unittest.TestCase):
    """Test characterizer."""
    
    def setUp(self):
        self.dc = DefectCharacterizer()
    
    def test_depth(self):
        """Should estimate depth."""
        d = self.dc.depth_estimate(10.0, 20.0)
        self.assertEqual(d, 2.0)
        print(f"  [PASS] Depth: {d}")
    
    def test_orientation(self):
        """Should analyze orientation."""
        inds = [Indication(0.0, 0.0, 1.0, 1.0, 0.5, 0.0),
                Indication(1.0, 0.0, 1.0, 1.0, 0.5, 90.0)]
        o = self.dc.orientation_analysis(inds)
        self.assertIn("dominant", o)
        print(f"  [PASS] Ori: {o}")


class TestMagneticParticleTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.mpt = MagneticParticleTesting()
    
    def test_inspect(self):
        """Should inspect."""
        img = [[0.0, 0.0, 0.0], [0.0, 0.5, 0.0], [0.0, 0.0, 0.0]]
        r = self.mpt.inspect_surface(img, 1.0)
        self.assertIn("indications", r)
        print(f"  [PASS] Insp: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.mpt.mpt_summary()
        self.assertIn("indications", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
