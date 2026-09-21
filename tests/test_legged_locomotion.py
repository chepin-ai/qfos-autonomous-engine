"""
Unit tests for legged locomotion module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from legged_locomotion import (FootState, GaitPattern,
                               FootTrajectory,
                               PhaseController,
                               TerrainAdaptation,
                               LeggedLocomotion)


class TestGaitPattern(unittest.TestCase):
    """Test gait."""
    
    def setUp(self):
        self.gp = GaitPattern()
    
    def test_trot(self):
        """Should generate trot."""
        c = self.gp.trot_gait(0.25)
        self.assertEqual(len(c), 4)
        print(f"  [PASS] Trot: {c}")
    
    def test_walk(self):
        """Should generate walk."""
        c = self.gp.walk_gait(0.5)
        self.assertEqual(len(c), 4)
        print(f"  [PASS] Walk: {c}")
    
    def test_pace(self):
        """Should generate pace."""
        c = self.gp.pace_gait(0.25)
        self.assertEqual(len(c), 4)
        print(f"  [PASS] Pace: {c}")
    
    def test_duty(self):
        """Should compute duty."""
        d = self.gp.duty_factor([True, True, False, False])
        self.assertEqual(d, 0.5)
        print(f"  [PASS] Duty: {d:.2f}")


class TestFootTrajectory(unittest.TestCase):
    """Test trajectory."""
    
    def setUp(self):
        self.ft = FootTrajectory(0.05)
    
    def test_swing(self):
        """Should compute swing."""
        x, z = self.ft.swing_trajectory(0.5, 0.0, 0.3)
        self.assertEqual(x, 0.15)
        self.assertGreater(z, 0)
        print(f"  [PASS] Swing: ({x:.2f}, {z:.3f})")
    
    def test_bezier(self):
        """Should compute Bezier."""
        p = self.ft.bezier_swing(0.5, (0.0, 0.0), (0.1, 0.05), (0.2, 0.05), (0.3, 0.0))
        self.assertEqual(len(p), 2)
        print(f"  [PASS] Bezier: {p}")


class TestPhaseController(unittest.TestCase):
    """Test phase."""
    
    def setUp(self):
        self.pc = PhaseController()
    
    def test_cycle(self):
        """Should compute cycle."""
        t = self.pc.gait_cycle_time()
        self.assertEqual(t, 0.5)
        print(f"  [PASS] T: {t:.2f}")
    
    def test_progression(self):
        """Should compute phase."""
        p = self.pc.phase_progression(0.25)
        self.assertEqual(p, 0.5)
        print(f"  [PASS] Phase: {p:.2f}")
    
    def test_stance(self):
        """Should check stance."""
        self.assertTrue(self.pc.is_stance(0.5))
        print("  [PASS] Stance")


class TestTerrainAdaptation(unittest.TestCase):
    """Test terrain."""
    
    def setUp(self):
        self.ta = TerrainAdaptation()
    
    def test_clearance(self):
        """Should compute clearance."""
        c = self.ta.ground_clearance([0.0, 0.02, 0.05, 0.01])
        self.assertGreater(c, 0.1)
        print(f"  [PASS] Clear: {c:.3f}")
    
    def test_step(self):
        """Should adjust step."""
        s = self.ta.step_length_adjustment(30.0)
        self.assertLess(s, 0.3)
        print(f"  [PASS] Step: {s:.3f}")


class TestLeggedLocomotion(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ll = LeggedLocomotion()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ll.locomotion_summary()
        self.assertIn("gaits", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
