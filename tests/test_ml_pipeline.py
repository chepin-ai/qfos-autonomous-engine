"""
Unit tests for machine learning pipeline module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ml_pipeline import OnlineRegressor, KalmanFilterEstimator, PerformanceOptimizer, MLPipeline, TrainingSample


class TestOnlineRegressor(unittest.TestCase):
    """Test online regressor."""
    
    def setUp(self):
        self.reg = OnlineRegressor(num_features=2, learning_rate=0.01)
    
    def test_predict(self):
        """Should make prediction."""
        pred = self.reg.predict([1.0, 2.0])
        self.assertIsInstance(pred, float)
        print(f"  [PASS] Predict: {pred:.4f}")
    
    def test_update(self):
        """Should update weights."""
        w0 = self.reg.weights[:]
        self.reg.update([1.0, 0.0], 5.0)
        self.assertNotEqual(self.reg.weights, w0)
        print("  [PASS] Update: weights changed")
    
    def test_train_batch(self):
        """Should train on batch."""
        samples = [TrainingSample([1.0, 0.0], 5.0),
                   TrainingSample([0.0, 1.0], 3.0),
                   TrainingSample([1.0, 1.0], 8.0)]
        self.reg.train_batch(samples, epochs=100)
        pred = self.reg.predict([1.0, 1.0])
        self.assertAlmostEqual(pred, 8.0, delta=2.0)
        print(f"  [PASS] Batch: predicted={pred:.2f}, target=8.0")
    
    def test_evaluate(self):
        """Should evaluate."""
        samples = [TrainingSample([1.0], 2.0), TrainingSample([2.0], 4.0)]
        metrics = self.reg.evaluate(samples)
        self.assertIn("mse", metrics)
        print(f"  [PASS] Eval: mse={metrics['mse']:.4f}")


class TestKalmanFilter(unittest.TestCase):
    """Test Kalman filter."""
    
    def setUp(self):
        self.kf = KalmanFilterEstimator(state_dim=1, process_noise=0.01,
                                        measurement_noise=1.0)
    
    def test_estimate(self):
        """Should estimate state."""
        self.kf.predict()
        self.kf.update(10.0)
        est = self.kf.get_state()
        self.assertGreater(est, 0.0)
        print(f"  [PASS] Estimate: {est:.3f}")
    
    def test_convergence(self):
        """Should converge to true value."""
        true_value = 5.0
        for _ in range(100):
            noise = (hash(str(_)) % 100 - 50) / 50.0
            self.kf.predict()
            self.kf.update(true_value + noise)
        est = self.kf.get_state()
        self.assertAlmostEqual(est, true_value, delta=0.5)
        print(f"  [PASS] Converge: est={est:.3f}, true={true_value}")


class TestPerformanceOptimizer(unittest.TestCase):
    """Test optimizer."""
    
    def setUp(self):
        self.opt = PerformanceOptimizer([(-1.0, 1.0), (-1.0, 1.0)])
    
    def test_optimize_step(self):
        """Should take optimization step."""
        def score(params):
            return -(params[0]**2 + params[1]**2)  # Maximize at (0,0)
        
        result = self.opt.optimize_step(score)
        self.assertIn("score", result)
        print(f"  [PASS] Step: score={result['score']:.4f}")
    
    def test_optimize(self):
        """Should optimize to maximum."""
        def score(params):
            return -(params[0]**2 + params[1]**2)
        
        result = self.opt.optimize(score, max_iterations=50)
        self.assertGreater(result["best_score"], -0.1)
        print(f"  [PASS] Optimize: best={result['best_score']:.4f}")


class TestMLPipeline(unittest.TestCase):
    """Test ML pipeline."""
    
    def setUp(self):
        self.pipe = MLPipeline()
        self.pipe.add_regressor("temp", 2)
        self.pipe.add_estimator("bias", 1)
        self.pipe.add_optimizer("thrust", [(0.0, 100.0)])
    
    def test_predict(self):
        """Should predict."""
        pred = self.pipe.predict("temp", [1.0, 0.0])
        self.assertIsInstance(pred, float)
        print(f"  [PASS] Pipeline predict: {pred:.4f}")
    
    def test_adapt(self):
        """Should adapt."""
        self.pipe.adapt("temp", [1.0, 0.0], 5.0)
        self.assertEqual(self.pipe.regressors["temp"].samples_seen, 1)
        print("  [PASS] Adapt: 1 sample")
    
    def test_estimate(self):
        """Should estimate."""
        est = self.pipe.estimate("bias", 10.0)
        self.assertGreater(est, 0.0)
        print(f"  [PASS] Estimate: {est:.3f}")
    
    def test_summary(self):
        """Should summarize."""
        summary = self.pipe.pipeline_summary()
        self.assertEqual(summary["regressors"], 1)
        print(f"  [PASS] Summary: {summary['regressors']} regressors")


if __name__ == '__main__':
    unittest.main(verbosity=2)
