"""
Unit tests for quantum time series forecasting module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_time_series_forecasting import (TimeSeriesPoint, QuantumStateEncoder,
                                             VariationalForecaster,
                                             QuantumFourierTransform,
                                             TrendAnalyzer,
                                             QuantumTimeSeriesForecasting)


class TestQuantumStateEncoder(unittest.TestCase):
    """Test encoder."""
    
    def setUp(self):
        self.enc = QuantumStateEncoder(4)
    
    def test_encode(self):
        """Should encode."""
        v = [1.0, 0.5, 0.25, 0.125]
        a = self.enc.encode(v)
        self.assertEqual(len(a), 16)
        print("  [PASS] Enc")
    
    def test_decode(self):
        """Should decode."""
        a = [complex(1.0, 0.0), complex(0.5, 0.0)]
        v = self.enc.decode(a)
        self.assertEqual(len(v), 2)
        print(f"  [PASS] Dec: {v}")


class TestVariationalForecaster(unittest.TestCase):
    """Test forecaster."""
    
    def setUp(self):
        self.vf = VariationalForecaster(4)
    
    def test_forecast(self):
        """Should forecast."""
        a = [complex(1.0, 0.0), complex(2.0, 0.0), complex(3.0, 0.0)]
        f = self.vf.forecast(a, 3)
        self.assertEqual(len(f), 3)
        print(f"  [PASS] Fcst: {f}")


class TestQuantumFourierTransform(unittest.TestCase):
    """Test QFT."""
    
    def setUp(self):
        self.qft = QuantumFourierTransform()
    
    def test_transform(self):
        """Should transform."""
        v = [1.0, 0.0, 0.0, 0.0]
        s = self.qft.transform(v)
        self.assertEqual(len(s), 4)
        print(f"  [PASS] QFT: {len(s)} bins")
    
    def test_dominant(self):
        """Should find dominant."""
        s = [complex(2.0, 0.0), complex(0.5, 0.0)]
        idx, mag = self.qft.dominant_frequency(s)
        self.assertEqual(idx, 0)
        print(f"  [PASS] Dom: idx={idx}, mag={mag}")


class TestTrendAnalyzer(unittest.TestCase):
    """Test trend."""
    
    def setUp(self):
        self.ta = TrendAnalyzer()
    
    def test_linear(self):
        """Should compute linear trend."""
        pts = [TimeSeriesPoint(0.0, 0.0), TimeSeriesPoint(1.0, 1.0), TimeSeriesPoint(2.0, 2.0)]
        slope, intercept = self.ta.linear_trend(pts)
        self.assertAlmostEqual(slope, 1.0, places=5)
        print(f"  [PASS] Trend: m={slope:.4f}, b={intercept:.4f}")
    
    def test_seasonality(self):
        """Should extract seasonality."""
        pts = [TimeSeriesPoint(0.0, 1.0), TimeSeriesPoint(1.0, 2.0), TimeSeriesPoint(2.0, 1.0)]
        s = self.ta.seasonality(pts, 2.0)
        self.assertGreater(len(s), 0)
        print(f"  [PASS] Seas: {s}")


class TestQuantumTimeSeriesForecasting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qtsf = QuantumTimeSeriesForecasting(4)
    
    def test_add(self):
        """Should add point."""
        self.qtsf.add_point(TimeSeriesPoint(0.0, 1.0))
        self.assertEqual(len(self.qtsf.history), 1)
        print("  [PASS] Add")
    
    def test_forecast(self):
        """Should forecast."""
        for i in range(5):
            self.qtsf.add_point(TimeSeriesPoint(float(i), float(i)))
        f = self.qtsf.forecast(3)
        self.assertEqual(len(f), 3)
        print(f"  [PASS] Fcst: {f}")
    
    def test_freq(self):
        """Should analyze frequency."""
        for i in range(8):
            self.qtsf.add_point(TimeSeriesPoint(float(i), math.sin(i)))
        r = self.qtsf.analyze_frequency()
        self.assertIn("dominant_freq_idx", r)
        print(f"  [PASS] Freq: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.qtsf.qtsf_summary()
        self.assertIn("history_length", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
