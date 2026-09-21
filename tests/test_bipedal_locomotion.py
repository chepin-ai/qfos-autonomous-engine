"""
Unit tests for bipedal locomotion module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bipedal_locomotion import (FootStep, ZeroMomentPoint,
                                CapturePoint,
                                WalkingPatternGeneration,
                                BalanceControl,
                                BipedalLocomotion)


class TestZeroMomentPoint(unittest.TestCase):
    """Test ZMP."""
    
    def setUp(self):
        self.zmp = ZeroMomentPoint()
    
    def test_zmp(self):
        """Should compute ZMP."""
        z = self.zmp.zmp_from_forces(0.1, 0.0, 10.0, 0.0, 100.0)
        self.assertAlmostEqual(z[0], 0.0, delta=1e-6)
        print(f"  [PASS] ZMP: {z}")
    
    def test_margin(self):
        """Should compute margin."""
        m = self.zmp.zmp_stability_margin(0.0, 0.0,
                                          [(-0.1, -0.05), (0.1, -0.05),
                                           (0.1, 0.05), (-0.1, 0.05)])
        self.assertGreater(m, 0)
        print(f"  [PASS] Marg: {m:.4f}")


class TestCapturePoint(unittest.TestCase):
    """Test capture."""
    
    def setUp(self):
        self.cp = CapturePoint()
    
    def test_cp(self):
        """Should compute capture point."""
        c = self.cp.capture_point(0.0, 1.0)
        self.assertGreater(c, 0)
        print(f"  [PASS] CP: {c:.4f}")
    
    def test_capturable(self):
        """Should check capturable."""
        ok = self.cp.is_capturable(0.3, 0.0)
        self.assertTrue(ok)
        print(f"  [PASS] Cap: {ok}")


class TestWalkingPatternGeneration(unittest.TestCase):
    """Test walking."""
    
    def setUp(self):
        self.wpg = WalkingPatternGeneration()
    
    def test_com(self):
        """Should compute COM."""
        c = self.wpg.com_trajectory(0.2)
        self.assertEqual(len(c), 2)
        print(f"  [PASS] COM: {c}")
    
    def test_swing(self):
        """Should compute swing foot."""
        s = self.wpg.swing_foot_trajectory(0.4, 0.0, 0.3)
        self.assertEqual(len(s), 2)
        self.assertGreater(s[1], 0)
        print(f"  [PASS] Swing: {s}")


class TestBalanceControl(unittest.TestCase):
    """Test balance."""
    
    def setUp(self):
        self.bc = BalanceControl()
    
    def test_ankle(self):
        """Should compute ankle torque."""
        t = self.bc.ankle_strategy(0.01, 0.05)
        self.assertGreater(t, 0)
        print(f"  [PASS] Ankle: {t:.2f}")
    
    def test_hip(self):
        """Should compute hip torque."""
        t = self.bc.hip_strategy(0.01, 0.1)
        self.assertGreater(t, 0)
        print(f"  [PASS] Hip: {t:.2f}")


class TestBipedalLocomotion(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.bl = BipedalLocomotion()
    
    def test_summary(self):
        """Should summarize."""
        s = self.bl.locomotion_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
