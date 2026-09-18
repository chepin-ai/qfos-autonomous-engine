"""
Unit tests for thermal control module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from thermal_control import ThermalControlSystem, ThermalZone, SIGMA


class TestThermalControl(unittest.TestCase):
    """Test thermal control calculations."""
    
    def setUp(self):
        self.tcs = ThermalControlSystem(solar_distance_au=1.0)
    
    def test_equilibrium_temperature_earth_orbit(self):
        """Earth orbit zone should be around room temperature."""
        zone = ThermalZone(
            name="bus", area_m2=1.0,
            absorptivity=0.3, emissivity=0.85,
            internal_heat_w=50.0
        )
        T_eq = self.tcs.equilibrium_temperature(zone, sun_facing=True)
        self.assertGreater(T_eq, 250)  # Above -23 C
        self.assertLess(T_eq, 400)     # Below 127 C
        print(f"  [PASS] Earth orbit bus: T_eq={T_eq-273.15:.1f} C ({T_eq:.1f} K)")
    
    def test_thermal_balance_multiple_zones(self):
        """Should calculate balance for multiple zones."""
        zones = [
            ThermalZone("electronics", 0.5, 0.2, 0.85, internal_heat_w=100.0, min_temp_k=253, max_temp_k=323),
            ThermalZone("radiator", 2.0, 0.1, 0.9, internal_heat_w=0.0, min_temp_k=223, max_temp_k=373),
        ]
        results = self.tcs.thermal_balance(zones)
        
        self.assertIn("electronics", results)
        self.assertIn("radiator", results)
        self.assertIn("_summary", results)
        print(f"  [PASS] Multi-zone: electronics={results['electronics']['equilibrium_temp_c']:.1f}C, status={results['electronics']['status']}")
    
    def test_cooling_required(self):
        """High internal heat should trigger cooling requirement."""
        zone = ThermalZone(
            name="hot", area_m2=0.1,
            absorptivity=0.9, emissivity=0.1,
            internal_heat_w=1000.0, max_temp_k=300
        )
        T_eq = self.tcs.equilibrium_temperature(zone)
        self.assertGreater(T_eq, 300)
        
        results = self.tcs.thermal_balance([zone])
        self.assertEqual(results["hot"]["status"], "COOLING_REQUIRED")
        print(f"  [PASS] Cooling required: T_eq={T_eq:.1f}K, cooler={results['hot']['cooler_power_w']:.1f}W")
    
    def test_heating_required(self):
        """Cold environment should trigger heating requirement."""
        tcs_cold = ThermalControlSystem(solar_distance_au=5.2)  # Jupiter distance
        zone = ThermalZone(
            name="cold", area_m2=1.0,
            absorptivity=0.1, emissivity=0.9,
            internal_heat_w=0.0, min_temp_k=273
        )
        results = tcs_cold.thermal_balance([zone])
        self.assertEqual(results["cold"]["status"], "HEATING_REQUIRED")
        print(f"  [PASS] Heating required at Jupiter: T_eq={results['cold']['equilibrium_temp_c']:.1f}C")
    
    def test_radiator_size(self):
        """Radiator size should scale with heat load."""
        area1 = self.tcs.radiator_size_required(100.0)
        area2 = self.tcs.radiator_size_required(200.0)
        self.assertGreater(area2, area1)
        print(f"  [PASS] Radiator: 100W={area1:.3f}m2, 200W={area2:.3f}m2")
    
    def test_mli_performance(self):
        """More MLI layers should reduce heat leak."""
        leak1 = self.tcs.multilayer_insulation_performance(1, 300, 100)
        leak5 = self.tcs.multilayer_insulation_performance(5, 300, 100)
        self.assertLess(leak5, leak1)
        print(f"  [PASS] MLI: 1-layer={leak1:.3f}W/m2, 5-layer={leak5:.3f}W/m2")
    
    def test_solar_array_temperature(self):
        """Solar array should be warmer than ambient due to absorbed solar."""
        T_array = self.tcs.solar_array_temperature()
        self.assertGreater(T_array, 250)
        self.assertLess(T_array, 400)
        print(f"  [PASS] Solar array temp: {T_array-273.15:.1f} C")


if __name__ == '__main__':
    unittest.main(verbosity=2)
