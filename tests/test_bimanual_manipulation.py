"""
Unit tests for bimanual manipulation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bimanual_manipulation import (ArmPose, DualArmCoordinator,
                                   TaskAllocator,
                                   HandoffPlanner,
                                   BimanualGraspPlanner,
                                   BimanualManipulation)


class TestDualArmCoordinator(unittest.TestCase):
    """Test coordinator."""
    
    def setUp(self):
        self.dac = DualArmCoordinator(0.8)
    
    def test_relative(self):
        """Should compute relative pose."""
        l = ArmPose(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        r = ArmPose(0.8, 0.0, 0.0, 0.0, 0.0, 0.0)
        dx, dy, dz = self.dac.relative_pose(l, r)
        self.assertEqual(dx, 0.8)
        print(f"  [PASS] Rel: ({dx:.2f}, {dy:.2f}, {dz:.2f})")
    
    def test_overlap(self):
        """Should compute overlap."""
        o = self.dac.workspace_overlap(0.6, 0.6)
        self.assertGreater(o, 0)
        print(f"  [PASS] Over: {o:.2f}")
    
    def test_symmetric(self):
        """Should compute symmetric grasps."""
        lg, rg = self.dac.symmetric_grasp_points((0.0, 0.0, 0.0), 0.2)
        self.assertEqual(lg.x, -0.1)
        self.assertEqual(rg.x, 0.1)
        print(f"  [PASS] Sym: ({lg.x:.2f}, {rg.x:.2f})")


class TestTaskAllocator(unittest.TestCase):
    """Test allocator."""
    
    def setUp(self):
        self.ta = TaskAllocator()
    
    def test_dominant(self):
        """Should choose dominant."""
        d = self.ta.dominant_arm(1.0, 1.2, 1.0)
        self.assertEqual(d, "left")
        print(f"  [PASS] Dom: {d}")
    
    def test_balance(self):
        """Should compute balance."""
        b = self.ta.load_balance(10.0, 10.0)
        self.assertEqual(b, 0.0)
        print(f"  [PASS] Bal: {b:.2f}")


class TestHandoffPlanner(unittest.TestCase):
    """Test handoff."""
    
    def setUp(self):
        self.hp = HandoffPlanner()
    
    def test_pose(self):
        """Should compute handoff pose."""
        l = ArmPose(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        r = ArmPose(0.6, 0.0, 0.0, 0.0, 0.0, 0.0)
        h = self.hp.handoff_pose(l, r)
        self.assertEqual(h.x, 0.3)
        print(f"  [PASS] Hand: ({h.x:.2f})")
    
    def test_direction(self):
        """Should compute direction."""
        l = ArmPose(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        r = ArmPose(1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        dx, dy, dz = self.hp.approach_direction(l, r)
        self.assertEqual(dx, 1.0)
        print(f"  [PASS] Dir: ({dx:.2f})")


class TestBimanualGraspPlanner(unittest.TestCase):
    """Test grasp."""
    
    def setUp(self):
        self.bgp = BimanualGraspPlanner()
    
    def test_stability(self):
        """Should compute stability."""
        s = self.bgp.grasp_stability((-0.1, 0.0, 0.0), (0.1, 0.0, 0.0), (0.0, 0.0, 0.0))
        self.assertEqual(s, 1.0)
        print(f"  [PASS] Stab: {s:.2f}")
    
    def test_force(self):
        """Should compute force."""
        f = self.bgp.required_grip_force(10.0, 0.5, 2.0)
        self.assertEqual(f, 20.0)
        print(f"  [PASS] F: {f:.1f} N")


class TestBimanualManipulation(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.bm = BimanualManipulation()
    
    def test_summary(self):
        """Should summarize."""
        s = self.bm.bimanual_summary()
        self.assertIn("capabilities", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
