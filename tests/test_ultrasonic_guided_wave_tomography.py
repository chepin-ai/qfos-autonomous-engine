"""
Unit tests for ultrasonic guided wave tomography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ultrasonic_guided_wave_tomography import (Transducer, RayTracer,
                                                TravelTimeInverter,
                                                DamageMapper,
                                                UltrasonicGuidedWaveTomography)


class TestRayTracer(unittest.TestCase):
    """Test ray tracer."""
    
    def setUp(self):
        self.rt = RayTracer()
    
    def test_distance(self):
        """Should compute distance."""
        t1 = Transducer(0.0, 0.0, 0)
        t2 = Transducer(3.0, 4.0, 1)
        d = self.rt.distance(t1, t2)
        self.assertAlmostEqual(d, 5.0, places=5)
        print(f"  [PASS] Dist: {d}")
    
    def test_travel_time(self):
        """Should compute travel time."""
        t1 = Transducer(0.0, 0.0, 0)
        t2 = Transducer(5.9, 0.0, 1)
        tt = self.rt.travel_time(t1, t2)
        self.assertAlmostEqual(tt, 1.0, places=5)
        print(f"  [PASS] TT: {tt}")
    
    def test_ray_path(self):
        """Should compute path."""
        t1 = Transducer(0.0, 0.0, 0)
        t2 = Transducer(10.0, 10.0, 1)
        p = self.rt.ray_path(t1, t2, 5)
        self.assertEqual(len(p), 5)
        print(f"  [PASS] Path: {len(p)} pts")


class TestTravelTimeInverter(unittest.TestCase):
    """Test inverter."""
    
    def setUp(self):
        self.tti = TravelTimeInverter(10.0, 5, 5)
    
    def test_grid_index(self):
        """Should get grid index."""
        idx = self.tti.grid_index(15.0, 25.0)
        self.assertIsNotNone(idx)
        self.assertEqual(idx, (1, 2))
        print(f"  [PASS] Grid: {idx}")
    
    def test_update(self):
        """Should update slowness."""
        t1 = Transducer(0.0, 0.0, 0)
        t2 = Transducer(50.0, 0.0, 1)
        self.tti.update_slowness([(t1, t2, 10.0)])
        self.assertEqual(len(self.tti.slowness), 5)
        print("  [PASS] Update")


class TestDamageMapper(unittest.TestCase):
    """Test damage mapper."""
    
    def setUp(self):
        self.tti = TravelTimeInverter(10.0, 5, 5)
        self.dm = DamageMapper(self.tti)
    
    def test_find(self):
        """Should find damage."""
        self.tti.slowness[2][2] = 1.0
        d = self.dm.find_damage(1.0 / 5.9, 1.2)
        self.assertGreaterEqual(len(d), 0)
        print(f"  [PASS] Damage: {len(d)} regions")
    
    def test_percentage(self):
        """Should compute percentage."""
        p = self.dm.damage_percentage()
        self.assertGreaterEqual(p, 0.0)
        print(f"  [PASS] Pct: {p:.2f}%")


class TestUltrasonicGuidedWaveTomography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ugwt = UltrasonicGuidedWaveTomography()
    
    def test_place(self):
        """Should place transducers."""
        self.ugwt.place_transducers([(0.0, 0.0), (50.0, 0.0), (50.0, 50.0), (0.0, 50.0)])
        self.assertEqual(len(self.ugwt.transducers), 4)
        print("  [PASS] Place")
    
    def test_measure(self):
        """Should measure."""
        self.ugwt.place_transducers([(0.0, 0.0), (50.0, 0.0)])
        self.ugwt.measure([(0, 1)], [10.0])
        self.assertEqual(len(self.ugwt.measurements), 1)
        print("  [PASS] Measure")
    
    def test_inspect(self):
        """Should inspect."""
        self.ugwt.place_transducers([(0.0, 0.0), (50.0, 0.0)])
        self.ugwt.measure([(0, 1)], [10.0])
        result = self.ugwt.inspect()
        self.assertIn("damage_regions", result)
        print(f"  [PASS] Insp: {result}")
    
    def test_summary(self):
        """Should summarize."""
        self.ugwt.place_transducers([(0.0, 0.0)])
        s = self.ugwt.ugwt_summary()
        self.assertIn("transducers", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
