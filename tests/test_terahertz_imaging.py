"""
Unit tests for terahertz imaging module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from terahertz_imaging import (THzPulse, THzPulseGenerator,
                               TimeDomainSpectroscopy,
                               MaterialParameterExtractor,
                               THzImageReconstructor,
                               TerahertzImaging)


class TestTHzPulseGenerator(unittest.TestCase):
    """Test generator."""
    
    def setUp(self):
        self.tpg = THzPulseGenerator(1.0, 1.0)
    
    def test_gaussian(self):
        """Should generate Gaussian."""
        t = [0.0, 0.5, 1.0, 1.5, 2.0]
        p = self.tpg.generate_gaussian_pulse(t)
        self.assertEqual(len(p.amplitude), 5)
        print(f"  [PASS] Gau: max={max(p.amplitude):.4f}")
    
    def test_delta(self):
        """Should generate delta."""
        t = [-1.0, 0.0, 1.0]
        p = self.tpg.generate_delta_pulse(t)
        self.assertEqual(p.amplitude[1], 1.0)
        print(f"  [PASS] Del: {p.amplitude}")


class TestTimeDomainSpectroscopy(unittest.TestCase):
    """Test TDS."""
    
    def setUp(self):
        self.tds = TimeDomainSpectroscopy()
    
    def test_fft(self):
        """Should compute FFT."""
        p = THzPulse([0.0, 0.5, 1.0, 1.5],
                     [1.0, 0.5, -0.5, -1.0])
        f = self.tds.fft(p)
        self.assertIsNotNone(f.spectrum)
        print(f"  [PASS] FFT: {len(f.spectrum)} bins")
    
    def test_transfer(self):
        """Should compute transfer function."""
        ref = THzPulse([0.0, 0.5, 1.0], [1.0, 0.5, 0.0])
        sam = THzPulse([0.0, 0.5, 1.0], [0.8, 0.4, 0.0])
        tf = self.tds.transfer_function(ref, sam)
        self.assertGreater(len(tf), 0)
        print(f"  [PASS] TF: {len(tf)} pts")


class TestMaterialParameterExtractor(unittest.TestCase):
    """Test extractor."""
    
    def setUp(self):
        self.mpe = MaterialParameterExtractor()
    
    def test_refractive(self):
        """Should extract n."""
        tf = [complex(0.9, 0.1)]
        f = [1.0]
        n = self.mpe.refractive_index(tf, f, 1.0)
        self.assertGreater(len(n), 0)
        print(f"  [PASS] n: {n[0]:.4f}")
    
    def test_absorption(self):
        """Should extract alpha."""
        tf = [complex(0.5, 0.0)]
        f = [1.0]
        a = self.mpe.absorption_coefficient(tf, f, 1.0)
        self.assertGreater(len(a), 0)
        print(f"  [PASS] alpha: {a[0]:.4f}")


class TestTHzImageReconstructor(unittest.TestCase):
    """Test reconstructor."""
    
    def setUp(self):
        self.tir = THzImageReconstructor(4, 4)
    
    def test_amplitude(self):
        """Should reconstruct amplitude."""
        scans = [[0.0, 1.0, 0.0]] * 16
        img = self.tir.reconstruct_amplitude(scans)
        self.assertEqual(len(img), 4)
        print(f"  [PASS] Amp: {len(img)}x{len(img[0])}")


class TestTerahertzImaging(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.thz = TerahertzImaging()
    
    def test_capture_ref(self):
        """Should capture reference."""
        self.thz.capture_reference([0.0, 0.5, 1.0])
        self.assertEqual(len(self.thz.reference.amplitude), 3)
        print("  [PASS] Ref")
    
    def test_capture_sample(self):
        """Should capture sample."""
        self.thz.capture_sample([0.0, 0.5, 1.0], [0.8, 0.4, 0.0])
        self.assertEqual(len(self.thz.samples), 1)
        print("  [PASS] Sam")
    
    def test_analyze(self):
        """Should analyze."""
        self.thz.capture_reference([0.0, 0.5, 1.0, 1.5])
        self.thz.capture_sample([0.0, 0.5, 1.0, 1.5], [0.8, 0.4, 0.0, 0.0])
        r = self.thz.analyze(1.0)
        self.assertIn("refractive_index", r)
        print(f"  [PASS] Anlz: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.thz.thz_summary()
        self.assertIn("samples", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
