"""
Unit tests for quantum circuit optimization module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_circuit_optimization import (GateOp, GateCanceler,
                                          GateFuser,
                                          DepthReducer,
                                          TemplateMatcher,
                                          CircuitRewriter,
                                          QuantumCircuitOptimization)


class TestGateCanceler(unittest.TestCase):
    """Test canceler."""
    
    def setUp(self):
        self.gc = GateCanceler()
    
    def test_cancel_xx(self):
        """Should cancel X-X."""
        circ = [GateOp("X", [0], []), GateOp("X", [0], [])]
        r = self.gc.cancel(circ)
        self.assertEqual(len(r), 0)
        print(f"  [PASS] Cxl: {len(r)}")
    
    def test_cancel_hh(self):
        """Should cancel H-H."""
        circ = [GateOp("H", [0], []), GateOp("H", [0], [])]
        r = self.gc.cancel(circ)
        self.assertEqual(len(r), 0)
        print("  [PASS] HH")


class TestGateFuser(unittest.TestCase):
    """Test fuser."""
    
    def setUp(self):
        self.gf = GateFuser()
    
    def test_fuse_rx(self):
        """Should fuse RX."""
        circ = [GateOp("RX", [0], [0.5]), GateOp("RX", [0], [0.5])]
        r = self.gf.fuse_rotations(circ)
        self.assertEqual(len(r), 1)
        self.assertAlmostEqual(r[0].params[0], 1.0)
        print(f"  [PASS] Fus: {r[0].params}")


class TestDepthReducer(unittest.TestCase):
    """Test depth."""
    
    def setUp(self):
        self.dr = DepthReducer()
    
    def test_depth(self):
        """Should compute depth."""
        circ = [GateOp("X", [0], []), GateOp("H", [1], [])]
        d = self.dr.circuit_depth(circ, 2)
        self.assertEqual(d, 1)
        print(f"  [PASS] D: {d}")
    
    def test_depth_sequential(self):
        """Should compute sequential depth."""
        circ = [GateOp("X", [0], []), GateOp("H", [0], [])]
        d = self.dr.circuit_depth(circ, 2)
        self.assertEqual(d, 2)
        print(f"  [PASS] Seq: {d}")


class TestTemplateMatcher(unittest.TestCase):
    """Test templates."""
    
    def setUp(self):
        self.tm = TemplateMatcher()
    
    def test_hxh_to_z(self):
        """Should replace H-X-H with Z."""
        circ = [GateOp("H", [0], []), GateOp("X", [0], []), GateOp("H", [0], [])]
        r = self.tm.match_and_replace(circ)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].name, "Z")
        print(f"  [PASS] Tmpl: {r[0].name}")


class TestQuantumCircuitOptimization(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qco = QuantumCircuitOptimization(3)
    
    def test_optimize(self):
        """Should optimize."""
        circ = [GateOp("X", [0], []), GateOp("X", [0], [])]
        r = self.qco.optimize(circ)
        self.assertEqual(len(r), 0)
        print("  [PASS] Opt")
    
    def test_stats(self):
        """Should compute stats."""
        circ = [GateOp("X", [0], []), GateOp("H", [1], [])]
        s = self.qco.stats(circ)
        self.assertEqual(s["num_gates"], 2)
        print(f"  [PASS] Stats: {s}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qco.qco_summary()
        self.assertIn("optimizers", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
