"""
Unit tests for eddy current inspection module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from eddy_current import (EddyDefectType, ImpedancePoint,
                          ImpedancePlane, ConductivityMeter,
                          LiftOffCompensator, EddyDefectDetector,
                          EddyCurrent)


class TestImpedancePlane(unittest.TestCase):
    """Test impedance plane."""
    
    def setUp(self):
        self.ip = ImpedancePlane()
        self.ip.add_point(ImpedancePoint(10.0, 5.0))
        self.ip.add_point(ImpedancePoint(12.0, 7.0))
    
    def test_magnitude(self):
        """Should compute magnitude."""
        mag = self.ip.magnitude(ImpedancePoint(3.0, 4.0))
        self.assertAlmostEqual(mag, 5.0)
        print("  [PASS] Mag")
    
    def test_phase(self):
        """Should compute phase."""
        ph = self.ip.phase_angle(ImpedancePoint(1.0, 1.0))
        self.assertAlmostEqual(ph, math.pi / 4, places=5)
        print("  [PASS] Phase")
    
    def test_trajectory(self):
        """Should compute trajectory."""
        tl = self.ip.trajectory_length()
        self.assertGreater(tl, 0)
        print(f"  [PASS] Traj: {tl:.3f}")


class TestConductivityMeter(unittest.TestCase):
    """Test conductivity meter."""
    
    def setUp(self):
        self.cm = ConductivityMeter()
    
    def test_estimate(self):
        """Should estimate conductivity."""
        ref = ImpedancePoint(10.0, 5.0)
        samp = ImpedancePoint(5.0, 2.5)
        c = self.cm.conductivity_from_impedance(ref, samp, 35.0)
        self.assertGreater(c, 0)
        print(f"  [PASS] Cond: {c:.1f}")
    
    def test_classify(self):
        """Should classify material."""
        mat = self.cm.classify_material(35.0)
        self.assertEqual(mat, "aluminum")
        print(f"  [PASS] Mat: {mat}")


class TestLiftOffCompensator(unittest.TestCase):
    """Test lift-off compensator."""
    
    def setUp(self):
        self.loc = LiftOffCompensator()
    
    def test_normalize(self):
        """Should normalize."""
        n = self.loc.normalized_impedance(
            ImpedancePoint(5.0, 5.0),
            ImpedancePoint(5.0, 0.0)
        )
        self.assertAlmostEqual(n[0], 1.0)
        print(f"  [PASS] Norm: {n}")


class TestEddyDefectDetector(unittest.TestCase):
    """Test defect detector."""
    
    def setUp(self):
        self.edd = EddyDefectDetector()
    
    def test_detect(self):
        """Should detect defects."""
        traj = [ImpedancePoint(10.0 + i, 5.0) for i in range(10)]
        traj[5] = ImpedancePoint(50.0, 5.0)
        ref = ImpedancePoint(10.0, 5.0)
        defects = self.edd.detect(traj, ref)
        self.assertGreater(len(defects), 0)
        print(f"  [PASS] Defects: {len(defects)}")
    
    def test_depth(self):
        """Should estimate depth."""
        d = self.edd.depth_estimate(20.0, 1000.0, 35.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Depth: {d:.4f}mm")


class TestEddyCurrent(unittest.TestCase):
    """Test unified eddy current."""
    
    def setUp(self):
        self.ec = EddyCurrent()
    
    def test_inspect(self):
        """Should inspect."""
        traj = [ImpedancePoint(10.0 + i * 0.1, 5.0) for i in range(20)]
        ref = ImpedancePoint(10.0, 5.0)
        r = self.ec.inspect(traj, ref, "aluminum")
        self.assertIn("estimated_conductivity", r)
        print(f"  [PASS] Insp: cond={r['estimated_conductivity']:.1f}")
    
    def test_skin_depth(self):
        """Should compute skin depth."""
        d = self.ec.skin_depth(1000.0, 35.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] Skin: {d:.4f}mm")
    
    def test_summary(self):
        """Should summarize."""
        traj = [ImpedancePoint(10.0, 5.0) for _ in range(5)]
        self.ec.inspect(traj, ImpedancePoint(10.0, 5.0))
        s = self.ec.inspection_summary()
        self.assertIn("inspections", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    import math
    unittest.main(verbosity=2)
