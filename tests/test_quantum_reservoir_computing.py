"""
Unit tests for quantum reservoir computing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_reservoir_computing import (ReservoirState, QuantumReservoirDynamics,
                                         TemporalProcessing,
                                         ReadoutTraining,
                                         MemoryCapacity,
                                         QuantumReservoirComputing)


class TestQuantumReservoirDynamics(unittest.TestCase):
    """Test dynamics."""
    
    def setUp(self):
        self.qrd = QuantumReservoirDynamics(5)
    
    def test_evolve(self):
        """Should evolve state."""
        s = self.qrd.evolve([0.0] * 5, 1.0)
        self.assertEqual(len(s), 5)
        print(f"  [PASS] State: {len(s)} qubits")
    
    def test_spectral(self):
        """Should compute radius."""
        m = [[0.1, 0.2], [0.3, 0.4]]
        r = self.qrd.reservoir_spectral_radius(m)
        self.assertGreater(r, 0)
        print(f"  [PASS] SR: {r:.2f}")


class TestTemporalProcessing(unittest.TestCase):
    """Test temporal."""
    
    def setUp(self):
        self.tp = TemporalProcessing()
    
    def test_memory(self):
        """Should compute memory."""
        inputs = [1.0, -1.0, 1.0, -1.0]
        states = [[0.5], [-0.5], [0.5], [-0.5]]
        m = self.tp.short_term_memory(inputs, states, 1)
        self.assertGreaterEqual(m, 0)
        print(f"  [PASS] MC: {m:.4f}")
    
    def test_nonlinear(self):
        """Should compute capacity."""
        c = self.tp.nonlinear_capacity([1.0, 2.0], [[0.1], [0.2]])
        self.assertGreaterEqual(c, 0)
        print(f"  [PASS] NLC: {c:.4f}")


class TestReadoutTraining(unittest.TestCase):
    """Test readout."""
    
    def setUp(self):
        self.rt = ReadoutTraining()
    
    def test_regression(self):
        """Should compute weights."""
        w = self.rt.linear_regression([[1.0], [2.0]], [1.0, 2.0])
        self.assertEqual(len(w), 1)
        print(f"  [PASS] W: {w}")
    
    def test_predict(self):
        """Should predict."""
        p = self.rt.predict([1.0, 2.0], [0.5, 0.5])
        self.assertEqual(p, 1.5)
        print(f"  [PASS] Pred: {p:.2f}")


class TestMemoryCapacity(unittest.TestCase):
    """Test memory."""
    
    def setUp(self):
        self.mc = MemoryCapacity()
    
    def test_total(self):
        """Should sum capacities."""
        t = self.mc.total_memory_capacity([0.5, 0.3, 0.1])
        self.assertEqual(t, 0.9)
        print(f"  [PASS] Tot: {t:.2f}")
    
    def test_critical(self):
        """Should find critical delay."""
        d = self.mc.critical_delay([0.5, 0.3, 0.05])
        self.assertEqual(d, 2)
        print(f"  [PASS] Dcrit: {d}")


class TestQuantumReservoirComputing(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qrc = QuantumReservoirComputing()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qrc.reservoir_summary()
        self.assertIn("components", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
