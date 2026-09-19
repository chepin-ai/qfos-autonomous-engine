"""
Unit tests for materials simulator module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from materials_simulator import Material, ThermalAnalyzer, StressAnalyzer, MaterialsSimulator


# Common materials
ALUMINUM = Material(
    name="Aluminum-6061",
    density=2700.0,
    thermal_conductivity=167.0,
    specific_heat=897.0,
    youngs_modulus=68.9e9,
    yield_strength=276e6,
    thermal_expansion=23.6e-6,
    emissivity=0.3
)

TITANIUM = Material(
    name="Titanium-6Al-4V",
    density=4430.0,
    thermal_conductivity=6.7,
    specific_heat=526.0,
    youngs_modulus=113.8e9,
    yield_strength=880e6,
    thermal_expansion=8.6e-6,
    emissivity=0.4
)


class TestThermalAnalyzer(unittest.TestCase):
    """Test thermal analyzer."""
    
    def setUp(self):
        self.ta = ThermalAnalyzer(ALUMINUM)
    
    def test_analyze(self):
        """Should compute thermal profile."""
        profile = self.ta.analyze(1000.0, 0.1, 0.005, ambient_temp=300.0)
        self.assertGreater(profile.max_temp, profile.min_temp)
        self.assertEqual(len(profile.temperatures), 11)
        print(f"  [PASS] Thermal: max={profile.max_temp:.1f}K")
    
    def test_heat_flux(self):
        """Should compute heat flux."""
        profile = self.ta.analyze(1000.0, 0.1, 0.005)
        self.assertEqual(profile.heat_flux, 10000.0)
        print(f"  [PASS] Flux: {profile.heat_flux:.0f} W/m^2")
    
    def test_thermal_shock_pass(self):
        """Should pass thermal shock check."""
        result = self.ta.thermal_shock_check(50.0, 10.0)
        self.assertTrue(result)
        print("  [PASS] Shock: pass")
    
    def test_thermal_shock_fail(self):
        """Should fail thermal shock check."""
        result = self.ta.thermal_shock_check(500.0, 1.0)
        self.assertFalse(result)
        print("  [PASS] Shock: fail")
    
    def test_titanium_lower_conductivity(self):
        """Titanium should have higher temp rise."""
        ta_al = ThermalAnalyzer(ALUMINUM)
        ta_ti = ThermalAnalyzer(TITANIUM)
        prof_al = ta_al.analyze(1000.0, 0.1, 0.005, ambient_temp=300.0)
        prof_ti = ta_ti.analyze(1000.0, 0.1, 0.005, ambient_temp=300.0)
        self.assertGreater(prof_ti.max_temp, prof_al.max_temp)
        print(f"  [PASS] Ti hotter: Ti={prof_ti.max_temp:.1f}K > Al={prof_al.max_temp:.1f}K")


class TestStressAnalyzer(unittest.TestCase):
    """Test stress analyzer."""
    
    def setUp(self):
        self.sa = StressAnalyzer(ALUMINUM)
    
    def test_tensile(self):
        """Should compute tensile stress."""
        result = self.sa.analyze_tensile(10000.0, 0.001)
        self.assertEqual(result.von_mises, 10e6)
        print(f"  [PASS] Tensile: {result.von_mises/1e6:.1f} MPa")
    
    def test_safety_factor(self):
        """Should compute safety factor."""
        result = self.sa.analyze_tensile(10000.0, 0.001)
        self.assertGreater(result.safety_factor, 1.0)
        print(f"  [PASS] SF: {result.safety_factor:.1f}")
    
    def test_yield_detection(self):
        """Should detect yielding."""
        result = self.sa.analyze_tensile(500000.0, 0.001)
        self.assertTrue(result.deformed)
        print("  [PASS] Yield: detected")
    
    def test_bending(self):
        """Should compute bending stress."""
        result = self.sa.analyze_bending(1000.0, 0.05, 0.1)
        self.assertGreater(result.von_mises, 0)
        print(f"  [PASS] Bending: {result.von_mises/1e6:.1f} MPa")
    
    def test_thermal_stress(self):
        """Should compute thermal stress."""
        stress = self.sa.thermal_stress(100.0, constrained=True)
        self.assertGreater(stress, 0)
        print(f"  [PASS] Thermal stress: {stress/1e6:.1f} MPa")
    
    def test_thermal_stress_free(self):
        """Should be zero if unconstrained."""
        stress = self.sa.thermal_stress(100.0, constrained=False)
        self.assertEqual(stress, 0.0)
        print("  [PASS] Free expansion: 0")


class TestMaterialsSimulator(unittest.TestCase):
    """Test materials simulator."""
    
    def setUp(self):
        self.sim = MaterialsSimulator()
        self.sim.add_material(ALUMINUM)
        self.sim.add_material(TITANIUM)
    
    def test_add_material(self):
        """Should add material."""
        self.assertEqual(len(self.sim.materials), 2)
        print("  [PASS] Add: 2 materials")
    
    def test_get_material(self):
        """Should get material."""
        mat = self.sim.get_material("Aluminum-6061")
        self.assertIsNotNone(mat)
        self.assertEqual(mat.density, 2700.0)
        print("  [PASS] Get: Aluminum")
    
    def test_thermal_analysis(self):
        """Should run thermal analysis."""
        profile = self.sim.thermal_analysis("Aluminum-6061", 1000.0, 0.1, 0.005)
        self.assertIsNotNone(profile)
        self.assertGreater(profile.max_temp, 0)
        print(f"  [PASS] Thermal sim: {profile.max_temp:.1f}K")
    
    def test_stress_analysis(self):
        """Should run stress analysis."""
        result = self.sim.stress_analysis("Aluminum-6061", "tensile",
                                          force=10000.0, cross_section=0.001)
        self.assertIsNotNone(result)
        self.assertGreater(result.safety_factor, 0)
        print(f"  [PASS] Stress sim: SF={result.safety_factor:.1f}")
    
    def test_check_component(self):
        """Should check requirements."""
        results = self.sim.check_component("Titanium-6Al-4V",
                                           {"yield_strength": 500e6, "density": 4000.0})
        self.assertTrue(results["yield_strength"])
        self.assertTrue(results["density"])
        print("  [PASS] Check: pass")
    
    def test_check_component_fail(self):
        """Should detect failures."""
        results = self.sim.check_component("Aluminum-6061",
                                           {"yield_strength": 500e6})
        self.assertFalse(results["yield_strength"])
        print("  [PASS] Check: fail")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.sim.simulator_summary()
        self.assertEqual(summary["materials"], 2)
        print(f"  [PASS] Summary: {summary['materials']} materials")


if __name__ == '__main__':
    unittest.main(verbosity=2)
