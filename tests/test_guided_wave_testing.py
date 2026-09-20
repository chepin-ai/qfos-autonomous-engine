"""
Unit tests for guided wave testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from guided_wave_testing import (WaveMode, DispersionCalculator,
                                  ModeSelector, DefectReflector,
                                  GuidedWaveTesting)


class TestDispersionCalculator(unittest.TestCase):
    """Test dispersion."""
    
    def setUp(self):
        self.dc = DispersionCalculator()
    
    def test_phase_velocity(self):
        """Should compute phase velocity."""
        v = self.dc.lamb_phase_velocity(5.0, 0)
        self.assertGreater(v, 0)
        print(f"  [PASS] Phase: {v:.2f}")
    
    def test_group_velocity(self):
        """Should compute group velocity."""
        v = self.dc.group_velocity(3000.0, 100000.0)
        self.assertGreater(v, 0)
        print(f"  [PASS] Group: {v:.2f}")
    
    def test_modes(self):
        """Should get modes."""
        modes = self.dc.modes_at_frequency(100000.0, 3)
        self.assertEqual(len(modes), 3)
        print(f"  [PASS] Modes: {[m.name for m in modes]}")


class TestModeSelector(unittest.TestCase):
    """Test selector."""
    
    def setUp(self):
        self.ms = ModeSelector()
        self.modes = [
            WaveMode("A0", 100000.0, 3000.0, 2850.0, 0.1),
            WaveMode("S0", 100000.0, 5000.0, 4750.0, 0.5),
        ]
    
    def test_penetration(self):
        """Should select by penetration."""
        m = self.ms.select_by_penetration(self.modes)
        self.assertIsNotNone(m)
        print(f"  [PASS] Pen: {m.name}")
    
    def test_resolution(self):
        """Should select by resolution."""
        m = self.ms.select_by_resolution(self.modes)
        self.assertIsNotNone(m)
        print(f"  [PASS] Res: {m.name}")


class TestDefectReflector(unittest.TestCase):
    """Test reflector."""
    
    def setUp(self):
        self.dr = DefectReflector()
    
    def test_reflection(self):
        """Should compute reflection."""
        r = self.dr.reflection_coefficient(3.0, 10.0)
        self.assertGreaterEqual(r, 0)
        self.assertLessEqual(r, 1.0)
        print(f"  [PASS] Refl: {r:.4f}")
    
    def test_tof(self):
        """Should compute TOF."""
        t = self.dr.time_of_flight(5.0, 3000.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] TOF: {t:.6f}")
    
    def test_locate(self):
        """Should locate defect."""
        d = self.dr.locate_defect(0.01, 3000.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Loc: {d:.4f}")


class TestGuidedWaveTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.gwt = GuidedWaveTesting()
    
    def test_select(self):
        """Should select mode."""
        self.gwt.select_mode(100000.0, "penetration")
        self.assertIsNotNone(self.gwt.selected_mode)
        print(f"  [PASS] Sel: {self.gwt.selected_mode.name}")
    
    def test_inspect(self):
        """Should inspect."""
        self.gwt.select_mode(100000.0)
        self.gwt.inspect([1.0, 2.0, 3.0], [2.0, 3.0, 1.0], 10.0)
        self.assertEqual(len(self.gwt.signals), 3)
        print("  [PASS] Inspect")
    
    def test_summary(self):
        """Should summarize."""
        self.gwt.select_mode(100000.0)
        s = self.gwt.gwt_summary()
        self.assertIn("mode", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
