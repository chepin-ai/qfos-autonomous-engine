"""
Unit tests for fracture mechanics module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fracture_mechanics import (CrackGrowth, StressIntensityFactor,
                                ParisLaw, JIntegral,
                                CTODCalculator,
                                FractureMechanics)


class TestStressIntensityFactor(unittest.TestCase):
    """Test SIF."""
    
    def setUp(self):
        self.sif = StressIntensityFactor()
    
    def test_mode_I_infinite(self):
        """Should compute infinite plate SIF."""
        K = self.sif.mode_I_infinite_plate(100.0, 10.0)
        self.assertGreater(K, 0)
        print(f"  [PASS] KI: {K:.2f} MPa*sqrt(m)")
    
    def test_mode_I_finite(self):
        """Should compute finite width SIF."""
        K = self.sif.mode_I_finite_width(100.0, 10.0, 200.0)
        self.assertGreater(K, 0)
        print(f"  [PASS] KIf: {K:.2f} MPa*sqrt(m)")
    
    def test_mode_I_edge(self):
        """Should compute edge crack SIF."""
        K = self.sif.mode_I_edge_crack(100.0, 10.0)
        self.assertGreater(K, 0)
        print(f"  [PASS] KIe: {K:.2f} MPa*sqrt(m)")
    
    def test_critical_stress(self):
        """Should compute critical stress."""
        sc = self.sif.critical_stress(30.0, 10.0)
        self.assertGreater(sc, 0)
        print(f"  [PASS] Sc: {sc:.2f} MPa")


class TestParisLaw(unittest.TestCase):
    """Test Paris law."""
    
    def setUp(self):
        self.paris = ParisLaw(1.0e-12, 3.0)
    
    def test_growth_rate(self):
        """Should compute growth rate."""
        dadn = self.paris.crack_growth_rate(10.0)
        self.assertGreater(dadn, 0)
        print(f"  [PASS] da/dN: {dadn:.6f} mm/cycle")
    
    def test_cycles_to_failure(self):
        """Should estimate cycles."""
        N = self.paris.cycles_to_failure(1.0, 50.0, 100.0)
        self.assertGreater(N, 0)
        print(f"  [PASS] Nf: {N} cycles")
    
    def test_simulate_growth(self):
        """Should simulate growth."""
        hist = self.paris.simulate_growth(1.0, 1000, 100.0)
        self.assertGreater(len(hist), 0)
        print(f"  [PASS] Hist: {len(hist)} points")


class TestJIntegral(unittest.TestCase):
    """Test J-integral."""
    
    def setUp(self):
        self.j = JIntegral()
    
    def test_elastic(self):
        """Should compute elastic J."""
        Je = self.j.elastic_component(30.0, 200.0)
        self.assertGreater(Je, 0)
        print(f"  [PASS] Je: {Je:.4f} kJ/m2")
    
    def test_plastic(self):
        """Should compute plastic J."""
        Jp = self.j.plastic_component(500.0, 0.1)
        self.assertGreater(Jp, 0)
        print(f"  [PASS] Jp: {Jp:.4f} kJ/m2")
    
    def test_total(self):
        """Should compute total J."""
        Jt = self.j.total_J(30.0, 200.0, 500.0, 0.1)
        self.assertGreater(Jt, 0)
        print(f"  [PASS] Jt: {Jt:.4f} kJ/m2")


class TestCTODCalculator(unittest.TestCase):
    """Test CTOD."""
    
    def setUp(self):
        self.ctod = CTODCalculator()
    
    def test_from_K(self):
        """Should compute CTOD from K."""
        d = self.ctod.from_K(30.0, 500.0, 200.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] CTOD: {d:.4f} mm")
    
    def test_from_J(self):
        """Should compute CTOD from J."""
        d = self.ctod.from_J(10.0, 500.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] CTODj: {d:.4f} mm")


class TestFractureMechanics(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.fm = FractureMechanics()
    
    def test_summary(self):
        """Should summarize."""
        s = self.fm.fracture_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
