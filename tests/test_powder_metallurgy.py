"""
Unit tests for powder metallurgy module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from powder_metallurgy import (PowderProperties, PowderCharacterization,
                               PowderCompaction,
                               SinteringKinetics,
                               PorosityAnalysis,
                               PowderMetallurgy)


class TestPowderCharacterization(unittest.TestCase):
    """Test characterization."""
    
    def setUp(self):
        self.pc = PowderCharacterization()
        self.powder = PowderProperties(10.0, 50.0, 100.0, 2.5, 3.0)
    
    def test_span(self):
        """Should compute span."""
        s = self.pc.span(self.powder)
        self.assertEqual(s, 1.8)
        print(f"  [PASS] Span: {s:.2f}")
    
    def test_hausner(self):
        """Should compute Hausner."""
        h = self.pc.hausner_ratio(self.powder)
        self.assertEqual(h, 1.2)
        print(f"  [PASS] H: {h:.2f}")
    
    def test_carr(self):
        """Should compute Carr."""
        c = self.pc.carr_index(self.powder)
        self.assertAlmostEqual(c, 16.67, delta=0.1)
        print(f"  [PASS] Carr: {c:.1f}%")


class TestPowderCompaction(unittest.TestCase):
    """Test compaction."""
    
    def setUp(self):
        self.pcomp = PowderCompaction()
    
    def test_green(self):
        """Should compute green density."""
        d = self.pcomp.green_density(10.0, 5.0)
        self.assertEqual(d, 2.0)
        print(f"  [PASS] Dgreen: {d:.1f}")
    
    def test_pressure(self):
        """Should estimate pressure."""
        p = self.pcomp.compaction_pressure(200.0, 0.8)
        self.assertGreater(p, 0)
        print(f"  [PASS] P: {p:.1f} MPa")
    
    def test_relative(self):
        """Should compute relative density."""
        r = self.pcomp.relative_density(6.0, 8.0)
        self.assertEqual(r, 0.75)
        print(f"  [PASS] RD: {r:.2f}")


class TestSinteringKinetics(unittest.TestCase):
    """Test sintering."""
    
    def setUp(self):
        self.sk = SinteringKinetics()
    
    def test_arrhenius(self):
        """Should compute rate."""
        k = self.sk.arrhenius_rate(1500.0, 200000.0)
        self.assertGreater(k, 0)
        print(f"  [PASS] k: {k:.4f}")
    
    def test_densification(self):
        """Should compute density."""
        d = self.sk.densification(0.7, 3600.0, 1e-4)
        self.assertGreater(d, 0.7)
        print(f"  [PASS] D: {d:.3f}")
    
    def test_grain(self):
        """Should compute grain size."""
        g = self.sk.grain_growth(5.0, 3600.0, 1e-3)
        self.assertGreater(g, 5.0)
        print(f"  [PASS] G: {g:.2f} um")


class TestPorosityAnalysis(unittest.TestCase):
    """Test porosity."""
    
    def setUp(self):
        self.pa = PorosityAnalysis()
    
    def test_porosity(self):
        """Should compute porosity."""
        p = self.pa.porosity(6.0, 8.0)
        self.assertEqual(p, 0.25)
        print(f"  [PASS] Por: {p:.2f}")
    
    def test_open(self):
        """Should compute open porosity."""
        p = self.pa.open_porosity(6.5, 7.0)
        self.assertGreater(p, 0)
        print(f"  [PASS] Open: {p:.3f}")


class TestPowderMetallurgy(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.pm = PowderMetallurgy()
    
    def test_summary(self):
        """Should summarize."""
        s = self.pm.metallurgy_summary()
        self.assertIn("processes", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
