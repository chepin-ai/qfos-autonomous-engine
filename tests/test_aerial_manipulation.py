"""
Unit tests for aerial manipulation module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aerial_manipulation import (UAVState, AerialArmKinematics,
                                 WrenchEstimation,
                                 AerialCompliance,
                                 AerialStability,
                                 AerialManipulation)


class TestAerialArmKinematics(unittest.TestCase):
    """Test kinematics."""
    
    def setUp(self):
        self.ak = AerialArmKinematics(0.5)
    
    def test_ee(self):
        """Should compute end-effector."""
        uav = UAVState(1.0, 2.0, 3.0, 0.0, 0.0, 0.0)
        x, y, z = self.ak.end_effector_position(uav, [0.0])
        self.assertAlmostEqual(x, 1.5, delta=0.01)
        print(f"  [PASS] EE: ({x:.2f}, {y:.2f}, {z:.2f})")
    
    def test_jacobian(self):
        """Should compute Jacobian."""
        j = self.ak.jacobian([0.0])
        self.assertEqual(len(j), 3)
        print(f"  [PASS] Jac: {j}")


class TestWrenchEstimation(unittest.TestCase):
    """Test wrench."""
    
    def setUp(self):
        self.we = WrenchEstimation()
    
    def test_force(self):
        """Should compute force."""
        f = self.we.force_from_acceleration(2.0, (1.0, 2.0, 3.0))
        self.assertEqual(f[0], 2.0)
        print(f"  [PASS] F: {f}")
    
    def test_torque(self):
        """Should compute torque."""
        t = self.we.torque_from_angular_accel(0.1, 5.0)
        self.assertEqual(t, 0.5)
        print(f"  [PASS] T: {t:.2f}")


class TestAerialCompliance(unittest.TestCase):
    """Test compliance."""
    
    def setUp(self):
        self.ac = AerialCompliance()
    
    def test_displacement(self):
        """Should compute displacement."""
        d = self.ac.compliant_displacement(50.0)
        self.assertEqual(d, 0.5)
        print(f"  [PASS] Disp: {d:.2f}")
    
    def test_damping(self):
        """Should compute damping."""
        f = self.ac.damping_force(2.0)
        self.assertEqual(f, 20.0)
        print(f"  [PASS] Damp: {f:.1f}")


class TestAerialStability(unittest.TestCase):
    """Test stability."""
    
    def setUp(self):
        self.as_ = AerialStability()
    
    def test_com_shift(self):
        """Should compute COM shift."""
        s = self.as_.center_of_mass_shift(0.5, 0.4, 2.0)
        self.assertAlmostEqual(s, 0.08, delta=0.01)
        print(f"  [PASS] COM: {s:.3f}")
    
    def test_margin(self):
        """Should compute margin."""
        m = self.as_.stability_margin(30.0, 20.0, 0.05)
        self.assertGreater(m, 0)
        print(f"  [PASS] Margin: {m:.3f}")


class TestAerialManipulation(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.am = AerialManipulation()
    
    def test_summary(self):
        """Should summarize."""
        s = self.am.aerial_summary()
        self.assertIn("capabilities", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
