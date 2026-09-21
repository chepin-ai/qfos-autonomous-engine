"""
Unit tests for grasp planning module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from grasp_planning import (ContactPoint, GraspQualityMetrics,
                            AntipodalGraspDetection,
                            ForceClosure,
                            GripperWorkspace,
                            GraspPlanning)


class TestGraspQualityMetrics(unittest.TestCase):
    """Test quality."""
    
    def setUp(self):
        self.gqm = GraspQualityMetrics()
    
    def test_epsilon(self):
        """Should compute epsilon."""
        c = [ContactPoint((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
             ContactPoint((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0))]
        e = self.gqm.epsilon_quality(c)
        self.assertGreater(e, 0)
        print(f"  [PASS] Eps: {e:.3f}")
    
    def test_volume(self):
        """Should compute volume."""
        c = [ContactPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
             ContactPoint((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
             ContactPoint((0.0, 1.0, 0.0), (0.0, 0.0, 1.0))]
        v = self.gqm.volume_quality(c)
        self.assertGreater(v, 0)
        print(f"  [PASS] Vol: {v:.3f}")


class TestAntipodalGraspDetection(unittest.TestCase):
    """Test antipodal."""
    
    def setUp(self):
        self.agd = AntipodalGraspDetection()
    
    def test_antipodal(self):
        """Should detect antipodal."""
        c1 = ContactPoint((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
        c2 = ContactPoint((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
        a = self.agd.is_antipodal(c1, c2)
        self.assertTrue(a)
        print(f"  [PASS] Anti: {a}")
    
    def test_center(self):
        """Should compute center."""
        c1 = ContactPoint((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
        c2 = ContactPoint((2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
        center = self.agd.grasp_center(c1, c2)
        self.assertEqual(center, (1.0, 0.0, 0.0))
        print(f"  [PASS] Ctr: {center}")


class TestForceClosure(unittest.TestCase):
    """Test closure."""
    
    def setUp(self):
        self.fc = ForceClosure()
    
    def test_closure(self):
        """Should check closure."""
        c = [ContactPoint((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
             ContactPoint((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0))]
        f = self.fc.is_force_closure(c)
        self.assertTrue(f)
        print(f"  [PASS] FC: {f}")
    
    def test_min_force(self):
        """Should compute min force."""
        c = [ContactPoint((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
             ContactPoint((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0))]
        f = self.fc.min_normal_force([10.0, 0.0, 0.0, 0.0, 0.0, 0.0], c)
        self.assertGreater(f, 0)
        print(f"  [PASS] Fmin: {f:.2f}")


class TestGripperWorkspace(unittest.TestCase):
    """Test workspace."""
    
    def setUp(self):
        self.gw = GripperWorkspace()
    
    def test_can(self):
        """Should check fit."""
        f = self.gw.can_grasp(50.0)
        self.assertTrue(f)
        print(f"  [PASS] Fit: {f}")
    
    def test_span(self):
        """Should compute span."""
        c1 = ContactPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
        c2 = ContactPoint((3.0, 4.0, 0.0), (0.0, 0.0, 1.0))
        s = self.gw.grasp_span(c1, c2)
        self.assertEqual(s, 5.0)
        print(f"  [PASS] Span: {s:.1f}")


class TestGraspPlanning(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.gp = GraspPlanning()
    
    def test_summary(self):
        """Should summarize."""
        s = self.gp.grasp_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
