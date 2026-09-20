"""
Unit tests for eddy current array module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from eddy_current_array import (ProbeOrientation, ECAReading,
                                 ECAProbe, ECAArray,
                                 CScanImager, ECADefectMapper,
                                 EddyCurrentArray)


class TestECAProbe(unittest.TestCase):
    """Test ECA probe."""
    
    def setUp(self):
        self.probe = ECAProbe(0, (0.0, 0.0), 100000.0)
    
    def test_impedance(self):
        """Should compute impedance."""
        z = self.probe.impedance(1.0, 0.0)
        self.assertNotEqual(z.real, 0)
        print(f"  [PASS] Z: {z}")
    
    def test_voltage(self):
        """Should compute voltage."""
        ref = self.probe.impedance(1.0, 0.0)
        z = self.probe.impedance(2.0, 0.0)
        v = self.probe.voltage(ref, z)
        self.assertNotEqual(v.real, 0)
        print(f"  [PASS] V: {v}")
    
    def test_lift_off_effect(self):
        """Should decrease with lift-off."""
        z0 = self.probe.impedance(1.0, 0.0)
        z1 = self.probe.impedance(1.0, 1.0)
        self.assertLess(abs(z1), abs(z0))
        print(f"  [PASS] LO: |z0|={abs(z0):.2f} |z1|={abs(z1):.2f}")


class TestECAArray(unittest.TestCase):
    """Test ECA array."""
    
    def setUp(self):
        self.array = ECAArray(8)
    
    def test_scan(self):
        """Should scan."""
        conds = [1.0] * 8
        los = [0.0] * 8
        readings = self.array.scan_line(conds, los)
        self.assertEqual(len(readings), 8)
        print(f"  [PASS] Scan: {len(readings)} readings")
    
    def test_coverage(self):
        """Should compute coverage."""
        w = self.array.coverage_width_mm()
        self.assertGreater(w, 0)
        print(f"  [PASS] Cov: {w:.1f} mm")


class TestCScanImager(unittest.TestCase):
    """Test C-scan imager."""
    
    def setUp(self):
        self.array = ECAArray(4)
        self.imager = CScanImager(self.array)
    
    def test_amplitude(self):
        """Should generate amplitude map."""
        readings = self.array.scan_line([1.0]*4, [0.0]*4)
        self.imager.add_scan_line(readings)
        amp = self.imager.amplitude_map()
        self.assertEqual(len(amp), 1)
        print(f"  [PASS] Amp: {amp[0]}")
    
    def test_phase(self):
        """Should generate phase map."""
        readings = self.array.scan_line([1.0]*4, [0.0]*4)
        self.imager.add_scan_line(readings)
        ph = self.imager.phase_map()
        self.assertEqual(len(ph), 1)
        print(f"  [PASS] Phase: {ph[0]}")
    
    def test_defect(self):
        """Should generate defect map."""
        readings = self.array.scan_line([5.0]*4, [0.0]*4)
        self.imager.add_scan_line(readings)
        dm = self.imager.defect_map(1.0)
        self.assertEqual(len(dm), 1)
        print(f"  [PASS] Defect: {dm[0]}")


class TestECADefectMapper(unittest.TestCase):
    """Test defect mapper."""
    
    def setUp(self):
        self.mapper = ECADefectMapper()
    
    def test_depth(self):
        """Should estimate depth."""
        d = self.mapper.defect_depth_estimate(30.0, 50.0, 1.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Depth: {d:.4f} mm")
    
    def test_length(self):
        """Should estimate length."""
        l = self.mapper.defect_length_estimate(5, 2.0)
        self.assertEqual(l, 10.0)
        print(f"  [PASS] Len: {l}")
    
    def test_severity(self):
        """Should compute severity."""
        s = self.mapper.severity_index(50.0, 2.0, 10.0)
        self.assertGreater(s, 0)
        print(f"  [PASS] Sev: {s:.4f}")


class TestEddyCurrentArray(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.eca = EddyCurrentArray(4)
    
    def test_scan(self):
        """Should full scan."""
        cond = [[1.0]*4 for _ in range(3)]
        lo = [[0.0]*4 for _ in range(3)]
        self.eca.scan(cond, lo)
        s = self.eca.cscan_summary()
        self.assertIn("scan_lines", s)
        print(f"  [PASS] Scan: {s}")
    
    def test_analyze(self):
        """Should analyze."""
        cond = [[5.0]*4 for _ in range(3)]
        lo = [[0.0]*4 for _ in range(3)]
        self.eca.scan(cond, lo)
        defects = self.eca.analyze_defects(1.0)
        self.assertIsInstance(defects, list)
        print(f"  [PASS] Ana: {len(defects)} defects")


if __name__ == '__main__':
    unittest.main(verbosity=2)
