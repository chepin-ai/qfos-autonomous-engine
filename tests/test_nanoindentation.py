"""
Unit tests for nanoindentation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nanoindentation import (LoadDisplacementData, OliverPharrAnalysis,
                             TipCalibration,
                             ModulusExtraction,
                             CreepCorrection,
                             Nanoindentation)


class TestOliverPharrAnalysis(unittest.TestCase):
    """Test OP."""
    
    def setUp(self):
        self.op = OliverPharrAnalysis()
    
    def test_stiffness(self):
        """Should compute stiffness."""
        data = [LoadDisplacementData(10.0, 100.0), LoadDisplacementData(5.0, 80.0)]
        s = self.op.contact_stiffness(data)
        self.assertEqual(s, 0.25)
        print(f"  [PASS] S: {s:.3f}")
    
    def test_depth(self):
        """Should compute hc."""
        hc = self.op.contact_depth(100.0, 10.0, 0.25)
        self.assertEqual(hc, 70.0)
        print(f"  [PASS] hc: {hc:.1f}")
    
    def test_area(self):
        """Should compute area."""
        a = self.op.contact_area(10.0)
        self.assertEqual(a, 2450.0)
        print(f"  [PASS] A: {a:.1f}")
    
    def test_hardness(self):
        """Should compute H."""
        h = self.op.hardness(10.0, 100.0)
        self.assertEqual(h, 0.1)
        print(f"  [PASS] H: {h:.3f}")
    
    def test_modulus(self):
        """Should compute Er."""
        e = self.op.reduced_modulus(1.0, 100.0)
        self.assertGreater(e, 0)
        print(f"  [PASS] Er: {e:.4f}")


class TestTipCalibration(unittest.TestCase):
    """Test tip."""
    
    def setUp(self):
        self.tc = TipCalibration()
    
    def test_area(self):
        """Should compute area."""
        a = self.tc.area_function(10.0)
        self.assertEqual(a, 2450.0)
        print(f"  [PASS] A: {a:.1f}")
    
    def test_compliance(self):
        """Should compute frame compliance."""
        c = self.tc.frame_compliance(0.01, 0.005)
        self.assertEqual(c, 0.005)
        print(f"  [PASS] Cf: {c:.4f}")


class TestModulusExtraction(unittest.TestCase):
    """Test modulus."""
    
    def setUp(self):
        self.me = ModulusExtraction()
    
    def test_youngs(self):
        """Should compute E."""
        e = self.me.youngs_modulus(100.0)
        self.assertGreater(e, 0)
        print(f"  [PASS] E: {e:.2f}")


class TestCreepCorrection(unittest.TestCase):
    """Test creep."""
    
    def setUp(self):
        self.cc = CreepCorrection()
    
    def test_displacement(self):
        """Should compute creep."""
        d = self.cc.creep_displacement(10.0)
        self.assertEqual(d, 10.0)
        print(f"  [PASS] Dc: {d:.1f}")


class TestNanoindentation(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ni = Nanoindentation()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ni.nanoindentation_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
