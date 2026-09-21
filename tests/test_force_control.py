"""
Unit tests for force control module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from force_control import (ForceTorque, HybridPositionForceControl,
                           AdmittanceControl,
                           ForceTracking,
                           ContactDetection,
                           ForceControl)


class TestHybridPositionForceControl(unittest.TestCase):
    """Test hybrid."""
    
    def setUp(self):
        self.hpf = HybridPositionForceControl()
    
    def test_position(self):
        """Should compute position output."""
        v = self.hpf.position_control(0.01)
        self.assertEqual(v, 1.0)
        print(f"  [PASS] Vp: {v:.2f}")
    
    def test_force(self):
        """Should compute force output."""
        v = self.hpf.force_control(2.0)
        self.assertEqual(v, 20.0)
        print(f"  [PASS] Vf: {v:.1f}")
    
    def test_hybrid(self):
        """Should compute hybrid command."""
        v = self.hpf.hybrid_command(0.01, 2.0, "force")
        self.assertEqual(v, 20.0)
        print(f"  [PASS] Vh: {v:.1f}")


class TestAdmittanceControl(unittest.TestCase):
    """Test admittance."""
    
    def setUp(self):
        self.ac = AdmittanceControl()
    
    def test_acceleration(self):
        """Should compute acceleration."""
        a = self.ac.desired_acceleration(5.0, 0.0, 0.0)
        self.assertEqual(a, 5.0)
        print(f"  [PASS] A: {a:.1f}")
    
    def test_stiffness(self):
        """Should return stiffness."""
        k = self.ac.apparent_stiffness()
        self.assertEqual(k, 100.0)
        print(f"  [PASS] K: {k:.1f}")


class TestForceTracking(unittest.TestCase):
    """Test tracking."""
    
    def setUp(self):
        self.ft = ForceTracking()
    
    def test_ramp(self):
        """Should compute ramp."""
        f = self.ft.ramp_force(5.0)
        self.assertEqual(f, 5.0)
        print(f"  [PASS] Framp: {f:.1f}")
    
    def test_sine(self):
        """Should compute sinusoidal."""
        f = self.ft.sinusoidal_force(0.25)
        self.assertAlmostEqual(f, 5.0, delta=1e-10)
        print(f"  [PASS] Fsin: {f:.2f}")
    
    def test_error(self):
        """Should compute error."""
        e = self.ft.tracking_error(10.0, 8.0)
        self.assertEqual(e, 2.0)
        print(f"  [PASS] Err: {e:.1f}")


class TestContactDetection(unittest.TestCase):
    """Test contact."""
    
    def setUp(self):
        self.cd = ContactDetection()
    
    def test_contact(self):
        """Should detect contact."""
        c = self.cd.is_in_contact(2.0)
        self.assertTrue(c)
        print(f"  [PASS] C: {c}")
    
    def test_magnitude(self):
        """Should compute magnitude."""
        m = self.cd.contact_force_magnitude(ForceTorque(3.0, 4.0, 0.0))
        self.assertEqual(m, 5.0)
        print(f"  [PASS] Mag: {m:.1f}")
    
    def test_normal(self):
        """Should estimate normal."""
        n = self.cd.contact_normal(ForceTorque(0.0, 0.0, 5.0))
        self.assertEqual(n, (0.0, 0.0, 1.0))
        print(f"  [PASS] N: {n}")


class TestForceControl(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.fc = ForceControl()
    
    def test_summary(self):
        """Should summarize."""
        s = self.fc.force_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
