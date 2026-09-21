"""
Unit tests for rheology module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rheology import (ShearPoint, NewtonianFluid,
                      PowerLawFluid,
                      MaxwellModel,
                      KelvinVoigtModel,
                      Rheology)


class TestNewtonianFluid(unittest.TestCase):
    """Test Newtonian."""
    
    def setUp(self):
        self.fluid = NewtonianFluid(0.001)  # Water-like
    
    def test_shear_stress(self):
        """Should compute stress."""
        tau = self.fluid.shear_stress(1000.0)
        self.assertAlmostEqual(tau, 1.0, delta=0.01)
        print(f"  [PASS] Tau: {tau:.3f} Pa")
    
    def test_reynolds(self):
        """Should compute Re."""
        re = self.fluid.reynolds_number(1000.0, 1.0, 0.1)
        self.assertGreater(re, 0)
        print(f"  [PASS] Re: {re:.0f}")


class TestPowerLawFluid(unittest.TestCase):
    """Test power law."""
    
    def setUp(self):
        self.fluid = PowerLawFluid(0.5, 0.8)
    
    def test_shear_stress(self):
        """Should compute stress."""
        tau = self.fluid.shear_stress(10.0)
        self.assertGreater(tau, 0)
        print(f"  [PASS] Tau: {tau:.3f} Pa")
    
    def test_apparent_viscosity(self):
        """Should compute viscosity."""
        eta = self.fluid.apparent_viscosity(10.0)
        self.assertGreater(eta, 0)
        print(f"  [PASS] Eta: {eta:.4f} Pa.s")


class TestMaxwellModel(unittest.TestCase):
    """Test Maxwell."""
    
    def setUp(self):
        self.m = MaxwellModel(1e6, 1e3)
    
    def test_relaxation_time(self):
        """Should compute tau."""
        tau = self.m.relaxation_time()
        self.assertAlmostEqual(tau, 0.001, delta=1e-6)
        print(f"  [PASS] Tau: {tau:.4f} s")
    
    def test_stress_relaxation(self):
        """Should relax."""
        s = self.m.stress_relaxation(100.0, 0.001)
        self.assertLess(s, 100.0)
        self.assertGreater(s, 0)
        print(f"  [PASS] SR: {s:.2f} Pa")
    
    def test_creep_compliance(self):
        """Should compute compliance."""
        j = self.m.creep_compliance(0.01)
        self.assertGreater(j, 0)
        print(f"  [PASS] J: {j:.2e} 1/Pa")


class TestKelvinVoigtModel(unittest.TestCase):
    """Test KV."""
    
    def setUp(self):
        self.kv = KelvinVoigtModel(1e6, 1e3)
    
    def test_retardation_time(self):
        """Should compute tau."""
        tau = self.kv.retardation_time()
        self.assertAlmostEqual(tau, 0.001, delta=1e-6)
        print(f"  [PASS] Tau: {tau:.4f} s")
    
    def test_creep_strain(self):
        """Should compute strain."""
        e = self.kv.creep_strain(1e6, 0.01)
        self.assertGreater(e, 0)
        print(f"  [PASS] Str: {e:.4f}")


class TestRheology(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.r = Rheology()
    
    def test_summary(self):
        """Should summarize."""
        s = self.r.rheology_summary()
        self.assertIn("models", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
