"""
Unit tests for dust mitigation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dust_mitigation import (DustLevel, MitigationMethod, DustReading,
                             DustDetector, ElectrostaticRemover,
                             SurfaceProtection, DustMitigationController)


class TestDustDetector(unittest.TestCase):
    """Test dust detector."""
    
    def setUp(self):
        self.dd = DustDetector()
    
    def test_clean(self):
        """Should assess clean."""
        reading = DustReading("S1", 5.0, 10.0, 0.5)
        level = self.dd.assess_level(reading)
        self.assertEqual(level, DustLevel.CLEAN)
        print(f"  [PASS] Clean: {level.value}")
    
    def test_heavy(self):
        """Should assess heavy."""
        reading = DustReading("S1", 400.0, 50.0, 50.0)
        level = self.dd.assess_level(reading)
        self.assertEqual(level, DustLevel.HEAVY)
        print(f"  [PASS] Heavy: {level.value}")
    
    def test_severe(self):
        """Should assess severe."""
        reading = DustReading("S1", 600.0, 100.0, 80.0)
        level = self.dd.assess_level(reading)
        self.assertEqual(level, DustLevel.SEVERE)
        print(f"  [PASS] Severe: {level.value}")
    
    def test_average_opacity(self):
        """Should compute average opacity."""
        self.dd.add_reading(DustReading("S1", 10.0, 5.0, 10.0))
        self.dd.add_reading(DustReading("S2", 20.0, 10.0, 20.0))
        avg = self.dd.average_opacity()
        self.assertEqual(avg, 15.0)
        print(f"  [PASS] Avg opacity: {avg}")
    
    def test_peak_count(self):
        """Should find peak."""
        self.dd.add_reading(DustReading("S1", 100.0, 5.0, 10.0))
        self.dd.add_reading(DustReading("S2", 200.0, 10.0, 20.0))
        peak = self.dd.peak_particle_count()
        self.assertEqual(peak, 200.0)
        print(f"  [PASS] Peak: {peak}")


class TestElectrostaticRemover(unittest.TestCase):
    """Test electrostatic remover."""
    
    def setUp(self):
        self.es = ElectrostaticRemover(max_field_kV_m=50.0)
    
    def test_activate(self):
        """Should activate."""
        self.es.activate()
        self.assertTrue(self.es.active)
        self.assertGreater(self.es.current_field, 0)
        print(f"  [PASS] Activate: {self.es.current_field:.1f} kV/m")
    
    def test_deactivate(self):
        """Should deactivate."""
        self.es.activate()
        self.es.deactivate()
        self.assertFalse(self.es.active)
        self.assertEqual(self.es.current_field, 0)
        print("  [PASS] Deactivate")
    
    def test_efficiency(self):
        """Should compute efficiency."""
        self.es.activate()
        eff = self.es.removal_efficiency(50.0)
        self.assertGreater(eff, 0)
        self.assertLessEqual(eff, 1.0)
        print(f"  [PASS] Efficiency: {eff:.3f}")
    
    def test_efficiency_inactive(self):
        """Should be zero when inactive."""
        eff = self.es.removal_efficiency(50.0)
        self.assertEqual(eff, 0.0)
        print("  [PASS] Inactive: 0.0")
    
    def test_power(self):
        """Should compute power."""
        self.es.activate()
        p = self.es.power_consumption_W()
        self.assertGreater(p, 0)
        print(f"  [PASS] Power: {p:.1f} W")


class TestSurfaceProtection(unittest.TestCase):
    """Test surface protection."""
    
    def setUp(self):
        self.sp = SurfaceProtection(coating_thickness_um=100.0)
    
    def test_protection_factor(self):
        """Should compute protection."""
        f = self.sp.protection_factor()
        self.assertEqual(f, 1.0)
        print(f"  [PASS] Factor: {f}")
    
    def test_accumulate(self):
        """Should accumulate dust."""
        self.sp.accumulate_dust(10.0)
        self.assertEqual(self.sp.dust_accumulated_g, 10.0)
        self.assertLess(self.sp.coating_integrity, 1.0)
        print(f"  [PASS] Accumulate: {self.sp.dust_accumulated_g}g")
    
    def test_clean(self):
        """Should clean surface."""
        self.sp.accumulate_dust(50.0)
        self.sp.clean_surface(0.9)
        self.assertLess(self.sp.dust_accumulated_g, 50.0)
        print(f"  [PASS] Clean: {self.sp.dust_accumulated_g:.1f}g")


class TestDustMitigationController(unittest.TestCase):
    """Test unified dust mitigation controller."""
    
    def setUp(self):
        self.mc = DustMitigationController()
    
    def test_add_reading(self):
        """Should add reading."""
        self.mc.add_reading("S1", 100.0, 10.0, 5.0)
        self.assertEqual(len(self.mc.detector.readings), 1)
        print("  [PASS] Add: 1 reading")
    
    def test_assess_clean(self):
        """Should assess clean."""
        self.mc.add_reading("S1", 5.0, 10.0, 0.5)
        level = self.mc.assess_situation()
        self.assertEqual(level, DustLevel.CLEAN)
        print(f"  [PASS] Assess: {level.value}")
    
    def test_mitigation_cycle(self):
        """Should run mitigation cycle."""
        self.mc.add_reading("S1", 600.0, 50.0, 60.0)
        result = self.mc.run_mitigation_cycle()
        self.assertIn("dust_level", result)
        self.assertEqual(result["dust_level"], "severe")
        print(f"  [PASS] Cycle: {result['dust_level']}")
    
    def test_activate_method(self):
        """Should activate method."""
        self.mc.activate_mitigation(MitigationMethod.ELECTROSTATIC)
        self.assertIn(MitigationMethod.ELECTROSTATIC, self.mc.active_methods)
        print("  [PASS] Activate: electrostatic")
    
    def test_summary(self):
        """Should provide summary."""
        self.mc.add_reading("S1", 50.0, 10.0, 5.0)
        summary = self.mc.mitigation_summary()
        self.assertIn("dust_level", summary)
        print(f"  [PASS] Summary: {summary['dust_level']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
