"""
Unit tests for grasp planning module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from grasp_planning import (GraspType, ContactPoint,
                            ForceClosureChecker, GraspQualityEvaluator,
                            HandConfiguration, GraspPlanner, GraspPlanning)


class TestForceClosure(unittest.TestCase):
    """Test force closure checker."""
    
    def setUp(self):
        self.fc = ForceClosureChecker()
    
    def test_two_contact_closure(self):
        """Should detect force closure with 2 contacts."""
        # Normals point inward (toward object center at origin)
        c1 = ContactPoint((0.05, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.5)
        c2 = ContactPoint((-0.05, 0.0, 0.0), (1.0, 0.0, 0.0), 0.5)
        result = self.fc.is_force_closure([c1, c2])
        self.assertTrue(result)
        print("  [PASS] FC 2-contact: True")
    
    def test_no_closure_single(self):
        """Should reject single contact."""
        c1 = ContactPoint((0.05, 0.0, 0.0), (1.0, 0.0, 0.0), 0.5)
        result = self.fc.is_force_closure([c1])
        self.assertFalse(result)
        print("  [PASS] FC 1-contact: False")
    
    def test_friction_cone(self):
        """Should compute friction cone."""
        c = ContactPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 0.5)
        edges = self.fc.friction_cone_edges(c)
        self.assertEqual(len(edges), 8)
        print(f"  [PASS] Cone: {len(edges)} edges")


class TestGraspQuality(unittest.TestCase):
    """Test grasp quality evaluator."""
    
    def setUp(self):
        self.gq = GraspQualityEvaluator()
        # Inward-pointing normals (toward object center)
        self.c1 = ContactPoint((0.05, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.5)
        self.c2 = ContactPoint((-0.05, 0.0, 0.0), (1.0, 0.0, 0.0), 0.5)
    
    def test_epsilon_quality(self):
        """Should compute epsilon quality."""
        q = self.gq.epsilon_quality([self.c1, self.c2])
        self.assertGreater(q, 0)
        print(f"  [PASS] Epsilon: {q:.4f}")
    
    def test_volume_quality(self):
        """Should compute volume quality."""
        q = self.gq.volume_quality([self.c1, self.c2])
        self.assertGreater(q, 0)
        print(f"  [PASS] Volume: {q:.4f}")
    
    def test_antipodal_quality(self):
        """Should compute antipodal quality."""
        q = self.gq.antipodal_quality([self.c1, self.c2])
        self.assertGreater(q, 0)
        print(f"  [PASS] Antipodal: {q:.4f}")
    
    def test_no_closure_zero_quality(self):
        """Should have zero quality for no closure."""
        q = self.gq.epsilon_quality([self.c1])
        self.assertEqual(q, 0.0)
        print("  [PASS] Zero: 0.0")


class TestHandConfiguration(unittest.TestCase):
    """Test hand configuration."""
    
    def setUp(self):
        self.hand = HandConfiguration(num_fingers=3)
    
    def test_fingertips(self):
        """Should compute fingertip positions."""
        tips = self.hand.fingertip_positions((0.0, 0.0, 0.0))
        self.assertEqual(len(tips), 3)
        print(f"  [PASS] Tips: {len(tips)}")
    
    def test_to_contacts(self):
        """Should convert to contacts."""
        self.hand.fingertip_positions()
        normals = [(0.0, 0.0, 1.0)] * 3
        contacts = self.hand.to_contacts(normals)
        self.assertEqual(len(contacts), 3)
        print(f"  [PASS] Contacts: {len(contacts)}")


class TestGraspPlanner(unittest.TestCase):
    """Test grasp planner."""
    
    def setUp(self):
        self.gp = GraspPlanner()
    
    def test_antipodal(self):
        """Should plan antipodal grasp."""
        grasp = self.gp.plan_antipodal(0.05)
        self.assertEqual(len(grasp), 2)
        print(f"  [PASS] Antipodal: {len(grasp)}")
    
    def test_circular(self):
        """Should plan circular grasp."""
        grasp = self.gp.plan_circular(0.05, 4)
        self.assertEqual(len(grasp), 4)
        print(f"  [PASS] Circular: {len(grasp)}")
    
    def test_select_best(self):
        """Should select best grasp."""
        g1 = self.gp.plan_antipodal(0.05)
        g2 = self.gp.plan_circular(0.05, 3)
        best, score = self.gp.select_best_grasp([g1, g2])
        self.assertIsNotNone(best)
        self.assertGreaterEqual(score, 0)
        print(f"  [PASS] Best: score={score:.4f}")


class TestGraspPlanning(unittest.TestCase):
    """Test unified grasp planning."""
    
    def setUp(self):
        self.gp = GraspPlanning()
    
    def test_plan_object(self):
        """Should plan for object."""
        grasp = self.gp.plan_for_object(0.05)
        self.assertGreater(len(grasp), 0)
        print(f"  [PASS] Plan: {len(grasp)} contacts")
    
    def test_summary(self):
        """Should provide summary."""
        self.gp.plan_for_object(0.05)
        s = self.gp.grasp_summary()
        self.assertIn("candidates", s)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
