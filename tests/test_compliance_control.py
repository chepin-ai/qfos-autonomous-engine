"""
Unit tests for compliance control module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from compliance_control import (ControlMode, CartesianState,
                                ImpedanceController, AdmittanceController,
                                StiffnessRegulator, DampingRegulator,
                                ComplianceControl)


class TestImpedanceController(unittest.TestCase):
    """Test impedance controller."""
    
    def setUp(self):
        self.ic = ImpedanceController(mass_kg=1.0, damping_Ns_m=10.0,
                                      stiffness_N_m=100.0)
    
    def test_zero_error(self):
        """Should have zero force at target."""
        f = self.ic.compute_force(0.0, 0.0, 0.0, 0.0)
        self.assertAlmostEqual(f, 0.0)
        print(f"  [PASS] Zero: {f}")
    
    def test_position_error(self):
        """Should generate restoring force."""
        f = self.ic.compute_force(0.1, 0.0, 0.0, 0.0)
        self.assertAlmostEqual(f, 10.0)
        print(f"  [PASS] Pos: {f}")
    
    def test_natural_freq(self):
        """Should compute omega_n."""
        w = self.ic.natural_frequency()
        self.assertAlmostEqual(w, 10.0)
        print(f"  [PASS] wn: {w}")
    
    def test_damping_ratio(self):
        """Should compute zeta."""
        z = self.ic.damping_ratio()
        self.assertAlmostEqual(z, 0.5)
        print(f"  [PASS] zeta: {z}")


class TestAdmittanceController(unittest.TestCase):
    """Test admittance controller."""
    
    def setUp(self):
        self.ac = AdmittanceController(mass_kg=1.0, damping_Ns_m=10.0,
                                       stiffness_N_m=100.0, dt=0.001)
    
    def test_zero_force(self):
        """Should stay at rest."""
        pos, vel = self.ac.update(0.0)
        self.assertAlmostEqual(pos, 0.0, places=3)
        print(f"  [PASS] Rest: pos={pos:.4f}")
    
    def test_step_force(self):
        """Should move under force."""
        for _ in range(1000):
            pos, vel = self.ac.update(10.0)
        self.assertGreater(pos, 0.0)
        print(f"  [PASS] Step: pos={pos:.4f}")
    
    def test_reset(self):
        """Should reset state."""
        self.ac.update(10.0)
        self.ac.reset()
        self.assertAlmostEqual(self.ac.position, 0.0)
        print("  [PASS] Reset")


class TestStiffnessRegulator(unittest.TestCase):
    """Test stiffness regulator."""
    
    def setUp(self):
        self.sr = StiffnessRegulator()
    
    def test_from_force(self):
        """Should compute stiffness."""
        k = self.sr.from_force(100.0, 0.01)
        # Clamped to max_stiffness=1000.0
        self.assertEqual(k, 1000.0)
        print(f"  [PASS] K: {k:.1f}")
    
    def test_clamped(self):
        """Should clamp to max."""
        k = self.sr.from_force(10000.0, 0.001)
        self.assertEqual(k, 1000.0)
        print("  [PASS] Clamp")


class TestDampingRegulator(unittest.TestCase):
    """Test damping regulator."""
    
    def setUp(self):
        self.dr = DampingRegulator()
    
    def test_critical(self):
        """Should compute critical damping."""
        b = self.dr.critical_damping(1.0, 100.0)
        self.assertAlmostEqual(b, 20.0)
        print(f"  [PASS] Bcrit: {b}")
    
    def test_optimal(self):
        """Should compute optimal damping."""
        b = self.dr.optimal_damping(1.0, 100.0, 0.7)
        self.assertAlmostEqual(b, 14.0)
        print(f"  [PASS] Bopt: {b}")


class TestComplianceControl(unittest.TestCase):
    """Test unified compliance control."""
    
    def setUp(self):
        self.cc = ComplianceControl()
    
    def test_mode(self):
        """Should set mode."""
        self.cc.set_mode(ControlMode.ADMITTANCE)
        self.assertEqual(self.cc.mode, ControlMode.ADMITTANCE)
        print("  [PASS] Mode")
    
    def test_impedance_control(self):
        """Should compute impedance force."""
        self.cc.set_mode(ControlMode.IMPEDANCE)
        out = self.cc.control(0.1, 0.0, 0.0, 0.0)
        self.assertNotEqual(out, 0.0)
        print(f"  [PASS] Imp: {out:.2f}")
    
    def test_summary(self):
        """Should provide summary."""
        s = self.cc.compliance_summary()
        self.assertIn("damping_ratio", s)
        print(f"  [PASS] Summary: z={s['damping_ratio']:.2f}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
