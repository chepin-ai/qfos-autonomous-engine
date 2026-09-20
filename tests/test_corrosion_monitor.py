"""
Unit tests for corrosion monitor module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from corrosion_monitor import (CorrosionType, CorrosionReading,
                               CorrosionRateCalculator, ElectrochemicalMonitor,
                               PittingDetector, CorrosionRiskAssessor,
                               CorrosionMonitor)


class TestCorrosionRateCalculator(unittest.TestCase):
    """Test corrosion rate calculator."""
    
    def setUp(self):
        self.calc = CorrosionRateCalculator()
    
    def test_from_rp(self):
        """Should compute from polarization resistance."""
        icorr = self.calc.from_polarization_resistance(1000.0)
        self.assertGreater(icorr, 0)
        print(f"  [PASS] i_corr: {icorr:.2f} uA/cm2")
    
    def test_from_weight_loss(self):
        """Should compute from weight loss."""
        cr = self.calc.from_weight_loss(100.0, 10.0, 1000.0)
        self.assertGreater(cr, 0)
        print(f"  [PASS] CR: {cr:.4f} mm/yr")
    
    def test_penetration(self):
        """Should convert to penetration rate."""
        pr = self.calc.to_penetration_rate(10.0)
        self.assertGreater(pr, 0)
        print(f"  [PASS] PR: {pr:.4f} mm/yr")


class TestElectrochemicalMonitor(unittest.TestCase):
    """Test electrochemical monitor."""
    
    def setUp(self):
        self.em = ElectrochemicalMonitor()
    
    def test_add_reading(self):
        """Should add reading."""
        r = CorrosionReading("s1", -500.0, 5.0, 25.0, 60.0)
        self.em.add_reading(r)
        self.assertEqual(len(self.em.readings), 1)
        print("  [PASS] Add: 1")
    
    def test_potential(self):
        """Should compute potential."""
        for i in range(5):
            r = CorrosionReading("s1", -500.0 + i * 10, 5.0, 25.0, 60.0)
            self.em.add_reading(r)
        e = self.em.corrosion_potential()
        self.assertAlmostEqual(e, -480.0)
        print(f"  [PASS] E_corr: {e:.1f} mV")
    
    def test_current(self):
        """Should compute current."""
        for _ in range(5):
            self.em.add_reading(CorrosionReading("s1", -500.0, 10.0, 25.0, 60.0))
        i = self.em.corrosion_current()
        self.assertAlmostEqual(i, 10.0)
        print(f"  [PASS] i_corr: {i:.1f}")
    
    def test_trend(self):
        """Should detect trend."""
        for i in range(10):
            r = CorrosionReading("s1", -500.0, 1.0 + i, 25.0, 60.0)
            self.em.add_reading(r)
        t = self.em.trend()
        self.assertEqual(t, "accelerating")
        print(f"  [PASS] Trend: {t}")


class TestPittingDetector(unittest.TestCase):
    """Test pitting detector."""
    
    def setUp(self):
        self.pd = PittingDetector()
    
    def test_detect_pitting(self):
        """Should detect pitting."""
        r = CorrosionReading("s1", -300.0, 20.0, 25.0, 60.0)
        p = self.pd.detect(r)
        self.assertTrue(p)
        print("  [PASS] Pitting: True")
    
    def test_no_pitting(self):
        """Should not detect pitting."""
        r = CorrosionReading("s1", -100.0, 1.0, 25.0, 60.0)
        p = self.pd.detect(r)
        self.assertFalse(p)
        print("  [PASS] No pitting")
    
    def test_index(self):
        """Should compute pitting index."""
        readings = [
            CorrosionReading("s1", -300.0, 20.0, 25.0, 60.0),
            CorrosionReading("s1", -100.0, 1.0, 25.0, 60.0),
        ]
        idx = self.pd.pitting_index(readings)
        self.assertAlmostEqual(idx, 0.5)
        print(f"  [PASS] Index: {idx}")
    
    def test_rate(self):
        """Should compute pitting rate."""
        depths = [0.0, 10.0, 25.0, 50.0]
        rate = self.pd.pitting_rate(depths, 100.0)
        self.assertAlmostEqual(rate, 0.5)
        print(f"  [PASS] Rate: {rate}")


class TestCorrosionRiskAssessor(unittest.TestCase):
    """Test risk assessor."""
    
    def setUp(self):
        self.ra = CorrosionRiskAssessor()
    
    def test_low_risk(self):
        """Should classify low risk."""
        level = self.ra.risk_level(1.0)
        self.assertEqual(level, "low")
        print("  [PASS] Low")
    
    def test_high_risk(self):
        """Should classify high risk."""
        level = self.ra.risk_level(7.0)
        self.assertEqual(level, "high")
        print("  [PASS] High")
    
    def test_remaining_life(self):
        """Should estimate life."""
        life = self.ra.remaining_life(1.0, 10.0)
        self.assertAlmostEqual(life, 10.0)
        print(f"  [PASS] Life: {life:.1f} yr")


class TestCorrosionMonitor(unittest.TestCase):
    """Test unified corrosion monitor."""
    
    def setUp(self):
        self.cm = CorrosionMonitor()
    
    def test_record(self):
        """Should record reading."""
        self.cm.record("s1", CorrosionReading("s1", -500.0, 5.0, 25.0, 60.0))
        self.assertEqual(len(self.cm.sensors["s1"]), 1)
        print("  [PASS] Record")
    
    def test_health(self):
        """Should assess health."""
        self.cm.record("s1", CorrosionReading("s1", -500.0, 5.0, 25.0, 60.0))
        h = self.cm.health_assessment("s1")
        self.assertIn("risk_level", h)
        print(f"  [PASS] Health: {h['risk_level']}")
    
    def test_summary(self):
        """Should provide summary."""
        self.cm.record("s1", CorrosionReading("s1", -500.0, 5.0, 25.0, 60.0))
        s = self.cm.system_summary()
        self.assertEqual(s["sensors"], 1)
        print(f"  [PASS] Summary: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
