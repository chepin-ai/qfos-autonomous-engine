"""
Unit tests for ISRU plant module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from isru_plant import WaterElectrolyzer, SabatierReactor, ISRUPlant


class TestWaterElectrolyzer(unittest.TestCase):
    """Test water electrolyzer."""
    
    def setUp(self):
        self.elec = WaterElectrolyzer(efficiency=0.7, max_power_kw=10.0)
    
    def test_process(self):
        """Should electrolyze water."""
        result = self.elec.process(1.0)
        self.assertGreater(result["o2_produced_kg"], 0.0)
        self.assertGreater(result["h2_produced_kg"], 0.0)
        print(f"  [PASS] Electrolysis: O2={result['o2_produced_kg']:.3f}kg, H2={result['h2_produced_kg']:.3f}kg")
    
    def test_mass_balance(self):
        """Should conserve mass."""
        result = self.elec.process(2.0)
        total_out = result["o2_produced_kg"] + result["h2_produced_kg"]
        # 2 H2O -> 2 H2 + O2, mass conserved
        self.assertAlmostEqual(total_out, 2.0, delta=0.1)
        print(f"  [PASS] Mass balance: in=2.0kg, out={total_out:.3f}kg")
    
    def test_o2_rate(self):
        """Should compute O2 rate."""
        rate = self.elec.o2_production_rate(0.001)
        self.assertGreater(rate, 0.0)
        print(f"  [PASS] O2 rate: {rate:.6f} kg/s")


class TestSabatierReactor(unittest.TestCase):
    """Test Sabatier reactor."""
    
    def setUp(self):
        self.sab = SabatierReactor(efficiency=0.8)
    
    def test_process(self):
        """Should produce CH4."""
        result = self.sab.process(co2_mass_kg=10.0, h2_mass_kg=5.0)
        self.assertGreater(result["ch4_produced_kg"], 0.0)
        print(f"  [PASS] Sabatier: CH4={result['ch4_produced_kg']:.3f}kg")
    
    def test_limiting_reagent(self):
        """Should identify limiting reagent."""
        result = self.sab.process(co2_mass_kg=1.0, h2_mass_kg=10.0)
        self.assertEqual(result["limiting_reagent"], "CO2")
        print(f"  [PASS] Limiting: {result['limiting_reagent']}")


class TestISRUPlant(unittest.TestCase):
    """Test integrated ISRU plant."""
    
    def setUp(self):
        self.plant = ISRUPlant(solar_power_kw=50.0, battery_capacity_kwh=100.0)
    
    def test_daily_production(self):
        """Should produce daily."""
        result = self.plant.daily_production(
            available_water_kg=50.0, available_co2_kg=100.0, daylight_hours=12.0
        )
        self.assertGreater(result["o2_produced_kg"], 0.0)
        self.assertGreater(result["ch4_produced_kg"], 0.0)
        print(f"  [PASS] Daily: O2={result['o2_produced_kg']:.2f}kg, CH4={result['ch4_produced_kg']:.2f}kg")
    
    def test_life_support(self):
        """Should assess life support."""
        self.plant.daily_production(available_water_kg=100.0, available_co2_kg=200.0)
        ls = self.plant.life_support_o2(crew_size=4)
        self.assertIn("daily_o2_need_kg", ls)
        print(f"  [PASS] Life support: need={ls['daily_o2_need_kg']:.2f}kg, prod={ls['daily_o2_production_kg']:.2f}kg")
    
    def test_propellant_summary(self):
        """Should summarize propellant."""
        self.plant.daily_production(available_water_kg=200.0, available_co2_kg=400.0)
        prop = self.plant.propellant_summary()
        self.assertIn("total_ch4_kg", prop)
        print(f"  [PASS] Propellant: CH4={prop['total_ch4_kg']:.2f}kg, O2={prop['total_o2_kg']:.2f}kg")
    
    def test_plant_status(self):
        """Should report status."""
        status = self.plant.plant_status()
        self.assertIn("battery_soc", status)
        print(f"  [PASS] Status: battery={status['battery_soc']:.1%}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
