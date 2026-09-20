"""
Unit tests for quantum teleportation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_teleportation import (QubitState, BellStatePreparator,
                                   BellMeasurement,
                                   ClassicalChannel,
                                   StateReconstructor,
                                   QuantumTeleportation)


class TestBellStatePreparator(unittest.TestCase):
    """Test preparator."""
    
    def setUp(self):
        self.bsp = BellStatePreparator()
    
    def test_prepare(self):
        """Should prepare."""
        s = self.bsp.prepare("Phi+")
        self.assertEqual(len(s), 2)
        print("  [PASS] Prep")
    
    def test_fidelity(self):
        """Should compute fidelity."""
        s = self.bsp.prepare("Phi+")
        f = self.bsp.fidelity(s, "Phi+")
        self.assertEqual(f, 1.0)
        print(f"  [PASS] Fid: {f}")


class TestBellMeasurement(unittest.TestCase):
    """Test measurement."""
    
    def setUp(self):
        self.bm = BellMeasurement()
    
    def test_measure(self):
        """Should measure."""
        q = QubitState(1.0, 0.0)
        r = self.bm.measure(q, q)
        self.assertEqual(len(r), 2)
        print(f"  [PASS] BSM: {r}")
    
    def test_corrections(self):
        """Should convert."""
        c = self.bm.outcome_to_corrections((1, 0))
        self.assertEqual(c, (True, False))
        print(f"  [PASS] Corr: {c}")


class TestClassicalChannel(unittest.TestCase):
    """Test channel."""
    
    def setUp(self):
        self.cc = ClassicalChannel(0.0, 0.0)
    
    def test_transmit(self):
        """Should transmit."""
        r = self.cc.transmit((0, 1))
        self.assertEqual(r, (0, 1))
        print(f"  [PASS] Tx: {r}")


class TestStateReconstructor(unittest.TestCase):
    """Test reconstructor."""
    
    def setUp(self):
        self.sr = StateReconstructor()
    
    def test_apply(self):
        """Should apply corrections."""
        q = QubitState(1.0, 0.0)
        r = self.sr.apply_corrections(q, False, False)
        self.assertEqual(r.alpha, 1.0)
        print("  [PASS] Appl")
    
    def test_fidelity(self):
        """Should compute fidelity."""
        q1 = QubitState(1.0, 0.0)
        q2 = QubitState(1.0, 0.0)
        f = self.sr.fidelity(q1, q2)
        self.assertEqual(f, 1.0)
        print(f"  [PASS] Fid: {f}")


class TestQuantumTeleportation(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qt = QuantumTeleportation()
    
    def test_teleport(self):
        """Should teleport."""
        q = QubitState(1.0, 0.0)
        r, f = self.qt.teleport(q)
        self.assertIsNotNone(r)
        print(f"  [PASS] TPort: F={f:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qt.qteleport_summary()
        self.assertIn("bell_states", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
