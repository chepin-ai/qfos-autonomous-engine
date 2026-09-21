"""
Unit tests for quantum benchmarking advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_benchmarking_advanced import (BenchmarkResult, RandomizedBenchmarking,
                                           QuantumVolume,
                                           CrossEntropyBenchmarking,
                                           FidelityEstimation,
                                           QuantumBenchmarkingAdvanced)


class TestRandomizedBenchmarking(unittest.TestCase):
    """Test RB."""
    
    def setUp(self):
        self.rb = RandomizedBenchmarking()
    
    def test_decay(self):
        """Should compute decay."""
        p = self.rb.decay_model(10, 0.99)
        self.assertGreater(p, 0)
        print(f"  [PASS] P: {p:.4f}")
    
    def test_fidelity(self):
        """Should compute fidelity."""
        f = self.rb.fidelity_from_decay(0.98)
        self.assertGreater(f, 0)
        print(f"  [PASS] F: {f:.4f}")
    
    def test_error(self):
        """Should compute error."""
        e = self.rb.error_per_gate(0.99)
        self.assertAlmostEqual(e, 0.01, delta=1e-10)
        print(f"  [PASS] E: {e:.3f}")


class TestQuantumVolume(unittest.TestCase):
    """Test QV."""
    
    def setUp(self):
        self.qv = QuantumVolume()
    
    def test_volume(self):
        """Should compute QV."""
        v = self.qv.quantum_volume(5, 5)
        self.assertEqual(v, 32)
        print(f"  [PASS] QV: {v}")
    
    def test_effective(self):
        """Should estimate effective qubits."""
        n = self.qv.effective_qubits(0.01)
        self.assertGreater(n, 0)
        print(f"  [PASS] N: {n}")


class TestCrossEntropyBenchmarking(unittest.TestCase):
    """Test XEB."""
    
    def setUp(self):
        self.xeb = CrossEntropyBenchmarking()
    
    def test_ce(self):
        """Should compute cross-entropy."""
        c = self.xeb.cross_entropy([0.5, 0.5], [0.5, 0.5])
        self.assertGreater(c, 0)
        print(f"  [PASS] CE: {c:.3f}")
    
    def test_xeb_fidelity(self):
        """Should compute XEB fidelity."""
        f = self.xeb.xeb_fidelity([0.5, 0.5], [0.5, 0.5])
        self.assertIsInstance(f, float)
        print(f"  [PASS] XEB: {f:.4f}")


class TestFidelityEstimation(unittest.TestCase):
    """Test fidelity."""
    
    def setUp(self):
        self.fe = FidelityEstimation()
    
    def test_state(self):
        """Should compute state fidelity."""
        s1 = [1.0, 0.0]
        s2 = [1.0, 0.0]
        f = self.fe.state_fidelity(s1, s2)
        self.assertEqual(f, 1.0)
        print(f"  [PASS] Fst: {f:.2f}")
    
    def test_process(self):
        """Should compute process fidelity."""
        chi = [[1.0, 0.0], [0.0, 0.0]]
        f = self.fe.process_fidelity(chi, chi)
        self.assertEqual(f, 1.0)
        print(f"  [PASS] Fpr: {f:.2f}")


class TestQuantumBenchmarkingAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qba = QuantumBenchmarkingAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qba.benchmarking_summary()
        self.assertIn("benchmarks", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
