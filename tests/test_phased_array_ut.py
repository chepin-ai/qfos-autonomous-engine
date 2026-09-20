"""
Unit tests for phased array UT module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from phased_array_ut import (ProbeElement, DelayLawGenerator,
                              BeamSteerer, SectorScanner,
                              DynamicDepthFocuser, PhasedArrayUT)


class TestDelayLawGenerator(unittest.TestCase):
    """Test delay law generator."""
    
    def setUp(self):
        self.dlg = DelayLawGenerator()
        self.elements = [ProbeElement(i * 1.0, 1.0, 5.0, 0.5) for i in range(8)]
    
    def test_steering(self):
        """Should compute steering delays."""
        d = self.dlg.steering_delays(self.elements, 30.0)
        self.assertEqual(len(d), 8)
        self.assertEqual(min(d), 0.0)
        print(f"  [PASS] Steer: {d[:3]}")
    
    def test_focusing(self):
        """Should compute focusing delays."""
        d = self.dlg.focusing_delays(self.elements, 50.0)
        self.assertEqual(len(d), 8)
        print(f"  [PASS] Focus: {d[:3]}")
    
    def test_combined(self):
        """Should compute combined delays."""
        d = self.dlg.combined_delays(self.elements, 30.0, 50.0)
        self.assertEqual(len(d), 8)
        self.assertEqual(min(d), 0.0)
        print("  [PASS] Combined")


class TestBeamSteerer(unittest.TestCase):
    """Test beam steerer."""
    
    def setUp(self):
        self.bs = BeamSteerer(16, 1.0)
    
    def test_steer(self):
        """Should steer."""
        d = self.bs.steer(45.0)
        self.assertEqual(len(d), 16)
        print("  [PASS] Steer")
    
    def test_aperture(self):
        """Should set aperture."""
        self.bs.set_aperture(4, 8)
        d = self.bs.steer(30.0)
        self.assertEqual(len(d), 8)
        print("  [PASS] Aperture")


class TestSectorScanner(unittest.TestCase):
    """Test sector scanner."""
    
    def setUp(self):
        self.ss = SectorScanner(BeamSteerer(16, 1.0), -30.0, 30.0, 5.0)
    
    def test_generate(self):
        """Should generate scan."""
        self.ss.generate_scan()
        self.assertGreater(self.ss.num_beams(), 0)
        print(f"  [PASS] Scan: {self.ss.num_beams()} beams")
    
    def test_beams(self):
        """Should have correct beam count."""
        self.ss.generate_scan()
        expected = int((60.0 / 5.0)) + 1
        self.assertEqual(self.ss.num_beams(), expected)
        print(f"  [PASS] Beams: {self.ss.num_beams()}")


class TestDynamicDepthFocuser(unittest.TestCase):
    """Test DDF."""
    
    def setUp(self):
        elements = [ProbeElement(i * 1.0, 1.0, 5.0, 0.5) for i in range(8)]
        self.ddf = DynamicDepthFocuser(DelayLawGenerator(), elements)
    
    def test_focus(self):
        """Should focus at depth."""
        d = self.ddf.focus_at_depth(50.0)
        self.assertEqual(len(d), 8)
        print("  [PASS] Focus")
    
    def test_scan(self):
        """Should scan depths."""
        result = self.ddf.depth_scan(20.0, 60.0, 20.0)
        self.assertEqual(len(result), 3)
        print(f"  [PASS] Scan: {len(result)} depths")


class TestPhasedArrayUT(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.pa = PhasedArrayUT()
    
    def test_sector_scan(self):
        """Should perform sector scan."""
        r = self.pa.perform_sector_scan()
        self.assertIn("beams", r)
        print(f"  [PASS] S-scan: {r}")
    
    def test_focus_depths(self):
        """Should focus depths."""
        r = self.pa.focus_depths(20.0, 60.0, 20.0)
        self.assertEqual(len(r), 3)
        print("  [PASS] Focus depths")
    
    def test_summary(self):
        """Should summarize."""
        s = self.pa.pa_summary()
        self.assertIn("elements", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
