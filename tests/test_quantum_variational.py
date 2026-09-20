"""
Unit tests for quantum variational module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_variational import (AnsatzType, VariationalParameter,
                                 PauliHamiltonian, VariationalAnsatz,
                                 ParameterOptimizer, VQE,
                                 QuantumVariational)


class TestPauliHamiltonian(unittest.TestCase):
    """Test Pauli Hamiltonian."""
    
    def test_expectation(self):
        """Should compute expectation."""
        H = PauliHamiltonian()
        H.add_term("Z", 1.0)
        e = H.expectation("0")
        self.assertAlmostEqual(e, 1.0)
        print(f"  [PASS] Exp: {e}")
    
    def test_negative(self):
        """Should compute negative expectation."""
        H = PauliHamiltonian()
        H.add_term("Z", 1.0)
        e = H.expectation("1")
        self.assertAlmostEqual(e, -1.0)
        print("  [PASS] Neg")
    
    def test_num_qubits(self):
        """Should return qubit count."""
        H = PauliHamiltonian()
        H.add_term("ZI", 0.5)
        self.assertEqual(H.num_qubits(), 2)
        print("  [PASS] N=2")


class TestVariationalAnsatz(unittest.TestCase):
    """Test variational ansatz."""
    
    def test_ry_params(self):
        """Should have correct parameter count."""
        ansatz = VariationalAnsatz(2, AnsatzType.RY)
        self.assertEqual(ansatz.num_parameters(), 2)
        print("  [PASS] RY params")
    
    def test_ryrz_params(self):
        """Should have 2N params."""
        ansatz = VariationalAnsatz(2, AnsatzType.RYRZ)
        self.assertEqual(ansatz.num_parameters(), 4)
        print("  [PASS] RYRZ params")
    
    def test_statevector_norm(self):
        """Should have unit norm."""
        ansatz = VariationalAnsatz(2, AnsatzType.RY)
        ansatz.set_parameters([0.0, 0.0])
        state = ansatz.statevector()
        norm = sum(abs(a)**2 for a in state)
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] Norm: {norm:.5f}")
    
    def test_statevector_rotation(self):
        """Should rotate state."""
        ansatz = VariationalAnsatz(1, AnsatzType.RY)
        ansatz.set_parameters([math.pi / 2])
        state = ansatz.statevector()
        # |0> rotated by pi/2 around Y -> 1/sqrt(2)(|0> + |1>)
        self.assertAlmostEqual(abs(state[0]), 1.0 / math.sqrt(2), places=3)
        print(f"  [PASS] Rotate: |a0|={abs(state[0]):.3f}")


class TestParameterOptimizer(unittest.TestCase):
    """Test optimizer."""
    
    def test_gradient_descent(self):
        """Should minimize simple function."""
        opt = ParameterOptimizer(learning_rate=0.1, max_iterations=50)
        
        def f(p):
            return (p[0] - 2.0)**2
        
        params, energy = opt.gradient_descent(f, [0.0])
        self.assertLess(abs(params[0] - 2.0), 0.5)
        print(f"  [PASS] GD: p={params[0]:.3f}, E={energy:.3f}")
    
    def test_nelder_mead(self):
        """Should minimize via random walk."""
        opt = ParameterOptimizer(learning_rate=0.5, max_iterations=100)
        
        def f(p):
            return p[0]**2
        
        params, energy = opt.nelder_mead(f, [1.0])
        self.assertLess(energy, 1.0)
        print(f"  [PASS] NM: E={energy:.4f}")


class TestVQE(unittest.TestCase):
    """Test VQE."""
    
    def setUp(self):
        self.H = PauliHamiltonian()
        self.H.add_term("Z", -1.0)
        self.ansatz = VariationalAnsatz(1, AnsatzType.RY)
        self.vqe = VQE(self.H, self.ansatz)
    
    def test_energy(self):
        """Should compute energy."""
        e = self.vqe.energy([0.0])
        self.assertAlmostEqual(e, -1.0, places=2)
        print(f"  [PASS] Energy: {e:.3f}")
    
    def test_run(self):
        """Should run VQE."""
        result = self.vqe.run(initial_params=[0.5], method="gradient")
        self.assertIn("ground_state_energy", result)
        print(f"  [PASS] Run: E={result['ground_state_energy']:.3f}")
    
    def test_ground_state(self):
        """Should return ground state."""
        self.vqe.run(initial_params=[0.0])
        state = self.vqe.ground_state()
        self.assertEqual(len(state), 2)
        print(f"  [PASS] State: {len(state)} amplitudes")


class TestQuantumVariational(unittest.TestCase):
    """Test unified quantum variational."""
    
    def test_setup(self):
        """Should setup VQE."""
        qv = QuantumVariational()
        H = PauliHamiltonian()
        H.add_term("Z", -1.0)
        qv.setup(H, AnsatzType.RY)
        self.assertIsNotNone(qv.vqe)
        print("  [PASS] Setup")
    
    def test_solve(self):
        """Should solve VQE."""
        qv = QuantumVariational()
        H = PauliHamiltonian()
        H.add_term("Z", -1.0)
        qv.setup(H, AnsatzType.RY)
        result = qv.solve()
        self.assertLess(result["ground_state_energy"], 0.0)
        print(f"  [PASS] Solve: E={result['ground_state_energy']:.3f}")
    
    def test_summary(self):
        """Should provide summary."""
        qv = QuantumVariational()
        H = PauliHamiltonian()
        H.add_term("Z", -1.0)
        qv.setup(H, AnsatzType.RY)
        qv.solve()
        s = qv.variational_summary()
        self.assertIn("best_energy", s)
        print(f"  [PASS] Summary: best={s['best_energy']:.3f}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
