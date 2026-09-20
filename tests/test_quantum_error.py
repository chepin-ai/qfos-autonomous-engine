"""
Unit tests for quantum error correction module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_error import (ErrorType, SyndromeType, ErrorEvent,
                           Syndrome, SurfaceCode, SyndromeDecoder,
                           ErrorModel, ThresholdEstimator, QuantumError)


class TestSurfaceCode(unittest.TestCase):
    """Test surface code."""
    
    def setUp(self):
        self.sc = SurfaceCode(distance=3)
    
    def test_qubit_counts(self):
        """Should compute qubit counts."""
        self.assertEqual(self.sc.data_qubits, 9)
        self.assertEqual(self.sc.ancilla_qubits, 4)
        self.assertEqual(self.sc.total_qubits, 13)
        print(f"  [PASS] Qubits: {self.sc.total_qubits}")
    
    def test_threshold(self):
        """Should have threshold."""
        th = self.sc.physical_error_rate_threshold()
        self.assertGreater(th, 0)
        print(f"  [PASS] Threshold: {th:.4f}")
    
    def test_logical_error_below(self):
        """Should suppress below threshold."""
        p_phys = 0.0001
        p_log = self.sc.logical_error_rate(p_phys)
        # Below threshold: logical error much lower than above-threshold value
        self.assertLess(p_log, 0.5)
        # With larger distance, suppression improves
        sc5 = SurfaceCode(distance=5)
        p_log5 = sc5.logical_error_rate(p_phys)
        self.assertLess(p_log5, p_log)  # d=5 suppresses more than d=3
        print(f"  [PASS] p_log(d3)={p_log:.6f}, p_log(d5)={p_log5:.6f}")
    
    def test_logical_error_above(self):
        """Should fail above threshold."""
        p_log = self.sc.logical_error_rate(0.1)
        self.assertEqual(p_log, 0.5)
        print("  [PASS] Above: 0.5")
    
    def test_overhead(self):
        """Should compute overhead."""
        oh = self.sc.overhead_ratio()
        self.assertEqual(oh, 9)
        print(f"  [PASS] Overhead: {oh}")


class TestSyndromeDecoder(unittest.TestCase):
    """Test syndrome decoder."""
    
    def setUp(self):
        self.sd = SyndromeDecoder()
    
    def test_empty(self):
        """Should return empty for no syndromes."""
        errors = self.sd.decode_simple()
        self.assertEqual(len(errors), 0)
        print("  [PASS] Empty: 0")
    
    def test_decode_x(self):
        """Should decode X syndromes."""
        self.sd.add_syndrome(Syndrome(SyndromeType.STABILIZER_X, 0, 1))
        errors = self.sd.decode_simple()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_type, ErrorType.BIT_FLIP)
        print("  [PASS] Decode X: 1")
    
    def test_decode_z(self):
        """Should decode Z syndromes."""
        self.sd.add_syndrome(Syndrome(SyndromeType.STABILIZER_Z, 0, 1))
        errors = self.sd.decode_simple()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_type, ErrorType.PHASE_FLIP)
        print("  [PASS] Decode Z: 1")
    
    def test_parity(self):
        """Should compute parity."""
        self.sd.add_syndrome(Syndrome(SyndromeType.STABILIZER_X, 0, 1))
        self.sd.add_syndrome(Syndrome(SyndromeType.STABILIZER_X, 1, 1))
        p = self.sd.syndrome_parity()
        self.assertEqual(p, 0)
        print("  [PASS] Parity: 0")


class TestErrorModel(unittest.TestCase):
    """Test error model."""
    
    def setUp(self):
        self.em = ErrorModel(bit_flip_prob=0.001, phase_flip_prob=0.001)
    
    def test_total_prob(self):
        """Should compute total error."""
        p = self.em.total_error_prob()
        self.assertGreater(p, 0.001)
        self.assertLess(p, 0.002)
        print(f"  [PASS] Total: {p:.6f}")
    
    def test_depolarizing(self):
        """Should compute depolarizing."""
        p = self.em.depolarizing_prob()
        self.assertGreater(p, 0)
        print(f"  [PASS] Depolar: {p:.6f}")
    
    def test_correlated(self):
        """Should compute correlated."""
        p = self.em.correlated_error_prob()
        self.assertGreaterEqual(p, 0)
        print(f"  [PASS] Correlated: {p:.6f}")


class TestThresholdEstimator(unittest.TestCase):
    """Test threshold estimator."""
    
    def setUp(self):
        self.te = ThresholdEstimator()
    
    def test_estimate(self):
        """Should estimate threshold."""
        self.te.add_sample(0.001, 0.0001)
        self.te.add_sample(0.01, 0.005)
        self.te.add_sample(0.1, 0.2)
        th = self.te.estimate_threshold()
        self.assertGreater(th, 0)
        print(f"  [PASS] Threshold: {th:.4f}")
    
    def test_suppression(self):
        """Should compute suppression."""
        self.te.add_sample(0.001, 0.0001)
        f = self.te.suppression_factor(0.001)
        self.assertGreater(f, 0)
        print(f"  [PASS] Suppression: {f:.4f}")


class TestQuantumError(unittest.TestCase):
    """Test unified quantum error correction."""
    
    def setUp(self):
        self.qe = QuantumError(code_distance=3)
    
    def test_measure_syndrome(self):
        """Should measure syndrome."""
        self.qe.measure_syndrome(0, SyndromeType.STABILIZER_X, 1)
        self.assertEqual(len(self.qe.decoder.syndromes), 1)
        print("  [PASS] Measure: 1")
    
    def test_decode(self):
        """Should decode and correct."""
        self.qe.measure_syndrome(0, SyndromeType.STABILIZER_X, 1)
        errors = self.qe.decode_and_correct()
        self.assertEqual(len(errors), 1)
        print(f"  [PASS] Decode: {len(errors)}")
    
    def test_below_threshold(self):
        """Should check threshold."""
        self.qe.error_model.p_x = 0.001
        below = self.qe.is_below_threshold()
        self.assertTrue(below)
        print("  [PASS] Below: True")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.qe.correction_summary()
        self.assertIn("code_distance", summary)
        self.assertIn("logical_error_rate", summary)
        print(f"  [PASS] Summary: d={summary['code_distance']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
