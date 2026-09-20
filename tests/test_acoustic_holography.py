"""
Unit tests for acoustic holography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from acoustic_holography import (HologramPlane, SpatialFourierTransform,
                                  BackPropagator, SoundFieldReconstructor,
                                  AcousticHolography)


class TestSpatialFourierTransform(unittest.TestCase):
    """Test SFT."""
    
    def setUp(self):
        self.sft = SpatialFourierTransform()
    
    def test_dft_1d(self):
        """Should compute 1D DFT."""
        s = [complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0)]
        d = self.sft.dft_1d(s)
        self.assertEqual(len(d), 4)
        self.assertAlmostEqual(d[0].real, 1.0, places=5)
        print("  [PASS] DFT1D")
    
    def test_idft_1d(self):
        """Should compute 1D IDFT."""
        s = [complex(1, 0), complex(0, 0), complex(0, 0), complex(0, 0)]
        d = self.sft.dft_1d(s)
        i = self.sft.idft_1d(d)
        self.assertAlmostEqual(i[0].real, 1.0, places=5)
        print("  [PASS] IDFT1D")
    
    def test_dft_2d(self):
        """Should compute 2D DFT."""
        m = [[complex(1, 0) for _ in range(4)] for _ in range(4)]
        d = self.sft.dft_2d(m)
        self.assertEqual(len(d), 4)
        print("  [PASS] DFT2D")
    
    def test_idft_2d(self):
        """Should compute 2D IDFT."""
        m = [[complex(1, 0) for _ in range(4)] for _ in range(4)]
        d = self.sft.dft_2d(m)
        i = self.sft.idft_2d(d)
        self.assertEqual(len(i), 4)
        print("  [PASS] IDFT2D")


class TestBackPropagator(unittest.TestCase):
    """Test back-propagator."""
    
    def setUp(self):
        self.bp = BackPropagator(1000.0)
    
    def test_wavenumber(self):
        """Should compute wavenumbers."""
        kx, ky = self.bp.wavenumber_components(4, 4, 0.1, 0.1)
        self.assertEqual(len(kx), 4)
        self.assertEqual(len(ky), 4)
        print("  [PASS] WN")
    
    def test_propagate(self):
        """Should propagate."""
        spec = [[complex(1, 0) for _ in range(4)] for _ in range(4)]
        p = self.bp.propagate(spec, 0.05, 0.1, 0.1)
        self.assertEqual(len(p), 4)
        print("  [PASS] Prop")


class TestSoundFieldReconstructor(unittest.TestCase):
    """Test reconstructor."""
    
    def setUp(self):
        sft = SpatialFourierTransform()
        bp = BackPropagator(1000.0)
        self.rec = SoundFieldReconstructor(sft, bp)
    
    def test_reconstruct(self):
        """Should reconstruct."""
        p = [[complex(1, 0) for _ in range(4)] for _ in range(4)]
        plane = HologramPlane(1.0, 1.0, 4, 4, 0.1, p)
        r = self.rec.reconstruct(plane, 0.05)
        self.assertEqual(len(r), 4)
        print("  [PASS] Recon")
    
    def test_intensity(self):
        """Should compute intensity."""
        p = [[complex(1, 0) for _ in range(4)] for _ in range(4)]
        i = self.rec.intensity(p)
        self.assertAlmostEqual(i[0][0], 1.0, places=5)
        print("  [PASS] Intensity")


class TestAcousticHolography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ah = AcousticHolography(1000.0)
    
    def test_record(self):
        """Should record."""
        p = [[complex(1, 0) for _ in range(4)] for _ in range(4)]
        self.ah.record_hologram(p)
        self.assertEqual(len(self.ah.planes), 1)
        print("  [PASS] Record")
    
    def test_reconstruct(self):
        """Should reconstruct."""
        p = [[complex(1, 0) for _ in range(4)] for _ in range(4)]
        self.ah.record_hologram(p)
        r = self.ah.reconstruct_at(0.05)
        self.assertEqual(len(r), 4)
        print("  [PASS] Reconstruct")
    
    def test_summary(self):
        """Should summarize."""
        s = self.ah.holography_summary()
        self.assertIn("frequency_Hz", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
