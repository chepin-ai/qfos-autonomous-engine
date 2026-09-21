"""
Unit tests for cable-driven manipulation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cable_driven_manipulation import (CableAttachment, TensionDistribution,
                                       CableCompliance,
                                       WorkspaceAnalysis,
                                       CableRouting,
                                       CableDrivenManipulation)


class TestTensionDistribution(unittest.TestCase):
    """Test tension."""
    
    def setUp(self):
        self.td = TensionDistribution(4)
    
    def test_bounds(self):
        """Should get bounds."""
        b = self.td.tension_bounds()
        self.assertEqual(b, (1.0, 100.0))
        print(f"  [PASS] Bounds: {b}")
    
    def test_feasible(self):
        """Should compute tensions."""
        dirs = [(0.0, 0.0, 1.0)] * 4
        t = self.td.feasible_tensions((0.0, 0.0, 10.0), dirs)
        self.assertEqual(len(t), 4)
        print(f"  [PASS] T: {t}")


class TestCableCompliance(unittest.TestCase):
    """Test compliance."""
    
    def setUp(self):
        self.cc = CableCompliance()
    
    def test_stiffness(self):
        """Should compute stiffness."""
        k = self.cc.cable_stiffness(200.0, 1.0, 1.0)
        self.assertEqual(k, 200000.0)
        print(f"  [PASS] K: {k:.0f}")
    
    def test_elongation(self):
        """Should compute elongation."""
        e = self.cc.elongation(100.0, 10000.0)
        self.assertEqual(e, 0.01)
        print(f"  [PASS] E: {e:.3f}")


class TestWorkspaceAnalysis(unittest.TestCase):
    """Test workspace."""
    
    def setUp(self):
        self.wa = WorkspaceAnalysis()
    
    def test_tension_workspace(self):
        """Should compute workspace."""
        pts = [CableAttachment(0.0, 0.0, 1.0), CableAttachment(1.0, 1.0, 1.0)]
        w = self.wa.tension_workspace(pts)
        self.assertEqual(w, 1.0)
        print(f"  [PASS] W: {w:.1f}")
    
    def test_dexterity(self):
        """Should compute dexterity."""
        d = self.wa.dexterity_index(6)
        self.assertEqual(d, 2.0)
        print(f"  [PASS] Dex: {d:.1f}")


class TestCableRouting(unittest.TestCase):
    """Test routing."""
    
    def setUp(self):
        self.cr = CableRouting()
    
    def test_length(self):
        """Should compute length."""
        a = CableAttachment(0.0, 0.0, 1.0)
        l = self.cr.cable_length(a, (0.0, 0.0, 0.0))
        self.assertEqual(l, 1.0)
        print(f"  [PASS] L: {l:.2f}")
    
    def test_direction(self):
        """Should compute direction."""
        a = CableAttachment(0.0, 0.0, 1.0)
        d = self.cr.cable_direction(a, (0.0, 0.0, 0.0))
        self.assertEqual(d, (0.0, 0.0, 1.0))
        print(f"  [PASS] Dir: {d}")


class TestCableDrivenManipulation(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.cdm = CableDrivenManipulation()
    
    def test_summary(self):
        """Should summarize."""
        s = self.cdm.cable_summary()
        self.assertIn("capabilities", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
