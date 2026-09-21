"""
Unit tests for XRD analysis module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xrd_analysis import (XRDPeak, BraggLaw,
                          PeakDetector,
                          PhaseIdentifier,
                          XRDAnalysis)


class TestBraggLaw(unittest.TestCase):
    """Test Bragg."""
    
    def setUp(self):
        self.b = BraggLaw(1.5406)
    
    def test_d_spacing(self):
        """Should compute d."""
        d = self.b.d_spacing(44.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] d: {d:.3f} A")
    
    def test_two_theta(self):
        """Should compute 2theta."""
        t = self.b.two_theta(2.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] 2th: {t:.1f} deg")
    
    def test_lattice(self):
        """Should compute lattice parameter."""
        a = self.b.lattice_parameter(2.0, (1, 1, 1))
        self.assertGreater(a, 0)
        print(f"  [PASS] a: {a:.3f} A")


class TestPeakDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.pd = PeakDetector(0.1)
    
    def test_find_peaks(self):
        """Should find peaks."""
        tt = [20.0, 30.0, 35.0, 40.0, 44.0, 50.0]
        I = [10.0, 20.0, 100.0, 30.0, 80.0, 15.0]
        peaks = self.pd.find_peaks(tt, I)
        self.assertGreater(len(peaks), 0)
        print(f"  [PASS] Peaks: {len(peaks)}")
    
    def test_gaussian_fit(self):
        """Should fit."""
        x = [30.0, 35.0, 40.0]
        y = [20.0, 100.0, 20.0]
        fit = self.pd.gaussian_fit(x, y, 35.0)
        self.assertGreater(fit["amplitude"], 0)
        print(f"  [PASS] Fit: A={fit['amplitude']:.1f}")


class TestPhaseIdentifier(unittest.TestCase):
    """Test phase ID."""
    
    def setUp(self):
        self.pi = PhaseIdentifier()
        self.pi.add_reference("Si", [(3.135, 100.0), (1.920, 55.0)])
        self.pi.add_reference("Al", [(2.338, 100.0), (2.024, 47.0)])
    
    def test_identify(self):
        """Should identify."""
        peaks = [XRDPeak(28.4, 100.0, 3.135),
                 XRDPeak(47.3, 55.0, 1.920)]
        results = self.pi.identify(peaks, 0.1)
        self.assertGreater(len(results), 0)
        print(f"  [PASS] ID: {results[0]['phase']}")


class TestXRDAnalysis(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.xrd = XRDAnalysis()
    
    def test_summary(self):
        """Should summarize."""
        s = self.xrd.xrd_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
