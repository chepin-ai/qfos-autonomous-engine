"""
Unit tests for quantum teleportation module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_teleportation import (QubitState, BellStateGenerator,
                                   BellMeasurement,
                                   StateReconstructor,
                                   QuantumTeleportation)


class TestBellStateGenerator(unittest.TestCase):
    """Test Bell generator."""
    
    def setUp(self):
        self.bsg = BellStateGenerator()
    
    def test_phi_plus(self):
        """Should generate Phi+."""
        a, b = self.bsg.phi_plus()
        self.assertAlmostEqual(abs(a.alpha), 1.0 / math.sqrt(2.0), places=5)
        print("  [PASS] Phi+")
    
    def test_phi_minus(self):
        """Should generate Phi-."""
        a, b = self.bsg.phi_minus()
        self.assertAlmostEqual(abs(a.alpha), 1.0 / math.sqrt(2.0), places=5)
        print("  [PASS] Phi-")


class TestBellMeasurement(unittest.TestCase):
    """Test Bell measurement."""
    
    def setUp(self):
        self.bm = BellMeasurement()
    
    def test_measure(self):
        """Should measure."""
        q1 = QubitState(1.0, 0.0)
        q2 = QubitState(1.0, 0.0)
        m = self.bm.measure(q1, q2)
        self.assertEqual(len(m), 2)
        print(f"  [PASS] Meas: {m}")
    
    def test_correction(self):
        """Should determine corrections."""
        gates = self.bm.correction_gates((1, 0))
        self.assertIn("X", gates)
        print(f"  [PASS] Corr: {gates}")


class TestStateReconstructor(unittest.TestCase):
    """Test reconstructor."""
    
    def setUp(self):
        self.sr = StateReconstructor()
    
    def test_apply_correction(self):
        """Should apply corrections."""
        s = QubitState(1.0, 0.0)
        c = self.sr.apply_correction(s, ["X"])
        self.assertAlmostEqual(c.alpha, 0.0, places=5)
        print("  [PASS] Corr")
    
    def test_fidelity(self):
        """Should compute fidelity."""
        s1 = QubitState(1.0, 0.0)
        s2 = QubitState(1.0, 0.0)
        f = self.sr.fidelity(s1, s2)
        self.assertAlmostEqual(f, 1.0, places=5)
        print(f"  [PASS] Fid: {f:.3f}")


class TestQuantumTeleportation(unittest.TestCase):
    """Test teleportation."""
    
    def setUp(self):
        self.qt = QuantumTeleportation()
    
    def test_teleport(self):
        """Should teleport."""
        state = QubitState(1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0))
        result = self.qt.teleport(state)
        self.assertIn("fidelity", result)
        print(f"  [PASS] Tel: fid={result['fidelity']:.3f}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qt.qt_summary()
        self.assertIn("protocol", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
