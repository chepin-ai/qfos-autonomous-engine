"""
Unit tests for radiation monitor module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from radiation_monitor import (RadiationType, RadiationEvent,
                               DoseCalculator, ShieldingAssessor,
                               RadiationDetector, RadiationMonitor)


class TestDoseCalculator(unittest.TestCase):
    """Test dose calculator."""
    
    def setUp(self):
        self.dc = DoseCalculator()
    
    def test_add_measurement(self):
        """Should add measurement."""
        self.dc.add_measurement(0, 100, 1.0, RadiationType.GAMMA, 1.0)
        self.assertGreater(self.dc.total_dose_gray, 0)
        print(f"  [PASS] Dose: {self.dc.total_dose_gray:.2e} Gy")
    
    def test_proton_higher_qf(self):
        """Proton should have higher equivalent dose."""
        self.dc.add_measurement(0, 100, 1.0, RadiationType.PROTON, 1.0)
        self.assertGreater(self.dc.total_dose_sievert, self.dc.total_dose_gray)
        print(f"  [PASS] Proton: Sv={self.dc.total_dose_sievert:.2e} > Gy={self.dc.total_dose_gray:.2e}")
    
    def test_dose_rate(self):
        """Should compute dose rate."""
        self.dc.add_measurement(0, 100, 1.0, RadiationType.GAMMA, 1.0)
        self.dc.add_measurement(30, 100, 1.0, RadiationType.GAMMA, 1.0)
        rate = self.dc.dose_rate(60)
        self.assertGreater(rate, 0)
        print(f"  [PASS] Rate: {rate:.2e} Gy/s")


class TestShieldingAssessor(unittest.TestCase):
    """Test shielding assessor."""
    
    def setUp(self):
        self.sa = ShieldingAssessor()
    
    def test_transmission(self):
        """Should compute transmission."""
        t = self.sa.transmission(1.5, RadiationType.GAMMA)
        self.assertAlmostEqual(t, 0.5, places=3)
        print(f"  [PASS] Transmission: {t:.3f}")
    
    def test_thicker_less_transmission(self):
        """Thicker shield should transmit less."""
        t1 = self.sa.transmission(1.5, RadiationType.GAMMA)
        t2 = self.sa.transmission(3.0, RadiationType.GAMMA)
        self.assertLess(t2, t1)
        print(f"  [PASS] Thick: {t2:.3f} < {t1:.3f}")
    
    def test_required_thickness(self):
        """Should compute required thickness."""
        thick = self.sa.required_thickness(0.1, RadiationType.GAMMA)
        self.assertGreater(thick, 0)
        print(f"  [PASS] Required: {thick:.2f} cm")
    
    def test_assess_protection(self):
        """Should assess protection."""
        events = [RadiationEvent(0, RadiationType.GAMMA, 1.0, 100)]
        score = self.sa.assess_protection(3.0, events)
        self.assertGreater(score, 0.5)
        print(f"  [PASS] Protection: {score:.2f}")


class TestRadiationDetector(unittest.TestCase):
    """Test radiation detector."""
    
    def setUp(self):
        self.rd = RadiationDetector(efficiency=1.0)
    
    def test_detect(self):
        """Should detect event."""
        event = RadiationEvent(0, RadiationType.GAMMA, 1.0, 5)
        detected = self.rd.detect(event)
        self.assertTrue(detected)
        print(f"  [PASS] Detect: {detected}")
    
    def test_threshold(self):
        """Should not detect below threshold."""
        event = RadiationEvent(0, RadiationType.GAMMA, 0.001)
        detected = self.rd.detect(event)
        self.assertFalse(detected)
        print("  [PASS] Threshold: False")
    
    def test_count_rate(self):
        """Should compute count rate."""
        for i in range(5):
            self.rd.detect(RadiationEvent(i, RadiationType.GAMMA, 1.0, 2))
        rate = self.rd.count_rate(5.0)
        self.assertEqual(rate, 2.0)
        print(f"  [PASS] Rate: {rate:.1f} cps")


class TestRadiationMonitor(unittest.TestCase):
    """Test unified radiation monitor."""
    
    def setUp(self):
        self.rm = RadiationMonitor()
    
    def test_record_event(self):
        """Should record event."""
        self.rm.record_event(RadiationEvent(0, RadiationType.GAMMA, 1.0, 10))
        self.assertEqual(len(self.rm.events), 1)
        print("  [PASS] Record: 1 event")
    
    def test_get_dose(self):
        """Should get dose."""
        self.rm.record_event(RadiationEvent(0, RadiationType.GAMMA, 1.0, 10), 100, 1.0)
        dose = self.rm.get_dose()
        self.assertIn("total_gray", dose)
        print(f"  [PASS] Dose: {dose['total_gray']:.2e} Gy")
    
    def test_is_safe(self):
        """Should assess safety."""
        self.assertTrue(self.rm.is_safe())
        print("  [PASS] Safe: True")
    
    def test_set_shielding(self):
        """Should set shielding."""
        self.rm.set_shielding(2.0)
        self.assertEqual(self.rm.shield_thickness_cm, 2.0)
        print("  [PASS] Shield: 2.0cm")
    
    def test_summary(self):
        """Should provide summary."""
        self.rm.record_event(RadiationEvent(0, RadiationType.GAMMA, 1.0, 5))
        summary = self.rm.monitor_summary()
        self.assertEqual(summary["events_recorded"], 1)
        print(f"  [PASS] Summary: {summary['events_recorded']} events")


if __name__ == '__main__':
    unittest.main(verbosity=2)
