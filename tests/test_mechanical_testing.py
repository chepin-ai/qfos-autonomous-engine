"""
Unit tests for mechanical testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mechanical_testing import (StressStrainPoint, TensileTest,
                                FatigueTest,
                                CreepTest,
                                CompressionTest,
                                MechanicalTesting)


class TestTensileTest(unittest.TestCase):
    """Test tensile."""
    
    def setUp(self):
        self.tt = TensileTest()
        for s in [0.0, 0.001, 0.002, 0.003]:
            self.tt.add_point(s, s * 200000.0)
    
    def test_young_modulus(self):
        """Should compute E."""
        e = self.tt.young_modulus()
        self.assertAlmostEqual(e, 200.0, delta=10.0)
        print(f"  [PASS] E: {e:.1f} GPa")
    
    def test_uts(self):
        """Should compute UTS."""
        u = self.tt.ultimate_tensile_strength()
        self.assertEqual(u, 600.0)
        print(f"  [PASS] UTS: {u}")


class TestFatigueTest(unittest.TestCase):
    """Test fatigue."""
    
    def setUp(self):
        self.ft = FatigueTest()
        self.ft.add_point(500.0, 1000)
        self.ft.add_point(400.0, 10000)
        self.ft.add_point(300.0, 100000)
    
    def test_endurance(self):
        """Should estimate endurance limit."""
        el = self.ft.endurance_limit(100000)
        self.assertGreaterEqual(el, 300.0)
        print(f"  [PASS] EL: {el:.1f}")
    
    def test_basquin(self):
        """Should fit Basquin."""
        sf, b = self.ft.basquin_law()
        self.assertGreater(sf, 0)
        print(f"  [PASS] Basq: sf={sf:.1f}, b={b:.4f}")


class TestCreepTest(unittest.TestCase):
    """Test creep."""
    
    def setUp(self):
        self.ct = CreepTest()
        for t in [0, 10, 20, 30, 40, 50]:
            self.ct.add_point(t, 0.001 + t * 0.0001)
    
    def test_creep_rate(self):
        """Should compute creep rate."""
        r = self.ct.creep_rate()
        self.assertGreater(r, 0)
        print(f"  [PASS] CR: {r:.6f}")


class TestCompressionTest(unittest.TestCase):
    """Test compression."""
    
    def setUp(self):
        self.ct = CompressionTest()
        for s in [0.0, 0.001, 0.002]:
            self.ct.add_point(s, s * 150000.0)
    
    def test_strength(self):
        """Should compute compressive strength."""
        cs = self.ct.compressive_strength()
        self.assertEqual(cs, 300.0)
        print(f"  [PASS] CS: {cs}")
    
    def test_modulus(self):
        """Should compute compressive modulus."""
        cm = self.ct.compressive_modulus()
        self.assertAlmostEqual(cm, 150.0, delta=5.0)
        print(f"  [PASS] CM: {cm:.1f} GPa")


class TestMechanicalTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.mt = MechanicalTesting()
    
    def test_summary(self):
        """Should summarize."""
        s = self.mt.mt_summary()
        self.assertIn("tests", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
