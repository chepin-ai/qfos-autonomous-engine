"""
Unit tests for quantum error correction module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_error_correction import (QubitState, BitFlipCode,
                                      PhaseFlipCode,
                                      ShorCode,
                                      SteaneCode,
                                      QuantumErrorCorrection)


class TestBitFlipCode(unittest.TestCase):
    """Test bit-flip code."""
    
    def setUp(self):
        self.bf = BitFlipCode()
    
    def test_encode(self):
        """Should encode."""
        c = self.bf.encode(0)
        self.assertEqual(c, [0, 0, 0])
        print("  [PASS] Enc0")
    
    def test_encode1(self):
        """Should encode 1."""
        c = self.bf.encode(1)
        self.assertEqual(c, [1, 1, 1])
        print("  [PASS] Enc1")
    
    def test_error(self):
        """Should apply error."""
        c = self.bf.apply_error([0, 0, 0], 1)
        self.assertEqual(c, [0, 1, 0])
        print("  [PASS] Err")
    
    def test_syndrome(self):
        """Should compute syndrome."""
        s = self.bf.syndrome([0, 1, 0])
        self.assertEqual(s, (1, 1))
        print(f"  [PASS] Syn: {s}")
    
    def test_correct(self):
        """Should correct."""
        c = self.bf.correct([0, 1, 0])
        self.assertEqual(c, [0, 0, 0])
        print("  [PASS] Corr")
    
    def test_decode(self):
        """Should decode."""
        d = self.bf.decode([0, 0, 0])
        self.assertEqual(d, 0)
        print("  [PASS] Dec")
    
    def test_roundtrip(self):
        """Should roundtrip."""
        c = self.bf.encode(1)
        c = self.bf.apply_error(c, 2)
        c = self.bf.correct(c)
        d = self.bf.decode(c)
        self.assertEqual(d, 1)
        print("  [PASS] RT")


class TestPhaseFlipCode(unittest.TestCase):
    """Test phase-flip code."""
    
    def setUp(self):
        self.pf = PhaseFlipCode()
    
    def test_encode(self):
        """Should encode."""
        c = self.pf.encode(0)
        self.assertEqual(c, ["+", "+", "+"])
        print("  [PASS] PhEnc")
    
    def test_phase_error(self):
        """Should apply phase error."""
        c = self.pf.apply_phase_error(["+", "+", "+"], 1)
        self.assertEqual(c[1], "-")
        print("  [PASS] PhErr")
    
    def test_syndrome(self):
        """Should measure syndrome."""
        s = self.pf.measure_phase_syndrome(["+", "-", "+"])
        self.assertEqual(s, (1, 1))
        print(f"  [PASS] PhSyn: {s}")
    
    def test_correct(self):
        """Should correct."""
        c = self.pf.correct(["+", "-", "+"])
        self.assertEqual(c, ["+", "+", "+"])
        print("  [PASS] PhCorr")


class TestShorCode(unittest.TestCase):
    """Test Shor code."""
    
    def setUp(self):
        self.sc = ShorCode()
    
    def test_encode(self):
        """Should encode."""
        c = self.sc.encode(0)
        self.assertEqual(len(c), 3)
        print("  [PASS] ShEnc")
    
    def test_decode(self):
        """Should decode."""
        c = self.sc.encode(1)
        d = self.sc.decode(c)
        self.assertEqual(d, 1)
        print("  [PASS] ShDec")


class TestSteaneCode(unittest.TestCase):
    """Test Steane code."""
    
    def setUp(self):
        self.st = SteaneCode()
    
    def test_syndrome(self):
        """Should compute syndrome."""
        c = [0, 0, 0, 0, 0, 0, 0]
        s = self.st.compute_syndrome(c)
        self.assertEqual(s, [0, 0, 0])
        print("  [PASS] StSyn")
    
    def test_correct(self):
        """Should correct."""
        c = [1, 0, 0, 0, 0, 0, 0]
        corr = self.st.correct(c)
        self.assertEqual(corr[0], 0)
        print("  [PASS] StCorr")


class TestQuantumErrorCorrection(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qec = QuantumErrorCorrection()
    
    def test_protect(self):
        """Should protect."""
        c = self.qec.protect_bit(0, "bit_flip")
        self.assertEqual(len(c), 3)
        print("  [PASS] Prot")
    
    def test_recover(self):
        """Should recover."""
        c = [0, 1, 0]
        r = self.qec.recover(c, "bit_flip")
        self.assertEqual(r, 0)
        print(f"  [PASS] Rec: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qec.qec_summary()
        self.assertIn("codes", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
