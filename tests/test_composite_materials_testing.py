"""
Unit tests for composite materials testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from composite_materials_testing import (PlyProperties, FiberVolumeFraction,
                                         LaminateStiffness,
                                         FailureCriteria,
                                         DelaminationAnalysis,
                                         CompositeMaterialsTesting)


class TestFiberVolumeFraction(unittest.TestCase):
    """Test fiber volume."""
    
    def setUp(self):
        self.fvf = FiberVolumeFraction()
    
    def test_rom(self):
        """Should compute ROM modulus."""
        E = self.fvf.rule_of_mixtures_E(230.0, 3.5, 0.6)
        self.assertGreater(E, 100.0)
        print(f"  [PASS] E1: {E:.1f} GPa")
    
    def test_inverse(self):
        """Should compute transverse modulus."""
        E = self.fvf.inverse_rule_E2(230.0, 3.5, 0.6)
        self.assertGreater(E, 0)
        print(f"  [PASS] E2: {E:.1f} GPa")
    
    def test_void(self):
        """Should compute void content."""
        v = self.fvf.void_content(1.6, 1.55)
        self.assertGreater(v, 0)
        print(f"  [PASS] Vv: {v:.3f}")


class TestLaminateStiffness(unittest.TestCase):
    """Test laminate."""
    
    def setUp(self):
        self.ls = LaminateStiffness()
    
    def test_transformed(self):
        """Should compute transformed stiffness."""
        ply = PlyProperties(150.0, 10.0, 5.0, 0.3, 0.25, 45.0)
        Q = self.ls.transformed_stiffness(ply)
        self.assertEqual(len(Q), 4)
        print(f"  [PASS] Q: {Q}")
    
    def test_A(self):
        """Should compute A matrix."""
        plies = [PlyProperties(150.0, 10.0, 5.0, 0.3, 0.25, 0.0),
                 PlyProperties(150.0, 10.0, 5.0, 0.3, 0.25, 90.0)]
        A = self.ls.A_matrix(plies)
        self.assertGreater(A, 0)
        print(f"  [PASS] A11: {A:.1f}")


class TestFailureCriteria(unittest.TestCase):
    """Test failure."""
    
    def setUp(self):
        self.fc = FailureCriteria()
    
    def test_tsai_wu(self):
        """Should compute Tsai-Wu."""
        f = self.fc.tsai_wu(500.0, 50.0, 30.0, 1500.0, 1200.0, 50.0, 200.0, 80.0)
        self.assertGreater(f, 0)
        print(f"  [PASS] TW: {f:.4f}")
    
    def test_max_stress(self):
        """Should compute max stress."""
        f = self.fc.max_stress(500.0, 30.0, 20.0, 1500.0, 1200.0, 50.0, 200.0, 80.0)
        self.assertGreater(f, 0)
        print(f"  [PASS] MS: {f:.4f}")


class TestDelaminationAnalysis(unittest.TestCase):
    """Test delam."""
    
    def setUp(self):
        self.da = DelaminationAnalysis()
    
    def test_gi(self):
        """Should compute G_I."""
        g = self.da.strain_energy_release_rate(100.0, 0.005, 0.001)
        self.assertGreater(g, 0)
        print(f"  [PASS] GI: {g:.1f} J/m2")
    
    def test_critical(self):
        """Should compute critical load."""
        f = self.da.critical_load(200.0, 0.01, 1e-6)
        self.assertGreater(f, 0)
        print(f"  [PASS] Fc: {f:.1f} N")


class TestCompositeMaterialsTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.cmt = CompositeMaterialsTesting()
    
    def test_summary(self):
        """Should summarize."""
        s = self.cmt.composite_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
