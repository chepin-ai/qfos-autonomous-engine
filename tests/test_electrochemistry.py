"""
Unit tests for electrochemistry module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from electrochemistry import (VoltammetryPoint, CyclicVoltammetry,
                              TafelAnalysis,
                              CorrosionAnalyzer,
                              Potentiostat,
                              Electrochemistry)


class TestCyclicVoltammetry(unittest.TestCase):
    """Test CV."""
    
    def setUp(self):
        self.cv = CyclicVoltammetry(0.1)
    
    def test_randles_sevcik(self):
        """Should compute peak current."""
        ip = self.cv.peak_current_randles_sevcik(1, 1.0, 1.0, 1e-5)
        self.assertGreater(ip, 0)
        print(f"  [PASS] ip: {ip:.4f}")
    
    def test_peaks(self):
        """Should find peaks."""
        data = [VoltammetryPoint(0.0, 0.0, 0.0),
                VoltammetryPoint(0.5, 1e-6, 5.0),
                VoltammetryPoint(1.0, 0.0, 10.0)]
        p = self.cv.find_peaks(data)
        self.assertIn("anodic_potential_V", p)
        print(f"  [PASS] Peaks: {p}")
    
    def test_formal(self):
        """Should compute formal potential."""
        e = self.cv.formal_potential(0.6, 0.4)
        self.assertEqual(e, 0.5)
        print(f"  [PASS] E0: {e}")


class TestTafelAnalysis(unittest.TestCase):
    """Test Tafel."""
    
    def setUp(self):
        self.ta = TafelAnalysis()
    
    def test_slope(self):
        """Should compute Tafel slope."""
        b = self.ta.tafel_slope(0.1, 1e-3, 1e-6)
        self.assertNotEqual(b, 0)
        print(f"  [PASS] Tafel: {b:.4f}")
    
    def test_exchange(self):
        """Should compute exchange current."""
        i0 = self.ta.exchange_current_from_tafel(0.12, 0.1, 1e-3)
        self.assertGreater(i0, 0)
        print(f"  [PASS] i0: {i0:.6f}")


class TestCorrosionAnalyzer(unittest.TestCase):
    """Test corrosion."""
    
    def setUp(self):
        self.ca = CorrosionAnalyzer()
    
    def test_rate(self):
        """Should compute corrosion rate."""
        r = self.ca.corrosion_rate_mpy(100.0, 27.9, 7.87)
        self.assertGreater(r, 0)
        print(f"  [PASS] MPY: {r:.2f}")
    
    def test_rp(self):
        """Should compute from Rp."""
        icorr = self.ca.polarization_resistance(0.12, 0.12, 1000.0, 0.0)
        self.assertGreater(icorr, 0)
        print(f"  [PASS] icorr: {icorr:.6f}")


class TestPotentiostat(unittest.TestCase):
    """Test potentiostat."""
    
    def setUp(self):
        self.ps = Potentiostat(10.0)
    
    def test_apply(self):
        """Should apply potential."""
        p = self.ps.apply_potential(0.5, 1e-6, 1.0)
        self.assertEqual(p.potential_V, 0.5)
        print("  [PASS] Apply")
    
    def test_sweep(self):
        """Should sweep."""
        data = self.ps.sweep(0.0, 1.0, 5, lambda v: v * 1e-6)
        self.assertEqual(len(data), 5)
        print(f"  [PASS] Sweep: {len(data)}")


class TestElectrochemistry(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ec = Electrochemistry()
    
    def test_analyze(self):
        """Should analyze CV."""
        data = [VoltammetryPoint(0.0, 0.0, 0.0),
                VoltammetryPoint(0.5, 1e-6, 5.0),
                VoltammetryPoint(1.0, -1e-6, 10.0)]
        r = self.ec.analyze_cv(data)
        self.assertIn("peak_separation_V", r)
        print(f"  [PASS] Anlz: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.ec.ec_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
