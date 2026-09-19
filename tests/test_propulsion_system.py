"""
Unit tests for propulsion system module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from propulsion_system import PropulsionSystem, Engine, EngineType


class TestEngine(unittest.TestCase):
    """Test engine."""
    
    def test_exhaust_velocity(self):
        """Should compute exhaust velocity."""
        e = Engine("Test", EngineType.BIPROPELLANT, 100.0, 300.0, 10.0)
        ve = e.exhaust_velocity_ms()
        self.assertAlmostEqual(ve, 300.0 * 9.80665, delta=0.1)
        print(f"  [PASS] Exhaust vel: {ve:.1f} m/s")
    
    def test_mass_flow(self):
        """Should compute mass flow."""
        e = Engine("Test", EngineType.BIPROPELLANT, 490.0, 320.0, 15.0)
        mdot = e.mass_flow_rate_kg_s()
        self.assertGreater(mdot, 0.0)
        print(f"  [PASS] Mass flow: {mdot:.4f} kg/s")
    
    def test_throttle(self):
        """Should throttle."""
        e = Engine("Test", EngineType.ION, 0.25, 3500.0, 8.0,
                   min_throttle_percent=20.0, max_throttle_percent=100.0)
        self.assertEqual(e.thrust_at_throttle(50.0), 0.125)
        self.assertEqual(e.thrust_at_throttle(10.0), 0.05)  # clamped to min
        print("  [PASS] Throttle: 50%=0.125N, 10%->20%=0.05N")


class TestPropulsionSystem(unittest.TestCase):
    """Test propulsion system."""
    
    def test_create_chemical(self):
        """Should create chemical system."""
        sys = PropulsionSystem.create_chemical_system(dry_mass_kg=1000.0, propellant_kg=500.0)
        self.assertEqual(len(sys.engines), 2)
        self.assertEqual(sys.propellant_mass_kg, 500.0)
        print(f"  [PASS] Chemical: {len(sys.engines)} engines, {sys.propellant_mass_kg} kg prop")
    
    def test_create_electric(self):
        """Should create electric system."""
        sys = PropulsionSystem.create_electric_system(dry_mass_kg=500.0, propellant_kg=50.0)
        self.assertEqual(len(sys.engines), 1)
        self.assertEqual(sys.engines[0].engine_type, EngineType.ION)
        print(f"  [PASS] Electric: ISP={sys.engines[0].isp_seconds} s")
    
    def test_create_hybrid(self):
        """Should create hybrid system."""
        sys = PropulsionSystem.create_hybrid_system()
        self.assertEqual(len(sys.engines), 2)
        types = [e.engine_type for e in sys.engines]
        self.assertIn(EngineType.BIPROPELLANT, types)
        self.assertIn(EngineType.ION, types)
        print("  [PASS] Hybrid: biprop + ion")
    
    def test_total_thrust(self):
        """Should compute total thrust."""
        sys = PropulsionSystem.create_chemical_system()
        thrust = sys.total_thrust_n()
        self.assertGreater(thrust, 500.0)
        print(f"  [PASS] Total thrust: {thrust:.1f} N")
    
    def test_burn_duration(self):
        """Should compute burn duration."""
        sys = PropulsionSystem.create_chemical_system()
        duration = sys.burn_duration_s(delta_v_ms=100.0)
        self.assertGreater(duration, 0.0)
        print(f"  [PASS] Burn 100m/s: {duration:.1f} s")
    
    def test_propellant_for_burn(self):
        """Should compute propellant for burn."""
        sys = PropulsionSystem.create_chemical_system()
        prop = sys.propellant_for_burn_kg(delta_v_ms=500.0)
        self.assertGreater(prop, 0.0)
        self.assertLess(prop, sys.propellant_mass_kg)
        print(f"  [PASS] Prop for 500m/s: {prop:.2f} kg")
    
    def test_can_perform_burn(self):
        """Should check burn feasibility."""
        sys = PropulsionSystem.create_chemical_system()
        self.assertTrue(sys.can_perform_burn(100.0))
        self.assertFalse(sys.can_perform_burn(100000.0))
        print("  [PASS] Burn feasibility")
    
    def test_execute_burn(self):
        """Should execute burn."""
        sys = PropulsionSystem.create_chemical_system()
        initial_prop = sys.propellant_mass_kg
        result = sys.execute_burn(delta_v_ms=100.0)
        self.assertTrue(result["success"])
        self.assertLess(sys.propellant_mass_kg, initial_prop)
        print(f"  [PASS] Burn: used {result['propellant_used_kg']:.2f} kg")
    
    def test_execute_burn_fail(self):
        """Should fail with insufficient propellant."""
        sys = PropulsionSystem.create_chemical_system()
        result = sys.execute_burn(delta_v_ms=100000.0)
        self.assertFalse(result["success"])
        print("  [PASS] Burn fail: insufficient prop")
    
    def test_system_summary(self):
        """Should provide summary."""
        sys = PropulsionSystem.create_chemical_system()
        summary = sys.system_summary()
        self.assertIn("num_engines", summary)
        self.assertIn("propellant_fraction", summary)
        print(f"  [PASS] Summary: {summary['num_engines']} engines")


if __name__ == '__main__':
    unittest.main(verbosity=2)
