"""
Unit tests for strain gauge analysis module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from strain_gauge_analysis import (StrainReading, BridgeCircuit,
                                   StressConverter,
                                   LoadCellCalibrator,
                                   FatigueMonitor,
                                   StrainGaugeAnalysis)


class TestBridgeCircuit(unittest.TestCase):
    """Test bridge."""
    
    def setUp(self):
        self.bc = BridgeCircuit(5.0, 350.0, 2.0)
    
    def test_quarter(self):
        """Should compute quarter bridge."""
        o = self.bc.quarter_bridge_output(1.0)
        self.assertGreater(o, 0)
        print(f"  [PASS] Qtr: {o:.6f}")
    
    def test_half(self):
        """Should compute half bridge."""
        o = self.bc.half_bridge_output(1.0, -1.0)
        self.assertGreater(o, 0)
        print(f"  [PASS] Half: {o:.6f}")
    
    def test_full(self):
        """Should compute full bridge."""
        o = self.bc.full_bridge_output([1.0, -1.0, 1.0, -1.0])
        self.assertGreater(o, 0)
        print(f"  [PASS] Full: {o:.6f}")
    
    def test_strain(self):
        """Should convert to strain."""
        s = self.bc.strain_from_output(0.001, "quarter")
        self.assertGreater(s, 0)
        print(f"  [PASS] Strain: {s:.2f} uE")


class TestStressConverter(unittest.TestCase):
    """Test stress."""
    
    def setUp(self):
        self.sc = StressConverter(200.0, 0.3)
    
    def test_uniaxial(self):
        """Should compute uniaxial."""
        s = self.sc.uniaxial_stress(1000.0)
        self.assertEqual(s, 200.0)
        print(f"  [PASS] Uni: {s} MPa")
    
    def test_biaxial(self):
        """Should compute biaxial."""
        sx, sy = self.sc.biaxial_stress(1000.0, 500.0)
        self.assertGreater(sx, 0)
        print(f"  [PASS] Bi: ({sx:.2f}, {sy:.2f})")


class TestLoadCellCalibrator(unittest.TestCase):
    """Test calibrator."""
    
    def setUp(self):
        self.lcc = LoadCellCalibrator()
    
    def test_sensitivity(self):
        """Should compute sensitivity."""
        self.lcc.add_point(0.0, 0.0)
        self.lcc.add_point(100.0, 2.0)
        s = self.lcc.sensitivity_mV_V_per_N()
        self.assertGreater(s, 0)
        print(f"  [PASS] Sens: {s:.6f}")
    
    def test_load(self):
        """Should convert to load."""
        self.lcc.add_point(0.0, 0.0)
        self.lcc.add_point(100.0, 2.0)
        l = self.lcc.load_from_output(1.0)
        self.assertEqual(l, 50.0)
        print(f"  [PASS] Load: {l} N")


class TestFatigueMonitor(unittest.TestCase):
    """Test fatigue."""
    
    def setUp(self):
        self.fm = FatigueMonitor()
    
    def test_rainflow(self):
        """Should count cycles."""
        h = [0.0, 100.0, -50.0, 80.0, 0.0]
        c = self.fm.rainflow_count(h)
        self.assertGreater(len(c), 0)
        print(f"  [PASS] RF: {len(c)} cycles")
    
    def test_miners(self):
        """Should compute damage."""
        h = [0.0, 1000.0, -1000.0, 0.0]
        self.fm.rainflow_count(h)
        d = self.fm.miners_rule(200.0)
        self.assertGreaterEqual(d, 0)
        print(f"  [PASS] Miner: {d:.6f}")


class TestStrainGaugeAnalysis(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.sga = StrainGaugeAnalysis()
    
    def test_add(self):
        """Should add reading."""
        self.sga.add_reading(StrainReading("G1", 1000.0, 20.0, 0.0))
        self.assertEqual(len(self.sga.readings), 1)
        print("  [PASS] Add")
    
    def test_analyze(self):
        """Should analyze."""
        self.sga.add_reading(StrainReading("G1", 0.0, 20.0, 0.0))
        self.sga.add_reading(StrainReading("G1", 1000.0, 20.0, 1000.0))
        self.sga.add_reading(StrainReading("G1", -500.0, 20.0, 2000.0))
        r = self.sga.analyze()
        self.assertIn("max_stress_MPa", r)
        print(f"  [PASS] Anlz: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.sga.sga_summary()
        self.assertIn("readings", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
