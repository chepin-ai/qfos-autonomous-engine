"""
Unit tests for sample acquisition module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sample_acquisition import (DrillState, SampleQuality, Sample,
                                DrillController, SampleHandler,
                                SampleProcessor, SampleAcquisition)


class TestDrillController(unittest.TestCase):
    """Test drill controller."""
    
    def setUp(self):
        self.dc = DrillController(max_depth_m=1.0, drill_rate_m_per_min=0.6)
    
    def test_start(self):
        """Should start drilling."""
        ok = self.dc.start_drilling(0.5)
        self.assertTrue(ok)
        self.assertEqual(self.dc.state, DrillState.DRILLING)
        print("  [PASS] Start: drilling")
    
    def test_start_over_max(self):
        """Should not start over max depth."""
        ok = self.dc.start_drilling(3.0)
        self.assertFalse(ok)
        print("  [PASS] Over max: False")
    
    def test_progress(self):
        """Should track progress."""
        self.dc.start_drilling(1.0)
        self.dc.update_drilling(30.0)
        self.assertGreater(self.dc.get_progress(), 0)
        print(f"  [PASS] Progress: {self.dc.get_progress():.2f}")
    
    def test_complete(self):
        """Should complete drilling."""
        self.dc.start_drilling(1.0)
        while self.dc.update_drilling(10.0):
            pass
        self.assertEqual(self.dc.state, DrillState.SAMPLE_COLLECTED)
        print("  [PASS] Complete: collected")
    
    def test_retract(self):
        """Should retract."""
        self.dc.start_drilling(0.5)
        self.dc.retract()
        self.assertEqual(self.dc.state, DrillState.RETRACTING)
        self.assertEqual(self.dc.current_depth, 0.0)
        print("  [PASS] Retract: 0m")


class TestSampleHandler(unittest.TestCase):
    """Test sample handler."""
    
    def setUp(self):
        self.sh = SampleHandler(max_samples=3)
    
    def test_collect(self):
        """Should collect sample."""
        s = self.sh.collect_sample(0.8, mass_g=15.0)
        self.assertEqual(s.quality, SampleQuality.GOOD)
        self.assertEqual(len(self.sh.samples), 1)
        print(f"  [PASS] Collect: {s.sample_id}, quality={s.quality.value}")
    
    def test_quality_by_depth(self):
        """Depth should affect quality."""
        shallow = self.sh.collect_sample(0.05)
        deep = self.sh.collect_sample(1.5)
        self.assertEqual(shallow.quality, SampleQuality.POOR)
        self.assertEqual(deep.quality, SampleQuality.EXCELLENT)
        print(f"  [PASS] Quality: shallow={shallow.quality.value}, deep={deep.quality.value}")
    
    def test_max_capacity(self):
        """Should enforce max capacity."""
        for _ in range(5):
            self.sh.collect_sample(0.5)
        self.assertEqual(len(self.sh.samples), 3)
        print("  [PASS] Capacity: 3")
    
    def test_total_mass(self):
        """Should compute total mass."""
        self.sh.collect_sample(0.5, mass_g=10.0)
        self.sh.collect_sample(0.6, mass_g=20.0)
        self.assertEqual(self.sh.total_mass(), 30.0)
        print(f"  [PASS] Mass: {self.sh.total_mass()}")
    
    def test_remaining(self):
        """Should compute remaining."""
        self.sh.collect_sample(0.5)
        self.assertEqual(self.sh.remaining_capacity(), 2)
        print(f"  [PASS] Remaining: {self.sh.remaining_capacity()}")


class TestSampleProcessor(unittest.TestCase):
    """Test sample processor."""
    
    def setUp(self):
        self.sp = SampleProcessor()
        self.sample = Sample("S001", 0.8, 10.0, 5.0, SampleQuality.GOOD)
    
    def test_grind(self):
        """Should grind sample."""
        ground = self.sp.grind(self.sample)
        self.assertLess(ground.mass_g, self.sample.mass_g)
        self.assertIn("grind_size_um", ground.composition)
        print(f"  [PASS] Grind: {ground.mass_g:.1f}g")
    
    def test_sieve(self):
        """Should sieve sample."""
        coarse, fine = self.sp.sieve(self.sample)
        self.assertLess(coarse.mass_g, self.sample.mass_g)
        self.assertLess(fine.mass_g, self.sample.mass_g)
        total = coarse.mass_g + fine.mass_g
        self.assertAlmostEqual(total, self.sample.mass_g, places=1)
        print(f"  [PASS] Sieve: coarse={coarse.mass_g:.1f}, fine={fine.mass_g:.1f}")


class TestSampleAcquisition(unittest.TestCase):
    """Test unified sample acquisition."""
    
    def setUp(self):
        self.sa = SampleAcquisition()
    
    def test_drill_and_collect(self):
        """Should drill and collect."""
        sample = self.sa.drill_and_collect(0.5, timestamp=100.0)
        self.assertIsNotNone(sample)
        self.assertEqual(self.sa.drill.state, DrillState.RETRACTING)
        print(f"  [PASS] Drill: {sample.sample_id}")
    
    def test_process(self):
        """Should process sample."""
        sample = self.sa.drill_and_collect(0.5)
        processed = self.sa.process_sample(sample.sample_id, "grind")
        self.assertIsNotNone(processed)
        print(f"  [PASS] Process: {processed.sample_id}")
    
    def test_summary(self):
        """Should provide summary."""
        self.sa.drill_and_collect(0.5)
        summary = self.sa.acquisition_summary()
        self.assertEqual(summary["samples_stored"], 1)
        print(f"  [PASS] Summary: {summary['samples_stored']} samples")


if __name__ == '__main__':
    unittest.main(verbosity=2)
