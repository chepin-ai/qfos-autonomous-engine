"""
Unit tests for quantum circuit module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_circuit import (QuantumCircuit, QuantumGate, QubitState,
                             H_GATE, X_GATE, Z_GATE, CNOT_GATE,
                             QuantumSimulator)


class TestQubitState(unittest.TestCase):
    """Test qubit state."""
    
    def test_initial_state(self):
        """Should create |0> state."""
        state = QubitState(amplitudes=[1.0, 0.0], num_qubits=1)
        self.assertEqual(state.probability(0), 1.0)
        print("  [PASS] |0>: prob=1.0")
    
    def test_probability_sum(self):
        """Probabilities should sum to 1."""
        state = QubitState(amplitudes=[1/math.sqrt(2), 1/math.sqrt(2)], num_qubits=1)
        total = sum(state.probability(i) for i in range(2))
        self.assertAlmostEqual(total, 1.0, places=5)
        print(f"  [PASS] Sum: {total:.3f}")
    
    def test_normalize(self):
        """Should normalize."""
        state = QubitState(amplitudes=[2.0, 0.0], num_qubits=1)
        state.normalize()
        self.assertAlmostEqual(state.probability(0), 1.0, places=5)
        print("  [PASS] Normalize: ok")


class TestQuantumGates(unittest.TestCase):
    """Test quantum gates."""
    
    def test_x_gate(self):
        """X should flip |0> to |1>."""
        state = QubitState(amplitudes=[1.0, 0.0], num_qubits=1)
        result = X_GATE.apply(state, [0])
        self.assertAlmostEqual(result.probability(1), 1.0, places=5)
        print("  [PASS] X|0> = |1>")
    
    def test_h_gate_superposition(self):
        """H should create superposition."""
        state = QubitState(amplitudes=[1.0, 0.0], num_qubits=1)
        result = H_GATE.apply(state, [0])
        self.assertAlmostEqual(result.probability(0), 0.5, places=5)
        self.assertAlmostEqual(result.probability(1), 0.5, places=5)
        print("  [PASS] H|0> = |+>")
    
    def test_z_gate_phase(self):
        """Z should flip phase of |1>."""
        state = QubitState(amplitudes=[0.0, 1.0], num_qubits=1)
        result = Z_GATE.apply(state, [0])
        self.assertAlmostEqual(result.probability(1), 1.0, places=5)
        self.assertAlmostEqual(result.amplitudes[1].real, -1.0, places=5)
        print("  [PASS] Z|1> = -|1>")
    
    def test_cnot_entangle(self):
        """CNOT should entangle qubits."""
        state = QubitState(amplitudes=[1.0, 0.0, 0.0, 0.0], num_qubits=2)
        # Apply H to qubit 0
        state = H_GATE.apply(state, [0])
        # Apply CNOT
        result = CNOT_GATE.apply(state, [0, 1])
        # Should be (|00> + |11>)/sqrt(2)
        self.assertAlmostEqual(result.probability(0), 0.5, places=5)
        self.assertAlmostEqual(result.probability(3), 0.5, places=5)
        print("  [PASS] CNOT: entangled")


class TestQuantumCircuit(unittest.TestCase):
    """Test quantum circuit."""
    
    def test_create(self):
        """Should create circuit."""
        qc = QuantumCircuit(2)
        self.assertEqual(qc.num_qubits, 2)
        print("  [PASS] Create: 2 qubits")
    
    def test_hadamard(self):
        """Should apply Hadamard."""
        qc = QuantumCircuit(1)
        qc.h(0)
        state = qc.execute()
        self.assertAlmostEqual(state.probability(0), 0.5, places=5)
        print("  [PASS] H: superposition")
    
    def test_x_gate(self):
        """Should apply X gate."""
        qc = QuantumCircuit(1)
        qc.x(0)
        state = qc.execute()
        self.assertAlmostEqual(state.probability(1), 1.0, places=5)
        print("  [PASS] X: flip")
    
    def test_bell_state(self):
        """Should create Bell state."""
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cnot(0, 1)
        state = qc.execute()
        self.assertAlmostEqual(state.probability(0), 0.5, places=5)
        self.assertAlmostEqual(state.probability(3), 0.5, places=5)
        print("  [PASS] Bell: (|00>+|11>)/sqrt(2)")
    
    def test_measure(self):
        """Should measure."""
        qc = QuantumCircuit(1)
        qc.h(0)
        counts = qc.measure(shots=1000)
        total = sum(counts.values())
        self.assertEqual(total, 1000)
        print(f"  [PASS] Measure: {total} shots")
    
    def test_circuit_depth(self):
        """Should track depth."""
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cnot(0, 1)
        self.assertEqual(qc.circuit_depth(), 2)
        print(f"  [PASS] Depth: {qc.circuit_depth()}")
    
    def test_summary(self):
        """Should provide summary."""
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cnot(0, 1)
        summary = qc.circuit_summary()
        self.assertEqual(summary["num_operations"], 2)
        print(f"  [PASS] Summary: {summary['num_operations']} ops")


class TestQuantumSimulator(unittest.TestCase):
    """Test quantum simulator."""
    
    def setUp(self):
        self.sim = QuantumSimulator()
    
    def test_create_circuit(self):
        """Should create named circuit."""
        qc = self.sim.create_circuit("test", 2)
        self.assertEqual(qc.num_qubits, 2)
        print("  [PASS] Create: test circuit")
    
    def test_run_circuit(self):
        """Should run circuit."""
        self.sim.create_circuit("bell", 2)
        self.sim.circuits["bell"].h(0)
        self.sim.circuits["bell"].cnot(0, 1)
        state = self.sim.run_circuit("bell")
        self.assertAlmostEqual(state.probability(0), 0.5, places=5)
        print("  [PASS] Run: Bell state")
    
    def test_bell_state_helper(self):
        """Should create Bell state."""
        qc = self.sim.bell_state()
        state = qc.execute()
        self.assertAlmostEqual(state.probability(0), 0.5, places=5)
        self.assertAlmostEqual(state.probability(3), 0.5, places=5)
        print("  [PASS] Helper: Bell state")
    
    def test_summary(self):
        """Should provide summary."""
        self.sim.create_circuit("c1", 2)
        summary = self.sim.simulator_summary()
        self.assertEqual(summary["circuits"], 1)
        print(f"  [PASS] Summary: {summary['circuits']} circuits")


if __name__ == '__main__':
    unittest.main(verbosity=2)
