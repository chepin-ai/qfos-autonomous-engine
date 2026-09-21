"""
Unit tests for impedance control module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from impedance_control import (ImpedanceParams, ImpedanceController,
                               AdmittanceController,
                               ComplianceRegulator,
                               ContactStability,
                               ImpedanceControl)


class TestImpedanceController(unittest.TestCase):
    """Test impedance."""
    
    def setUp(self):
        self.ic = ImpedanceController(ImpedanceParams(1.0, 10.0, 100.0))
    
    def test_compute_force(self):
        """Should compute force."""
        F = self.ic.compute_force(0.01, 0.1)
        self.assertGreater(F, 0)
        print(f"  [PASS] F: {F:.2f} N")
    
    def test_natural_frequency(self):
        """Should compute natural frequency."""
        wn = self.ic.natural_frequency()
        self.assertEqual(wn, 10.0)
        print(f"  [PASS] wn: {wn:.2f} rad/s")
    
    def test_damping_ratio(self):
        """Should compute damping ratio."""
        z = self.ic.damping_ratio()
        self.assertEqual(z, 0.5)
        print(f"  [PASS] zeta: {z:.2f}")


class TestAdmittanceController(unittest.TestCase):
    """Test admittance."""
    
    def setUp(self):
        self.ac = AdmittanceController(ImpedanceParams(1.0, 10.0, 100.0))
    
    def test_compute_position(self):
        """Should compute position."""
        p, v = self.ac.compute_position(10.0, 0.01)
        self.assertIsNotNone(p)
        print(f"  [PASS] p: {p:.4f}, v: {v:.4f}")


class TestComplianceRegulator(unittest.TestCase):
    """Test compliance."""
    
    def setUp(self):
        self.cr = ComplianceRegulator()
    
    def test_adaptive_stiffness(self):
        """Should adapt stiffness."""
        K = self.cr.adaptive_stiffness(5.0, 10.0, 100.0)
        self.assertGreater(K, 100.0)
        print(f"  [PASS] K: {K:.2f}")
    
    def test_safety_limit(self):
        """Should limit force."""
        F = self.cr.safety_limit(150.0, 100.0)
        self.assertEqual(F, 100.0)
        print(f"  [PASS] Flim: {F:.2f}")


class TestContactStability(unittest.TestCase):
    """Test stability."""
    
    def setUp(self):
        self.cs = ContactStability()
    
    def test_stable(self):
        """Should check stability."""
        self.assertTrue(self.cs.stable_contact(ImpedanceParams(1.0, 10.0, 50.0), 100.0))
        print("  [PASS] Stable")
    
    def test_passivity(self):
        """Should compute margin."""
        m = self.cs.passivity_margin(ImpedanceParams(1.0, 10.0, 100.0))
        self.assertEqual(m, 0.5)
        print(f"  [PASS] Margin: {m:.2f}")


class TestImpedanceControl(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ic = ImpedanceControl()
        self.ic.set_params(1.0, 10.0, 100.0)
    
    def test_summary(self):
        """Should summarize."""
        s = self.ic.impedance_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
