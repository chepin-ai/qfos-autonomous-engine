"""
Unit tests for fatigue testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fatigue_testing import (CycleCount, SNCurve,
                             MinersRule,
                             RainflowCounter,
                             MeanStressCorrection,
                             FatigueTesting)


class TestSNCurve(unittest.TestCase):
    """Test S-N."""
    
    def setUp(self):
        self.sn = SNCurve(1000.0, -0.1, 1.0, -0.6)
    
    def test_cycles(self):
        """Should compute cycles."""
        N = self.sn.cycles_to_failure(500.0)
        self.assertGreater(N, 0)
        print(f"  [PASS] N: {N:.0f}")
    
    def test_endurance(self):
        """Should compute endurance."""
        e = self.sn.endurance_limit(1e6)
        self.assertGreater(e, 0)
        print(f"  [PASS] Se: {e:.2f} MPa")
    
    def test_strain_life(self):
        """Should compute strain life."""
        N = self.sn.strain_life(0.002, 200.0)
        self.assertGreater(N, 0)
        print(f"  [PASS] N: {N:.0f}")


class TestMinersRule(unittest.TestCase):
    """Test Miner."""
    
    def setUp(self):
        self.miner = MinersRule()
        self.sn = SNCurve(1000.0, -0.1, 1.0, -0.6)
    
    def test_damage(self):
        """Should compute damage."""
        d = self.miner.damage_ratio(1000.0, 10000.0)
        self.assertEqual(d, 0.1)
        print(f"  [PASS] D: {d:.2f}")
    
    def test_total(self):
        """Should compute total."""
        cycles = [CycleCount(100.0, 0.0, 1000.0), CycleCount(200.0, 0.0, 500.0)]
        d = self.miner.total_damage(cycles, self.sn)
        self.assertGreater(d, 0)
        print(f"  [PASS] Dt: {d:.4f}")
    
    def test_remaining(self):
        """Should compute remaining."""
        r = self.miner.remaining_life(0.7)
        self.assertAlmostEqual(r, 0.3, delta=0.01)
        print(f"  [PASS] Rem: {r:.2f}")


class TestRainflowCounter(unittest.TestCase):
    """Test rainflow."""
    
    def setUp(self):
        self.rf = RainflowCounter()
    
    def test_extract(self):
        """Should extract cycles."""
        hist = [0.0, 50.0, -30.0, 40.0, -20.0, 0.0]
        c = self.rf.extract_cycles(hist)
        self.assertGreater(len(c), 0)
        print(f"  [PASS] Cycles: {len(c)}")
    
    def test_range(self):
        """Should count ranges."""
        hist = [0.0, 50.0, -30.0, 40.0, -20.0]
        r = self.rf.range_count(hist, 10.0)
        self.assertGreater(len(r), 0)
        print(f"  [PASS] Ranges: {r}")


class TestMeanStressCorrection(unittest.TestCase):
    """Test correction."""
    
    def setUp(self):
        self.ms = MeanStressCorrection()
    
    def test_goodman(self):
        """Should apply Goodman."""
        s = self.ms.goodman(100.0, 50.0, 500.0)
        self.assertGreater(s, 100.0)
        print(f"  [PASS] G: {s:.2f}")
    
    def test_gerber(self):
        """Should apply Gerber."""
        s = self.ms.gerber(100.0, 50.0, 500.0)
        self.assertGreater(s, 100.0)
        print(f"  [PASS] Ge: {s:.2f}")
    
    def test_soderberg(self):
        """Should apply Soderberg."""
        s = self.ms.soderberg(100.0, 50.0, 300.0)
        self.assertGreater(s, 100.0)
        print(f"  [PASS] So: {s:.2f}")


class TestFatigueTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ft = FatigueTesting()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ft.fatigue_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
