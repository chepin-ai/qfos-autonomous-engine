"""
Unit tests for tribology modeling module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tribology_modeling import (SurfacePair, FrictionModels,
                                WearMechanisms,
                                LubricationRegimes,
                                ContactMechanics,
                                TribologyModeling)


class TestFrictionModels(unittest.TestCase):
    """Test friction."""
    
    def setUp(self):
        self.fm = FrictionModels()
    
    def test_coulomb(self):
        """Should compute Coulomb friction."""
        f = self.fm.coulomb_friction(100.0, 0.3)
        self.assertEqual(f, 30.0)
        print(f"  [PASS] F: {f:.1f}")
    
    def test_stribeck(self):
        """Should compute Stribeck."""
        mu = self.fm.stribeck_curve(0.5)
        self.assertLess(mu, 0.5)
        print(f"  [PASS] Mu: {mu:.4f}")


class TestWearMechanisms(unittest.TestCase):
    """Test wear."""
    
    def setUp(self):
        self.wm = WearMechanisms()
    
    def test_archard(self):
        """Should compute Archard wear."""
        v = self.wm.archard_wear(100.0, 1000.0)
        self.assertGreater(v, 0)
        print(f"  [PASS] V: {v:.2e}")
    
    def test_rate(self):
        """Should compute wear rate."""
        r = self.wm.wear_rate(1e-9, 1000.0)
        self.assertEqual(r, 1e-12)
        print(f"  [PASS] Rate: {r:.2e}")


class TestLubricationRegimes(unittest.TestCase):
    """Test lubrication."""
    
    def setUp(self):
        self.lr = LubricationRegimes()
    
    def test_lambda(self):
        """Should compute lambda."""
        l = self.lr.film_thickness_ratio(2.0, 1.0)
        self.assertEqual(l, 2.0)
        print(f"  [PASS] L: {l:.1f}")
    
    def test_regime(self):
        """Should identify regime."""
        r = self.lr.regime(2.0)
        self.assertEqual(r, "mixed")
        print(f"  [PASS] Reg: {r}")
    
    def test_film(self):
        """Should compute film."""
        h = self.lr.minimum_film_thickness(0.1, 1.0, 1000.0)
        self.assertGreater(h, 0)
        print(f"  [PASS] H: {h:.2e}")


class TestContactMechanics(unittest.TestCase):
    """Test contact."""
    
    def setUp(self):
        self.cm = ContactMechanics()
    
    def test_area(self):
        """Should compute area."""
        a = self.cm.hertz_contact_area(1000.0)
        self.assertGreater(a, 0)
        print(f"  [PASS] A: {a:.2e}")
    
    def test_pressure(self):
        """Should compute pressure."""
        p = self.cm.max_contact_pressure(1000.0, 1e-4)
        self.assertGreater(p, 0)
        print(f"  [PASS] P: {p:.2e}")


class TestTribologyModeling(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.tm = TribologyModeling()
    
    def test_summary(self):
        """Should summarize."""
        s = self.tm.tribology_summary()
        self.assertIn("models", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
