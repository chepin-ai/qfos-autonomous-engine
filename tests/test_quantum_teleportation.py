"""
Unit tests for quantum teleportation module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_teleportation import (Qubit, BellStateGenerator,
                                   QuantumTeleportationProtocol,
                                   FidelityEstimator,
                                   EntanglementSwapper,
                                   QuantumTeleportation)


class TestBellStateGenerator(unittest.TestCase):
    """Test Bell states."""
    
    def setUp(self):
        self.bsg = BellStateGenerator()
    
    def test_phi_plus(self):
        """Should get phi_plus."""
        s = self.bsg.get("phi_plus")
        self.assertAlmostEqual(abs(s[0]), 1/math.sqrt(2), places=5)
        print("  [PASS] Phi+")
    
    def test_measure(self):
        """Should measure in Bell basis."""
        s = self.bsg.get("psi_minus")
        m = self.bsg.measure_bell(s)
        self.assertEqual(m, "psi_minus")
        print(f"  [PASS] Meas: {m}")


class TestQuantumTeleportationProtocol(unittest.TestCase):
    """Test protocol."""
    
    def setUp(self):
        self.qtp = QuantumTeleportationProtocol()
    
    def test_teleport(self):
        """Should teleport."""
        unknown = Qubit(1.0, 0.0)
        bell = BellStateGenerator().get("phi_plus")
        t, outcome = self.qtp.teleport(unknown, bell)
        self.assertIn(outcome, ["00", "01", "10", "11"])
        print(f"  [PASS] Tele: {outcome}")
    
    def test_deterministic(self):
        """Should teleport deterministically."""
        unknown = Qubit(1.0, 0.0)
        bell = BellStateGenerator().get("phi_plus")
        t = self.qtp.teleport_deterministic(unknown, bell, "00")
        self.assertAlmostEqual(abs(t.alpha), 1.0, places=5)
        print("  [PASS] Det")


class TestFidelityEstimator(unittest.TestCase):
    """Test fidelity."""
    
    def setUp(self):
        self.fe = FidelityEstimator()
    
    def test_fidelity(self):
        """Should compute fidelity."""
        s1 = Qubit(1.0, 0.0)
        s2 = Qubit(1.0, 0.0)
        f = self.fe.state_fidelity(s1, s2)
        self.assertAlmostEqual(f, 1.0, places=5)
        print(f"  [PASS] Fid: {f:.4f}")
    
    def test_average(self):
        """Should compute average."""
        a = self.fe.average_fidelity([1.0, 0.5, 0.75])
        self.assertEqual(a, 0.75)
        print(f"  [PASS] Avg: {a}")


class TestEntanglementSwapper(unittest.TestCase):
    """Test swapping."""
    
    def setUp(self):
        self.es = EntanglementSwapper()
    
    def test_swap(self):
        """Should swap entanglement."""
        p1 = BellStateGenerator().get("phi_plus")
        p2 = BellStateGenerator().get("phi_plus")
        s = self.es.swap(p1, p2, "phi_plus")
        self.assertEqual(len(s), 4)
        print("  [PASS] Swap")


class TestQuantumTeleportation(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qt = QuantumTeleportation()
    
    def test_teleport(self):
        """Should teleport."""
        unknown = Qubit(1.0, 0.0)
        r = self.qt.teleport(unknown)
        self.assertIn("fidelity", r)
        print(f"  [PASS] Tele: {r['fidelity']:.4f}")
    
    def test_swap(self):
        """Should swap."""
        s = self.qt.entanglement_swap("phi_plus", "phi_plus", "phi_plus")
        self.assertEqual(len(s), 4)
        print("  [PASS] Swap")
    
    def test_summary(self):
        """Should summarize."""
        self.qt.teleport(Qubit(1.0, 0.0))
        s = self.qt.qt_summary()
        self.assertIn("teleportations", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
