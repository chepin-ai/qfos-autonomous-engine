"""
Unit tests for slip detection module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from slip_detection import (TactileReading, TactileSlipDetection,
                            IncipientSlipEstimation,
                            FrictionLimitEstimation,
                            RecoveryControl,
                            SlipDetection)


class TestTactileSlipDetection(unittest.TestCase):
    """Test tactile."""
    
    def setUp(self):
        self.tsd = TactileSlipDetection()
    
    def test_ratio(self):
        """Should compute ratio."""
        r = self.tsd.friction_ratio(10.0, 8.0)
        self.assertEqual(r, 0.8)
        print(f"  [PASS] R: {r:.2f}")
    
    def test_slip(self):
        """Should detect slip."""
        readings = [TactileReading(10.0, 8.1, 0.0), TactileReading(10.0, 8.1, 0.0)]
        s = self.tsd.is_slipping(readings)
        self.assertTrue(s)
        print(f"  [PASS] Slip: {s}")
    
    def test_direction(self):
        """Should estimate direction."""
        readings = [TactileReading(10.0, 3.0, 4.0)]
        d = self.tsd.slip_direction(readings)
        self.assertAlmostEqual(d[0], 0.6, delta=1e-10)
        self.assertAlmostEqual(d[1], 0.8, delta=1e-10)
        print(f"  [PASS] Dir: ({d[0]:.2f}, {d[1]:.2f})")


class TestIncipientSlipEstimation(unittest.TestCase):
    """Test incipient."""
    
    def setUp(self):
        self.ise = IncipientSlipEstimation()
    
    def test_margin(self):
        """Should compute margin."""
        m = self.ise.slip_margin(0.5, 0.8)
        self.assertAlmostEqual(m, 0.3, delta=1e-10)
        print(f"  [PASS] M: {m:.2f}")
    
    def test_time(self):
        """Should estimate time."""
        t = self.ise.time_to_slip(0.5, 0.8, 1.0, 10.0)
        self.assertAlmostEqual(t, 3.0, delta=1e-10)
        print(f"  [PASS] T: {t:.1f}")


class TestFrictionLimitEstimation(unittest.TestCase):
    """Test friction."""
    
    def setUp(self):
        self.fle = FrictionLimitEstimation()
    
    def test_static(self):
        """Should estimate static."""
        f = self.fle.estimate_static_friction(0.5)
        self.assertEqual(f, 0.6)
        print(f"  [PASS] Fs: {f:.2f}")
    
    def test_kinetic(self):
        """Should estimate kinetic."""
        readings = [TactileReading(10.0, 4.0, 3.0)]
        f = self.fle.estimate_kinetic_friction(readings)
        self.assertEqual(f, 0.5)
        print(f"  [PASS] Fk: {f:.2f}")


class TestRecoveryControl(unittest.TestCase):
    """Test recovery."""
    
    def setUp(self):
        self.rc = RecoveryControl()
    
    def test_grip(self):
        """Should adjust grip."""
        g = self.rc.grip_adjustment(True, 10.0)
        self.assertEqual(g, 12.0)
        print(f"  [PASS] G: {g:.1f}")
    
    def test_reposition(self):
        """Should compute offset."""
        o = self.rc.contact_reposition((1.0, 0.0))
        self.assertEqual(o, (-1.0, 0.0))
        print(f"  [PASS] Off: {o}")


class TestSlipDetection(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.sd = SlipDetection()
    
    def test_summary(self):
        """Should summarize."""
        s = self.sd.slip_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
