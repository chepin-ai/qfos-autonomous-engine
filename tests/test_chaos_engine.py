"""
Unit tests for chaos engineering module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chaos_engine import ChaosEngine, ChaosExperiment, SteadyStateMonitor, ExperimentStatus


class TestSteadyStateMonitor(unittest.TestCase):
    """Test steady state monitor."""
    
    def setUp(self):
        self.mon = SteadyStateMonitor()
    
    def test_add_check(self):
        """Should add check."""
        self.mon.add_check("health", lambda: True)
        result = self.mon.verify()
        self.assertTrue(result["all_pass"])
        print("  [PASS] Check: pass")
    
    def test_add_metric(self):
        """Should add metric."""
        self.mon.add_metric("cpu", (0.0, 100.0))
        self.mon.record_metric("cpu", 50.0)
        result = self.mon.verify()
        self.assertTrue(result["all_pass"])
        print("  [PASS] Metric: pass")
    
    def test_metric_fail(self):
        """Should detect metric violation."""
        self.mon.add_metric("cpu", (0.0, 50.0))
        self.mon.record_metric("cpu", 75.0)
        result = self.mon.verify()
        self.assertFalse(result["all_pass"])
        print("  [PASS] Metric fail: detected")


class TestChaosExperiment(unittest.TestCase):
    """Test chaos experiment."""
    
    def setUp(self):
        self.exp = ChaosExperiment("exp_1", "Test experiment")
        self.exp.monitor.add_check("always_ok", lambda: True)
        self.disrupted = False
        self.rolled_back = False
        self.exp.add_disruption(lambda: setattr(self, 'disrupted', True))
        self.exp.add_rollback(lambda: setattr(self, 'rolled_back', True))
    
    def test_run(self):
        """Should run experiment."""
        result = self.exp.run()
        self.assertEqual(result.status, ExperimentStatus.COMPLETED)
        self.assertTrue(self.disrupted)
        self.assertTrue(self.rolled_back)
        print("  [PASS] Run: completed")
    
    def test_steady_state(self):
        """Should verify steady state."""
        result = self.exp.run()
        self.assertTrue(result.steady_state_met)
        print("  [PASS] Steady state: met")
    
    def test_logs(self):
        """Should produce logs."""
        result = self.exp.run()
        self.assertGreater(len(result.logs), 0)
        print(f"  [PASS] Logs: {len(result.logs)} entries")


class TestChaosEngine(unittest.TestCase):
    """Test chaos engine."""
    
    def setUp(self):
        self.engine = ChaosEngine()
    
    def test_create_experiment(self):
        """Should create experiment."""
        exp = self.engine.create_experiment("exp_1")
        self.assertIn("exp_1", self.engine.experiments)
        print("  [PASS] Create: exp_1")
    
    def test_run_experiment(self):
        """Should run experiment."""
        exp = self.engine.create_experiment("exp_1")
        exp.monitor.add_check("ok", lambda: True)
        result = self.engine.run_experiment("exp_1")
        self.assertIsNotNone(result)
        self.assertEqual(result.status, ExperimentStatus.COMPLETED)
        print("  [PASS] Run: completed")
    
    def test_run_all(self):
        """Should run all pending."""
        exp1 = self.engine.create_experiment("exp_1")
        exp1.monitor.add_check("ok", lambda: True)
        exp2 = self.engine.create_experiment("exp_2")
        exp2.monitor.add_check("ok", lambda: True)
        results = self.engine.run_all()
        self.assertEqual(len(results), 2)
        print(f"  [PASS] Run all: {len(results)} experiments")
    
    def test_resilience_score(self):
        """Should compute resilience score."""
        exp = self.engine.create_experiment("exp_1")
        exp.monitor.add_check("ok", lambda: True)
        self.engine.run_experiment("exp_1")
        score = self.engine.get_resilience_score()
        self.assertEqual(score, 1.0)
        print(f"  [PASS] Resilience: {score}")
    
    def test_stats(self):
        """Should provide stats."""
        exp = self.engine.create_experiment("exp_1")
        exp.monitor.add_check("ok", lambda: True)
        self.engine.run_experiment("exp_1")
        stats = self.engine.get_experiment_stats()
        self.assertEqual(stats["completed"], 1)
        print(f"  [PASS] Stats: {stats['completed']} completed")
    
    def test_summary(self):
        """Should provide summary."""
        exp = self.engine.create_experiment("exp_1")
        exp.monitor.add_check("ok", lambda: True)
        self.engine.run_experiment("exp_1")
        summary = self.engine.engine_summary()
        self.assertEqual(summary["experiments_run"], 1)
        print(f"  [PASS] Summary: {summary['experiments_run']} run")


if __name__ == '__main__':
    unittest.main(verbosity=2)
