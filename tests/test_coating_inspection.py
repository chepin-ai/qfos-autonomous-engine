"""
Unit tests for coating inspection module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from coating_inspection import (CoatingDefectType, CoatingMeasurement,
                                ThicknessGauge, AdhesionTester,
                                DefectDetector, GlossMeter,
                                CoatingInspection)


class TestThicknessGauge(unittest.TestCase):
    """Test thickness gauge."""
    
    def setUp(self):
        self.tg = ThicknessGauge(nominal_thickness_um=100.0)
    
    def test_in_spec(self):
        """Should accept in-spec thickness."""
        self.assertTrue(self.tg.is_in_spec(105.0))
        print("  [PASS] In spec")
    
    def test_out_of_spec(self):
        """Should reject out-of-spec."""
        self.assertFalse(self.tg.is_in_spec(50.0))
        print("  [PASS] Out of spec")
    
    def test_deviation(self):
        """Should compute deviation."""
        d = self.tg.deviation(110.0)
        self.assertAlmostEqual(d, 10.0)
        print(f"  [PASS] Dev: {d:.1f}%")
    
    def test_uniformity(self):
        """Should compute uniformity."""
        cv = self.tg.uniformity([100.0, 102.0, 98.0, 101.0])
        self.assertGreater(cv, 0)
        print(f"  [PASS] CV: {cv:.2f}%")
    
    def test_coverage(self):
        """Should compute coverage."""
        cov = self.tg.coverage_estimate([100.0, 50.0, 105.0], 1.0)
        self.assertAlmostEqual(cov, 2.0 / 3.0)
        print(f"  [PASS] Coverage: {cov:.2f}")


class TestAdhesionTester(unittest.TestCase):
    """Test adhesion tester."""
    
    def setUp(self):
        self.at = AdhesionTester(min_adhesion_MPa=5.0)
    
    def test_excellent(self):
        """Should classify excellent."""
        grade = self.at.assess(10.0)
        self.assertEqual(grade, "excellent")
        print("  [PASS] Excellent")
    
    def test_poor(self):
        """Should classify poor."""
        grade = self.at.assess(1.0)
        self.assertEqual(grade, "poor")
        print("  [PASS] Poor")
    
    def test_pull_off(self):
        """Should compute pull-off."""
        strength = self.at.pull_off_strength(100.0, 20.0)
        self.assertGreater(strength, 0)
        print(f"  [PASS] Pull-off: {strength:.2f} MPa")


class TestDefectDetector(unittest.TestCase):
    """Test defect detector."""
    
    def setUp(self):
        self.dd = DefectDetector()
    
    def test_no_defect(self):
        """Should not detect good coating."""
        m = CoatingMeasurement((0.0, 0.0), 100.0, 80.0, 10.0)
        d, t = self.dd.detect(m)
        self.assertFalse(d)
        print("  [PASS] No defect")
    
    def test_detect_pinhole(self):
        """Should detect pinhole."""
        m = CoatingMeasurement((0.0, 0.0), 5.0, 10.0, 10.0)
        d, t = self.dd.detect(m)
        self.assertTrue(d)
        self.assertEqual(t, CoatingDefectType.PINHOLE)
        print("  [PASS] Pinhole")
    
    def test_defect_density(self):
        """Should compute density."""
        defects = [
            CoatingMeasurement((0.0, 0.0), 5.0, 10.0, 10.0),
            CoatingMeasurement((1.0, 0.0), 5.0, 10.0, 10.0),
        ]
        d = self.dd.defect_density(defects, 10.0)
        self.assertAlmostEqual(d, 0.2)
        print(f"  [PASS] Density: {d}")


class TestGlossMeter(unittest.TestCase):
    """Test gloss meter."""
    
    def setUp(self):
        self.gm = GlossMeter()
    
    def test_high_gloss(self):
        """Should classify high gloss."""
        g = self.gm.classify_gloss(85.0)
        self.assertEqual(g, "high_gloss")
        print("  [PASS] High gloss")
    
    def test_matte(self):
        """Should classify matte."""
        g = self.gm.classify_gloss(5.0)
        self.assertEqual(g, "matte")
        print("  [PASS] Matte")
    
    def test_haze(self):
        """Should compute haze."""
        h = self.gm.haze_index(50.0, 80.0)
        self.assertGreater(h, 0)
        print(f"  [PASS] Haze: {h:.1f}")


class TestCoatingInspection(unittest.TestCase):
    """Test unified coating inspection."""
    
    def setUp(self):
        self.ci = CoatingInspection()
    
    def test_measure(self):
        """Should add measurement."""
        self.ci.measure(CoatingMeasurement((0.0, 0.0), 100.0, 80.0, 10.0))
        self.assertEqual(len(self.ci.measurements), 1)
        print("  [PASS] Measure")
    
    def test_report(self):
        """Should generate report."""
        self.ci.measure(CoatingMeasurement((0.0, 0.0), 100.0, 80.0, 10.0))
        self.ci.measure(CoatingMeasurement((1.0, 0.0), 102.0, 82.0, 11.0))
        r = self.ci.inspection_report()
        self.assertIn("avg_thickness_um", r)
        print(f"  [PASS] Report: avg={r['avg_thickness_um']:.1f}")
    
    def test_grade(self):
        """Should compute grade."""
        for i in range(10):
            self.ci.measure(CoatingMeasurement((float(i), 0.0), 100.0, 80.0, 10.0))
        g = self.ci.quality_grade()
        self.assertIn(g, ["A", "B", "C", "F"])
        print(f"  [PASS] Grade: {g}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
