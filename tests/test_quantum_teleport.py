"""
Unit tests for quantum teleportation module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_teleport import (PauliOp, QubitState, BellState,
                              TeleportationProtocol, EntanglementMetrics,
                              FidelityEstimator, QuantumTeleport)


class TestQubitState(unittest.TestCase):
    """Test qubit state."""
    
    def test_normalize(self):
        """Should normalize."""
        q = QubitState(3.0, 4.0)
        q.normalize()
        norm = abs(q.alpha)**2 + abs(q.beta)**2
        self.assertAlmostEqual(norm, 1.0)
        print(f"  [PASS] Norm: {norm:.4f}")
    
    def test_fidelity_same(self):
        """Should have fidelity 1 for same state."""
        q1 = QubitState(1.0 / math.sqrt(2), 1.0 / math.sqrt(2))
        q2 = QubitState(1.0 / math.sqrt(2), 1.0 / math.sqrt(2))
        f = q1.fidelity(q2)
        self.assertAlmostEqual(f, 1.0)
        print(f"  [PASS] Fidelity: {f:.4f}")
    
    def test_fidelity_orthogonal(self):
        """Should have fidelity 0 for orthogonal."""
        q1 = QubitState(1.0, 0.0)
        q2 = QubitState(0.0, 1.0)
        f = q1.fidelity(q2)
        self.assertAlmostEqual(f, 0.0)
        print(f"  [PASS] Orthogonal: {f:.4f}")
    
    def test_apply_x(self):
        """Should apply X."""
        q = QubitState(1.0, 0.0)
        qx = q.apply_pauli(PauliOp.X)
        self.assertAlmostEqual(abs(qx.alpha), 0.0)
        self.assertAlmostEqual(abs(qx.beta), 1.0)
        print("  [PASS] X gate")
    
    def test_apply_z(self):
        """Should apply Z."""
        q = QubitState(0.0, 1.0)
        qz = q.apply_pauli(PauliOp.Z)
        self.assertAlmostEqual(qz.beta, -1.0)
        print("  [PASS] Z gate")


class TestBellState(unittest.TestCase):
    """Test Bell state."""
    
    def test_phi_plus(self):
        """Should create |Phi+>."""
        c00, c01, c10, c11 = BellState.phi_plus()
        self.assertAlmostEqual(abs(c00), 1.0 / math.sqrt(2))
        self.assertAlmostEqual(abs(c11), 1.0 / math.sqrt(2))
        self.assertAlmostEqual(abs(c01), 0.0)
        print("  [PASS] Phi+")
    
    def test_phi_minus(self):
        """Should create |Phi->."""
        c00, c01, c10, c11 = BellState.phi_minus()
        self.assertAlmostEqual(c00, 1.0 / math.sqrt(2))
        self.assertAlmostEqual(c11, -1.0 / math.sqrt(2))
        print("  [PASS] Phi-")
    
    def test_psi_plus(self):
        """Should create |Psi+>."""
        c00, c01, c10, c11 = BellState.psi_plus()
        self.assertAlmostEqual(abs(c01), 1.0 / math.sqrt(2))
        self.assertAlmostEqual(abs(c10), 1.0 / math.sqrt(2))
        print("  [PASS] Psi+")
    
    def test_measurement(self):
        """Should measure Bell state."""
        bits = BellState.bell_measurement(BellState.phi_plus())
        self.assertIn(bits, [(0, 0), (0, 1), (1, 0), (1, 1)])
        print(f"  [PASS] Measure: {bits}")


class TestTeleportationProtocol(unittest.TestCase):
    """Test teleportation protocol."""
    
    def setUp(self):
        self.tp = TeleportationProtocol()
    
    def test_prepare_bell(self):
        """Should prepare Bell pair."""
        a, b = self.tp.prepare_bell_pair()
        self.assertIsNotNone(a)
        self.assertIsNotNone(b)
        print("  [PASS] Bell pair")
    
    def test_alice_measurement(self):
        """Should measure."""
        psi = QubitState(1.0, 0.0)
        a, _ = self.tp.prepare_bell_pair()
        bits = self.tp.alice_measurement(psi, a)
        self.assertEqual(len(bits), 2)
        print(f"  [PASS] Bits: {bits}")
    
    def test_bob_correction(self):
        """Should correct."""
        q = QubitState(1.0, 0.0)
        corrected = self.tp.bob_correction(q, (0, 0))
        self.assertAlmostEqual(abs(corrected.alpha), 1.0)
        print("  [PASS] Correction")
    
    def test_teleport(self):
        """Should teleport."""
        psi = QubitState(1.0 / math.sqrt(2), 1.0 / math.sqrt(2))
        received, bits = self.tp.teleport(psi)
        self.assertIsNotNone(received)
        print(f"  [PASS] Teleport: bits={bits}")


class TestEntanglementMetrics(unittest.TestCase):
    """Test entanglement metrics."""
    
    def test_concurrence_phi_plus(self):
        """Should have concurrence 1 for |Phi+>."""
        c00, c01, c10, c11 = BellState.phi_plus()
        c = EntanglementMetrics.concurrence(c00, c01, c10, c11)
        self.assertAlmostEqual(c, 1.0)
        print(f"  [PASS] C: {c:.4f}")
    
    def test_concurrence_separable(self):
        """Should have concurrence 0 for separable."""
        c = EntanglementMetrics.concurrence(1.0, 0.0, 0.0, 0.0)
        self.assertAlmostEqual(c, 0.0)
        print(f"  [PASS] C=0")
    
    def test_entropy_max(self):
        """Should have max entropy for Bell state."""
        c00, c01, c10, c11 = BellState.phi_plus()
        e = EntanglementMetrics.entanglement_entropy(c00, c01, c10, c11)
        self.assertAlmostEqual(e, 1.0)
        print(f"  [PASS] S: {e:.4f}")
    
    def test_is_entangled(self):
        """Should detect entanglement."""
        c00, c01, c10, c11 = BellState.phi_plus()
        self.assertTrue(EntanglementMetrics.is_entangled(c00, c01, c10, c11))
        print("  [PASS] Entangled")


class TestFidelityEstimator(unittest.TestCase):
    """Test fidelity estimator."""
    
    def test_theoretical(self):
        """Should have theoretical 1.0."""
        fe = FidelityEstimator()
        f = fe.theoretical_fidelity(QubitState())
        self.assertAlmostEqual(f, 1.0)
        print("  [PASS] Theory: 1.0")
    
    def test_noisy(self):
        """Should estimate noisy fidelity."""
        fe = FidelityEstimator()
        f = fe.noisy_fidelity(QubitState(), noise_level=0.01)
        self.assertLess(f, 1.0)
        self.assertGreater(f, 0.95)
        print(f"  [PASS] Noisy: {f:.4f}")
    
    def test_average(self):
        """Should compute average."""
        fe = FidelityEstimator()
        f = fe.average_fidelity(noise_level=0.01)
        self.assertGreater(f, 0.95)
        print(f"  [PASS] Avg: {f:.4f}")


class TestQuantumTeleport(unittest.TestCase):
    """Test unified quantum teleport."""
    
    def setUp(self):
        self.qt = QuantumTeleport()
    
    def test_send(self):
        """Should send state."""
        psi = QubitState(1.0, 0.0)
        received, fid = self.qt.send(psi)
        self.assertIsNotNone(received)
        self.assertGreaterEqual(fid, 0.0)
        print(f"  [PASS] Send: fid={fid:.4f}")
    
    def test_entanglement_check(self):
        """Should check entanglement."""
        e = self.qt.entanglement_check()
        self.assertIn("concurrence", e)
        print(f"  [PASS] Entangle: C={e['concurrence']:.4f}")
    
    def test_summary(self):
        """Should provide summary."""
        psi = QubitState(1.0, 0.0)
        self.qt.send(psi)
        s = self.qt.protocol_summary()
        self.assertEqual(s["teleported_states"], 1)
        print(f"  [PASS] Summary: {s['teleported_states']} states")


if __name__ == '__main__':
    unittest.main(verbosity=2)
