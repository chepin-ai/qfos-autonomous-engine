"""
Unit tests for manipulator kinematics module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from manipulator_kinematics import (JointType, DHParameter,
                                    ForwardKinematics, InverseKinematics,
                                    JacobianCalculator, WorkspaceAnalyzer,
                                    SingularityDetector, ManipulatorKinematics)


class TestForwardKinematics(unittest.TestCase):
    """Test forward kinematics."""
    
    def setUp(self):
        dh = [DHParameter(0, 0, 0.3, 0), DHParameter(0, 0, 0.3, 0)]
        self.fk = ForwardKinematics(dh)
    
    def test_zero_config(self):
        """Should compute zero configuration."""
        pos = self.fk.solve([0.0, 0.0])
        self.assertAlmostEqual(pos[0], 0.6, places=3)
        self.assertAlmostEqual(pos[1], 0.0, places=3)
        print(f"  [PASS] Zero: ({pos[0]:.3f}, {pos[1]:.3f})")
    
    def test_90_deg(self):
        """Should compute 90-degree config."""
        import math
        pos = self.fk.solve([math.pi / 2, 0.0])
        self.assertAlmostEqual(pos[0], 0.0, places=3)
        self.assertAlmostEqual(pos[1], 0.6, places=3)
        print(f"  [PASS] 90deg: ({pos[0]:.3f}, {pos[1]:.3f})")


class TestInverseKinematics(unittest.TestCase):
    """Test inverse kinematics."""
    
    def setUp(self):
        self.ik = InverseKinematics([0.3, 0.3])
    
    def test_reachable(self):
        """Should solve reachable target."""
        sols = self.ik.solve_2dof(0.4, 0.3)
        self.assertGreater(len(sols), 0)
        print(f"  [PASS] IK: {len(sols)} solutions")
    
    def test_unreachable(self):
        """Should reject unreachable."""
        sols = self.ik.solve_2dof(1.0, 0.0)
        self.assertEqual(len(sols), 0)
        print("  [PASS] Unreachable")
    
    def test_reachable_check(self):
        """Should check reachability."""
        self.assertTrue(self.ik.reachable(0.4, 0.3))
        self.assertFalse(self.ik.reachable(1.0, 0.0))
        print("  [PASS] Reach check")


class TestJacobian(unittest.TestCase):
    """Test Jacobian calculator."""
    
    def setUp(self):
        self.jac = JacobianCalculator([0.3, 0.3])
    
    def test_determinant(self):
        """Should compute determinant."""
        import math
        J = self.jac.compute_2dof(math.pi / 4, math.pi / 4)
        det = self.jac.determinant(J)
        self.assertNotEqual(det, 0.0)
        print(f"  [PASS] Det: {det:.4f}")
    
    def test_manipulability(self):
        """Should compute manipulability."""
        import math
        J = self.jac.compute_2dof(0.0, math.pi / 2)
        w = self.jac.manipulability(J)
        self.assertGreater(w, 0)
        print(f"  [PASS] Manip: {w:.4f}")


class TestWorkspace(unittest.TestCase):
    """Test workspace analyzer."""
    
    def setUp(self):
        self.ws = WorkspaceAnalyzer([0.3, 0.3])
    
    def test_reach(self):
        """Should compute reach."""
        min_r, max_r = self.ws.reach()
        self.assertAlmostEqual(max_r, 0.6)
        self.assertAlmostEqual(min_r, 0.0)
        print(f"  [PASS] Reach: [{min_r:.1f}, {max_r:.1f}]")
    
    def test_in_workspace(self):
        """Should check workspace."""
        self.assertTrue(self.ws.is_in_workspace(0.4, 0.0))
        self.assertFalse(self.ws.is_in_workspace(1.0, 0.0))
        print("  [PASS] Workspace")
    
    def test_sample(self):
        """Should sample boundary."""
        pts = self.ws.sample_workspace(10)
        self.assertEqual(len(pts), 10)
        print(f"  [PASS] Sample: {len(pts)}")


class TestSingularity(unittest.TestCase):
    """Test singularity detector."""
    
    def setUp(self):
        self.sd = SingularityDetector()
    
    def test_singular(self):
        """Should detect singularity."""
        J = [[1.0, 1.0], [1.0, 1.0]]
        self.assertTrue(self.sd.check(J))
        print("  [PASS] Singular")
    
    def test_nonsingular(self):
        """Should not detect normal config."""
        J = [[1.0, 0.0], [0.0, 1.0]]
        self.assertFalse(self.sd.check(J))
        print("  [PASS] Non-singular")
    
    def test_condition(self):
        """Should compute condition number."""
        J = [[2.0, 0.0], [0.0, 1.0]]
        cond = self.sd.condition_number(J)
        self.assertAlmostEqual(cond, 2.0)
        print(f"  [PASS] Cond: {cond:.1f}")


class TestManipulatorKinematics(unittest.TestCase):
    """Test unified kinematics."""
    
    def setUp(self):
        self.mk = ManipulatorKinematics([0.3, 0.3])
    
    def test_forward(self):
        """Should compute FK."""
        pos = self.mk.forward([0.0, 0.0])
        self.assertIsNotNone(pos)
        print(f"  [PASS] FK: {pos}")
    
    def test_inverse(self):
        """Should compute IK."""
        sols = self.mk.inverse((0.4, 0.3))
        self.assertGreater(len(sols), 0)
        print(f"  [PASS] IK: {len(sols)}")
    
    def test_singularity(self):
        """Should check singularity."""
        import math
        s = self.mk.check_singularity([0.0, math.pi])
        self.assertIsInstance(s, bool)
        print(f"  [PASS] Sing: {s}")
    
    def test_summary(self):
        """Should provide summary."""
        s = self.mk.kinematic_summary()
        self.assertIn("max_reach", s)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
