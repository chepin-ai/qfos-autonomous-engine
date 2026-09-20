"""
Unit tests for penetrant inspection module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from penetrant_inspection import (IndicationType, SensitivityLevel,
                                  Indication, DyePenetrant,
                                  Developer, IndicationDetector,
                                  SensitivityAnalyzer,
                                  PenetrantInspection)


class TestDyePenetrant(unittest.TestCase):
    """Test dye penetrant."""
    
    def setUp(self):
        self.dp = DyePenetrant(SensitivityLevel.HIGH)
    
    def test_penetration(self):
        """Should estimate depth."""
        d = self.dp.penetration_depth(5.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Depth: {d:.2f}mm")
    
    def test_visibility(self):
        """Should compute visibility."""
        v = self.dp.visibility_score(0.3)
        self.assertGreater(v, 0)
        self.assertLessEqual(v, 1.0)
        print(f"  [PASS] Vis: {v:.3f}")
    
    def test_sensitivity(self):
        """Should have correct sensitivity."""
        self.assertEqual(self.dp.sensitivity, SensitivityLevel.HIGH)
        print("  [PASS] Sens")


class TestDeveloper(unittest.TestCase):
    """Test developer."""
    
    def setUp(self):
        self.dev = Developer()
    
    def test_extract(self):
        """Should extract indication."""
        ind = self.dev.extract_indication(0.8, 0.2)
        self.assertAlmostEqual(ind, 0.6)
        print("  [PASS] Extract")
    
    def test_spreading(self):
        """Should compute spreading."""
        s = self.dev.spreading_factor(2.0)
        self.assertGreater(s, 1.0)
        print(f"  [PASS] Spread: {s:.3f}")


class TestIndicationDetector(unittest.TestCase):
    """Test indication detector."""
    
    def setUp(self):
        self.id = IndicationDetector()
    
    def test_detect(self):
        """Should detect indications."""
        intensities = [0.05, 0.05, 0.3, 0.5, 0.3, 0.05, 0.05]
        positions = [(float(i), 0.0) for i in range(len(intensities))]
        inds = self.id.detect(intensities, positions)
        self.assertGreater(len(inds), 0)
        print(f"  [PASS] Inds: {len(inds)}")
    
    def test_rejectable(self):
        """Should identify rejectable."""
        ind = Indication(0, 0, 5.0, 1.0, 0.8, IndicationType.CRACK)
        self.assertTrue(self.id.rejectable(ind, 3.0))
        print("  [PASS] Reject")
    
    def test_linear(self):
        """Should filter linear."""
        inds = [
            Indication(0, 0, 10.0, 1.0, 0.8, IndicationType.CRACK),
            Indication(1, 0, 2.0, 2.0, 0.5, IndicationType.POROSITY)
        ]
        linear = self.id.linear_indications(inds)
        self.assertEqual(len(linear), 1)
        print("  [PASS] Linear")


class TestSensitivityAnalyzer(unittest.TestCase):
    """Test sensitivity analyzer."""
    
    def setUp(self):
        self.sa = SensitivityAnalyzer()
    
    def test_mds(self):
        """Should estimate MDS."""
        self.sa.calibrate(20.0, 0.5)
        self.sa.calibrate(10.0, 0.3)
        mds = self.sa.minimum_detectable_size()
        self.assertEqual(mds, 10.0)
        print(f"  [PASS] MDS: {mds}")
    
    def test_probability(self):
        """Should compute detection probability."""
        self.sa.calibrate(10.0, 0.5)
        p = self.sa.detection_probability(20.0)
        self.assertGreater(p, 0.5)
        print(f"  [PASS] Prob: {p:.3f}")


class TestPenetrantInspection(unittest.TestCase):
    """Test unified penetrant inspection."""
    
    def setUp(self):
        self.pi = PenetrantInspection()
    
    def test_inspect(self):
        """Should inspect."""
        intensities = [0.05] * 5 + [0.5, 0.6, 0.5] + [0.05] * 5
        positions = [(float(i), 0.0) for i in range(len(intensities))]
        r = self.pi.inspect(intensities, positions)
        self.assertIn("indications", r)
        print(f"  [PASS] Insp: inds={r['indications']}")
    
    def test_set_sensitivity(self):
        """Should set sensitivity."""
        self.pi.set_sensitivity(SensitivityLevel.VERY_HIGH)
        self.assertEqual(self.pi.penetrant.sensitivity, SensitivityLevel.VERY_HIGH)
        print("  [PASS] SetSens")
    
    def test_summary(self):
        """Should summarize."""
        intensities = [0.05] * 10
        positions = [(float(i), 0.0) for i in range(10)]
        self.pi.inspect(intensities, positions)
        s = self.pi.inspection_summary()
        self.assertIn("inspections", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
