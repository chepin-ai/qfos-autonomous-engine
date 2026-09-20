"""
Unit tests for shearography module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from shearography import (SpecklePattern, ShearImageGenerator,
                          PhaseDifferenceCalculator,
                          SpecklePatternAnalyzer,
                          DeformationDefectDetector,
                          Shearography)


class TestShearImageGenerator(unittest.TestCase):
    """Test generator."""
    
    def setUp(self):
        self.sig = ShearImageGenerator(2)
    
    def test_shear_x(self):
        """Should shear in x."""
        img = [1.0, 2.0, 3.0, 4.0]
        s = self.sig.shear_image(img, 2, 2, "x")
        self.assertEqual(len(s), 4)
        print(f"  [PASS] ShearX: {s}")
    
    def test_shear_y(self):
        """Should shear in y."""
        img = [1.0, 2.0, 3.0, 4.0]
        s = self.sig.shear_image(img, 2, 2, "y")
        self.assertEqual(len(s), 4)
        print(f"  [PASS] ShearY: {s}")
    
    def test_speckle(self):
        """Should generate speckle."""
        sp = self.sig.generate_speckle(10, 10)
        self.assertEqual(len(sp.intensity), 100)
        print("  [PASS] Speckle")


class TestPhaseDifferenceCalculator(unittest.TestCase):
    """Test phase."""
    
    def setUp(self):
        self.pdc = PhaseDifferenceCalculator()
    
    def test_diff(self):
        """Should compute phase diff."""
        ref = [1.0, 2.0, 3.0]
        defm = [1.5, 2.5, 3.5]
        d = self.pdc.phase_difference(ref, defm)
        self.assertEqual(len(d), 3)
        print(f"  [PASS] PD: {d}")
    
    def test_wrap(self):
        """Should wrap phase."""
        p = self.pdc.wrap_phase(4.0)
        self.assertLessEqual(abs(p), math.pi)
        print(f"  [PASS] Wrap: {p:.4f}")
    
    def test_unwrap(self):
        """Should unwrap phase."""
        wrapped = [0.0, math.pi - 0.1, -math.pi + 0.1]
        u = self.pdc.unwrap_phase(wrapped)
        self.assertEqual(len(u), 3)
        print(f"  [PASS] Unwrap: {u}")


class TestSpecklePatternAnalyzer(unittest.TestCase):
    """Test analyzer."""
    
    def setUp(self):
        self.spa = SpecklePatternAnalyzer()
    
    def test_contrast(self):
        """Should compute contrast."""
        sp = SpecklePattern([0.0, 0.5, 1.0, 0.5], 2, 2)
        c = self.spa.contrast(sp)
        self.assertGreater(c, 0)
        print(f"  [PASS] Cont: {c:.4f}")
    
    def test_correlation(self):
        """Should compute correlation."""
        sp1 = SpecklePattern([1.0, 2.0, 3.0, 4.0], 2, 2)
        sp2 = SpecklePattern([1.0, 2.0, 3.0, 4.0], 2, 2)
        corr = self.spa.correlation(sp1, sp2)
        self.assertAlmostEqual(corr, 1.0, places=5)
        print(f"  [PASS] Corr: {corr:.4f}")


class TestDeformationDefectDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.ddd = DeformationDefectDetector(0.5)
    
    def test_detect(self):
        """Should detect defects."""
        phase = [0.1, 0.1, 0.1, 1.0, 1.0, 0.1, 0.1, 0.1, 0.1]
        d = self.ddd.detect_defects(phase, 3, 3)
        self.assertGreater(len(d), 0)
        print(f"  [PASS] Def: {len(d)}")
    
    def test_no_defect(self):
        """Should not detect if uniform."""
        phase = [0.1] * 9
        d = self.ddd.detect_defects(phase, 3, 3)
        self.assertEqual(len(d), 0)
        print("  [PASS] NoDef")


class TestShearography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.sh = Shearography(2)
    
    def test_capture(self):
        """Should capture."""
        img = [1.0, 2.0, 3.0, 4.0]
        self.sh.capture_reference(img, 2, 2)
        self.assertEqual(len(self.sh.reference), 4)
        print("  [PASS] Cap")
    
    def test_inspect(self):
        """Should inspect."""
        ref = [1.0] * 9
        defm = [1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0]
        self.sh.capture_reference(ref, 3, 3)
        self.sh.capture_deformed(defm, 3, 3)
        r = self.sh.inspect(3, 3)
        self.assertIn("defects", r)
        print(f"  [PASS] Insp: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.sh.shearography_summary()
        self.assertIn("shear", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
