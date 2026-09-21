"""
Unit tests for tactile sensing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tactile_sensing import (TactileReading, TactileArrayProcessing,
                             SlipDetectionFromTexture,
                             ForceDistributionEstimation,
                             MaterialIdentification,
                             TactileSensing)


class TestTactileArrayProcessing(unittest.TestCase):
    """Test array."""
    
    def setUp(self):
        self.tap = TactileArrayProcessing()
        self.readings = [TactileReading(0, 0, 1.0, 0.0, 0.0),
                         TactileReading(1, 0, 2.0, 0.0, 0.0),
                         TactileReading(0, 1, 0.5, 0.0, 0.0)]
    
    def test_force(self):
        """Should compute total force."""
        f = self.tap.total_force(self.readings)
        self.assertEqual(f, 3.5)
        print(f"  [PASS] F: {f:.1f}")
    
    def test_cop(self):
        """Should compute center of pressure."""
        c = self.tap.center_of_pressure(self.readings)
        self.assertAlmostEqual(c[0], (0*1.0 + 1*2.0 + 0*0.5) / 3.5, delta=1e-10)
        print(f"  [PASS] CoP: {c}")
    
    def test_map(self):
        """Should build pressure map."""
        m = self.tap.pressure_map(self.readings)
        self.assertEqual(m[0][0], 1.0)
        print(f"  [PASS] Map: {len(m)}x{len(m[0])}")


class TestSlipDetectionFromTexture(unittest.TestCase):
    """Test slip."""
    
    def setUp(self):
        self.sdft = SlipDetectionFromTexture()
    
    def test_variation(self):
        """Should compute variation."""
        r = [TactileReading(0, 0, 1.0, 0.0, 0.0),
             TactileReading(1, 0, 3.0, 0.0, 0.0)]
        v = self.sdft.texture_variation(r)
        self.assertGreater(v, 0)
        print(f"  [PASS] Var: {v:.2f}")
    
    def test_shear(self):
        """Should compute shear."""
        r = [TactileReading(0, 0, 1.0, 3.0, 4.0)]
        s = self.sdft.shear_magnitude(r)
        self.assertEqual(s, 5.0)
        print(f"  [PASS] Shear: {s:.1f}")
    
    def test_slip(self):
        """Should detect slip."""
        r = [TactileReading(0, 0, 1.0, 3.0, 4.0)]
        s = self.sdft.is_slipping(r, threshold=4.0)
        self.assertTrue(s)
        print(f"  [PASS] Slip: {s}")


class TestForceDistributionEstimation(unittest.TestCase):
    """Test force."""
    
    def setUp(self):
        self.fde = ForceDistributionEstimation()
    
    def test_area(self):
        """Should compute contact area."""
        r = [TactileReading(0, 0, 1.0, 0.0, 0.0),
             TactileReading(1, 0, 0.05, 0.0, 0.0)]
        a = self.fde.contact_area(r)
        self.assertEqual(a, 1)
        print(f"  [PASS] Area: {a}")
    
    def test_avg(self):
        """Should compute average."""
        r = [TactileReading(0, 0, 1.0, 0.0, 0.0),
             TactileReading(1, 0, 3.0, 0.0, 0.0)]
        a = self.fde.average_pressure(r)
        self.assertEqual(a, 2.0)
        print(f"  [PASS] Avg: {a:.1f}")
    
    def test_gradient(self):
        """Should compute gradient."""
        r = [TactileReading(0, 0, 1.0, 0.0, 0.0),
             TactileReading(3, 4, 5.0, 0.0, 0.0)]
        g = self.fde.pressure_gradient(r)
        self.assertGreater(g[0], 0)
        print(f"  [PASS] Grad: {g}")


class TestMaterialIdentification(unittest.TestCase):
    """Test material."""
    
    def setUp(self):
        self.mi = MaterialIdentification()
    
    def test_id(self):
        """Should identify."""
        m = self.mi.identify(0.9, 0.1)
        self.assertEqual(m, "metal")
        print(f"  [PASS] Mat: {m}")


class TestTactileSensing(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ts = TactileSensing()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ts.tactile_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
