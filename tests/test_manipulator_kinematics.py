"""
Unit tests for manipulator kinematics module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from manipulator_kinematics import (DHParameter, ForwardKinematics,
                                    InverseKinematics,
                                    JacobianCalculator,
                                    WorkspaceAnalyzer,
                                    ManipulatorKinematics)


class TestForwardKinematics(unittest.TestCase):
    """Test forward kinematics."""
    
    def setUp(self):
        self.fk = ForwardKinematics()
    
    def test_dh_transform(self):
        """Should compute DH transform."""
        dh = DHParameter(0.0, 0.0, 1.0, 0.0)
        T = self.fk.dh_transform(dh)
        self.assertEqual(T[0][3], 1.0)
        print("  [PASS] DH")
    
    def test_multiply(self):
        """Should multiply matrices."""
        a = [[1.0, 0.0, 0.0, 0.0],
             [0.0, 1.0, 0.0, 0.0],
             [0.0, 0.0, 1.0, 0.0],
             [0.0, 0.0, 0.0, 1.0]]
        b = a
        r = self.fk.multiply_matrices(a, b)
        self.assertEqual(r[0][0], 1.0)
        print("  [PASS] Mul")
    
    def test_solve(self):
        """Should solve FK."""
        dh = [DHParameter(0.0, 0.0, 1.0, 0.0)]
        T = self.fk.solve(dh)
        self.assertEqual(T[0][3], 1.0)
        print("  [PASS] FK")
    
    def test_extract(self):
        """Should extract position."""
        T = [[1.0, 0.0, 0.0, 2.0],
             [0.0, 1.0, 0.0, 3.0],
             [0.0, 0.0, 1.0, 4.0],
             [0.0, 0.0, 0.0, 1.0]]
        p = self.fk.extract_position(T)
        self.assertEqual(p, (2.0, 3.0, 4.0))
        print(f"  [PASS] Pos: {p}")


class TestInverseKinematics(unittest.TestCase):
    """Test inverse kinematics."""
    
    def setUp(self):
        self.ik = InverseKinematics()
    
    def test_2r(self):
        """Should solve 2R IK."""
        sol = self.ik.planar_2r(1.5, 0.0, 1.0, 1.0)
        self.assertGreater(len(sol), 0)
        print(f"  [PASS] IK: {len(sol)} sols")
    
    def test_unreachable(self):
        """Should detect unreachable."""
        sol = self.ik.planar_2r(10.0, 0.0, 1.0, 1.0)
        self.assertEqual(len(sol), 0)
        print("  [PASS] Unreach")


class TestJacobianCalculator(unittest.TestCase):
    """Test Jacobian."""
    
    def setUp(self):
        self.jc = JacobianCalculator()
    
    def test_2r_jacobian(self):
        """Should compute 2R Jacobian."""
        J = self.jc.planar_2r_jacobian(0.0, math.pi/2, 1.0, 1.0)
        self.assertEqual(len(J), 2)
        print("  [PASS] Jac")
    
    def test_det(self):
        """Should compute determinant."""
        J = [[1.0, 0.0], [0.0, 1.0]]
        d = self.jc.determinant(J)
        self.assertEqual(d, 1.0)
        print(f"  [PASS] Det: {d}")


class TestWorkspaceAnalyzer(unittest.TestCase):
    """Test workspace."""
    
    def setUp(self):
        self.wa = WorkspaceAnalyzer()
    
    def test_workspace(self):
        """Should compute workspace."""
        w = self.wa.planar_2r_workspace(1.0, 1.0)
        self.assertEqual(w["r_max"], 2.0)
        print(f"  [PASS] WS: {w}")
    
    def test_reachable(self):
        """Should check reachability."""
        r = self.wa.is_reachable(1.5, 0.0, 1.0, 1.0)
        self.assertTrue(r)
        print("  [PASS] Reach")


class TestManipulatorKinematics(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.mk = ManipulatorKinematics()
    
    def test_set_dh(self):
        """Should set DH."""
        self.mk.set_dh_params([DHParameter(0.0, 0.0, 1.0, 0.0)])
        self.assertEqual(len(self.mk.dh_params), 1)
        print("  [PASS] Set")
    
    def test_forward(self):
        """Should solve forward."""
        self.mk.set_dh_params([DHParameter(0.0, 0.0, 1.0, 0.0)])
        r = self.mk.forward_solve()
        self.assertIn("x", r)
        print(f"  [PASS] Fwd: {r['x']}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.mk.mk_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
