"""
Unit tests for exoskeleton control module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from exoskeleton_control import (JointState, ImpedanceControl,
                                 GaitAssistance,
                                 InteractionForceEstimation,
                                 AdaptiveSupport,
                                 ExoskeletonControl)


class TestImpedanceControl(unittest.TestCase):
    """Test impedance."""
    
    def setUp(self):
        self.ic = ImpedanceControl()
    
    def test_torque(self):
        """Should compute torque."""
        t = self.ic.desired_torque(0.1, 0.5)
        self.assertEqual(t, 15.0)
        print(f"  [PASS] T: {t:.1f}")
    
    def test_inertia(self):
        """Should return inertia."""
        m = self.ic.apparent_inertia()
        self.assertEqual(m, 0.5)
        print(f"  [PASS] M: {m:.2f}")


class TestGaitAssistance(unittest.TestCase):
    """Test gait."""
    
    def setUp(self):
        self.ga = GaitAssistance()
    
    def test_phase(self):
        """Should detect phase."""
        p = self.ga.gait_phase(0.5, 1.0)
        self.assertEqual(p, "swing")
        print(f"  [PASS] Phase: {p}")
    
    def test_assistance(self):
        """Should compute assistance."""
        a = self.ga.assistance_torque("stance", 100.0)
        self.assertEqual(a, 30.0)
        print(f"  [PASS] A: {a:.1f}")


class TestInteractionForceEstimation(unittest.TestCase):
    """Test interaction."""
    
    def setUp(self):
        self.ife = InteractionForceEstimation()
    
    def test_torque(self):
        """Should compute interaction."""
        t = self.ife.interaction_torque(50.0, 10.0)
        self.assertEqual(t, 47.0)
        print(f"  [PASS] Tint: {t:.1f}")
    
    def test_power(self):
        """Should compute power."""
        p = self.ife.interaction_power(10.0, 2.0)
        self.assertEqual(p, 20.0)
        print(f"  [PASS] P: {p:.1f}")


class TestAdaptiveSupport(unittest.TestCase):
    """Test adaptive."""
    
    def setUp(self):
        self.as_ = AdaptiveSupport()
    
    def test_level(self):
        """Should compute support."""
        s = self.as_.support_level(5.0)
        self.assertGreater(s, 0)
        print(f"  [PASS] Sup: {s:.3f}")
    
    def test_fatigue(self):
        """Should compute compensation."""
        c = self.as_.fatigue_compensation(150.0)
        self.assertGreater(c, 0)
        print(f"  [PASS] Comp: {c:.3f}")


class TestExoskeletonControl(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ec = ExoskeletonControl()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ec.exoskeleton_summary()
        self.assertIn("capabilities", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
