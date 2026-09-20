"""
Unit tests for eddy current testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from eddy_current_testing import (CoilMeasurement, ImpedanceAnalyzer,
                                  CrackDetector,
                                  LiftOffCompensator,
                                  MaterialPropertyEvaluator,
                                  EddyCurrentTesting)


class TestImpedanceAnalyzer(unittest.TestCase):
    """Test analyzer."""
    
    def setUp(self):
        self.ia = ImpedanceAnalyzer()
        self.m = CoilMeasurement(10000.0, 50.0, 30.0, 0.5)
    
    def test_magnitude(self):
        """Should compute magnitude."""
        mag = self.ia.impedance_magnitude(self.m)
        self.assertAlmostEqual(mag, 58.31, places=1)
        print(f"  [PASS] Mag: {mag:.2f}")
    
    def test_phase(self):
        """Should compute phase."""
        p = self.ia.phase_angle(self.m)
        self.assertGreater(p, 0)
        print(f"  [PASS] Phase: {p:.4f}")
    
    def test_skin_depth(self):
        """Should compute skin depth."""
        d = self.ia.skin_depth(1e6, 4.0 * 3.14159 * 1e-7, 10000.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Skin: {d:.6f}")


class TestCrackDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.cd = CrackDetector(5.0)
        self.ref = CoilMeasurement(10000.0, 50.0, 30.0, 0.5)
    
    def test_detect(self):
        """Should detect crack."""
        scan = CoilMeasurement(10000.0, 55.0, 35.0, 0.5)
        d = self.cd.detect(self.ref, scan)
        self.assertTrue(d)
        print(f"  [PASS] Crack: {d}")
    
    def test_depth(self):
        """Should estimate depth."""
        d = self.cd.crack_depth_estimate(10.0, 0.5)
        self.assertEqual(d, 0.05)
        print(f"  [PASS] Depth: {d}")


class TestLiftOffCompensator(unittest.TestCase):
    """Test compensator."""
    
    def setUp(self):
        self.loc = LiftOffCompensator()
    
    def test_compensate(self):
        """Should compensate."""
        m = CoilMeasurement(10000.0, 50.0, 30.0, 1.0)
        c = self.loc.compensate(m, 0.5)
        self.assertAlmostEqual(c.lift_off_mm, 0.5)
        print("  [PASS] Comp")


class TestMaterialPropertyEvaluator(unittest.TestCase):
    """Test evaluator."""
    
    def setUp(self):
        self.mpe = MaterialPropertyEvaluator()
    
    def test_conductivity(self):
        """Should estimate conductivity."""
        s = self.mpe.conductivity(50.0, 5.0, 10000.0)
        self.assertGreater(s, 0)
        print(f"  [PASS] Cond: {s:.2f}")
    
    def test_permeability(self):
        """Should estimate permeability."""
        mu = self.mpe.permeability(30.0, 1e-3)
        self.assertGreater(mu, 0)
        print(f"  [PASS] Mu: {mu:.2f}")


class TestEddyCurrentTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ect = EddyCurrentTesting()
    
    def test_set_reference(self):
        """Should set reference."""
        m = CoilMeasurement(10000.0, 50.0, 30.0, 0.5)
        self.ect.set_reference(m)
        self.assertIsNotNone(self.ect.reference)
        print("  [PASS] Ref")
    
    def test_scan(self):
        """Should scan."""
        m = CoilMeasurement(10000.0, 55.0, 35.0, 0.5)
        self.ect.scan(m)
        self.assertEqual(len(self.ect.measurements), 1)
        print("  [PASS] Scan")
    
    def test_inspect(self):
        """Should inspect."""
        self.ect.set_reference(CoilMeasurement(10000.0, 50.0, 30.0, 0.5))
        self.ect.scan(CoilMeasurement(10000.0, 55.0, 35.0, 0.5))
        r = self.ect.inspect()
        self.assertIn("crack_indications", r)
        print(f"  [PASS] Insp: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.ect.ect_summary()
        self.assertIn("measurements", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
