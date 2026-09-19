"""
Unit tests for attitude determination module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from attitude_determination import (Quaternion, VectorMeasurement, QUESTSolver,
                                    StarTracker, AttitudeDetermination)


class TestQuaternion(unittest.TestCase):
    """Test quaternion."""
    
    def test_normalize(self):
        """Should normalize."""
        q = Quaternion(2, 0, 0, 0)
        q.normalize()
        self.assertEqual(q.w, 1.0)
        print("  [PASS] Normalize: identity")
    
    def test_identity_rotation(self):
        """Identity should not rotate."""
        q = Quaternion(1, 0, 0, 0)
        v = q.rotate_vector((1, 0, 0))
        self.assertEqual(v, (1, 0, 0))
        print("  [PASS] Identity: no rotation")
    
    def test_90_degree_rotation(self):
        """Should rotate 90 degrees around Z."""
        q = Quaternion.from_axis_angle((0, 0, 1), math.pi / 2)
        v = q.rotate_vector((1, 0, 0))
        self.assertAlmostEqual(v[0], 0.0, places=5)
        self.assertAlmostEqual(v[1], 1.0, places=5)
        print("  [PASS] 90deg Z: (0, 1, 0)")
    
    def test_rotation_matrix(self):
        """Should produce rotation matrix."""
        q = Quaternion(1, 0, 0, 0)
        R = q.to_rotation_matrix()
        self.assertEqual(R[0][0], 1.0)
        print("  [PASS] Matrix: identity")
    
    def test_conjugate(self):
        """Should conjugate."""
        q = Quaternion(0.707, 0.707, 0, 0)
        qc = q.conjugate()
        self.assertEqual(qc.x, -0.707)
        print("  [PASS] Conjugate: negated")


class TestQUESTSolver(unittest.TestCase):
    """Test QUEST solver."""
    
    def setUp(self):
        self.quest = QUESTSolver()
    
    def test_add_measurement(self):
        """Should add measurement."""
        self.quest.add_measurement(VectorMeasurement((1, 0, 0), (1, 0, 0)))
        self.assertEqual(len(self.quest.measurements), 1)
        print("  [PASS] Add: 1 measurement")
    
    def test_solve_identity(self):
        """Should solve for identity attitude."""
        self.quest.add_measurement(VectorMeasurement((1, 0, 0), (1, 0, 0)))
        self.quest.add_measurement(VectorMeasurement((0, 1, 0), (0, 1, 0)))
        q = self.quest.solve()
        self.assertIsNotNone(q)
        # For identity, body = reference, so q should be close to identity
        self.assertGreater(q.w, 0.9)
        print(f"  [PASS] Identity: w={q.w:.3f}")
    
    def test_solve_rotation(self):
        """Should solve for rotated attitude."""
        # 90 degree rotation around Z
        true_q = Quaternion.from_axis_angle((0, 0, 1), math.pi / 2)
        
        # Reference vectors
        r1 = (1, 0, 0)
        r2 = (0, 1, 0)
        
        # Body vectors (rotated)
        b1 = true_q.rotate_vector(r1)
        b2 = true_q.rotate_vector(r2)
        
        self.quest.add_measurement(VectorMeasurement(b1, r1))
        self.quest.add_measurement(VectorMeasurement(b2, r2))
        
        q = self.quest.solve()
        self.assertIsNotNone(q)
        print(f"  [PASS] Rotation: w={q.w:.3f}")
    
    def test_insufficient_measurements(self):
        """Should return None with < 2 measurements."""
        self.quest.add_measurement(VectorMeasurement((1, 0, 0), (1, 0, 0)))
        q = self.quest.solve()
        self.assertIsNone(q)
        print("  [PASS] Insufficient: None")


class TestStarTracker(unittest.TestCase):
    """Test star tracker."""
    
    def setUp(self):
        self.st = StarTracker(fov_deg=30.0)
        self.st.add_star("Polaris", (0, 0, 1))
        self.st.add_star("Vega", (0.5, 0.5, 0.707))
    
    def test_add_star(self):
        """Should add star."""
        self.assertEqual(len(self.st.catalog), 2)
        print("  [PASS] Catalog: 2 stars")
    
    def test_observe(self):
        """Should observe stars."""
        q = Quaternion(1, 0, 0, 0)  # Identity
        obs = self.st.observe(q)
        self.assertGreater(len(obs), 0)
        print(f"  [PASS] Observe: {len(obs)} stars")
    
    def test_observe_identity(self):
        """Identity should see +Z stars."""
        q = Quaternion(1, 0, 0, 0)
        obs = self.st.observe(q)
        names = [name for name, _ in obs]
        self.assertIn("Polaris", names)
        print("  [PASS] Identity: sees Polaris")
    
    def test_identify_pattern(self):
        """Should identify pattern."""
        q = Quaternion(1, 0, 0, 0)
        obs = self.st.observe(q)
        measurements = self.st.identify_pattern(obs)
        self.assertGreater(len(measurements), 0)
        print(f"  [PASS] Pattern: {len(measurements)} measurements")


class TestAttitudeDetermination(unittest.TestCase):
    """Test unified attitude determination."""
    
    def setUp(self):
        self.ad = AttitudeDetermination()
    
    def test_add_measurement(self):
        """Should add measurement."""
        self.ad.add_vector_measurement((1, 0, 0), (1, 0, 0))
        self.assertEqual(len(self.ad.quest.measurements), 1)
        print("  [PASS] Add: 1 measurement")
    
    def test_determine_attitude(self):
        """Should determine attitude."""
        self.ad.add_vector_measurement((1, 0, 0), (1, 0, 0))
        self.ad.add_vector_measurement((0, 1, 0), (0, 1, 0))
        q = self.ad.determine_attitude()
        self.assertIsNotNone(q)
        print(f"  [PASS] Attitude: w={q.w:.3f}")
    
    def test_add_star(self):
        """Should add star."""
        self.ad.add_star("Polaris", (0, 0, 1))
        self.assertIn("Polaris", self.ad.star_tracker.catalog)
        print("  [PASS] Star: Polaris")
    
    def test_observe_stars(self):
        """Should observe stars."""
        self.ad.add_star("Polaris", (0, 0, 1))
        self.ad.current_attitude = Quaternion(1, 0, 0, 0)
        obs = self.ad.observe_stars()
        self.assertGreater(len(obs), 0)
        print(f"  [PASS] Observe: {len(obs)} stars")
    
    def test_summary(self):
        """Should provide summary."""
        self.ad.add_vector_measurement((1, 0, 0), (1, 0, 0))
        summary = self.ad.determination_summary()
        self.assertEqual(summary["measurements"], 1)
        print(f"  [PASS] Summary: {summary['measurements']} measurements")


if __name__ == '__main__':
    unittest.main(verbosity=2)
