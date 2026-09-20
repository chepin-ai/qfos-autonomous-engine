"""
Unit tests for contact detection module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from contact_detection import (ContactType, Wrench,
                               ForceContactDetector, TactileArray,
                               ProximityDetector, SlipDetector,
                               ContactDetection)


class TestWrench(unittest.TestCase):
    """Test wrench."""
    
    def test_magnitude(self):
        """Should compute magnitude."""
        w = Wrench(fx=3.0, fy=4.0, fz=0.0)
        self.assertAlmostEqual(w.magnitude(), 5.0)
        print("  [PASS] Mag")
    
    def test_torque_magnitude(self):
        """Should compute torque."""
        w = Wrench(tx=1.0, ty=1.0, tz=1.0)
        self.assertAlmostEqual(w.torque_magnitude(), math.sqrt(3))
        print("  [PASS] Torque")


class TestForceContactDetector(unittest.TestCase):
    """Test force contact detector."""
    
    def setUp(self):
        self.fcd = ForceContactDetector(force_threshold_N=5.0)
    
    def test_no_contact(self):
        """Should not detect below threshold."""
        w = Wrench(fx=1.0, fy=1.0)
        self.assertFalse(self.fcd.detect(w))
        print("  [PASS] No contact")
    
    def test_contact(self):
        """Should detect above threshold."""
        w = Wrench(fx=10.0)
        self.assertTrue(self.fcd.detect(w))
        print("  [PASS] Contact")
    
    def test_direction(self):
        """Should estimate direction."""
        w = Wrench(fx=1.0, fy=0.0, fz=0.0)
        d = self.fcd.contact_direction(w)
        self.assertAlmostEqual(d[0], 1.0)
        print(f"  [PASS] Dir: {d}")


class TestTactileArray(unittest.TestCase):
    """Test tactile array."""
    
    def setUp(self):
        self.ta = TactileArray(rows=4, cols=4)
    
    def test_total_force(self):
        """Should sum pressure."""
        self.ta.set_pressure(0, 0, 1.0)
        self.ta.set_pressure(1, 1, 2.0)
        self.assertAlmostEqual(self.ta.total_force(), 3.0)
        print("  [PASS] Total")
    
    def test_center_of_pressure(self):
        """Should compute COP."""
        self.ta.set_pressure(0, 0, 1.0)
        self.ta.set_pressure(1, 1, 1.0)
        cop = self.ta.center_of_pressure()
        self.assertGreater(cop[0], 0)
        print(f"  [PASS] COP: {cop}")
    
    def test_max_pressure(self):
        """Should find max."""
        self.ta.set_pressure(2, 2, 5.0)
        self.assertAlmostEqual(self.ta.max_pressure(), 5.0)
        print("  [PASS] Max")


class TestProximityDetector(unittest.TestCase):
    """Test proximity detector."""
    
    def setUp(self):
        self.pd = ProximityDetector(threshold_mm=10.0)
    
    def test_detect(self):
        """Should detect near object."""
        self.assertTrue(self.pd.detect(5.0))
        print("  [PASS] Detect")
    
    def test_no_detect(self):
        """Should not detect far object."""
        self.assertFalse(self.pd.detect(20.0))
        print("  [PASS] No detect")
    
    def test_velocity(self):
        """Should compute approach."""
        v = self.pd.approach_velocity(10.0, 5.0, 1.0)
        self.assertAlmostEqual(v, 5.0)
        print(f"  [PASS] Vel: {v}")


class TestSlipDetector(unittest.TestCase):
    """Test slip detector."""
    
    def setUp(self):
        self.sd = SlipDetector(friction_coefficient=0.5)
    
    def test_no_slip(self):
        """Should not detect below limit."""
        self.assertFalse(self.sd.detect_slip(10.0, 4.0))
        print("  [PASS] No slip")
    
    def test_slip(self):
        """Should detect above limit."""
        self.assertTrue(self.sd.detect_slip(10.0, 6.0))
        print("  [PASS] Slip")
    
    def test_margin(self):
        """Should compute margin."""
        m = self.sd.safety_margin(10.0, 4.0)
        self.assertAlmostEqual(m, 0.8)
        print(f"  [PASS] Margin: {m}")


class TestContactDetection(unittest.TestCase):
    """Test unified contact detection."""
    
    def setUp(self):
        self.cd = ContactDetection()
    
    def test_update(self):
        """Should update state."""
        s = self.cd.update(Wrench(fx=10.0))
        self.assertTrue(s["contact"])
        print("  [PASS] Update")
    
    def test_summary(self):
        """Should provide summary."""
        self.cd.update(Wrench(fx=1.0))
        self.cd.update(Wrench(fx=10.0))
        s = self.cd.contact_summary()
        self.assertIn("contact_events", s)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    import math
    unittest.main(verbosity=2)
