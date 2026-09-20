"""
Unit tests for acoustic emission testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from acoustic_emission_testing import (AEEvent, AEEventDetector,
                                       SourceLocator,
                                       SeverityAssessor,
                                       AcousticEmissionTesting)


class TestAEEventDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.det = AEEventDetector(40.0)
    
    def test_detect(self):
        """Should detect events."""
        wf = [0.0] * 100 + [100.0] * 50 + [0.0] * 100
        events = self.det.detect(wf, 1.0, 0.0)
        self.assertGreater(len(events), 0)
        print(f"  [PASS] Det: {len(events)} events")
    
    def test_threshold(self):
        """Should respect threshold."""
        wf = [0.0] * 100 + [0.5] * 50 + [0.0] * 100
        events = self.det.detect(wf, 1.0, 0.0)
        self.assertEqual(len(events), 0)
        print("  [PASS] Thresh")


class TestSourceLocator(unittest.TestCase):
    """Test locator."""
    
    def setUp(self):
        self.loc = SourceLocator([
            (0.0, 0.0, 0.0), (100.0, 0.0, 0.0), (50.0, 100.0, 0.0)
        ])
    
    def test_locate(self):
        """Should locate source."""
        times = [0.0, 0.5, 0.3]
        pos = self.loc.locate(times, 5.0)
        self.assertEqual(len(pos), 3)
        print(f"  [PASS] Loc: ({pos[0]:.1f}, {pos[1]:.1f})")


class TestSeverityAssessor(unittest.TestCase):
    """Test assessor."""
    
    def setUp(self):
        self.sa = SeverityAssessor()
    
    def test_severity(self):
        """Should compute severity."""
        events = [AEEvent(60.0, 1e6, 100.0, 30.0, 10, 100.0, 0.0)]
        s = self.sa.severity_index(events)
        self.assertGreater(s, 0)
        print(f"  [PASS] Sev: {s:.2f}")
    
    def test_b_value(self):
        """Should compute b-value."""
        events = [
            AEEvent(40.0, 1e3, 50.0, 15.0, 5, 100.0, 0.0),
            AEEvent(50.0, 1e4, 80.0, 25.0, 8, 100.0, 0.0),
            AEEvent(60.0, 1e5, 100.0, 30.0, 10, 100.0, 0.0)
        ]
        b = self.sa.b_value(events)
        self.assertGreaterEqual(b, 0)
        print(f"  [PASS] b: {b:.4f}")


class TestAcousticEmissionTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.aet = AcousticEmissionTesting(40.0)
    
    def test_set_sensors(self):
        """Should set sensors."""
        self.aet.set_sensors([(0.0, 0.0, 0.0), (100.0, 0.0, 0.0)])
        self.assertIsNotNone(self.aet.locator)
        print("  [PASS] Sens")
    
    def test_process(self):
        """Should process waveform."""
        wf = [0.0] * 100 + [100.0] * 50 + [0.0] * 100
        self.aet.process(wf, 1.0)
        self.assertGreater(len(self.aet.events), 0)
        print("  [PASS] Proc")
    
    def test_inspect(self):
        """Should inspect."""
        wf = [0.0] * 100 + [100.0] * 50 + [0.0] * 100
        self.aet.process(wf, 1.0)
        r = self.aet.inspect()
        self.assertIn("events", r)
        print(f"  [PASS] Insp: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.aet.aet_summary()
        self.assertIn("events", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
