"""
Unit tests for quantum error correction advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_error_correction_advanced import (PauliOperator, StabilizerCode,
                                               SurfaceCodeDecoder,
                                               ThresholdAnalysis,
                                               FaultTolerantGate,
                                               QuantumErrorCorrectionAdvanced)


class TestStabilizerCode(unittest.TestCase):
    """Test stabilizer."""
    
    def setUp(self):
        self.sc = StabilizerCode(5, 4)
    
    def test_params(self):
        """Should compute parameters."""
        n, k, d = self.sc.code_parameters()
        self.assertEqual(n, 5)
        self.assertEqual(k, 1)
        self.assertGreater(d, 0)
        print(f"  [PASS] [[{n},{k},{d}]]")
    
    def test_syndrome(self):
        """Should compute syndrome."""
        err = PauliOperator({0}, set())
        stab = [PauliOperator(set(), {0}), PauliOperator(set(), {1})]
        s = self.sc.syndrome(err, stab)
        self.assertEqual(len(s), 2)
        print(f"  [PASS] Syn: {s}")
    
    def test_logical_rate(self):
        """Should estimate logical rate."""
        p = self.sc.logical_error_rate(0.01)
        self.assertGreater(p, 0)
        print(f"  [PASS] Pl: {p:.6f}")


class TestSurfaceCodeDecoder(unittest.TestCase):
    """Test surface."""
    
    def setUp(self):
        self.scd = SurfaceCodeDecoder(3)
    
    def test_weight(self):
        """Should compute weight."""
        w = self.scd.syndrome_weight([0, 1, 0, 1])
        self.assertEqual(w, 2)
        print(f"  [PASS] W: {w}")
    
    def test_decode(self):
        """Should decode."""
        pairs = self.scd.decode_mwpm([1, 1], [(0, 0), (1, 0)])
        self.assertGreater(len(pairs), 0)
        print(f"  [PASS] Pairs: {len(pairs)}")
    
    def test_logical_prob(self):
        """Should compute logical prob."""
        p = self.scd.logical_error_probability(0.01)
        self.assertGreater(p, 0)
        print(f"  [PASS] Pl: {p:.6f}")


class TestThresholdAnalysis(unittest.TestCase):
    """Test threshold."""
    
    def setUp(self):
        self.th = ThresholdAnalysis()
    
    def test_estimate(self):
        """Should estimate threshold."""
        t = self.th.threshold_estimate(3, [0.01, 0.05, 0.1], [0.001, 0.04, 0.09])
        self.assertGreater(t, 0)
        print(f"  [PASS] Th: {t:.3f}")
    
    def test_overhead(self):
        """Should compute overhead."""
        o = self.th.overhead_ratio(17, 1)
        self.assertEqual(o, 17.0)
        print(f"  [PASS] O: {o:.1f}")


class TestFaultTolerantGate(unittest.TestCase):
    """Test FT gate."""
    
    def setUp(self):
        self.ft = FaultTolerantGate()
    
    def test_depth(self):
        """Should compute depth."""
        d = self.ft.transversal_cnot_depth(5)
        self.assertEqual(d, 5)
        print(f"  [PASS] D: {d}")
    
    def test_magic(self):
        """Should compute magic cost."""
        c = self.ft.magic_state_cost("T")
        self.assertEqual(c, 1)
        print(f"  [PASS] Cost: {c}")


class TestQuantumErrorCorrectionAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qec = QuantumErrorCorrectionAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qec.qec_summary()
        self.assertIn("codes", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
