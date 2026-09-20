"""
Unit tests for material stress module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from material_stress import (StressState, StressTensor,
                             StrainAnalyzer, FatigueAnalyzer,
                             YieldAssessor, MaterialStress)


class TestStressTensor(unittest.TestCase):
    """Test stress tensor."""
    
    def test_von_mises_uniaxial(self):
        """Should compute von Mises for uniaxial."""
        s = StressTensor(sigma_x=100e6)
        vm = s.von_mises()
        self.assertAlmostEqual(vm, 100e6, places=3)
        print(f"  [PASS] VM: {vm/1e6:.1f} MPa")
    
    def test_von_mises_shear(self):
        """Should compute von Mises with shear."""
        s = StressTensor(tau_xy=50e6)
        vm = s.von_mises()
        expected = math.sqrt(3) * 50e6
        self.assertAlmostEqual(vm, expected, places=3)
        print(f"  [PASS] VM shear: {vm/1e6:.1f} MPa")
    
    def test_hydrostatic(self):
        """Should compute hydrostatic stress."""
        s = StressTensor(sigma_x=100e6, sigma_y=50e6, sigma_z=30e6)
        h = s.hydrostatic()
        self.assertAlmostEqual(h, 60e6, places=3)
        print(f"  [PASS] Hydro: {h/1e6:.1f} MPa")
    
    def test_principal(self):
        """Should compute principal stresses."""
        s = StressTensor(sigma_x=100e6, sigma_y=50e6, tau_xy=0.0)
        p = s.principal_stresses()
        self.assertAlmostEqual(p[0], 100e6, places=3)
        self.assertAlmostEqual(p[1], 50e6, places=3)
        # sigma_z defaults to 0, so min principal is 0
        print(f"  [PASS] Principal: [{p[0]/1e6:.1f}, {p[1]/1e6:.1f}, {p[2]/1e6:.1f}]")


class TestStrainAnalyzer(unittest.TestCase):
    """Test strain analyzer."""
    
    def setUp(self):
        self.sa = StrainAnalyzer(youngs_modulus_Pa=70e9)
    
    def test_normal_strain(self):
        """Should compute normal strain."""
        e = self.sa.normal_strain(70e6)
        self.assertAlmostEqual(e, 0.001)
        print(f"  [PASS] Strain: {e:.4f}")
    
    def test_shear_strain(self):
        """Should compute shear strain."""
        g = self.sa.shear_strain(35e6)
        self.assertGreater(g, 0)
        print(f"  [PASS] Shear: {g:.6f}")
    
    def test_energy_density(self):
        """Should compute strain energy."""
        s = StressTensor(sigma_x=100e6)
        u = self.sa.strain_energy_density(s)
        self.assertGreater(u, 0)
        print(f"  [PASS] Energy: {u:.1f} J/m^3")


class TestFatigueAnalyzer(unittest.TestCase):
    """Test fatigue analyzer."""
    
    def setUp(self):
        self.fa = FatigueAnalyzer(endurance_limit_Pa=100e6,
                                  fatigue_strength_coeff=1000e6,
                                  fatigue_ductility_exponent=-0.1)
    
    def test_infinite_life(self):
        """Should return infinite life below endurance."""
        n = self.fa.cycles_to_failure(50e6)
        self.assertEqual(n, float('inf'))
        print("  [PASS] Infinite: below endurance")
    
    def test_finite_life(self):
        """Should compute finite life."""
        n = self.fa.cycles_to_failure(200e6)
        self.assertGreater(n, 0)
        self.assertNotEqual(n, float('inf'))
        print(f"  [PASS] Finite: {n:.0f} cycles")
    
    def test_miner_damage(self):
        """Should compute Miner damage."""
        cycles = [(200e6, 1000), (300e6, 100)]
        d = self.fa.miner_damage(cycles)
        self.assertGreater(d, 0)
        print(f"  [PASS] Damage: {d:.6f}")
    
    def test_remaining_life(self):
        """Should compute remaining life."""
        cycles = [(200e6, 100)]
        rl = self.fa.remaining_life(cycles)
        self.assertGreater(rl, 0)
        print(f"  [PASS] Remaining: {rl:.4f}")


class TestYieldAssessor(unittest.TestCase):
    """Test yield assessor."""
    
    def setUp(self):
        self.ya = YieldAssessor(yield_strength_Pa=250e6)
    
    def test_elastic(self):
        """Should detect elastic."""
        s = StressTensor(sigma_x=100e6)
        state = self.ya.assess_von_mises(s)
        self.assertEqual(state, StressState.ELASTIC)
        print("  [PASS] Elastic")
    
    def test_yielded(self):
        """Should detect yielded."""
        s = StressTensor(sigma_x=300e6)
        state = self.ya.assess_von_mises(s)
        self.assertEqual(state, StressState.YIELDED)
        print("  [PASS] Yielded")
    
    def test_safety_factor(self):
        """Should compute safety factor."""
        s = StressTensor(sigma_x=125e6)
        sf = self.ya.safety_factor(s)
        self.assertAlmostEqual(sf, 2.0)
        print(f"  [PASS] SF: {sf}")
    
    def test_margin(self):
        """Should compute margin."""
        s = StressTensor(sigma_x=125e6)
        m = self.ya.margin_of_safety(s)
        self.assertAlmostEqual(m, 1.0)
        print(f"  [PASS] Margin: {m}")


class TestMaterialStress(unittest.TestCase):
    """Test unified material stress."""
    
    def setUp(self):
        self.ms = MaterialStress()
    
    def test_record(self):
        """Should record stress."""
        self.ms.record_stress(StressTensor(sigma_x=100e6))
        self.assertEqual(len(self.ms.history), 1)
        print("  [PASS] Record: 1")
    
    def test_state(self):
        """Should get state."""
        self.ms.record_stress(StressTensor(sigma_x=100e6))
        state = self.ms.current_state()
        self.assertEqual(state, StressState.ELASTIC)
        print(f"  [PASS] State: {state.value}")
    
    def test_health(self):
        """Should assess health."""
        self.ms.record_stress(StressTensor(sigma_x=100e6))
        health = self.ms.structural_health()
        self.assertIn("safety_factor", health)
        self.assertEqual(health["state"], "elastic")
        print(f"  [PASS] Health: SF={health['safety_factor']:.2f}")
    
    def test_cumulative_damage(self):
        """Should compute damage."""
        self.ms.record_stress(StressTensor(sigma_x=100e6))
        self.ms.record_stress(StressTensor(sigma_x=200e6))
        d = self.ms.cumulative_damage()
        self.assertGreaterEqual(d, 0)
        print(f"  [PASS] Damage: {d:.6f}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
