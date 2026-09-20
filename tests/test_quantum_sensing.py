"""
Unit tests for quantum sensing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_sensing import (QuantumProbe, PhaseEstimator,
                             QuantumMetrology,
                             QuantumEnhancedMeasurement,
                             CramerRaoBound,
                             QuantumSensing)


class TestPhaseEstimator(unittest.TestCase):
    """Test phase estimation."""
    
    def setUp(self):
        self.pe = PhaseEstimator()
    
    def test_estimate(self):
        """Should estimate phase."""
        m = [0, 1, 0]
        p = self.pe.estimate(m)
        self.assertGreaterEqual(p, 0)
        print(f"  [PASS] Est: {p:.4f}")
    
    def test_precision(self):
        """Should compute precision."""
        p = self.pe.precision(3)
        self.assertGreater(p, 0)
        print(f"  [PASS] Prec: {p:.4f}")


class TestQuantumMetrology(unittest.TestCase):
    """Test metrology."""
    
    def setUp(self):
        self.qm = QuantumMetrology()
    
    def test_shot_noise(self):
        """Should compute shot noise."""
        v = self.qm.shot_noise_limit(100)
        self.assertEqual(v, 0.01)
        print(f"  [PASS] SQL: {v}")
    
    def test_heisenberg(self):
        """Should compute Heisenberg."""
        v = self.qm.heisenberg_limit(100)
        self.assertEqual(v, 0.0001)
        print(f"  [PASS] HL: {v}")
    
    def test_probe(self):
        """Should create probe."""
        p = self.qm.optimal_probe(3)
        self.assertEqual(p.num_qubits, 3)
        print(f"  [PASS] Probe: {len(p.amplitudes)} amps")


class TestQuantumEnhancedMeasurement(unittest.TestCase):
    """Test enhanced."""
    
    def setUp(self):
        self.qem = QuantumEnhancedMeasurement()
    
    def test_squeezed(self):
        """Should compute squeezed precision."""
        v = self.qem.squeezed_state_precision(10.0, 100)
        self.assertLess(v, 0.01)
        print(f"  [PASS] Sqz: {v:.6f}")
    
    def test_entangled(self):
        """Should compute entangled precision."""
        v = self.qem.entangled_state_precision(100)
        self.assertEqual(v, 0.0001)
        print(f"  [PASS] Ent: {v}")


class TestCramerRaoBound(unittest.TestCase):
    """Test CRB."""
    
    def setUp(self):
        self.crb = CramerRaoBound()
    
    def test_classical(self):
        """Should compute classical bound."""
        b = self.crb.classical_bound(10.0)
        self.assertEqual(b, 0.1)
        print(f"  [PASS] CRB: {b}")
    
    def test_quantum(self):
        """Should compute quantum bound."""
        b = self.crb.quantum_bound(100.0)
        self.assertEqual(b, 0.01)
        print(f"  [PASS] QCRB: {b}")


class TestQuantumSensing(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qs = QuantumSensing()
    
    def test_add(self):
        """Should add measurement."""
        self.qs.add_measurement(1)
        self.assertEqual(len(self.qs.measurements), 1)
        print("  [PASS] Add")
    
    def test_estimate(self):
        """Should estimate."""
        self.qs.add_measurement(0)
        self.qs.add_measurement(1)
        p = self.qs.estimate_phase()
        self.assertGreaterEqual(p, 0)
        print(f"  [PASS] Est: {p:.4f}")
    
    def test_precision(self):
        """Should compute precision."""
        p = self.qs.sensing_precision(100)
        self.assertEqual(p, 0.01)
        print(f"  [PASS] Prec: {p}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qs.qs_summary()
        self.assertIn("measurements", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
