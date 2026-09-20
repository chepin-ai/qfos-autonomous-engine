"""
Unit tests for acoustic emission module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from acoustic_emission import (AEEventType, AEHit, AESensor,
                               AEEventDetector, AESourceLocator,
                               AcousticEmission)


class TestAESensor(unittest.TestCase):
    """Test AE sensor."""
    
    def setUp(self):
        self.s = AESensor(0, (0.0, 0.0), 40.0)
    
    def test_detect(self):
        """Should detect above threshold."""
        h = self.s.detect(50.0, 1.0, 100.0, 5.0, 10, 0.0)
        self.assertIsNotNone(h)
        self.assertEqual(h.sensor_id, 0)
        print("  [PASS] Detect")
    
    def test_no_detect(self):
        """Should not detect below threshold."""
        h = self.s.detect(30.0, 1.0, 100.0, 5.0, 10, 0.0)
        self.assertIsNone(h)
        print("  [PASS] NoDetect")
    
    def test_hit_rate(self):
        """Should compute hit rate."""
        self.s.detect(50.0, 1.0, 100.0, 5.0, 10, 0.0)
        self.s.detect(55.0, 1.5, 120.0, 6.0, 15, 1.0)
        r = self.s.hit_rate(2.0)
        self.assertGreaterEqual(r, 0.0)
        print(f"  [PASS] Rate: {r:.1f}")


class TestAEEventDetector(unittest.TestCase):
    """Test event detector."""
    
    def setUp(self):
        self.ed = AEEventDetector()
    
    def test_cluster(self):
        """Should cluster hits."""
        hits = [
            AEHit(0, 50.0, 1.0, 100.0, 5.0, 10, 0.0),
            AEHit(1, 55.0, 1.2, 110.0, 6.0, 12, 2.0),
            AEHit(2, 60.0, 1.5, 120.0, 7.0, 15, 10.0)
        ]
        clusters = self.ed.cluster_hits(hits)
        self.assertGreater(len(clusters), 0)
        print(f"  [PASS] Clusters: {len(clusters)}")
    
    def test_event_energy(self):
        """Should compute energy."""
        cluster = [AEHit(0, 50.0, 1.0, 100.0, 5.0, 10, 0.0),
                   AEHit(1, 55.0, 2.0, 110.0, 6.0, 12, 2.0)]
        e = self.ed.event_energy(cluster)
        self.assertEqual(e, 3.0)
        print(f"  [PASS] E: {e}")
    
    def test_classify(self):
        """Should classify event."""
        cluster = [AEHit(0, 85.0, 1.0, 50.0, 5.0, 10, 0.0)]
        t = self.ed.classify_event(cluster)
        self.assertIsInstance(t, AEEventType)
        print(f"  [PASS] Type: {t.value}")


class TestAESourceLocator(unittest.TestCase):
    """Test source locator."""
    
    def setUp(self):
        self.sl = AESourceLocator()
    
    def test_tdoa(self):
        """Should locate source."""
        pos = [(0.0, 0.0), (100.0, 0.0), (0.0, 100.0)]
        times = [0.0, 20.0, 20.0]
        src = self.sl.time_difference_of_arrival(pos, times)
        self.assertIsNotNone(src)
        print(f"  [PASS] Src: {src}")
    
    def test_distance(self):
        """Should compute distance."""
        d = self.sl.distance_to_source((0.0, 0.0), (30.0, 40.0))
        self.assertAlmostEqual(d, 50.0)
        print(f"  [PASS] Dist: {d}")
    
    def test_arrival(self):
        """Should compute arrival."""
        t = self.sl.expected_arrival((0.0, 0.0), (50.0, 0.0), 0.0)
        self.assertEqual(t, 10.0)
        print(f"  [PASS] Arr: {t}")


class TestAcousticEmission(unittest.TestCase):
    """Test unified AE."""
    
    def setUp(self):
        self.ae = AcousticEmission()
        self.ae.add_sensor((0.0, 0.0), 40.0)
        self.ae.add_sensor((100.0, 0.0), 40.0)
    
    def test_add_sensor(self):
        """Should add sensor."""
        self.assertEqual(len(self.ae.sensors), 2)
        print("  [PASS] AddSens")
    
    def test_monitor(self):
        """Should monitor."""
        signals = [
            {"amplitude": 50.0, "energy": 1.0, "duration": 100.0, "rise_time": 5.0, "counts": 10, "timestamp": 0.0},
            {"amplitude": 55.0, "energy": 1.2, "duration": 110.0, "rise_time": 6.0, "counts": 12, "timestamp": 2.0}
        ]
        self.ae.monitor(signals)
        self.assertGreater(len(self.ae.events), 0)
        print(f"  [PASS] Events: {len(self.ae.events)}")
    
    def test_locate(self):
        """Should locate."""
        src = self.ae.locate_source([0.0, 20.0, 20.0])
        self.assertIsNotNone(src)
        print(f"  [PASS] Locate: {src}")
    
    def test_summary(self):
        """Should summarize."""
        signals = [{"amplitude": 50.0, "energy": 1.0, "duration": 100.0, "rise_time": 5.0, "counts": 10, "timestamp": 0.0}]
        self.ae.monitor(signals)
        s = self.ae.emission_summary()
        self.assertIn("total_events", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
