"""
Unit tests for motion planning sampling module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from motion_planning_sampling import (ConfigNode, PRMSampling,
                                      RRTVariants,
                                      BiasedSampling,
                                      ConfigurationSpaceCoverage,
                                      MotionPlanningSampling)


class TestPRMSampling(unittest.TestCase):
    """Test PRM."""
    
    def setUp(self):
        self.prm = PRMSampling((0.0, 10.0, 0.0, 10.0))
    
    def test_uniform(self):
        """Should sample uniformly."""
        p = self.prm.uniform_sample()
        self.assertEqual(len(p), 2)
        print(f"  [PASS] U: ({p[0]:.2f}, {p[1]:.2f})")
    
    def test_gaussian(self):
        """Should sample Gaussian."""
        p = self.prm.gaussian_sample(5.0, 5.0)
        self.assertEqual(len(p), 2)
        print(f"  [PASS] G: ({p[0]:.2f}, {p[1]:.2f})")
    
    def test_obstacle(self):
        """Should sample with bias."""
        p = self.prm.obstacle_bias_sample([(5.0, 5.0)])
        self.assertEqual(len(p), 2)
        print(f"  [PASS] OB: ({p[0]:.2f}, {p[1]:.2f})")


class TestRRTVariants(unittest.TestCase):
    """Test RRT."""
    
    def setUp(self):
        self.rrt = RRTVariants()
    
    def test_nearest(self):
        """Should find nearest."""
        nodes = [ConfigNode(0.0, 0.0), ConfigNode(3.0, 4.0)]
        i = self.rrt.nearest_neighbor(nodes, (3.0, 4.0))
        self.assertEqual(i, 1)
        print(f"  [PASS] NN: {i}")
    
    def test_steer(self):
        """Should steer."""
        node = ConfigNode(0.0, 0.0)
        n = self.rrt.steer(node, (1.0, 0.0))
        self.assertAlmostEqual(n.x, 0.5, delta=1e-10)
        print(f"  [PASS] S: ({n.x:.2f}, {n.y:.2f})")


class TestBiasedSampling(unittest.TestCase):
    """Test biased."""
    
    def setUp(self):
        self.bs = BiasedSampling((10.0, 10.0))
    
    def test_goal(self):
        """Should sample goal-biased."""
        p = self.bs.goal_biased_sample((0.0, 10.0, 0.0, 10.0))
        self.assertEqual(len(p), 2)
        print(f"  [PASS] GB: ({p[0]:.2f}, {p[1]:.2f})")
    
    def test_heuristic(self):
        """Should sample heuristically."""
        p = self.bs.heuristic_sample((0.0, 0.0), (10.0, 10.0))
        self.assertAlmostEqual(p[0], 3.0, delta=1e-10)
        self.assertAlmostEqual(p[1], 3.0, delta=1e-10)
        print(f"  [PASS] H: ({p[0]:.2f}, {p[1]:.2f})")


class TestConfigurationSpaceCoverage(unittest.TestCase):
    """Test coverage."""
    
    def setUp(self):
        self.csc = ConfigurationSpaceCoverage()
    
    def test_ratio(self):
        """Should compute coverage."""
        points = [(1.0, 1.0), (5.0, 5.0), (9.0, 9.0)]
        r = self.csc.coverage_ratio(points, (0.0, 10.0, 0.0, 10.0), 2.0)
        self.assertGreaterEqual(r, 0)
        print(f"  [PASS] Cov: {r:.3f}")
    
    def test_dispersion(self):
        """Should compute dispersion."""
        points = [(5.0, 5.0)]
        d = self.csc.dispersion(points, (0.0, 10.0, 0.0, 10.0))
        self.assertEqual(d, 0.0)
        print(f"  [PASS] Disp: {d:.2f}")


class TestMotionPlanningSampling(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.mps = MotionPlanningSampling()
    
    def test_summary(self):
        """Should summarize."""
        s = self.mps.sampling_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
