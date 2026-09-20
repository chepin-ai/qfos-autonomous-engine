"""
Unit tests for eddy current array module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from eddy_current_array import (CoilConfig, ImpedancePlaneAnalyzer,
                                 LiftOffCompensator, DefectClassifier,
                                 ECAProbeSimulator, EddyCurrentArray)


class TestImpedancePlaneAnalyzer(unittest.TestCase):
    """Test impedance plane."""
    
    def setUp(self):
        self.ipa = ImpedancePlaneAnalyzer()
    
    def test_normalize(self):
        """Should normalize."""
        r, i = self.ipa.normalize(2.0, 4.0, 1.0, 2.0)
        self.assertAlmostEqual(r, 2.0)
        self.assertAlmostEqual(i, 2.0)
        print("  [PASS] Norm")
    
    def test_angle(self):
        """Should compute angle."""
        a = self.ipa.angle(1.0, 1.0)
        self.assertAlmostEqual(a, 45.0, places=5)
        print(f"  [PASS] Angle: {a:.2f}")
    
    def test_magnitude(self):
        """Should compute magnitude."""
        m = self.ipa.magnitude(3.0, 4.0)
        self.assertAlmostEqual(m, 5.0, places=5)
        print(f"  [PASS] Mag: {m}")
    
    def test_trajectory(self):
        """Should analyze trajectory."""
        readings = [(1.0, 0.0), (2.0, 1.0), (3.0, 2.0)]
        t = self.ipa.trajectory(readings)
        self.assertIn("start_angle", t)
        print(f"  [PASS] Traj: {t}")


class TestLiftOffCompensator(unittest.TestCase):
    """Test lift-off."""
    
    def setUp(self):
        self.loc = LiftOffCompensator()
    
    def test_calibrate(self):
        """Should calibrate."""
        self.loc.calibrate([0.0, 0.5, 1.0], [1.0, 1.1, 1.2], [0.0, 0.1, 0.2])
        self.assertEqual(len(self.loc.lift_off_curve), 3)
        print("  [PASS] Cal")
    
    def test_compensate(self):
        """Should compensate."""
        self.loc.calibrate([0.0, 1.0], [1.0, 1.2], [0.0, 0.2])
        r, i = self.loc.compensate(2.2, 0.3, 1.0)
        self.assertAlmostEqual(r, 1.0, places=5)
        print(f"  [PASS] Comp: ({r:.2f}, {i:.2f})")


class TestDefectClassifier(unittest.TestCase):
    """Test classifier."""
    
    def setUp(self):
        self.dc = DefectClassifier()
    
    def test_classify(self):
        """Should classify."""
        c = self.dc.classify(45.0, 0.2)
        self.assertIn(c, ["crack", "corrosion", "lift_off", "noise", "unknown"])
        print(f"  [PASS] Class: {c}")
    
    def test_trajectory(self):
        """Should classify trajectory."""
        traj = [(1.0, 0.0), (2.0, 2.0)]
        c = self.dc.classify_trajectory(traj)
        self.assertIn(c, ["crack", "corrosion", "lift_off", "noise", "unknown"])
        print(f"  [PASS] Traj: {c}")


class TestECAProbeSimulator(unittest.TestCase):
    """Test simulator."""
    
    def setUp(self):
        self.sim = ECAProbeSimulator(CoilConfig(3.0, 50, 100000.0))
    
    def test_impedance(self):
        """Should compute impedance."""
        r, i = self.sim.impedance()
        self.assertGreater(r, 0)
        self.assertGreater(i, 0)
        print(f"  [PASS] Z: ({r:.4f}, {i:.4f})")
    
    def test_scan(self):
        """Should simulate scan."""
        readings = self.sim.scan_response([-2.0, -1.0, 0.0, 1.0, 2.0], 1.0)
        self.assertEqual(len(readings), 5)
        print("  [PASS] Scan")


class TestEddyCurrentArray(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.eca = EddyCurrentArray()
    
    def test_scan(self):
        """Should scan."""
        self.eca.scan([-1.0, 0.0, 1.0], 1.0)
        self.assertEqual(len(self.eca.readings), 3)
        print("  [PASS] Scan")
    
    def test_analyze(self):
        """Should analyze."""
        self.eca.scan([-2.0, 0.0, 2.0], 1.0)
        a = self.eca.analyze()
        self.assertIn("classification", a)
        print(f"  [PASS] Anlz: {a}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.eca.eca_summary()
        self.assertIn("frequency_Hz", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
