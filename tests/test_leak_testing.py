"""
Unit tests for leak testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from leak_testing import (LeakReading, PressureDecayAnalyzer,
                          HeliumMassSpectrometry,
                          BubbleLeakTester,
                          LeakQuantifier,
                          LeakTesting)


class TestPressureDecayAnalyzer(unittest.TestCase):
    """Test decay."""
    
    def setUp(self):
        self.pda = PressureDecayAnalyzer(0.001)
    
    def test_leak_rate(self):
        """Should compute leak rate."""
        r = self.pda.leak_rate(1000.0, 10.0)
        self.assertEqual(r, 0.1)
        print(f"  [PASS] Rate: {r}")
    
    def test_pressure(self):
        """Should compute pressure."""
        p = self.pda.pressure_at_time(100000.0, 0.1, 10.0)
        self.assertEqual(p, 99000.0)
        print(f"  [PASS] Pres: {p}")


class TestHeliumMassSpectrometry(unittest.TestCase):
    """Test helium."""
    
    def setUp(self):
        self.hms = HeliumMassSpectrometry(1e-10)
    
    def test_detect(self):
        """Should detect."""
        d = self.hms.detect(1e-8)
        self.assertTrue(d)
        print(f"  [PASS] Det: {d}")
    
    def test_rate(self):
        """Should compute rate."""
        r = self.hms.leak_rate(1e-8, 1.0)
        self.assertEqual(r, 1e-8)
        print(f"  [PASS] Rate: {r}")


class TestBubbleLeakTester(unittest.TestCase):
    """Test bubble."""
    
    def setUp(self):
        self.blt = BubbleLeakTester(1.0)
    
    def test_rate(self):
        """Should compute rate from bubbles."""
        r = self.blt.leak_rate_from_bubbles(60.0, 10.0)
        self.assertGreater(r, 0)
        print(f"  [PASS] Rate: {r:.6f}")
    
    def test_detect(self):
        """Should detect."""
        d = self.blt.detect([{"size": 2.0}])
        self.assertTrue(d)
        print("  [PASS] Det")


class TestLeakQuantifier(unittest.TestCase):
    """Test quantifier."""
    
    def setUp(self):
        self.lq = LeakQuantifier()
    
    def test_classify(self):
        """Should classify."""
        c = self.lq.classify(1e-7)
        self.assertEqual(c, "minor")
        print(f"  [PASS] Cls: {c}")
    
    def test_total(self):
        """Should compute total."""
        readings = [LeakReading(0.0, 100000.0, 1e-6, 20.0),
                    LeakReading(10.0, 99900.0, 1e-6, 20.0)]
        t = self.lq.total_leak(readings)
        self.assertEqual(t, 1e-6)
        print(f"  [PASS] Tot: {t}")


class TestLeakTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.lt = LeakTesting(0.001)
    
    def test_add(self):
        """Should add reading."""
        self.lt.add_reading(LeakReading(0.0, 100000.0, 1e-6, 20.0))
        self.assertEqual(len(self.lt.readings), 1)
        print("  [PASS] Add")
    
    def test_inspect(self):
        """Should inspect."""
        self.lt.add_reading(LeakReading(0.0, 100000.0, 1e-6, 20.0))
        r = self.lt.inspect()
        self.assertIn("classification", r)
        print(f"  [PASS] Insp: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.lt.lt_summary()
        self.assertIn("readings", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
