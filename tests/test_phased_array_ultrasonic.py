"""
Unit tests for phased array ultrasonic module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from phased_array_ultrasonic import (AScan, PAElement, PAProbe,
                                      SectorialScan, TotalFocusingMethod,
                                      PhasedArrayUltrasonic)


class TestPAElement(unittest.TestCase):
    """Test PA element."""
    
    def setUp(self):
        self.elem = PAElement(0, 0.0, 1.0, 5.0)
    
    def test_delay_angle(self):
        """Should compute delay."""
        d = self.elem.delay_for_angle(30.0)
        self.assertEqual(d, 0.0)
        print(f"  [PASS] Delay: {d:.4f}")
    
    def test_focal_delay(self):
        """Should compute focal delay."""
        d = self.elem.focal_delay(50.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Focal: {d:.4f}")


class TestPAProbe(unittest.TestCase):
    """Test PA probe."""
    
    def setUp(self):
        self.probe = PAProbe(16, 1.0, 5.0)
    
    def test_focal_law(self):
        """Should compute focal law."""
        delays = self.probe.focal_law(30.0, 50.0)
        self.assertEqual(len(delays), 16)
        self.assertEqual(delays[0], 0.0)
        print(f"  [PASS] Law: {len(delays)} delays")
    
    def test_beam_spread(self):
        """Should compute beam spread."""
        spread = self.probe.beam_spread(0.0)
        self.assertGreater(spread, 0)
        print(f"  [PASS] Spread: {spread:.4f} deg")


class TestSectorialScan(unittest.TestCase):
    """Test sectorial scan."""
    
    def setUp(self):
        self.probe = PAProbe(8)
        self.scan = SectorialScan(self.probe)
    
    def test_set_angles(self):
        """Should set angles."""
        self.scan.set_angles(30.0, 70.0, 5.0)
        self.assertGreater(len(self.scan.angles), 0)
        print(f"  [PASS] Angles: {len(self.scan.angles)}")
    
    def test_simulate(self):
        """Should simulate A-scan."""
        self.scan.set_angles(30.0, 30.0)
        scans = self.scan.simulate_ascan(30.0, [(50.0, 1.0, 0.0)])
        self.assertEqual(len(scans), 1)
        print(f"  [PASS] Sim: {scans[0].depth_mm} mm")
    
    def test_bscan(self):
        """Should generate B-scan."""
        self.scan.set_angles(30.0, 30.0)
        self.scan.simulate_ascan(30.0, [(50.0, 1.0, 0.0)])
        img = self.scan.bscan_image()
        self.assertGreater(len(img), 0)
        print(f"  [PASS] B-scan: {len(img)}x{len(img[0])}")


class TestTFM(unittest.TestCase):
    """Test TFM."""
    
    def setUp(self):
        self.probe = PAProbe(4)
        self.tfm = TotalFocusingMethod(self.probe)
    
    def test_add_channel(self):
        """Should add FMC channel."""
        self.tfm.add_fmc_channel(0, 0, [AScan(0, 10.0, 1.0, 50.0)])
        self.assertEqual(len(self.tfm.fmc_data), 1)
        print("  [PASS] FMC")
    
    def test_tfm_image(self):
        """Should generate TFM image."""
        self.tfm.add_fmc_channel(0, 0, [AScan(0, 10.0, 1.0, 50.0)])
        img = self.tfm.tfm_image([0.0, 1.0], [10.0, 20.0])
        self.assertEqual(len(img), 2)
        print(f"  [PASS] TFM: {len(img)}x{len(img[0])}")


class TestPhasedArrayUltrasonic(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.paut = PhasedArrayUltrasonic(8)
    
    def test_sector_scan(self):
        """Should sector scan."""
        self.paut.sector_scan(30.0, 40.0, [(50.0, 1.0, 0.0)])
        s = self.paut.paut_summary()
        self.assertGreater(s["sector_angles"], 0)
        print(f"  [PASS] Sector: {s}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.paut.paut_summary()
        self.assertIn("elements", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
