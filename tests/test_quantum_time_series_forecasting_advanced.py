"""
Unit tests for quantum time series forecasting advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_time_series_forecasting_advanced import (ForecastResult,
                                                      QuantumAutoregressiveModel,
                                                      QuantumExponentialSmoothing,
                                                      QuantumSeasonalDecomposition,
                                                      QuantumAnomalyDetection,
                                                      QuantumTimeSeriesForecastingAdvanced)


class TestQuantumAutoregressiveModel(unittest.TestCase):
    """Test AR."""
    
    def setUp(self):
        self.qar = QuantumAutoregressiveModel()
    
    def test_fit(self):
        """Should fit coefficients."""
        c = self.qar.fit([1.0, 2.0, 3.0, 4.0, 5.0])
        self.assertEqual(len(c), 3)
        print(f"  [PASS] Coef: {c}")
    
    def test_predict(self):
        """Should predict."""
        self.qar.fit([1.0, 2.0, 3.0, 4.0, 5.0])
        p = self.qar.predict([3.0, 4.0, 5.0], steps=2)
        self.assertEqual(len(p), 2)
        print(f"  [PASS] Pred: {p}")


class TestQuantumExponentialSmoothing(unittest.TestCase):
    """Test smoothing."""
    
    def setUp(self):
        self.qes = QuantumExponentialSmoothing()
    
    def test_smooth(self):
        """Should smooth."""
        s = self.qes.smooth([1.0, 2.0, 3.0])
        self.assertEqual(len(s), 3)
        print(f"  [PASS] Sm: {s}")
    
    def test_forecast(self):
        """Should forecast."""
        self.qes.smooth([1.0, 2.0, 3.0])
        f = self.qes.forecast(2)
        self.assertEqual(len(f), 2)
        print(f"  [PASS] Fc: {f}")


class TestQuantumSeasonalDecomposition(unittest.TestCase):
    """Test seasonal."""
    
    def setUp(self):
        self.qsd = QuantumSeasonalDecomposition(season_length=3)
    
    def test_indices(self):
        """Should compute indices."""
        i = self.qsd.seasonal_indices([1.0, 2.0, 3.0, 1.0, 2.0, 3.0])
        self.assertEqual(len(i), 3)
        print(f"  [PASS] Idx: {i}")
    
    def test_deseason(self):
        """Should deseasonalize."""
        d = self.qsd.deseasonalize([1.0, 2.0, 3.0])
        self.assertEqual(len(d), 3)
        print(f"  [PASS] DS: {d}")


class TestQuantumAnomalyDetection(unittest.TestCase):
    """Test anomaly."""
    
    def setUp(self):
        self.qad = QuantumAnomalyDetection(threshold_sigma=1.0)
    
    def test_detect(self):
        """Should detect."""
        a = self.qad.detect([1.0, 2.0, 1.0, 2.0, 1.0, 100.0])
        self.assertTrue(a[-1])
        print(f"  [PASS] Anom: {a}")
    
    def test_score(self):
        """Should compute score."""
        s = self.qad.anomaly_score(100.0, [1.0, 2.0, 3.0, 4.0, 5.0])
        self.assertGreater(s, 0)
        print(f"  [PASS] Sc: {s:.2f}")


class TestQuantumTimeSeriesForecastingAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qtsfa = QuantumTimeSeriesForecastingAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qtsfa.forecasting_summary()
        self.assertIn("components", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
