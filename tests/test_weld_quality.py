"""
Unit tests for weld quality module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from weld_quality import (WeldDefectType, WeldMeasurement,
                          BeadGeometryAnalyzer, PorosityDetector,
                          CrackDetector, WeldQuality)


class TestBeadGeometry(unittest.TestCase):
    """Test bead geometry analyzer."""
    
    def setUp(self):
        self.bg = BeadGeometryAnalyzer()
    
    def test_aspect_ratio(self):
        """Should compute aspect ratio."""
        ar = self.bg.aspect_ratio(5.0, 2.0)
        self.assertAlmostEqual(ar, 2.5)
        print(f"  [PASS] AR: {ar}")
    
    def test_width_deviation(self):
        """Should compute width deviation."""
        d = self.bg.width_deviation(5.5)
        self.assertAlmostEqual(d, 10.0)
        print(f"  [PASS] Dev: {d:.1f}%")
    
    def test_reinforcement(self):
        """Should compute reinforcement."""
        rf = self.bg.reinforcement_factor(2.0, 5.0)
        self.assertAlmostEqual(rf, 0.4)
        print(f"  [PASS] RF: {rf}")
    
    def test_dilution(self):
        """Should compute dilution."""
        d = self.bg.dilution(10.0, 3.0)
        self.assertAlmostEqual(d, 30.0)
        print(f"  [PASS] Dilution: {d:.1f}%")


class TestPorosityDetector(unittest.TestCase):
    """Test porosity detector."""
    
    def setUp(self):
        self.pd = PorosityDetector()
    
    def test_density(self):
        """Should compute pore density."""
        d = self.pd.pore_density(10, 2.0)
        self.assertAlmostEqual(d, 5.0)
        print(f"  [PASS] Density: {d}")
    
    def test_acceptable(self):
        """Should assess acceptable."""
        a = self.pd.assess(2, 1.0)
        self.assertEqual(a, "acceptable")
        print("  [PASS] Acceptable")
    
    def test_reject(self):
        """Should assess reject."""
        a = self.pd.assess(20, 1.0, 2.0)
        self.assertEqual(a, "reject")
        print("  [PASS] Reject")


class TestCrackDetector(unittest.TestCase):
    """Test crack detector."""
    
    def setUp(self):
        self.cd = CrackDetector()
    
    def test_none(self):
        """Should assess no crack."""
        a = self.cd.assess(0.0)
        self.assertEqual(a, "none")
        print("  [PASS] None")
    
    def test_critical(self):
        """Should assess critical."""
        a = self.cd.assess(5.0)
        self.assertEqual(a, "critical")
        print("  [PASS] Critical")
    
    def test_total_length(self):
        """Should sum crack lengths."""
        total = self.cd.total_crack_length([1.0, 2.0, 0.5])
        self.assertAlmostEqual(total, 3.5)
        print(f"  [PASS] Total: {total}")


class TestWeldQuality(unittest.TestCase):
    """Test unified weld quality."""
    
    def setUp(self):
        self.wq = WeldQuality()
    
    def test_add(self):
        """Should add measurement."""
        self.wq.add_measurement(WeldMeasurement((0.0, 0.0), 5.0, 2.0, 3.0))
        self.assertEqual(len(self.wq.measurements), 1)
        print("  [PASS] Add")
    
    def test_report(self):
        """Should generate report."""
        self.wq.add_measurement(WeldMeasurement((0.0, 0.0), 5.0, 2.0, 3.0, 0, 0.0))
        r = self.wq.quality_report()
        self.assertIn("grade", r)
        print(f"  [PASS] Grade: {r['grade']}")
    
    def test_pass(self):
        """Should pass good weld."""
        self.wq.add_measurement(WeldMeasurement((0.0, 0.0), 5.0, 2.0, 3.0, 0, 0.0))
        self.assertTrue(self.wq.pass_fail())
        print("  [PASS] Pass")
    
    def test_fail(self):
        """Should fail bad weld."""
        self.wq.add_measurement(WeldMeasurement((0.0, 0.0), 5.0, 2.0, 3.0, 0, 10.0))
        self.assertFalse(self.wq.pass_fail())
        print("  [PASS] Fail")


if __name__ == '__main__':
    unittest.main(verbosity=2)
