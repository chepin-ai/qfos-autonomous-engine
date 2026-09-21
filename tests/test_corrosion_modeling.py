"""
Unit tests for corrosion modeling module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from corrosion_modeling import (CorrosionEnvironment, PittingCorrosion,
                                GalvanicCorrosion,
                                PassivationKinetics,
                                CorrosionRatePrediction,
                                CorrosionModeling)


class TestPittingCorrosion(unittest.TestCase):
    """Test pitting."""
    
    def setUp(self):
        self.pc = PittingCorrosion()
    
    def test_growth_rate(self):
        """Should compute rate."""
        r = self.pc.pit_growth_rate(100.0)
        self.assertGreater(r, 0)
        print(f"  [PASS] R: {r:.2e}")
    
    def test_depth(self):
        """Should compute depth."""
        d = self.pc.pit_depth(1e-9, 1000.0)
        self.assertAlmostEqual(d, 1e-6, delta=1e-15)
        print(f"  [PASS] D: {d:.2e}")
    
    def test_cpt(self):
        """Should compute CPT."""
        c = self.pc.critical_pitting_temperature(1800.0, 300.0)
        self.assertGreater(c, 0)
        print(f"  [PASS] CPT: {c:.1f}")


class TestGalvanicCorrosion(unittest.TestCase):
    """Test galvanic."""
    
    def setUp(self):
        self.gc = GalvanicCorrosion()
    
    def test_current(self):
        """Should compute current."""
        c = self.gc.galvanic_current(0.5, 10.0)
        self.assertEqual(c, 0.05)
        print(f"  [PASS] I: {c:.3f}")
    
    def test_rate(self):
        """Should compute rate."""
        r = self.gc.corrosion_rate_from_current(0.1)
        self.assertGreater(r, 0)
        print(f"  [PASS] CR: {r:.2e}")


class TestPassivationKinetics(unittest.TestCase):
    """Test passivation."""
    
    def setUp(self):
        self.pk = PassivationKinetics()
    
    def test_thickness(self):
        """Should compute thickness."""
        t = self.pk.oxide_thickness(100.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] Tox: {t:.2e}")
    
    def test_current(self):
        """Should compute current."""
        c = self.pk.passivation_current(0.6)
        self.assertGreater(c, 0)
        print(f"  [PASS] Ipass: {c:.2e}")


class TestCorrosionRatePrediction(unittest.TestCase):
    """Test prediction."""
    
    def setUp(self):
        self.crp = CorrosionRatePrediction()
    
    def test_tafel(self):
        """Should compute rate."""
        r = self.crp.tafel_rate(1.0)
        self.assertGreater(r, 0)
        print(f"  [PASS] R: {r:.2e}")
    
    def test_lifetime(self):
        """Should predict lifetime."""
        l = self.crp.lifetime_prediction(10.0, 1.0)
        self.assertEqual(l, 10.0)
        print(f"  [PASS] LT: {l:.1f}")


class TestCorrosionModeling(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.cm = CorrosionModeling()
    
    def test_summary(self):
        """Should summarize."""
        s = self.cm.corrosion_summary()
        self.assertIn("models", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
