"""
Unit tests for quantum time series forecasting module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_time_series_forecasting import (QuantumRecurrentCell,
                                              QuantumFourierForecaster,
                                              TrendExtractor,
                                              PredictionConfidence,
                                              QuantumTimeSeriesForecasting)


class TestQuantumRecurrentCell(unittest.TestCase):
    """Test recurrent cell."""
    
    def setUp(self):
        self.cell = QuantumRecurrentCell(4)
    
    def test_step(self):
        """Should step."""
        s = self.cell.step(1.0)
        self.assertEqual(len(s), 4)
        print(f"  [PASS] Step: {s}")
    
    def test_output(self):
        """Should output."""
        self.cell.step(1.0)
        o = self.cell.output()
        self.assertIsNotNone(o)
        print(f"  [PASS] Out: {o:.4f}")


class TestQuantumFourierForecaster(unittest.TestCase):
    """Test Fourier forecaster."""
    
    def setUp(self):
        self.ff = QuantumFourierForecaster(4)
    
    def test_dft(self):
        """Should compute DFT."""
        series = [1.0, 0.0, -1.0, 0.0]
        spec = self.ff.dft(series)
        self.assertEqual(len(spec), 4)
        print("  [PASS] DFT")
    
    def test_predict(self):
        """Should predict."""
        series = [1.0, 2.0, 3.0, 2.0, 1.0]
        p = self.ff.predict(series, 2)
        self.assertEqual(len(p), 2)
        print(f"  [PASS] Pred: {p}")


class TestTrendExtractor(unittest.TestCase):
    """Test trend."""
    
    def setUp(self):
        self.te = TrendExtractor()
    
    def test_linear(self):
        """Should fit linear trend."""
        series = [0.0, 1.0, 2.0, 3.0, 4.0]
        slope, intercept = self.te.linear_trend(series)
        self.assertAlmostEqual(slope, 1.0, places=5)
        print(f"  [PASS] Trend: {slope:.4f}x + {intercept:.4f}")
    
    def test_detrend(self):
        """Should detrend."""
        series = [0.0, 1.0, 2.0, 3.0, 4.0]
        d = self.te.detrend(series)
        self.assertAlmostEqual(sum(d), 0.0, places=5)
        print(f"  [PASS] Detrend: sum={sum(d):.4f}")


class TestPredictionConfidence(unittest.TestCase):
    """Test confidence."""
    
    def setUp(self):
        self.pc = PredictionConfidence()
    
    def test_interval(self):
        """Should compute intervals."""
        intervals = self.pc.interval([1.0, 2.0], [0.1, 0.2, 0.1])
        self.assertEqual(len(intervals), 2)
        self.assertLess(intervals[0][0], intervals[0][1])
        print(f"  [PASS] CI: {intervals}")


class TestQuantumTimeSeriesForecasting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qtsf = QuantumTimeSeriesForecasting()
    
    def test_add(self):
        """Should add history."""
        self.qtsf.add_history(1.0)
        self.qtsf.add_history(2.0)
        self.assertEqual(len(self.qtsf.history), 2)
        print("  [PASS] Add")
    
    def test_recurrent(self):
        """Should forecast recurrent."""
        for v in [1.0, 2.0, 3.0, 2.0, 1.0]:
            self.qtsf.add_history(v)
        p = self.qtsf.forecast_recurrent(2)
        self.assertEqual(len(p), 2)
        print(f"  [PASS] Rec: {p}")
    
    def test_fourier(self):
        """Should forecast Fourier."""
        for v in [1.0, 2.0, 3.0, 2.0, 1.0]:
            self.qtsf.add_history(v)
        p = self.qtsf.forecast_fourier(2)
        self.assertEqual(len(p), 2)
        print(f"  [PASS] Fou: {p}")
    
    def test_combined(self):
        """Should forecast combined."""
        for v in [1.0, 2.0, 3.0, 2.0, 1.0]:
            self.qtsf.add_history(v)
        p = self.qtsf.forecast_combined(2)
        self.assertEqual(len(p), 2)
        print(f"  [PASS] Comb: {p}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qtsf.qtsf_summary()
        self.assertIn("history_length", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
