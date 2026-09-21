"""
Unit tests for humanoid balance module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from humanoid_balance import (CoMState, ZeroMomentPoint,
                              CapturePoint,
                              LinearInvertedPendulum,
                              PushRecovery,
                              HumanoidBalance)


class TestZeroMomentPoint(unittest.TestCase):
    """Test ZMP."""
    
    def setUp(self):
        self.zmp = ZeroMomentPoint()
    
    def test_from_com(self):
        """Should compute ZMP."""
        com = CoMState(0.1, 0.0, 0.8, 0.5, 0.0, 0.0)
        px, py = self.zmp.zmp_from_com(com, 0.8)
        self.assertNotEqual(px, com.x)
        print(f"  [PASS] ZMP: ({px:.3f}, {py:.3f})")
    
    def test_margin(self):
        """Should compute margin."""
        poly = [(-0.1, -0.05), (0.1, -0.05), (0.1, 0.05), (-0.1, 0.05)]
        m = self.zmp.stability_margin(0.0, 0.0, poly)
        self.assertGreater(m, 0)
        print(f"  [PASS] Margin: {m:.3f}")


class TestCapturePoint(unittest.TestCase):
    """Test capture."""
    
    def setUp(self):
        self.cp = CapturePoint()
    
    def test_cp(self):
        """Should compute capture point."""
        com = CoMState(0.0, 0.0, 0.8, 0.5, 0.0, 0.0)
        cx, cy = self.cp.capture_point(com, 0.8)
        self.assertGreater(cx, com.x)
        print(f"  [PASS] CP: ({cx:.3f}, {cy:.3f})")
    
    def test_capturable(self):
        """Should check capturable."""
        poly = [(-0.2, -0.1), (0.2, -0.1), (0.2, 0.1), (-0.2, 0.1)]
        self.assertTrue(self.cp.is_capturable(0.0, 0.0, poly))
        print("  [PASS] Capture")


class TestLinearInvertedPendulum(unittest.TestCase):
    """Test LIPM."""
    
    def setUp(self):
        self.lipm = LinearInvertedPendulum(0.8)
    
    def test_trajectory(self):
        """Should compute trajectory."""
        x, vx = self.lipm.com_trajectory(0.01, 0.1, 0.5)
        self.assertNotEqual(x, 0.01)
        print(f"  [PASS] x: {x:.4f}")
    
    def test_orbital(self):
        """Should compute orbital energy."""
        e = self.lipm.orbital_energy(0.1, 0.2)
        self.assertIsInstance(e, float)
        print(f"  [PASS] E: {e:.4f}")


class TestPushRecovery(unittest.TestCase):
    """Test recovery."""
    
    def setUp(self):
        self.pr = PushRecovery()
    
    def test_step(self):
        """Should compute step length."""
        s = self.pr.required_step_length(100.0, 0.1, 60.0, 0.8)
        self.assertGreater(s, 0)
        print(f"  [PASS] Step: {s:.3f}")
    
    def test_ankle(self):
        """Should compute ankle torque."""
        t = self.pr.ankle_strategy_torque(0.02)
        self.assertGreater(t, 0)
        print(f"  [PASS] T: {t:.1f} Nm")


class TestHumanoidBalance(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.hb = HumanoidBalance()
    
    def test_summary(self):
        """Should summarize."""
        s = self.hb.balance_summary()
        self.assertIn("models", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
