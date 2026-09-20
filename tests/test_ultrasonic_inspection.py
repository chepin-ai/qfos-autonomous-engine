"""
Unit tests for ultrasonic inspection module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ultrasonic_inspection import (DefectType, AScan,
                                   TimeOfFlight, DefectDetector,
                                   AttenuationAnalyzer, ThicknessGauge,
                                   UltrasonicInspection)


class TestTimeOfFlight(unittest.TestCase):
    """Test time-of-flight."""
    
    def setUp(self):
        self.tof = TimeOfFlight()
    
    def test_thickness(self):
        """Should compute thickness."""
        t = self.tof.thickness(10.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] Thick: {t:.4f}m")
    
    def test_roundtrip(self):
        """Should roundtrip."""
        t = 0.005
        tof = self.tof.time_of_flight(t)
        t2 = self.tof.thickness(tof)
        self.assertAlmostEqual(t, t2, places=6)
        print("  [PASS] Round")
    
    def test_materials(self):
        """Should set materials."""
        self.tof.set_material("aluminum")
        self.assertEqual(self.tof.v, 6320.0)
        print("  [PASS] Mat")


class TestDefectDetector(unittest.TestCase):
    """Test defect detector."""
    
    def setUp(self):
        self.dd = DefectDetector()
    
    def test_detect(self):
        """Should detect defects."""
        scans = [
            AScan(1.0, 0.2),
            AScan(5.0, 0.8),
            AScan(10.0, 0.3)
        ]
        defects = self.dd.detect(scans, backwall_amplitude=1.0)
        self.assertGreater(len(defects), 0)
        print(f"  [PASS] Defects: {len(defects)}")
    
    def test_depth(self):
        """Should compute depth."""
        d = self.dd.depth_from_tof(5.0, 5900.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Depth: {d:.4f}")


class TestAttenuationAnalyzer(unittest.TestCase):
    """Test attenuation analyzer."""
    
    def setUp(self):
        self.aa = AttenuationAnalyzer()
    
    def test_coefficient(self):
        """Should compute attenuation."""
        a = self.aa.attenuation_coefficient(1.0, 0.5, 0.1)
        self.assertGreater(a, 0)
        print(f"  [PASS] Atten: {a:.2f}dB/m")
    
    def test_predict(self):
        """Should predict amplitude."""
        amp = self.aa.predicted_amplitude(1.0, 10.0, 0.5)
        self.assertLess(amp, 1.0)
        print(f"  [PASS] Pred: {amp:.4f}")


class TestThicknessGauge(unittest.TestCase):
    """Test thickness gauge."""
    
    def setUp(self):
        self.tg = ThicknessGauge()
    
    def test_measure(self):
        """Should measure thickness."""
        t = self.tg.measure(10.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] Meas: {t:.3f}mm")
    
    def test_average(self):
        """Should compute average."""
        self.tg.measure(10.0)
        self.tg.measure(20.0)
        avg = self.tg.average_thickness()
        self.assertGreater(avg, 0)
        print(f"  [PASS] Avg: {avg:.3f}")
    
    def test_tolerance(self):
        """Should check tolerance."""
        self.tg.measurements = [10.0, 10.05, 9.98]
        self.assertTrue(self.tg.within_tolerance(10.0, 0.1))
        print("  [PASS] Tol")


class TestUltrasonicInspection(unittest.TestCase):
    """Test unified inspection."""
    
    def setUp(self):
        self.ui = UltrasonicInspection()
    
    def test_inspect(self):
        """Should inspect."""
        scans = [AScan(float(i), 0.1 + i * 0.05) for i in range(20)]
        r = self.ui.inspect(scans, "steel")
        self.assertIn("thickness_mm", r)
        print(f"  [PASS] Insp: thick={r['thickness_mm']:.2f}mm")
    
    def test_summary(self):
        """Should summarize."""
        scans = [AScan(float(i), 0.1) for i in range(10)]
        self.ui.inspect(scans)
        s = self.ui.summary()
        self.assertIn("inspections", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
