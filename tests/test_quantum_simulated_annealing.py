"""
Unit tests for quantum simulated annealing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_simulated_annealing import (ClassicalAnnealing, QuantumTunneling,
                                         QuantumAnnealer, ReplicaExchange,
                                         QuantumSimulatedAnnealing)


def simple_hamiltonian(state):
    """Simple test Hamiltonian: minimize number of 1s."""
    return sum(state)


class TestClassicalAnnealing(unittest.TestCase):
    """Test classical annealing."""
    
    def setUp(self):
        self.ca = ClassicalAnnealing()
    
    def test_acceptance(self):
        """Should accept better."""
        self.assertEqual(self.ca.acceptance_probability(-1.0), 1.0)
        print("  [PASS] Accept better")
    
    def test_reject_worse(self):
        """Should sometimes accept worse."""
        prob = self.ca.acceptance_probability(10.0)
        self.assertGreater(prob, 0)
        self.assertLess(prob, 1.0)
        print(f"  [PASS] Accept worse: {prob:.4f}")
    
    def test_cool(self):
        """Should reduce temperature."""
        old = self.ca.temp
        self.ca.cool()
        self.assertLess(self.ca.temp, old)
        print(f"  [PASS] Cool: {old:.2f}->{self.ca.temp:.2f}")


class TestQuantumTunneling(unittest.TestCase):
    """Test quantum tunneling."""
    
    def setUp(self):
        self.qt = QuantumTunneling()
    
    def test_tunnel_prob(self):
        """Should compute probability."""
        p = self.qt.tunnel_probability(1.0, 1.0)
        self.assertGreater(p, 0)
        self.assertLess(p, 1.0)
        print(f"  [PASS] Tunnel: {p:.4f}")
    
    def test_zero_barrier(self):
        """Should tunnel through zero barrier."""
        self.assertEqual(self.qt.tunnel_probability(0.0, 1.0), 1.0)
        print("  [PASS] Zero barrier")


class TestQuantumAnnealer(unittest.TestCase):
    """Test quantum annealer."""
    
    def setUp(self):
        self.qa = QuantumAnnealer(num_qubits=4)
    
    def test_energy(self):
        """Should evaluate energy."""
        E = self.qa.energy([1, 0, 1, 0], simple_hamiltonian)
        self.assertEqual(E, 2)
        print(f"  [PASS] Energy: {E}")
    
    def test_flip(self):
        """Should flip spin."""
        s = self.qa.flip_spin([0, 0, 0, 0], 1)
        self.assertEqual(s[1], 1)
        print("  [PASS] Flip")
    
    def test_anneal(self):
        """Should anneal."""
        self.qa.anneal(simple_hamiltonian, 100)
        self.assertGreater(len(self.qa.energy_history), 0)
        print(f"  [PASS] Anneal: best={self.qa.best_energy()}")


class TestReplicaExchange(unittest.TestCase):
    """Test replica exchange."""
    
    def setUp(self):
        self.re = ReplicaExchange(num_replicas=3)
    
    def test_init(self):
        """Should init replicas."""
        self.re.init_replicas(4)
        self.assertEqual(len(self.re.replicas), 3)
        print("  [PASS] Init")
    
    def test_exchange_prob(self):
        """Should compute exchange prob."""
        p = self.re.exchange_probability(0.0, 1.0, 1.0, 2.0)
        self.assertGreaterEqual(p, 0)
        self.assertLessEqual(p, 1.0)
        print(f"  [PASS] ExProb: {p:.4f}")


class TestQuantumSimulatedAnnealing(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qsa = QuantumSimulatedAnnealing()
    
    def test_classical(self):
        """Should solve classically."""
        r = self.qsa.solve(simple_hamiltonian, 4, "classical")
        self.assertEqual(r["method"], "classical")
        print(f"  [PASS] Classical: E={r['energy']}")
    
    def test_quantum(self):
        """Should solve quantum."""
        r = self.qsa.solve(simple_hamiltonian, 4, "quantum")
        self.assertEqual(r["method"], "quantum")
        print(f"  [PASS] Quantum: E={r['energy']}")
    
    def test_replica(self):
        """Should solve with replica."""
        r = self.qsa.solve(simple_hamiltonian, 4, "replica")
        self.assertEqual(r["method"], "replica")
        print(f"  [PASS] Replica: E={r['energy']}")
    
    def test_summary(self):
        """Should summarize."""
        self.qsa.solve(simple_hamiltonian, 4, "quantum")
        s = self.qsa.annealing_summary()
        self.assertEqual(s["runs"], 1)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
