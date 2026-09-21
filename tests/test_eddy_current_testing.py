"""
Unit tests for eddy current testing module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from eddy_current_testing import (ImpedancePoint, ImpedanceAnalyzer,
                                  FlawDetector,
                                  ConductivityMeter,
                                  LiftOffCompensator,
                                  EddyCurrentTesting)


class TestImpedanceAnalyzer(unittest.TestCase):
    """Test impedance."""
    
    def setUp(self):
        self.ia = ImpedanceAnalyzer(1e-3, 10.0)
    
    def test_impedance(self):
        """Should compute impedance."""
        R, X = self.ia.impedance(1000.0, 5.0, 2.0)
        self.assertGreater(R, 0)
        print(f"  [PASS] Z: R={R:.1f}, X={X:.2f}")
    
    def test_magnitude(self):
        """Should compute magnitude."""
        m = self.ia.magnitude(10.0, 10.0)
        self.assertAlmostEqual(m, math.sqrt(200), delta=0.1)
        print(f"  [PASS] Mag: {m:.2f}")
    
    def test_phase(self):
        """Should compute phase."""
        p = self.ia.phase_angle(10.0, 10.0)
        self.assertAlmostEqual(p, 45.0, delta=0.1)
        print(f"  [PASS] Ph: {p:.1f} deg")
    
    def test_skin_depth(self):
        """Should compute skin depth."""
        d = self.ia.skin_depth(1e7, 1000.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] SD: {d:.4f} m")


class TestFlawDetector(unittest.TestCase):
    """Test flaw detection."""
    
    def setUp(self):
        self.fd = FlawDetector(5.0)
    
    def test_detect(self):
        """Should detect flaws."""
        base = [ImpedancePoint(1000.0, 10.0, 5.0)]
        meas = [ImpedancePoint(1000.0, 15.0, 5.0)]
        flaws = self.fd.detect_from_impedance(base, meas)
        self.assertGreater(len(flaws), 0)
        print(f"  [PASS] Flaws: {len(flaws)}")
    
    def test_depth(self):
        """Should estimate depth."""
        d = self.fd.crack_depth_estimate(20.0, 1e-3)
        self.assertGreater(d, 0)
        print(f"  [PASS] D: {d:.4f} m")


class TestConductivityMeter(unittest.TestCase):
    """Test conductivity."""
    
    def setUp(self):
        self.cm = ConductivityMeter()
    
    def test_conductivity(self):
        """Should compute conductivity."""
        c = self.cm.conductivity_from_impedance(1e-6, 1e-3, 1e-6)
        self.assertGreater(c, 0)
        print(f"  [PASS] Cond: {c:.2e} S/m")
    
    def test_iacs(self):
        """Should convert to IACS."""
        iacs = self.cm.iacs_conductivity(5.8e7)
        self.assertAlmostEqual(iacs, 100.0, delta=0.1)
        print(f"  [PASS] IACS: {iacs:.1f}%")


class TestLiftOffCompensator(unittest.TestCase):
    """Test lift-off."""
    
    def setUp(self):
        self.lo = LiftOffCompensator()
    
    def test_compensate(self):
        """Should compensate."""
        R, X = self.lo.compensated_impedance(10.0, 5.0, 2e-3, 1e-3)
        self.assertAlmostEqual(R, 5.0, delta=0.1)
        print(f"  [PASS] Comp: R={R:.1f}, X={X:.1f}")


class TestEddyCurrentTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ect = EddyCurrentTesting()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ect.ect_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
