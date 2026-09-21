"""
Unit tests for quantum metrology module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_metrology import (EstimationResult, PhaseEstimator,
                               QuantumFisherInformation,
                               QuantumSensor,
                               QuantumMetrology)


class TestPhaseEstimator(unittest.TestCase):
    """Test phase."""
    
    def setUp(self):
        self.pe = PhaseEstimator(3)
    
    def test_estimate(self):
        """Should estimate."""
        r = self.pe.estimate_phase(0.5, 1000)
        self.assertGreater(r.fisher_information, 0)
        print(f"  [PASS] Est: {r.estimated_value:.3f} +/- {r.uncertainty:.4f}")
    
    def test_scaling(self):
        """Should compute scaling."""
        p = self.pe.precision_scaling(4)
        self.assertAlmostEqual(p, 1.0 / 16.0, delta=0.001)
        print(f"  [PASS] Sc: {p:.4f}")


class TestQuantumFisherInformation(unittest.TestCase):
    """Test QFI."""
    
    def setUp(self):
        self.qfi = QuantumFisherInformation()
    
    def test_pure_state(self):
        """Should compute QFI."""
        state = [1.0 / math.sqrt(2), 1.0 / math.sqrt(2)]
        dstate = [0.0, 0.0]
        f = self.qfi.qfi_pure_state(dstate, state)
        self.assertGreaterEqual(f, 0)
        print(f"  [PASS] QFI: {f:.2f}")
    
    def test_ghz(self):
        """Should compute GHZ QFI."""
        f = self.qfi.qfi_ghz_state(4)
        self.assertEqual(f, 16.0)
        print(f"  [PASS] GHZ: {f:.0f}")
    
    def test_product(self):
        """Should compute SQL."""
        f = self.qfi.qfi_product_state(4)
        self.assertEqual(f, 4.0)
        print(f"  [PASS] SQL: {f:.0f}")


class TestQuantumSensor(unittest.TestCase):
    """Test sensor."""
    
    def setUp(self):
        self.s = QuantumSensor()
    
    def test_frequency(self):
        """Should estimate frequency."""
        df = self.s.frequency_estimation(1.0, 10.0)
        self.assertGreater(df, 0)
        print(f"  [PASS] df: {df:.4f} Hz")
    
    def test_magnetic(self):
        """Should compute sensitivity."""
        sens = self.s.magnetic_field_sensitivity(28.0, 1.0, 100)
        self.assertGreater(sens, 0)
        print(f"  [PASS] B: {sens:.2e} T/sqrt(Hz)")
    
    def test_gravity(self):
        """Should compute gravity sensitivity."""
        sens = self.s.gravimetry_sensitivity(1.0)
        self.assertGreater(sens, 0)
        print(f"  [PASS] g: {sens:.2e} m/s2/sqrt(Hz)")


class TestQuantumMetrology(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qm = QuantumMetrology()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qm.metrology_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
