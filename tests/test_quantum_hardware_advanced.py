"""
Unit tests for quantum hardware advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_hardware_advanced import (QubitParams, TransmonQubit,
                                       CouplingStrength,
                                       GateCalibration,
                                       ReadoutResonator,
                                       QuantumHardwareAdvanced)


class TestTransmonQubit(unittest.TestCase):
    """Test transmon."""
    
    def setUp(self):
        self.tq = TransmonQubit(15.0, 0.3)
    
    def test_freq(self):
        """Should compute frequency."""
        f = self.tq.qubit_frequency()
        self.assertGreater(f, 0)
        print(f"  [PASS] f01: {f:.3f} GHz")
    
    def test_anharmonicity(self):
        """Should compute anharmonicity."""
        a = self.tq.anharmonicity()
        self.assertLess(a, 0)
        print(f"  [PASS] alpha: {a:.3f} GHz")
    
    def test_dispersion(self):
        """Should compute dispersion."""
        d = self.tq.charge_dispersion(0.0)
        self.assertLess(abs(d), 0.3)
        print(f"  [PASS] Disp: {d:.6f}")


class TestCouplingStrength(unittest.TestCase):
    """Test coupling."""
    
    def setUp(self):
        self.cs = CouplingStrength()
    
    def test_capacitive(self):
        """Should compute coupling."""
        g = self.cs.capacitive_coupling(10.0)
        self.assertGreater(g, 0)
        print(f"  [PASS] g: {g:.2f} MHz")
    
    def test_swap(self):
        """Should compute swap time."""
        t = self.cs.swap_time(10.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] Tswap: {t:.1f} ns")


class TestGateCalibration(unittest.TestCase):
    """Test calibration."""
    
    def setUp(self):
        self.gc = GateCalibration()
    
    def test_rabi(self):
        """Should compute Rabi."""
        r = self.gc.rabi_frequency(0.5)
        self.assertEqual(r, 50.0)
        print(f"  [PASS] Rabi: {r:.1f} MHz")
    
    def test_pi(self):
        """Should compute pi pulse."""
        t = self.gc.pi_pulse_duration(50.0)
        self.assertEqual(t, 10.0)
        print(f"  [PASS] Tpi: {t:.1f} ns")
    
    def test_fidelity(self):
        """Should estimate fidelity."""
        f = self.gc.gate_fidelity(100.0, 20.0)
        self.assertGreater(f, 0)
        print(f"  [PASS] F: {f:.4f}")


class TestReadoutResonator(unittest.TestCase):
    """Test readout."""
    
    def setUp(self):
        self.rr = ReadoutResonator()
    
    def test_shift(self):
        """Should compute shift."""
        s = self.rr.dispersive_shift(50.0, 3000.0)
        self.assertGreater(s, 0)
        print(f"  [PASS] Chi: {s:.3f} MHz")
    
    def test_time(self):
        """Should compute measurement time."""
        t = self.rr.measurement_time()
        self.assertGreater(t, 0)
        print(f"  [PASS] Tmeas: {t:.1f} ns")


class TestQuantumHardwareAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qha = QuantumHardwareAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qha.hardware_summary()
        self.assertIn("components", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
