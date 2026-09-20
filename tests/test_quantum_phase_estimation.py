"""
Unit tests for quantum phase estimation module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_phase_estimation import (PhaseGate, QuantumFourierTransform,
                                      PhaseEstimator, EigenvalueEstimator,
                                      ControlledUnitary, QuantumPhaseEstimation)


class TestPhaseGate(unittest.TestCase):
    """Test phase gate."""
    
    def test_controlled_phase(self):
        """Should compute phase."""
        p = PhaseGate.controlled_phase(1)
        self.assertAlmostEqual(abs(p), 1.0)
        print(f"  [PASS] Phase: {p}")
    
    def test_phase_k2(self):
        """Should have phase -1 for k=1."""
        p = PhaseGate.controlled_phase(1)
        # e^(2*pi*i / 2) = e^(pi*i) = -1
        self.assertAlmostEqual(p.real, -1.0)
        self.assertAlmostEqual(p.imag, 0.0, places=5)
        print("  [PASS] Phase k=1")


class TestQFT(unittest.TestCase):
    """Test QFT."""
    
    def setUp(self):
        self.qft = QuantumFourierTransform(2)
    
    def test_identity(self):
        """Should be invertible."""
        state = [1.0, 0.0, 0.0, 0.0]
        fwd = self.qft.apply(state)
        inv = self.qft.inverse(fwd)
        self.assertAlmostEqual(abs(inv[0]), 1.0, places=5)
        print("  [PASS] Invertible")
    
    def test_unitary(self):
        """Should preserve norm."""
        state = [0.5, 0.5, 0.5, 0.5]
        out = self.qft.apply(state)
        norm = sum(abs(a)**2 for a in out)
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] Norm: {norm:.4f}")


class TestPhaseEstimator(unittest.TestCase):
    """Test phase estimator."""
    
    def setUp(self):
        self.pe = PhaseEstimator(num_precision_qubits=4)
    
    def test_estimate_exact(self):
        """Should estimate exact binary fraction."""
        phase = 0.25  # 1/4 = 0.01 binary
        est = self.pe.estimate(phase)
        error = abs(est - phase)
        self.assertLess(error, 0.1)
        print(f"  [PASS] Est: {est:.4f}, err={error:.4f}")
    
    def test_precision(self):
        """Should have correct precision."""
        p = self.pe.precision()
        self.assertAlmostEqual(p, 1.0 / 16.0)
        print(f"  [PASS] Prec: {p:.4f}")
    
    def test_success(self):
        """Should succeed for exact phase."""
        phase = 0.125  # 1/8
        success = self.pe.success_probability(phase)
        self.assertEqual(success, 1.0)
        print("  [PASS] Success")


class TestEigenvalueEstimator(unittest.TestCase):
    """Test eigenvalue estimator."""
    
    def setUp(self):
        self.ee = EigenvalueEstimator(3)
    
    def test_estimate(self):
        """Should estimate eigenvalue."""
        val = self.ee.estimate_eigenvalue(0.25, 4.0)
        self.assertGreater(val, 0)
        print(f"  [PASS] Eigen: {val:.4f}")
    
    def test_energy(self):
        """Should estimate energy."""
        e = self.ee.energy_estimate(0.25, 1.0)
        self.assertNotEqual(e, 0.0)
        print(f"  [PASS] Energy: {e:.4f}")


class TestControlledUnitary(unittest.TestCase):
    """Test controlled unitary."""
    
    def setUp(self):
        self.cu = ControlledUnitary()
    
    def test_apply(self):
        """Should apply unitary."""
        state = [1.0, 0.0]
        out = self.cu.apply_power(1, state)
        self.assertEqual(len(out), 2)
        print("  [PASS] Apply")
    
    def test_phase(self):
        """Should extract phase."""
        phi = self.cu.phase_from_unitary()
        self.assertGreaterEqual(phi, 0.0)
        self.assertLess(phi, 1.0)
        print(f"  [PASS] Phase: {phi:.4f}")


class TestQuantumPhaseEstimation(unittest.TestCase):
    """Test unified QPE."""
    
    def setUp(self):
        self.qpe = QuantumPhaseEstimation(4)
    
    def test_estimate(self):
        """Should estimate."""
        result = self.qpe.estimate(0.25)
        self.assertIn("estimated_phase", result)
        print(f"  [PASS] Est: {result['estimated_phase']:.4f}")
    
    def test_energy(self):
        """Should estimate energy."""
        e = self.qpe.estimate_energy(0.125, 1.0)
        self.assertNotEqual(e, 0.0)
        print(f"  [PASS] Energy: {e:.4f}")
    
    def test_summary(self):
        """Should provide summary."""
        self.qpe.estimate(0.25)
        s = self.qpe.qpe_summary()
        self.assertIn("runs", s)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
