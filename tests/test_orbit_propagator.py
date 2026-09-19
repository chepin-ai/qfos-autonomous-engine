"""
Unit tests for orbit propagator module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orbit_propagator import (KeplerianElements, StateVector,
                              KeplerPropagator, SGP4Propagator,
                              OrbitPropagator)


class TestKeplerianElements(unittest.TestCase):
    """Test Keplerian elements."""
    
    def test_period(self):
        """Should compute period."""
        e = KeplerianElements(7000, 0.1, 0.5, 0, 0, 0)
        p = e.period()
        self.assertGreater(p, 5000)
        print(f"  [PASS] Period: {p:.0f}s")
    
    def test_mean_motion(self):
        """Should compute mean motion."""
        e = KeplerianElements(7000, 0.1, 0.5, 0, 0, 0)
        n = e.mean_motion()
        self.assertGreater(n, 0)
        print(f"  [PASS] Mean motion: {n:.6f} rad/s")


class TestKeplerPropagator(unittest.TestCase):
    """Test Kepler propagator."""
    
    def setUp(self):
        self.prop = KeplerPropagator()
        self.elements = KeplerianElements(
            semi_major_axis=7000.0,
            eccentricity=0.1,
            inclination=math.radians(45.0),
            raan=math.radians(30.0),
            arg_perigee=math.radians(60.0),
            true_anomaly=math.radians(0.0)
        )
    
    def test_propagate_period(self):
        """Should return to start after one period."""
        period = self.elements.period()
        prop = self.prop.propagate(self.elements, period)
        # Should be approximately same anomaly
        diff = abs(prop.true_anomaly - self.elements.true_anomaly)
        self.assertLess(diff, 0.1)
        print(f"  [PASS] Period: diff={diff:.4f} rad")
    
    def test_propagate_zero(self):
        """Should not change at dt=0."""
        prop = self.prop.propagate(self.elements, 0)
        self.assertAlmostEqual(prop.true_anomaly, self.elements.true_anomaly, places=5)
        print("  [PASS] Zero dt: unchanged")
    
    def test_elements_to_state(self):
        """Should convert to state vector."""
        state = self.prop.elements_to_state(self.elements)
        self.assertEqual(len(state.position), 3)
        self.assertEqual(len(state.velocity), 3)
        r = math.sqrt(sum(c**2 for c in state.position))
        self.assertAlmostEqual(r, 6300.0, delta=50.0)  # ~a(1-e)
        print(f"  [PASS] State: r={r:.1f} km")
    
    def test_state_to_elements_roundtrip(self):
        """Should round-trip convert."""
        state = self.prop.elements_to_state(self.elements)
        recovered = self.prop.state_to_elements(state)
        self.assertAlmostEqual(recovered.semi_major_axis, self.elements.semi_major_axis, delta=1.0)
        self.assertAlmostEqual(recovered.eccentricity, self.elements.eccentricity, delta=0.01)
        print(f"  [PASS] Roundtrip: a={recovered.semi_major_axis:.1f}")
    
    def test_circular_orbit(self):
        """Should handle circular orbit."""
        circ = KeplerianElements(7000, 0.0, 0.0, 0.0, 0.0, 0.0)
        state = self.prop.elements_to_state(circ)
        r = math.sqrt(sum(c**2 for c in state.position))
        self.assertAlmostEqual(r, 7000.0, delta=1.0)
        print(f"  [PASS] Circular: r={r:.1f} km")


class TestSGP4Propagator(unittest.TestCase):
    """Test SGP4 propagator."""
    
    def setUp(self):
        self.sgp4 = SGP4Propagator()
        self.elements = KeplerianElements(
            semi_major_axis=7000.0,
            eccentricity=0.05,
            inclination=math.radians(51.6),
            raan=math.radians(0.0),
            arg_perigee=math.radians(0.0),
            true_anomaly=math.radians(0.0)
        )
    
    def test_propagate_j2(self):
        """Should propagate with J2."""
        prop = self.sgp4.propagate_with_j2(self.elements, 3600)
        self.assertNotEqual(prop.raan, self.elements.raan)
        print(f"  [PASS] J2: RAAN shift={math.degrees(prop.raan - self.elements.raan):.4f} deg")
    
    def test_raan_regression(self):
        """RAAN should regress for prograde orbit."""
        prop = self.sgp4.propagate_with_j2(self.elements, 86400)
        self.assertLess(prop.raan, self.elements.raan)
        print("  [PASS] RAAN regression: confirmed")


class TestOrbitPropagator(unittest.TestCase):
    """Test unified orbit propagator."""
    
    def setUp(self):
        self.op = OrbitPropagator()
        self.elements = KeplerianElements(
            semi_major_axis=7000.0,
            eccentricity=0.1,
            inclination=math.radians(45.0),
            raan=0.0,
            arg_perigee=0.0,
            true_anomaly=0.0
        )
    
    def test_propagate_kepler(self):
        """Should propagate without J2."""
        prop = self.op.propagate(self.elements, 1000, use_j2=False)
        self.assertNotEqual(prop.true_anomaly, self.elements.true_anomaly)
        print("  [PASS] Kepler: propagated")
    
    def test_propagate_j2(self):
        """Should propagate with J2."""
        prop = self.op.propagate(self.elements, 1000, use_j2=True)
        self.assertNotEqual(prop.raan, self.elements.raan)
        print("  [PASS] J2: propagated")
    
    def test_generate_ephemeris(self):
        """Should generate ephemeris."""
        states = self.op.generate_ephemeris(self.elements, 0, 3600, 600)
        self.assertGreater(len(states), 5)
        print(f"  [PASS] Ephemeris: {len(states)} states")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.op.propagator_summary()
        self.assertIn("mu", summary)
        print(f"  [PASS] Summary: mu={summary['mu']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
