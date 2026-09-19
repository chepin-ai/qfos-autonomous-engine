"""
Unit tests for docking mechanism module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from docking_mechanism import (DockingState, CaptureStatus, AlignmentData,
                               CaptureRing, LatchController, SealSystem,
                               DockingController)


class TestCaptureRing(unittest.TestCase):
    """Test capture ring."""
    
    def setUp(self):
        self.cr = CaptureRing(capture_range_m=0.5)
    
    def test_capture_possible(self):
        """Should detect capture possible."""
        align = AlignmentData(lateral_error_m=0.02, angular_error_deg=0.5,
                             closing_velocity_ms=0.1, range_m=0.3)
        status = self.cr.assess_capture(align)
        self.assertEqual(status, CaptureStatus.CAPTURED)
        print(f"  [PASS] Capture: {status.value}")
    
    def test_misaligned(self):
        """Should detect misalignment."""
        align = AlignmentData(lateral_error_m=0.02, angular_error_deg=10.0,
                             closing_velocity_ms=0.1, range_m=0.3)
        status = self.cr.assess_capture(align)
        self.assertEqual(status, CaptureStatus.MISALIGNED)
        print(f"  [PASS] Misaligned: {status.value}")
    
    def test_dampen(self):
        """Should dampen velocity."""
        force = self.cr.dampen(0.5)
        self.assertLess(force, 0)
        print(f"  [PASS] Dampen: {force:.1f} N")


class TestLatchController(unittest.TestCase):
    """Test latch controller."""
    
    def setUp(self):
        self.lc = LatchController(num_latches=12)
    
    def test_engage(self):
        """Should engage latch."""
        result = self.lc.engage_latch(0, 1000.0)
        self.assertTrue(result)
        self.assertTrue(self.lc.latch_states[0])
        print("  [PASS] Engage: latch 0")
    
    def test_release(self):
        """Should release latch."""
        self.lc.engage_latch(0)
        self.lc.release_latch(0)
        self.assertFalse(self.lc.latch_states[0])
        print("  [PASS] Release: latch 0")
    
    def test_all_engaged(self):
        """Should check all engaged."""
        for i in range(12):
            self.lc.engage_latch(i)
        self.assertTrue(self.lc.all_engaged())
        print("  [PASS] All engaged")
    
    def test_engagement_fraction(self):
        """Should compute fraction."""
        self.lc.engage_latch(0)
        self.lc.engage_latch(1)
        self.assertAlmostEqual(self.lc.engagement_fraction(), 2/12, places=3)
        print(f"  [PASS] Fraction: {self.lc.engagement_fraction():.3f}")
    
    def test_total_force(self):
        """Should compute total force."""
        self.lc.engage_latch(0, 1000.0)
        self.lc.engage_latch(1, 1500.0)
        self.assertEqual(self.lc.total_force(), 2500.0)
        print(f"  [PASS] Force: {self.lc.total_force()}")


class TestSealSystem(unittest.TestCase):
    """Test seal system."""
    
    def setUp(self):
        self.ss = SealSystem(seal_diameter_m=1.2)
    
    def test_engage(self):
        """Should engage seal."""
        self.ss.engage_seal()
        self.assertTrue(self.ss.seal_engaged)
        print("  [PASS] Engage: seal")
    
    def test_pressure_check(self):
        """Should pass pressure check."""
        self.ss.engage_seal()
        result = self.ss.pressure_check()
        self.assertTrue(result)
        print(f"  [PASS] Pressure: {result}")
    
    def test_pressure_not_engaged(self):
        """Should fail without seal."""
        result = self.ss.pressure_check()
        self.assertFalse(result)
        print("  [PASS] No seal: False")
    
    def test_circumference(self):
        """Should compute circumference."""
        c = self.ss.seal_circumference()
        self.assertAlmostEqual(c, 3.7699, places=3)
        print(f"  [PASS] Circumference: {c:.3f}")


class TestDockingController(unittest.TestCase):
    """Test unified docking controller."""
    
    def setUp(self):
        self.dc = DockingController()
    
    def test_initial_state(self):
        """Should start idle."""
        self.assertEqual(self.dc.state, DockingState.IDLE)
        print("  [PASS] State: idle")
    
    def test_docking_sequence(self):
        """Should execute docking sequence."""
        self.dc.update_alignment(0.02, 0.5, 0.1, 0.3)
        states = []
        for _ in range(10):
            state = self.dc.perform_docking()
            states.append(state)
            if state == DockingState.DOCKED:
                break
        self.assertIn(DockingState.DOCKED, states)
        print(f"  [PASS] Docked in {len(states)} steps")
    
    def test_undocking_sequence(self):
        """Should execute undocking sequence."""
        # First dock
        self.dc.update_alignment(0.02, 0.5, 0.1, 0.3)
        for _ in range(10):
            if self.dc.perform_docking() == DockingState.DOCKED:
                break
        # Then undock
        states = []
        for _ in range(10):
            state = self.dc.undock()
            states.append(state)
            if state == DockingState.IDLE:
                break
        self.assertIn(DockingState.IDLE, states)
        print(f"  [PASS] Undocked in {len(states)} steps")
    
    def test_misaligned_error(self):
        """Should error on misalignment."""
        self.dc.update_alignment(0.02, 10.0, 0.1, 0.3)
        self.dc.perform_docking()  # IDLE -> APPROACHING
        state = self.dc.perform_docking()
        self.assertEqual(state, DockingState.ERROR)
        print("  [PASS] Error: misaligned")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.dc.docking_summary()
        self.assertIn("state", summary)
        self.assertIn("latch_engagement", summary)
        print(f"  [PASS] Summary: {summary['state']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
