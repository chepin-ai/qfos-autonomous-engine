"""
Unit tests for quantum interferometry module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_interferometry import (InterferencePattern,
                                    MachZehnderInterferometer,
                                    MichelsonInterferometer,
                                    SagnacInterferometer,
                                    QuantumEnhancedSensitivity,
                                    QuantumInterferometry)


class TestMachZehnder(unittest.TestCase):
    """Test MZI."""
    
    def setUp(self):
        self.mzi = MachZehnderInterferometer()
    
    def test_intensity(self):
        """Should compute intensity."""
        I1, I2 = self.mzi.output_intensity(1.0, math.pi)
        self.assertAlmostEqual(I1, 0.0, delta=0.01)
        self.assertAlmostEqual(I2, 1.0, delta=0.01)
        print(f"  [PASS] I: ({I1:.3f}, {I2:.3f})")
    
    def test_phase(self):
        """Should estimate phase."""
        phi = self.mzi.phase_from_intensities(0.75, 0.25)
        self.assertAlmostEqual(phi, math.pi / 3.0, delta=0.1)
        print(f"  [PASS] phi: {phi:.3f}")
    
    def test_visibility(self):
        """Should compute visibility."""
        V = self.mzi.visibility(1.0, 0.0)
        self.assertEqual(V, 1.0)
        print(f"  [PASS] V: {V:.2f}")


class TestMichelson(unittest.TestCase):
    """Test Michelson."""
    
    def setUp(self):
        self.mic = MichelsonInterferometer(633.0)
    
    def test_path_diff(self):
        """Should compute path difference."""
        d = self.mic.path_difference(1e-6)
        self.assertEqual(d, 2e-6)
        print(f"  [PASS] d: {d:.2e}")
    
    def test_fringe_count(self):
        """Should count fringes."""
        n = self.mic.fringe_count(633e-9)
        self.assertAlmostEqual(n, 2.0, delta=0.01)
        print(f"  [PASS] N: {n:.1f}")
    
    def test_displacement(self):
        """Should compute displacement."""
        d = self.mic.displacement_from_fringes(2.0)
        self.assertAlmostEqual(d, 633e-9, delta=1e-12)
        print(f"  [PASS] d: {d:.2e}")


class TestSagnac(unittest.TestCase):
    """Test Sagnac."""
    
    def setUp(self):
        self.sag = SagnacInterferometer(1.0, 633.0)
    
    def test_phase(self):
        """Should compute phase."""
        phi = self.sag.sagnac_phase(1.0)
        self.assertGreater(phi, 0)
        print(f"  [PASS] phi: {phi:.6e}")
    
    def test_velocity(self):
        """Should compute angular velocity."""
        phi = self.sag.sagnac_phase(1.0)
        w = self.sag.angular_velocity_from_phase(phi)
        self.assertAlmostEqual(w, 1.0, delta=0.01)
        print(f"  [PASS] w: {w:.3f}")


class TestQuantumEnhancedSensitivity(unittest.TestCase):
    """Test sensitivity."""
    
    def setUp(self):
        self.qs = QuantumEnhancedSensitivity()
    
    def test_shot_noise(self):
        """Should compute shot noise."""
        s = self.qs.shot_noise_limit(100.0)
        self.assertEqual(s, 0.1)
        print(f"  [PASS] SN: {s:.3f}")
    
    def test_heisenberg(self):
        """Should compute Heisenberg limit."""
        s = self.qs.noo_n_state_sensitivity(100.0)
        self.assertEqual(s, 0.01)
        print(f"  [PASS] HL: {s:.3f}")


class TestQuantumInterferometry(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qi = QuantumInterferometry()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qi.interferometry_summary()
        self.assertIn("interferometers", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
