"""
Unit tests for automated UT scanner module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from automated_ut_scanner import (ScanPattern, ScanPoint,
                                   UTProbe, ScanPathPlanner,
                                   EncoderTracker, DefectReporter,
                                   AutomatedUTScanner)


class TestUTProbe(unittest.TestCase):
    """Test UT probe."""
    
    def setUp(self):
        self.probe = UTProbe(0, 10.0, 5.0)
    
    def test_beam_spread(self):
        """Should compute beam spread."""
        s = self.probe.beam_spread_deg()
        self.assertGreater(s, 0)
        print(f"  [PASS] Spread: {s:.4f} deg")
    
    def test_near_field(self):
        """Should compute near field."""
        nf = self.probe.near_field_mm()
        self.assertGreater(nf, 0)
        print(f"  [PASS] NF: {nf:.4f} mm")


class TestScanPathPlanner(unittest.TestCase):
    """Test path planner."""
    
    def setUp(self):
        self.planner = ScanPathPlanner((100.0, 100.0), 10.0)
    
    def test_raster(self):
        """Should generate raster path."""
        path = self.planner.raster_path()
        self.assertGreater(len(path), 0)
        print(f"  [PASS] Raster: {len(path)} points")
    
    def test_spiral(self):
        """Should generate spiral path."""
        path = self.planner.spiral_path((50.0, 50.0), 40.0)
        self.assertGreater(len(path), 0)
        print(f"  [PASS] Spiral: {len(path)} points")
    
    def test_coverage(self):
        """Should compute coverage."""
        c = self.planner.coverage_percent(10.0)
        self.assertGreater(c, 0)
        print(f"  [PASS] Cov: {c:.1f}%")


class TestEncoderTracker(unittest.TestCase):
    """Test encoder."""
    
    def setUp(self):
        self.enc = EncoderTracker(100.0)
    
    def test_position(self):
        """Should compute position."""
        self.enc.update(500, 300)
        x, y = self.enc.position_mm()
        self.assertEqual(x, 5.0)
        self.assertEqual(y, 3.0)
        print(f"  [PASS] Pos: ({x}, {y})")
    
    def test_reset(self):
        """Should reset."""
        self.enc.update(100, 100)
        self.enc.reset()
        self.assertEqual(self.enc.x_counts, 0)
        print("  [PASS] Reset")


class TestDefectReporter(unittest.TestCase):
    """Test reporter."""
    
    def setUp(self):
        self.rep = DefectReporter()
    
    def test_add(self):
        """Should add defect."""
        self.rep.add_defect(10.0, 20.0, 15.0, 5.0)
        self.assertEqual(self.rep.defect_count(), 1)
        print("  [PASS] Add")
    
    def test_critical(self):
        """Should count critical."""
        self.rep.add_defect(0.0, 0.0, 25.0)
        self.assertEqual(self.rep.critical_count(), 1)
        print("  [PASS] Crit")


class TestAutomatedUTScanner(unittest.TestCase):
    """Test unified scanner."""
    
    def setUp(self):
        self.scanner = AutomatedUTScanner((100.0, 100.0))
    
    def test_plan_raster(self):
        """Should plan raster."""
        self.scanner.plan_raster(10.0)
        self.assertGreater(len(self.scanner.path), 0)
        print(f"  [PASS] Plan: {len(self.scanner.path)} pts")
    
    def test_record(self):
        """Should record point."""
        self.scanner.record_point(500, 300, 20.0, 5.0)
        self.assertEqual(len(self.scanner.scan_data), 1)
        print("  [PASS] Rec")
    
    def test_summary(self):
        """Should summarize."""
        self.scanner.plan_raster(20.0)
        self.scanner.record_point(0, 0, 5.0)
        s = self.scanner.scanner_summary()
        self.assertIn("path_points", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
