"""
Unit tests for corrosion testing module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from corrosion_testing import (EISPoint, PolarizationCurve,
                               TafelAnalysis,
                               PittingPotential,
                               ElectrochemicalImpedance,
                               CorrosionTesting)


class TestPolarizationCurve(unittest.TestCase):
    """Test polarization."""
    
    def setUp(self):
        self.pc = PolarizationCurve(0.12, -0.12)
    
    def test_icorr(self):
        """Should compute corrosion current."""
        i = self.pc.corrosion_current(100.0)
        self.assertGreater(i, 0)
        print(f"  [PASS] icorr: {i:.6e}")
    
    def test_rate(self):
        """Should compute corrosion rate."""
        cr = self.pc.corrosion_rate_mpy(1e-6)
        self.assertGreater(cr, 0)
        print(f"  [PASS] CR: {cr:.4f} mpy")
    
    def test_tafel(self):
        """Should compute Tafel potential."""
        E = self.pc.tafel_potential(-0.5, 1e-5, 1e-6, 0.12)
        self.assertGreater(E, -0.5)
        print(f"  [PASS] E: {E:.3f} V")


class TestTafelAnalysis(unittest.TestCase):
    """Test Tafel."""
    
    def setUp(self):
        self.ta = TafelAnalysis()
    
    def test_extrapolate(self):
        """Should extrapolate."""
        i = self.ta.extrapolate_icorr([-0.6, -0.5, -0.4], [1e-7, 1e-6, 1e-5], -0.5)
        self.assertGreater(i, 0)
        print(f"  [PASS] icorr: {i:.0e}")
    
    def test_slope(self):
        """Should compute slope."""
        s = self.ta.tafel_slope([0.0, 1.0], [-0.5, -0.38])
        self.assertAlmostEqual(s, 0.12, delta=0.01)
        print(f"  [PASS] beta: {s:.2f}")


class TestPittingPotential(unittest.TestCase):
    """Test pitting."""
    
    def setUp(self):
        self.pp = PittingPotential()
    
    def test_pitting(self):
        """Should find pitting potential."""
        Ep = self.pp.pitting_potential([-0.5, -0.4, -0.3], [1e-7, 1e-6, 1e-4], 1e-5)
        self.assertIsNotNone(Ep)
        print(f"  [PASS] Epit: {Ep:.2f} V")
    
    def test_protection(self):
        """Should find protection potential."""
        Epr = self.pp.protection_potential([-0.3, -0.4, -0.5], [1e-4, 1e-6, 1e-7], 1e-5)
        self.assertIsNotNone(Epr)
        print(f"  [PASS] Eprot: {Epr:.2f} V")


class TestElectrochemicalImpedance(unittest.TestCase):
    """Test EIS."""
    
    def setUp(self):
        self.eis = ElectrochemicalImpedance()
    
    def test_magnitude(self):
        """Should compute |Z|."""
        z = self.eis.impedance_magnitude(100.0, -50.0)
        self.assertAlmostEqual(z, math.sqrt(10000 + 2500), delta=0.1)
        print(f"  [PASS] |Z|: {z:.1f}")
    
    def test_phase(self):
        """Should compute phase."""
        phi = self.eis.phase_angle(100.0, -50.0)
        self.assertLess(phi, 0)
        print(f"  [PASS] phi: {phi:.1f} deg")
    
    def test_rp(self):
        """Should extract Rp."""
        points = [EISPoint(0.1, 100.0, -10.0), EISPoint(1.0, 80.0, -5.0)]
        rp = self.eis.polarization_resistance(points)
        self.assertGreater(rp, 0)
        print(f"  [PASS] Rp: {rp:.1f} Ohm")


class TestCorrosionTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ct = CorrosionTesting()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ct.corrosion_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
