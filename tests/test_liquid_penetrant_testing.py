"""
Unit tests for liquid penetrant testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from liquid_penetrant_testing import (PenetrantIndication, PenetrantApplicator,
                                      DeveloperApplicator,
                                      PenetrantIndicationDetector,
                                      LiquidPenetrantTesting)


class TestPenetrantApplicator(unittest.TestCase):
    """Test applicator."""
    
    def setUp(self):
        self.pa = PenetrantApplicator("visible", 5.0)
    
    def test_dwell(self):
        """Should compute dwell time."""
        t = self.pa.dwell_time(20.0, 20.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] Dwell: {t:.1f} min")
    
    def test_coverage(self):
        """Should compute coverage."""
        v = self.pa.coverage(10000.0)
        self.assertEqual(v, 10.0)
        print(f"  [PASS] Vol: {v} mL")


class TestDeveloperApplicator(unittest.TestCase):
    """Test developer."""
    
    def setUp(self):
        self.da = DeveloperApplicator("dry")
    
    def test_time(self):
        """Should compute dev time."""
        t = self.da.development_time("visible")
        self.assertEqual(t, 7.0)
        print(f"  [PASS] Dev: {t} min")
    
    def test_thickness(self):
        """Should compute thickness."""
        th = self.da.thickness()
        self.assertGreater(th, 0)
        print(f"  [PASS] Thick: {th:.4f} mm")


class TestPenetrantIndicationDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.det = PenetrantIndicationDetector(0.5, 0.1)
    
    def test_detect(self):
        """Should detect indications."""
        img = [
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.5, 0.5, 0.0],
            [0.0, 0.5, 0.5, 0.0],
            [0.0, 0.0, 0.0, 0.0]
        ]
        inds = self.det.detect(img, 1.0)
        self.assertEqual(len(inds), 1)
        print(f"  [PASS] Det: {len(inds)}")
    
    def test_classify(self):
        """Should classify."""
        ind = PenetrantIndication(0.0, 0.0, 2.0, 0.5, "linear")
        c = self.det.classify_defect(ind)
        self.assertEqual(c, "moderate")
        print(f"  [PASS] Cls: {c}")


class TestLiquidPenetrantTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.lpt = LiquidPenetrantTesting()
    
    def test_inspect(self):
        """Should inspect."""
        img = [
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.5, 0.5, 0.0],
            [0.0, 0.5, 0.5, 0.0],
            [0.0, 0.0, 0.0, 0.0]
        ]
        r = self.lpt.inspect(img, 1.0, 20.0)
        self.assertIn("indications", r)
        print(f"  [PASS] Insp: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.lpt.lpt_summary()
        self.assertIn("indications", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
