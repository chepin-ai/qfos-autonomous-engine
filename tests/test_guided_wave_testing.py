"""
Unit tests for guided wave testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from guided_wave_testing import (WaveMode, GuidedWaveSignal,
                                  DispersionCurve, WaveTransducer,
                                  DefectLocalizer, GuidedWaveTesting)


class TestDispersionCurve(unittest.TestCase):
    """Test dispersion curve."""
    
    def setUp(self):
        self.dc = DispersionCurve(5.0, 5.9)
    
    def test_lamb_velocity(self):
        """Should compute Lamb velocity."""
        v = self.dc.lamb_wave_velocity(1.0, "A0")
        self.assertGreater(v, 0)
        print(f"  [PASS] A0: {v:.4f}")
    
    def test_phase_velocity(self):
        """Should compute phase velocity."""
        vp = self.dc.phase_velocity(1.0, "S0")
        self.assertGreater(vp, 0)
        print(f"  [PASS] Vp: {vp:.4f}")
    
    def test_wavelength(self):
        """Should compute wavelength."""
        wl = self.dc.wavelength_mm(1.0, 3.0)
        self.assertEqual(wl, 3.0)
        print(f"  [PASS] WL: {wl}")


class TestWaveTransducer(unittest.TestCase):
    """Test transducer."""
    
    def setUp(self):
        self.t = WaveTransducer(0, 0.0, 0.0)
    
    def test_excite(self):
        """Should excite."""
        sigs = self.t.excite(1.0, 1.0, 5)
        self.assertEqual(len(sigs), 5)
        print(f"  [PASS] Excite: {len(sigs)} signals")


class TestDefectLocalizer(unittest.TestCase):
    """Test localizer."""
    
    def setUp(self):
        self.loc = DefectLocalizer([0.0, 100.0, 200.0])
    
    def test_tof(self):
        """Should compute TOF."""
        tof = self.loc.time_of_flight(100.0, 5.0)
        self.assertEqual(tof, 20.0)
        print(f"  [PASS] TOF: {tof}")
    
    def test_localize(self):
        """Should localize."""
        pos = self.loc.localize_1d(40.0, 5.0, 0.0)
        self.assertEqual(len(pos), 2)
        print(f"  [PASS] Loc: {pos}")


class TestGuidedWaveTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.gwut = GuidedWaveTesting(5.0)
    
    def test_add_transducer(self):
        """Should add transducer."""
        self.gwut.add_transducer(0.0)
        self.assertEqual(len(self.gwut.transducers), 1)
        print("  [PASS] AddT")
    
    def test_excite(self):
        """Should excite."""
        self.gwut.add_transducer(0.0)
        sigs = self.gwut.excite(0, 1.0)
        self.assertGreater(len(sigs), 0)
        print(f"  [PASS] Exc: {len(sigs)}")
    
    def test_analyze(self):
        """Should analyze."""
        r = self.gwut.analyze(20.0, 1.0, "A0")
        self.assertIn("velocity_mm_us", r)
        print(f"  [PASS] Ana: {r['velocity_mm_us']:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.gwut.gwut_summary()
        self.assertIn("transducers", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
