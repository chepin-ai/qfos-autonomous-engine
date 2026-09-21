"""
Unit tests for manipulator kinematics module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from manipulator_kinematics import (DHParameter, Pose3D,
                                    ForwardKinematics,
                                    InverseKinematics,
                                    JacobianCalculator,
                                    WorkspaceAnalyzer,
                                    ManipulatorKinematics)


class TestForwardKinematics(unittest.TestCase):
    """Test FK."""
    
    def setUp(self):
        dh = [DHParameter(0.0, 0.0, 1.0, 0.0),
              DHParameter(0.0, 0.0, 1.0, 0.0)]
        self.fk = ForwardKinematics(dh)
    
    def test_matrix(self):
        """Should generate matrix."""
        m = self.fk.transformation_matrix(DHParameter(0.0, 0.0, 1.0, 0.0))
        self.assertAlmostEqual(m[0][0], 1.0)
        print("  [PASS] Mat")
    
    def test_multiply(self):
        """Should multiply."""
        I = [[1.0, 0.0, 0.0, 0.0],
             [0.0, 1.0, 0.0, 0.0],
             [0.0, 0.0, 1.0, 0.0],
             [0.0, 0.0, 0.0, 1.0]]
        r = self.fk.matrix_multiply(I, I)
        self.assertAlmostEqual(r[0][0], 1.0)
        print("  [PASS] Mul")
    
    def test_end_effector(self):
        """Should compute pose."""
        pose = self.fk.end_effector_pose([0.0, 0.0])
        self.assertAlmostEqual(pose.x, 2.0, delta=0.01)
        print(f"  [PASS] EE: ({pose.x:.2f}, {pose.y:.2f})")


class TestInverseKinematics(unittest.TestCase):
    """Test IK."""
    
    def setUp(self):
        self.ik = InverseKinematics(1.0, 1.0)
    
    def test_solve(self):
        """Should solve."""
        sols = self.ik.solve_2dof(1.0, 1.0)
        self.assertGreater(len(sols), 0)
        print(f"  [PASS] IK: {len(sols)} sols")
    
    def test_reachable(self):
        """Should reject unreachable."""
        sols = self.ik.solve_2dof(3.0, 0.0)
        self.assertEqual(len(sols), 0)
        print("  [PASS] Unreach")


class TestJacobianCalculator(unittest.TestCase):
    """Test Jacobian."""
    
    def setUp(self):
        self.j = JacobianCalculator([1.0, 1.0])
    
    def test_jacobian(self):
        """Should compute."""
        J = self.j.planar_jacobian([0.0, 0.0])
        self.assertEqual(len(J), 2)
        print(f"  [PASS] J: {J}")
    
    def test_manipulability(self):
        """Should compute."""
        J = self.j.planar_jacobian([0.0, math.pi / 2])
        m = self.j.manipulability(J)
        self.assertGreater(m, 0)
        print(f"  [PASS] Man: {m:.2f}")


class TestWorkspaceAnalyzer(unittest.TestCase):
    """Test workspace."""
    
    def setUp(self):
        self.w = WorkspaceAnalyzer([1.0, 1.0])
    
    def test_radius(self):
        """Should compute radius."""
        min_r, max_r = self.w.reachable_radius()
        self.assertEqual(max_r, 2.0)
        print(f"  [PASS] R: [{min_r:.1f}, {max_r:.1f}]")
    
    def test_area(self):
        """Should compute area."""
        a = self.w.dexterous_workspace()
        self.assertGreater(a, 0)
        print(f"  [PASS] A: {a:.2f}")


class TestManipulatorKinematics(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.mk = ManipulatorKinematics()
    
    def test_summary(self):
        """Should summarize."""
        s = self.mk.mk_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
