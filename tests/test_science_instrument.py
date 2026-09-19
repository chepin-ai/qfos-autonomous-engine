"""
Unit tests for science instrument module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from science_instrument import (InstrumentState, DataQuality, ScienceData,
                                InstrumentController, DataAcquisition,
                                CalibrationEngine, ScienceInstrument)


class TestInstrumentController(unittest.TestCase):
    """Test instrument controller."""
    
    def setUp(self):
        self.ctrl = InstrumentController("cam1", "camera")
    
    def test_power_on(self):
        """Should power on."""
        self.ctrl.power_on()
        self.assertEqual(self.ctrl.state, InstrumentState.IDLE)
        print("  [PASS] Power: idle")
    
    def test_configure(self):
        """Should configure."""
        self.ctrl.configure({"exposure": 0.1})
        self.assertEqual(self.ctrl.config["exposure"], 0.1)
        print("  [PASS] Config: exposure=0.1")
    
    def test_start_acquisition(self):
        """Should start acquisition."""
        self.ctrl.power_on()
        ok = self.ctrl.start_acquisition()
        self.assertTrue(ok)
        self.assertEqual(self.ctrl.state, InstrumentState.ACQUIRING)
        print("  [PASS] Acquire: started")
    
    def test_acquire_data(self):
        """Should acquire data."""
        data = self.ctrl.acquire_data([1.0, 2.0, 3.0], 100.0)
        self.assertEqual(data.instrument_id, "cam1")
        self.assertEqual(len(data.values), 3)
        print(f"  [PASS] Data: {len(data.values)} values")
    
    def test_acquire_nan(self):
        """Should flag NaN as poor."""
        data = self.ctrl.acquire_data([1.0, math.nan], 0.0)
        self.assertEqual(data.quality, DataQuality.POOR)
        print("  [PASS] NaN: poor quality")
    
    def test_calibrate(self):
        """Should apply calibration."""
        self.ctrl.calibrate(1.0, 2.0)
        data = self.ctrl.acquire_data([2.0, 3.0], 0.0)
        cal = self.ctrl.apply_calibration(data)
        self.assertEqual(cal.values[0], (2.0 - 1.0) * 2.0)
        print(f"  [PASS] Cal: {cal.values[0]}")


class TestDataAcquisition(unittest.TestCase):
    """Test data acquisition."""
    
    def setUp(self):
        self.daq = DataAcquisition()
        self.daq.register_instrument(InstrumentController("s1", "spectrometer"))
    
    def test_register(self):
        """Should register instrument."""
        self.assertIn("s1", self.daq.instruments)
        print("  [PASS] Register: s1")
    
    def test_acquire(self):
        """Should acquire data."""
        data = self.daq.acquire_from("s1", [10.0, 20.0], 50.0)
        self.assertIsNotNone(data)
        self.assertEqual(self.daq.buffer_size(), 1)
        print(f"  [PASS] Buffer: {self.daq.buffer_size()}")
    
    def test_get_by_quality(self):
        """Should filter by quality."""
        self.daq.acquire_from("s1", [1.0, 2.0], 0.0)
        good = self.daq.get_data_by_quality(DataQuality.GOOD)
        self.assertEqual(len(good), 1)
        print(f"  [PASS] Quality: {len(good)} good")
    
    def test_clear(self):
        """Should clear buffer."""
        self.daq.acquire_from("s1", [1.0], 0.0)
        self.daq.clear_buffer()
        self.assertEqual(self.daq.buffer_size(), 0)
        print("  [PASS] Clear: 0")


class TestCalibrationEngine(unittest.TestCase):
    """Test calibration engine."""
    
    def setUp(self):
        self.ce = CalibrationEngine()
        for raw, ref in [(0, 1), (1, 3), (2, 5)]:
            self.ce.add_calibration_point("s1", raw, ref)
    
    def test_compute(self):
        """Should compute calibration."""
        coeffs = self.ce.compute_calibration("s1")
        self.assertIsNotNone(coeffs)
        offset, gain = coeffs
        self.assertAlmostEqual(gain, 2.0, places=1)
        print(f"  [PASS] Cal: gain={gain:.1f}, offset={offset:.1f}")
    
    def test_apply(self):
        """Should apply to instrument."""
        inst = InstrumentController("s1", "spectrometer")
        self.ce.apply_to_instrument(inst)
        self.assertAlmostEqual(inst.calibration_gain, 2.0, places=1)
        print(f"  [PASS] Apply: gain={inst.calibration_gain:.1f}")


class TestScienceInstrument(unittest.TestCase):
    """Test unified science instrument."""
    
    def setUp(self):
        self.si = ScienceInstrument()
        self.si.register("cam1", "camera")
    
    def test_register(self):
        """Should register."""
        summary = self.si.instrument_summary("cam1")
        self.assertEqual(summary["id"], "cam1")
        print(f"  [PASS] Summary: {summary['id']}")
    
    def test_acquire_flow(self):
        """Should acquire and calibrate."""
        self.si.acquire("cam1", [1.0, 2.0, 3.0], 10.0)
        self.assertEqual(self.si.daq.buffer_size(), 1)
        print(f"  [PASS] Flow: {self.si.daq.buffer_size()} packet")
    
    def test_overall_summary(self):
        """Should provide summary."""
        self.si.acquire("cam1", [1.0], 0.0)
        summary = self.si.science_summary()
        self.assertEqual(summary["instruments"], 1)
        self.assertEqual(summary["buffered_packets"], 1)
        print(f"  [PASS] Overall: {summary['buffered_packets']} packets")


if __name__ == '__main__':
    unittest.main(verbosity=2)
