"""
Unit tests for tribology module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tribology import (FrictionMeasurement, FrictionAnalyzer,
                       WearAnalyzer,
                       LubricationRegime,
                       BearingLifePredictor,
                       Tribology)


class TestFrictionAnalyzer(unittest.TestCase):
    """Test friction analyzer."""
    
    def setUp(self):
        self.fa = FrictionAnalyzer()
    
    def test_coefficient(self):
        """Should compute mu."""
        m = FrictionMeasurement(100.0, 30.0, 0.5)
        mu = self.fa.coefficient(m)
        self.assertEqual(mu, 0.3)
        print(f"  [PASS] mu: {mu}")
    
    def test_zero_normal(self):
        """Should handle zero normal force."""
        m = FrictionMeasurement(0.0, 10.0, 0.5)
        mu = self.fa.coefficient(m)
        self.assertEqual(mu, 0.0)
        print("  [PASS] Zero")
    
    def test_average(self):
        """Should average."""
        self.fa.add_measurement(FrictionMeasurement(100.0, 20.0, 0.5))
        self.fa.add_measurement(FrictionMeasurement(100.0, 30.0, 0.5))
        avg = self.fa.average_coefficient()
        self.assertEqual(avg, 0.25)
        print(f"  [PASS] Avg: {avg}")
    
    def test_stribeck(self):
        """Should compute Stribeck number."""
        s = self.fa.stribeck_number(0.1, 1.0, 1000.0)
        self.assertEqual(s, 0.0001)
        print(f"  [PASS] St: {s}")


class TestWearAnalyzer(unittest.TestCase):
    """Test wear analyzer."""
    
    def setUp(self):
        self.wa = WearAnalyzer()
    
    def test_archard(self):
        """Should compute Archard coefficient."""
        k = self.wa.archard_wear_rate(0.1, 100.0, 1000.0)
        self.assertEqual(k, 1e-6)
        print(f"  [PASS] K: {k}")
    
    def test_wear_rate(self):
        """Should compute wear rate."""
        r = self.wa.wear_rate_per_distance(0.5, 1000.0)
        self.assertEqual(r, 0.0005)
        print(f"  [PASS] WR: {r}")
    
    def test_specific(self):
        """Should compute specific wear rate."""
        r = self.wa.specific_wear_rate(0.1, 100.0, 1000.0)
        self.assertEqual(r, 1e-6)
        print(f"  [PASS] SWR: {r}")


class TestLubricationRegime(unittest.TestCase):
    """Test lubrication."""
    
    def setUp(self):
        self.lr = LubricationRegime()
    
    def test_boundary(self):
        """Should detect boundary."""
        r = self.lr.regime(0.5, 1.0)
        self.assertEqual(r, "boundary")
        print(f"  [PASS] Reg: {r}")
    
    def test_hydrodynamic(self):
        """Should detect hydrodynamic."""
        r = self.lr.regime(20.0, 1.0)
        self.assertEqual(r, "hydrodynamic")
        print(f"  [PASS] Reg: {r}")
    
    def test_lambda(self):
        """Should compute lambda."""
        l = self.lr.lambda_ratio(3.0, 1.0, 1.0)
        self.assertAlmostEqual(l, 2.121, places=2)
        print(f"  [PASS] Lambda: {l:.3f}")


class TestBearingLifePredictor(unittest.TestCase):
    """Test bearing."""
    
    def setUp(self):
        self.bp = BearingLifePredictor()
    
    def test_l10(self):
        """Should compute L10."""
        l = self.bp.l10_life(0.0, 10000.0, 5000.0)
        self.assertEqual(l, 8.0)
        print(f"  [PASS] L10: {l}")
    
    def test_adjusted(self):
        """Should adjust."""
        l = self.bp.adjusted_life(8.0, 0.5, 1.0, 1.0)
        self.assertEqual(l, 4.0)
        print(f"  [PASS] Adj: {l}")


class TestTribology(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.trib = Tribology()
    
    def test_friction(self):
        """Should test friction."""
        m = FrictionMeasurement(100.0, 25.0, 0.5)
        r = self.trib.test_friction(m)
        self.assertIn("mu", r)
        print(f"  [PASS] Fric: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.trib.tribo_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
