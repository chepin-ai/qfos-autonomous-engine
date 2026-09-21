"""
Unit tests for powder metallurgy module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from powder_metallurgy import (PowderParticle, PowderCharacterization,
                               CompactionModeling,
                               SinteringKinetics,
                               Densification,
                               PowderMetallurgy)


class TestPowderCharacterization(unittest.TestCase):
    """Test characterization."""
    
    def setUp(self):
        self.pc = PowderCharacterization()
        self.particles = [PowderParticle(10.0, 7.87),
                          PowderParticle(20.0, 7.87),
                          PowderParticle(30.0, 7.87)]
    
    def test_smd(self):
        """Should compute SMD."""
        s = self.pc.sauter_mean_diameter(self.particles)
        self.assertGreater(s, 0)
        print(f"  [PASS] SMD: {s:.2f}")
    
    def test_packing(self):
        """Should compute packing."""
        p = self.pc.packing_density(self.particles, 4.0)
        self.assertGreater(p, 0)
        print(f"  [PASS] Pack: {p:.4f}")
    
    def test_ssa(self):
        """Should compute SSA."""
        s = self.pc.specific_surface_area(self.particles)
        self.assertGreater(s, 0)
        print(f"  [PASS] SSA: {s:.4e}")


class TestCompactionModeling(unittest.TestCase):
    """Test compaction."""
    
    def setUp(self):
        self.cm = CompactionModeling()
    
    def test_relative(self):
        """Should compute relative density."""
        r = self.cm.relative_density(5.0)
        self.assertGreater(r, 0)
        print(f"  [PASS] RD: {r:.4f}")
    
    def test_pressure(self):
        """Should compute pressure."""
        p = self.cm.compaction_pressure(200.0, 0.8)
        self.assertGreater(p, 0)
        print(f"  [PASS] P: {p:.2f}")


class TestSinteringKinetics(unittest.TestCase):
    """Test sintering."""
    
    def setUp(self):
        self.sk = SinteringKinetics()
    
    def test_rate(self):
        """Should compute densification rate."""
        r = self.sk.densification_rate(3600.0)
        self.assertGreater(r, 0)
        print(f"  [PASS] Rate: {r:.4e}")
    
    def test_neck(self):
        """Should compute neck growth."""
        n = self.sk.neck_growth_ratio(3600.0)
        self.assertGreater(n, 0)
        print(f"  [PASS] Neck: {n:.4f}")


class TestDensification(unittest.TestCase):
    """Test densification."""
    
    def setUp(self):
        self.d = Densification()
    
    def test_final(self):
        """Should compute final density."""
        f = self.d.final_density(4.0, 15.0)
        self.assertGreater(f, 4.0)
        print(f"  [PASS] FD: {f:.4f}")
    
    def test_shrinkage(self):
        """Should compute shrinkage."""
        s = self.d.shrinkage_from_density(4.0, 6.0)
        self.assertGreater(s, 0)
        print(f"  [PASS] Shrink: {s:.2f}%")


class TestPowderMetallurgy(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.pm = PowderMetallurgy()
    
    def test_summary(self):
        """Should summarize."""
        s = self.pm.powder_summary()
        self.assertIn("processes", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
