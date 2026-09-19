"""
Unit tests for antenna pointing module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from antenna_pointing import (PointingTarget, GimbalController,
                              TrackingAlgorithm, BeamSteering,
                              AntennaPointing)


class TestGimbalController(unittest.TestCase):
    """Test gimbal controller."""
    
    def setUp(self):
        self.gc = GimbalController(max_rate_degs=10.0)
    
    def test_get_pointing(self):
        """Should get initial pointing."""
        az, el = self.gc.get_pointing()
        self.assertEqual(az, 0.0)
        self.assertEqual(el, 0.0)
        print("  [PASS] Pointing: (0, 0)")
    
    def test_slew_to(self):
        """Should slew to target."""
        done = self.gc.slew_to(5.0, 3.0, dt=1.0)
        az, el = self.gc.get_pointing()
        self.assertGreater(az, 0)
        self.assertGreater(el, 0)
        print(f"  [PASS] Slew: ({az:.1f}, {el:.1f}), done={done}")
    
    def test_slew_converge(self):
        """Should eventually converge."""
        for _ in range(20):
            done = self.gc.slew_to(5.0, 3.0, dt=0.5)
            if done:
                break
        az, el = self.gc.get_pointing()
        self.assertAlmostEqual(az, 5.0, places=0)
        self.assertAlmostEqual(el, 3.0, places=0)
        print(f"  [PASS] Converge: ({az:.1f}, {el:.1f})")
    
    def test_pointing_error(self):
        """Should compute error."""
        err = self.gc.pointing_error(10.0, 5.0)
        self.assertGreater(err, 0)
        print(f"  [PASS] Error: {err:.1f}deg")


class TestTrackingAlgorithm(unittest.TestCase):
    """Test tracking algorithm."""
    
    def setUp(self):
        self.ta = TrackingAlgorithm()
        for i in range(5):
            self.ta.update(i, i*2, i*1)
    
    def test_update(self):
        """Should update history."""
        self.assertEqual(len(self.ta.target_history), 5)
        print("  [PASS] History: 5")
    
    def test_predict(self):
        """Should predict future position."""
        pred = self.ta.predict(10.0)
        self.assertIsNotNone(pred)
        self.assertGreater(pred[0], 0)
        print(f"  [PASS] Predict: ({pred[0]:.1f}, {pred[1]:.1f})")
    
    def test_tracking_rate(self):
        """Should compute tracking rate."""
        rate = self.ta.tracking_rate()
        self.assertAlmostEqual(rate[0], 2.0, places=0)
        self.assertAlmostEqual(rate[1], 1.0, places=0)
        print(f"  [PASS] Rate: ({rate[0]:.1f}, {rate[1]:.1f})")


class TestBeamSteering(unittest.TestCase):
    """Test beam steering."""
    
    def setUp(self):
        self.bs = BeamSteering(wavelength_m=0.03, element_spacing_m=0.015)
    
    def test_phase_shift(self):
        """Should compute phase shift."""
        phi = self.bs.phase_shift(30.0, 1)
        self.assertNotEqual(phi, 0)
        print(f"  [PASS] Phase: {math.degrees(phi):.1f}deg")
    
    def test_array_factor_boresight(self):
        """Should have max at boresight."""
        af = self.bs.array_factor(0.0, 8, 0.0)
        self.assertAlmostEqual(af, 1.0, places=5)
        print(f"  [PASS] AF boresight: {af:.3f}")
    
    def test_array_factor_off(self):
        """Should decrease off boresight."""
        af = self.bs.array_factor(0.0, 8, 30.0)
        self.assertLess(af, 1.0)
        print(f"  [PASS] AF off: {af:.3f}")
    
    def test_beamwidth(self):
        """Should estimate beamwidth."""
        bw = self.bs.beamwidth(8)
        self.assertGreater(bw, 0)
        self.assertLess(bw, 90)
        print(f"  [PASS] Beamwidth: {bw:.1f}deg")


class TestAntennaPointing(unittest.TestCase):
    """Test unified antenna pointing."""
    
    def setUp(self):
        self.ap = AntennaPointing()
    
    def test_point_to_target(self):
        """Should point to target."""
        target = PointingTarget(10.0, 5.0, target_id="ground")
        done = self.ap.point_to_target(target, dt=1.0)
        az, el = self.ap.gimbal.get_pointing()
        self.assertGreater(az, 0)
        print(f"  [PASS] Point: ({az:.1f}, {el:.1f})")
    
    def test_track_target(self):
        """Should track and predict."""
        measurements = [(0, 0, 0), (1, 2, 1), (2, 4, 2)]
        pred = self.ap.track_target(measurements, 5.0)
        self.assertIsNotNone(pred)
        print(f"  [PASS] Track: ({pred[0]:.1f}, {pred[1]:.1f})")
    
    def test_beam_phases(self):
        """Should compute beam phases."""
        phases = self.ap.compute_beam_phases(15.0, 4)
        self.assertEqual(len(phases), 4)
        print(f"  [PASS] Phases: {len(phases)} elements")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.ap.pointing_summary()
        self.assertIn("azimuth", summary)
        print(f"  [PASS] Summary: az={summary['azimuth']:.1f}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
