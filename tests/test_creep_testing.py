"""
Unit tests for creep testing module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from creep_testing import (CreepDataPoint, SteadyStateCreep,
                           LarsonMillerParameter,
                           StressRupture,
                           TertiaryCreep,
                           CreepTesting)


class TestSteadyStateCreep(unittest.TestCase):
    """Test steady state."""
    
    def setUp(self):
        self.ss = SteadyStateCreep(1.0e-10, 5.0, 200.0)
    
    def test_creep_rate(self):
        """Should compute creep rate."""
        rate = self.ss.creep_rate(100.0, 800.0)
        self.assertGreater(rate, 0)
        print(f"  [PASS] Rate: {rate:.2e} 1/h")
    
    def test_activation_energy(self):
        """Should estimate Q."""
        rates = [1e-5, 1e-4, 1e-3]
        temps = [700.0, 800.0, 900.0]
        Q = self.ss.activation_energy(rates, temps)
        self.assertIsInstance(Q, float)
        print(f"  [PASS] Q: {Q:.1f} kJ/mol")


class TestLarsonMiller(unittest.TestCase):
    """Test LMP."""
    
    def setUp(self):
        self.lmp = LarsonMillerParameter(20.0)
    
    def test_parameter(self):
        """Should compute LMP."""
        p = self.lmp.parameter(800.0, 1000.0)
        self.assertGreater(p, 0)
        print(f"  [PASS] LMP: {p:.2f}")
    
    def test_rupture_time(self):
        """Should predict rupture."""
        tr = self.lmp.rupture_time(20.0, 800.0)
        self.assertGreater(tr, 0)
        print(f"  [PASS] Tr: {tr:.1f} h")


class TestStressRupture(unittest.TestCase):
    """Test rupture."""
    
    def setUp(self):
        self.sr = StressRupture()
    
    def test_monkman_grant(self):
        """Should compute MG product."""
        mg = self.sr.monkman_grant(1e-5, 0.1)
        self.assertEqual(mg, 10000.0)
        print(f"  [PASS] MG: {mg:.0f}")
    
    def test_rupture_life(self):
        """Should estimate life."""
        life = self.sr.rupture_life_stress(100.0)
        self.assertGreater(life, 0)
        print(f"  [PASS] Life: {life:.2f} h")


class TestTertiaryCreep(unittest.TestCase):
    """Test tertiary."""
    
    def setUp(self):
        self.tc = TertiaryCreep()
    
    def test_damage(self):
        """Should compute damage."""
        d = self.tc.damage_parameter(80.0, 100.0)
        self.assertAlmostEqual(d, 0.2, delta=0.01)
        print(f"  [PASS] D: {d:.2f}")


class TestCreepTesting(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ct = CreepTesting()
    
    def test_summary(self):
        """Should summarize."""
        s = self.ct.creep_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
