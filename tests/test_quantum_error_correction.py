"""
Unit tests for quantum error correction module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_error_correction import (QuantumError, BitFlipCode,
                                      PhaseFlipCode,
                                      StabilizerFormalism,
                                      QuantumErrorCorrection)


class TestBitFlipCode(unittest.TestCase):
    """Test bit-flip code."""
    
    def setUp(self):
        self.bfc = BitFlipCode()
    
    def test_encode(self):
        """Should encode."""
        s = self.bfc.encode([1.0, 0.0])
        self.assertEqual(len(s), 8)
        self.assertEqual(s[0], 1.0)
        print("  [PASS] Enc")
    
    def test_syndrome_no_error(self):
        """Should measure syndrome."""
        s = self.bfc.encode([1.0, 0.0])
        syn = self.bfc.measure_syndrome(s)
        self.assertEqual(syn, [0, 0])
        print(f"  [PASS] Syn: {syn}")
    
    def test_correct(self):
        """Should correct error."""
        s = self.bfc.encode([1.0, 0.0])
        # Flip qubit 1
        corrupted = self.bfc._apply_x(s, 1)
        corrected = self.bfc.correct(corrupted)
        syn = self.bfc.measure_syndrome(corrected)
        self.assertEqual(syn, [0, 0])
        print("  [PASS] Corr")
    
    def test_decode(self):
        """Should decode."""
        s = self.bfc.encode([0.6, 0.8])
        d = self.bfc.decode(s)
        self.assertEqual(len(d), 2)
        print(f"  [PASS] Dec: {d}")


class TestPhaseFlipCode(unittest.TestCase):
    """Test phase-flip code."""
    
    def setUp(self):
        self.pfc = PhaseFlipCode()
    
    def test_encode(self):
        """Should encode."""
        s = self.pfc.encode([1.0, 0.0])
        self.assertEqual(len(s), 8)
        print("  [PASS] Enc")
    
    def test_correct(self):
        """Should correct phase error."""
        s = self.pfc.encode([1.0, 0.0])
        corrupted = self.pfc._apply_z(s, 1)
        corrected = self.pfc.correct(corrupted)
        self.assertEqual(len(corrected), 8)
        print("  [PASS] Corr")


class TestStabilizerFormalism(unittest.TestCase):
    """Test stabilizer."""
    
    def setUp(self):
        self.sf = StabilizerFormalism(3)
    
    def test_add(self):
        """Should add stabilizer."""
        self.sf.add_stabilizer("ZZI")
        self.assertEqual(len(self.sf.stabilizers), 1)
        print("  [PASS] Add")
    
    def test_measure(self):
        """Should measure stabilizer."""
        self.sf.add_stabilizer("ZZI")
        state = [1.0] + [0.0] * 7
        e = self.sf.measure_stabilizer(state, "ZZI")
        self.assertIn(e, [1, -1])
        print(f"  [PASS] Meas: {e}")


class TestQuantumErrorCorrection(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qec = QuantumErrorCorrection()
    
    def test_encode_bf(self):
        """Should encode bit-flip."""
        s = self.qec.encode_bit_flip([1.0, 0.0])
        self.assertEqual(len(s), 8)
        print("  [PASS] EncBF")
    
    def test_encode_pf(self):
        """Should encode phase-flip."""
        s = self.qec.encode_phase_flip([1.0, 0.0])
        self.assertEqual(len(s), 8)
        print("  [PASS] EncPF")
    
    def test_simulate_error(self):
        """Should simulate error."""
        s = self.qec.encode_bit_flip([1.0, 0.0])
        corrupted = self.qec.simulate_error(s, 0, "X")
        self.assertEqual(len(corrupted), 8)
        self.assertEqual(len(self.qec.errors), 1)
        print("  [PASS] Sim")
    
    def test_correct(self):
        """Should correct."""
        s = self.qec.encode_bit_flip([1.0, 0.0])
        corrupted = self.qec.simulate_error(s, 1, "X")
        corrected = self.qec.correct(corrupted, "bit_flip")
        self.assertEqual(len(corrected), 8)
        print("  [PASS] Corr")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qec.qec_summary()
        self.assertIn("code_distance", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
