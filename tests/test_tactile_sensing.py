"""
Unit tests for tactile sensing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tactile_sensing import (TactileReading, PressureDistribution,
                             SlipDetector,
                             TextureClassifier,
                             GraspForceEstimator,
                             TactileSensing)


class TestPressureDistribution(unittest.TestCase):
    """Test pressure."""
    
    def setUp(self):
        self.pd = PressureDistribution(5)
        self.readings = [
            TactileReading(0.2, 0.3, 10.0, 0.1, 0.1),
            TactileReading(0.5, 0.5, 20.0, 0.2, 0.0),
            TactileReading(0.8, 0.7, 15.0, 0.0, 0.1)
        ]
    
    def test_total_force(self):
        """Should compute total force."""
        F = self.pd.total_force(self.readings)
        self.assertEqual(F, 45.0)
        print(f"  [PASS] F: {F:.1f}")
    
    def test_cop(self):
        """Should compute COP."""
        cop = self.pd.center_of_pressure(self.readings)
        self.assertIsNotNone(cop)
        print(f"  [PASS] COP: ({cop[0]:.2f}, {cop[1]:.2f})")
    
    def test_map(self):
        """Should create map."""
        m = self.pd.pressure_map(self.readings)
        self.assertEqual(len(m), 5)
        print("  [PASS] Map")


class TestSlipDetector(unittest.TestCase):
    """Test slip."""
    
    def setUp(self):
        self.sd = SlipDetector(0.5)
    
    def test_shear(self):
        """Should compute shear."""
        s = self.sd.shear_magnitude(TactileReading(0.0, 0.0, 10.0, 0.3, 0.4))
        self.assertAlmostEqual(s, 0.5, delta=0.01)
        print(f"  [PASS] Shear: {s:.3f}")
    
    def test_slip(self):
        """Should detect slip."""
        self.assertTrue(self.sd.is_slipping(TactileReading(0.0, 0.0, 10.0, 0.5, 0.5)))
        print("  [PASS] Slip")
    
    def test_ratio(self):
        """Should compute ratio."""
        r = [TactileReading(0.0, 0.0, 10.0, 0.6, 0.0),
             TactileReading(0.0, 0.0, 10.0, 0.0, 0.0)]
        ratio = self.sd.slip_ratio(r)
        self.assertEqual(ratio, 0.5)
        print(f"  [PASS] Ratio: {ratio:.2f}")


class TestTextureClassifier(unittest.TestCase):
    """Test texture."""
    
    def setUp(self):
        self.tc = TextureClassifier()
    
    def test_roughness(self):
        """Should compute roughness."""
        r = [TactileReading(0.0, 0.0, 5.0, 0.0, 0.0),
             TactileReading(0.0, 0.0, 15.0, 0.0, 0.0)]
        rough = self.tc.roughness_index(r)
        self.assertGreater(rough, 0)
        print(f"  [PASS] R: {rough:.2f}")
    
    def test_classify(self):
        """Should classify."""
        r = [TactileReading(0.0, 0.0, 10.0, 0.0, 0.0)]
        c = self.tc.classify_texture(r)
        self.assertEqual(c, "smooth")
        print(f"  [PASS] Tex: {c}")


class TestGraspForceEstimator(unittest.TestCase):
    """Test grasp."""
    
    def setUp(self):
        self.gf = GraspForceEstimator(0.5)
    
    def test_required(self):
        """Should compute required force."""
        F = self.gf.required_normal_force(10.0, 2)
        self.assertEqual(F, 10.0)
        print(f"  [PASS] Freq: {F:.2f} N")
    
    def test_margin(self):
        """Should compute margin."""
        m = self.gf.safety_margin(15.0, 10.0)
        self.assertEqual(m, 1.5)
        print(f"  [PASS] Margin: {m:.2f}")


class TestTactileSensing(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ts = TactileSensing()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ts.tactile_summary()
        self.assertIn("capabilities", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
