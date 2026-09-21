"""
Unit tests for fatigue analysis module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fatigue_analysis import (StressCycle, SNCurve,
                              MinersRule,
                              ParisLaw,
                              RainflowCounting,
                              FatigueAnalysis)


class TestSNCurve(unittest.TestCase):
    """Test S-N."""
    
    def setUp(self):
        self.sn = SNCurve()
    
    def test_cycles(self):
        """Should compute cycles."""
        n = self.sn.cycles_to_failure(500.0)
        self.assertGreater(n, 0)
        print(f"  [PASS] N: {n:.2e}")
    
    def test_limit(self):
        """Should compute limit."""
        l = self.sn.fatigue_limit()
        self.assertGreater(l, 0)
        print(f"  [PASS] Lim: {l:.2f}")
    
    def test_strength(self):
        """Should compute strength."""
        s = self.sn.fatigue_strength(1e5)
        self.assertGreater(s, 0)
        print(f"  [PASS] S: {s:.2f}")


class TestMinersRule(unittest.TestCase):
    """Test Miner."""
    
    def setUp(self):
        self.miner = MinersRule()
        self.sn = SNCurve()
    
    def test_damage(self):
        """Should compute damage."""
        d = self.miner.damage_per_cycle(500.0, self.sn)
        self.assertGreater(d, 0)
        print(f"  [PASS] D: {d:.2e}")
    
    def test_cumulative(self):
        """Should compute cumulative."""
        c = [StressCycle(0, 500, 1000), StressCycle(0, 300, 10000)]
        d = self.miner.cumulative_damage(c, self.sn)
        self.assertGreaterEqual(d, 0)
        print(f"  [PASS] CD: {d:.4f}")
    
    def test_remaining(self):
        """Should compute remaining."""
        r = self.miner.remaining_life(0.5)
        self.assertEqual(r, 0.5)
        print(f"  [PASS] R: {r:.2f}")


class TestParisLaw(unittest.TestCase):
    """Test Paris."""
    
    def setUp(self):
        self.pl = ParisLaw()
    
    def test_rate(self):
        """Should compute rate."""
        r = self.pl.crack_growth_rate(20.0)
        self.assertGreater(r, 0)
        print(f"  [PASS] da/dN: {r:.2e}")
    
    def test_cycles(self):
        """Should compute cycles."""
        n = self.pl.cycles_to_critical(1e-3, 1e-2, 20.0)
        self.assertGreater(n, 0)
        print(f"  [PASS] Nf: {n:.2e}")


class TestRainflowCounting(unittest.TestCase):
    """Test rainflow."""
    
    def setUp(self):
        self.rf = RainflowCounting()
    
    def test_extract(self):
        """Should extract cycles."""
        h = [100.0, -50.0, 80.0, -40.0]
        c = self.rf.extract_cycles(h)
        self.assertGreater(len(c), 0)
        print(f"  [PASS] Cycles: {len(c)}")
    
    def test_histogram(self):
        """Should build histogram."""
        c = [StressCycle(0, 100, 1), StressCycle(0, 200, 2)]
        b = self.rf.stress_range_histogram(c, 5)
        self.assertGreater(sum(b), 0)
        print(f"  [PASS] Bins: {b}")


class TestFatigueAnalysis(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.fa = FatigueAnalysis()
    
    def test_summary(self):
        """Should summarize."""
        s = self.fa.fatigue_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
