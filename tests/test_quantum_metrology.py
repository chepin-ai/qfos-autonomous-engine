"""
Unit tests for quantum metrology module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_metrology import (QuantumPhaseSensor, RamseyInterferometer,
                                QuantumFisherInfo, QuantumMetrology)


class TestQuantumPhaseSensor(unittest.TestCase):
    """Test phase sensor."""
    
    def setUp(self):
        self.ps = QuantumPhaseSensor(2)
    
    def test_ghz(self):
        """Should prepare GHZ."""
        s = self.ps.prepare_ghz()
        self.assertEqual(len(s), 4)
        norm = sum(abs(z)**2 for z in s)
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] GHZ: norm={norm:.4f}")
    
    def test_phase(self):
        """Should apply phase."""
        s = self.ps.prepare_ghz()
        sp = self.ps.apply_phase(s, math.pi / 4)
        self.assertEqual(len(sp), 4)
        print("  [PASS] Phase")
    
    def test_estimate(self):
        """Should estimate phase."""
        s = self.ps.prepare_ghz()
        s = self.ps.apply_phase(s, 0.1)
        est = self.ps.estimate_phase(s)
        self.assertIsNotNone(est)
        print(f"  [PASS] Est: {est:.4f}")


class TestRamseyInterferometer(unittest.TestCase):
    """Test Ramsey."""
    
    def setUp(self):
        self.r = RamseyInterferometer()
    
    def test_sequence(self):
        """Should simulate sequence."""
        p = self.r.ramsey_sequence(0.1, 1.0)
        self.assertGreaterEqual(p, 0)
        self.assertLessEqual(p, 1.0)
        print(f"  [PASS] Seq: P={p:.4f}")
    
    def test_estimate(self):
        """Should estimate detuning."""
        p = self.r.ramsey_sequence(0.1, 1.0)
        est = self.r.estimate_detuning(p, 1.0)
        self.assertGreaterEqual(est, 0)
        print(f"  [PASS] Est: {est:.4f}")
    
    def test_sensitivity(self):
        """Should compute sensitivity."""
        s = self.r.sensitivity(1.0, 100)
        self.assertGreater(s, 0)
        print(f"  [PASS] Sens: {s:.4f}")


class TestQuantumFisherInfo(unittest.TestCase):
    """Test QFI."""
    
    def setUp(self):
        self.qfi = QuantumFisherInfo()
    
    def test_pure(self):
        """Should compute pure state QFI."""
        state = [complex(1.0, 0.0), complex(0.0, 0.0)]
        deriv = [complex(0.0, 0.0), complex(1.0, 0.0)]
        f = self.qfi.pure_state_qfi(deriv, state)
        self.assertGreaterEqual(f, 0)
        print(f"  [PASS] Pure: {f:.4f}")
    
    def test_ghz(self):
        """Should compute GHZ QFI."""
        f = self.qfi.ghz_qfi(4)
        self.assertEqual(f, 16.0)
        print(f"  [PASS] GHZ: {f:.4f}")
    
    def test_coherent(self):
        """Should compute coherent QFI."""
        f = self.qfi.coherent_state_qfi(4)
        self.assertEqual(f, 4.0)
        print(f"  [PASS] Coherent: {f:.4f}")
    
    def test_advantage(self):
        """Should compute advantage."""
        a = self.qfi.quantum_advantage(4)
        self.assertEqual(a, 4.0)
        print(f"  [PASS] Adv: {a:.4f}")


class TestQuantumMetrology(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qm = QuantumMetrology()
    
    def test_setup(self):
        """Should setup."""
        self.qm.setup_phase_sensor(4)
        self.assertIsNotNone(self.qm.phase_sensor)
        print("  [PASS] Setup")
    
    def test_measure(self):
        """Should measure."""
        r = self.qm.measure_phase(0.1)
        self.assertIn("estimated_phase", r)
        print(f"  [PASS] Meas: est={r['estimated_phase']:.4f}")
    
    def test_ramsey(self):
        """Should do Ramsey."""
        r = self.qm.ramsey_measurement(0.1, 1.0)
        self.assertIn("probability", r)
        print(f"  [PASS] Ramsey: P={r['probability']:.4f}")
    
    def test_qfi(self):
        """Should compute QFI."""
        r = self.qm.compute_qfi(4)
        self.assertEqual(r["ghz_qfi"], 16.0)
        print(f"  [PASS] QFI: {r}")
    
    def test_summary(self):
        """Should summarize."""
        self.qm.measure_phase(0.1)
        s = self.qm.metrology_summary()
        self.assertIn("measurements", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
