"""
Unit tests for microwave testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from microwave_testing import (MicrowaveMode, SParameter,
                                DielectricEstimator, MicrowaveAntenna,
                                SubsurfaceImager, MicrowaveTesting)


class TestDielectricEstimator(unittest.TestCase):
    """Test dielectric estimator."""
    
    def setUp(self):
        self.de = DielectricEstimator(10.0)
    
    def test_permittivity(self):
        """Should estimate permittivity."""
        eps = self.de.permittivity_from_reflection(0.5, 0.0, 10.0)
        self.assertGreater(eps.real, 1.0)
        print(f"  [PASS] Eps: {eps}")
    
    def test_loss_tangent(self):
        """Should compute loss tangent."""
        tan = self.de.loss_tangent(complex(4.0, 0.1))
        self.assertGreater(tan, 0)
        print(f"  [PASS] Tan: {tan:.4f}")
    
    def test_penetration(self):
        """Should compute penetration."""
        d = self.de.penetration_depth_mm(10.0, complex(4.0, 0.1))
        self.assertGreater(d, 0)
        print(f"  [PASS] Pen: {d:.4f} mm")


class TestMicrowaveAntenna(unittest.TestCase):
    """Test antenna."""
    
    def setUp(self):
        self.ant = MicrowaveAntenna(10.0, 50.0)
    
    def test_beamwidth(self):
        """Should compute beamwidth."""
        bw = self.ant.beamwidth_deg()
        self.assertGreater(bw, 0)
        print(f"  [PASS] BW: {bw:.4f} deg")
    
    def test_near_field(self):
        """Should compute near field."""
        nf = self.ant.near_field_mm()
        self.assertGreater(nf, 0)
        print(f"  [PASS] NF: {nf:.4f} mm")


class TestSubsurfaceImager(unittest.TestCase):
    """Test imager."""
    
    def setUp(self):
        self.img = SubsurfaceImager(5.0)
    
    def test_bscan(self):
        """Should generate B-scan."""
        a_scans = [[1.0, 0.5, 0.2], [1.0, 0.6, 0.3]]
        b = self.img.bscan(a_scans)
        self.assertEqual(len(b), 3)
        print(f"  [PASS] B-scan: {len(b)}x{len(b[0])}")
    
    def test_cscan(self):
        """Should extract C-scan."""
        b = [[1.0, 2.0], [0.5, 0.6], [0.2, 0.3]]
        c = self.img.cscan(b, 0)
        self.assertEqual(len(c), 2)
        print("  [PASS] C-scan")


class TestMicrowaveTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.mwt = MicrowaveTesting()
    
    def test_measure(self):
        """Should record measurement."""
        self.mwt.measure_reflection(10.0, 0.5, 0.0)
        self.assertEqual(len(self.mwt.measurements), 1)
        print("  [PASS] Meas")
    
    def test_analyze(self):
        """Should analyze."""
        self.mwt.measure_reflection(10.0, 0.5, 0.0)
        r = self.mwt.analyze_permittivity(0)
        self.assertIn("permittivity_real", r)
        print(f"  [PASS] Ana: eps'={r['permittivity_real']:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.mwt.microwave_summary()
        self.assertIn("measurements", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
