"""
Unit tests for quantum phase estimation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_phase_estimation import (PhaseEstimate, InverseQFT,
                                      ControlledUnitary,
                                      PhaseEstimator,
                                      EigenvalueEstimator,
                                      QuantumPhaseEstimation)


class TestInverseQFT(unittest.TestCase):
    """Test inverse QFT."""
    
    def setUp(self):
        self.iqft = InverseQFT(3)
    
    def test_apply(self):
        """Should apply."""
        state = [1.0] * 8
        out = self.iqft.apply(state)
        self.assertEqual(len(out), 8)
        print("  [PASS] IQFT")
    
    def test_binary_to_phase(self):
        """Should convert."""
        p = self.iqft.binary_to_phase(4)
        self.assertEqual(p, 0.5)
        print(f"  [PASS] Bin: {p}")


class TestControlledUnitary(unittest.TestCase):
    """Test controlled unitary."""
    
    def setUp(self):
        u = [[0.0, 1.0], [1.0, 0.0]]  # X gate
        self.cu = ControlledUnitary(u)
    
    def test_power(self):
        """Should compute U^k."""
        uk = self.cu.power(2)
        self.assertEqual(uk[0][0], 1.0)
        print("  [PASS] Pow")
    
    def test_power_zero(self):
        """Should compute U^0."""
        u0 = self.cu.power(0)
        self.assertEqual(u0[0][0], 1.0)
        print("  [PASS] Pow0")


class TestPhaseEstimator(unittest.TestCase):
    """Test phase estimator."""
    
    def setUp(self):
        self.pe = PhaseEstimator(3)
    
    def test_estimate(self):
        """Should estimate."""
        est = self.pe.estimate_phase(0.25)
        self.assertIsNotNone(est.phase)
        print(f"  [PASS] Est: {est.phase:.3f}")
    
    def test_eigenvalue(self):
        """Should convert to eigenvalue."""
        ev = self.pe.estimate_eigenvalue(0.25)
        self.assertIsInstance(ev, complex)
        print(f"  [PASS] EV: {ev}")


class TestEigenvalueEstimator(unittest.TestCase):
    """Test eigenvalue estimator."""
    
    def setUp(self):
        self.ee = EigenvalueEstimator(4)
    
    def test_estimate(self):
        """Should estimate."""
        h = [[1.0, 0.0], [0.0, 2.0]]
        e = self.ee.estimate(h)
        self.assertEqual(e, 1.5)
        print(f"  [PASS] Eig: {e}")
    
    def test_ground(self):
        """Should estimate ground state."""
        h = [[1.0, 0.0], [0.0, -0.5]]
        e = self.ee.ground_state_energy(h)
        self.assertEqual(e, -0.5)
        print(f"  [PASS] GS: {e}")


class TestQuantumPhaseEstimation(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qpe = QuantumPhaseEstimation(4)
    
    def test_estimate(self):
        """Should estimate."""
        est = self.qpe.estimate(0.125)
        self.assertIsNotNone(est)
        print(f"  [PASS] QPE: {est.phase:.3f}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qpe.qpe_summary()
        self.assertIn("precision_bits", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
