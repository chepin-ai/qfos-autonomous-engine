"""
Unit tests for link budget module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from link_budget import LinkBudgetCalculator, LinkBudgetResult


class TestLinkBudget(unittest.TestCase):
    """Test link budget calculations."""
    
    def setUp(self):
        self.calc = LinkBudgetCalculator(system_noise_temp_k=290.0)
    
    def test_earth_mars_link(self):
        """Earth-Mars link at opposition should be viable."""
        result = self.calc.calculate_link(
            tx_power_w=100.0,
            tx_dish_diameter_m=3.0,
            rx_dish_diameter_m=70.0,
            distance_km=55e6,  # ~55 million km (opposition)
            frequency_ghz=8.4,
            data_rate_bps=1e6
        )
        self.assertIsInstance(result, LinkBudgetResult)
        self.assertGreater(result.snr_db, 0)
        print(f"  [PASS] Earth-Mars X-band: SNR={result.snr_db:.1f} dB, margin={result.margin_db:.1f} dB, status={result.status}")
    
    def test_far_distance_fail(self):
        """Very far distance should result in link failure."""
        result = self.calc.calculate_link(
            tx_power_w=1.0,
            tx_dish_diameter_m=0.5,
            rx_dish_diameter_m=10.0,
            distance_km=1e9,  # 1 billion km
            frequency_ghz=2.29,
            data_rate_bps=1e6
        )
        self.assertEqual(result.status, 'FAIL')
        print(f"  [PASS] Far link correctly FAIL: margin={result.margin_db:.1f} dB")
    
    def test_path_loss_increases_with_distance(self):
        """Path loss should increase with distance."""
        result_near = self.calc.calculate_link(
            tx_power_w=10.0, tx_dish_diameter_m=1.0, rx_dish_diameter_m=10.0,
            distance_km=1e6, frequency_ghz=8.4, data_rate_bps=1e3
        )
        result_far = self.calc.calculate_link(
            tx_power_w=10.0, tx_dish_diameter_m=1.0, rx_dish_diameter_m=10.0,
            distance_km=10e6, frequency_ghz=8.4, data_rate_bps=1e3
        )
        self.assertGreater(result_far.path_loss_db, result_near.path_loss_db)
        print(f"  [PASS] Path loss: near={result_near.path_loss_db:.1f} dB, far={result_far.path_loss_db:.1f} dB")
    
    def test_mission_phases(self):
        """Different mission phases should have different configs."""
        for phase in ['launch', 'cruise', 'approach', 'emergency']:
            result = self.calc.calculate_for_mission_phase(
                phase=phase, distance_km=100e6, data_rate_bps=1e4, tx_power_w=20.0
            )
            self.assertIn(result.status, ['OK', 'MARGINAL', 'FAIL'])
        print(f"  [PASS] All 4 mission phases calculated")
    
    def test_max_data_rate(self):
        """Max data rate should be positive."""
        rate = self.calc.max_data_rate(
            tx_power_w=100.0, tx_dish_diameter_m=3.0, rx_dish_diameter_m=70.0,
            distance_km=55e6, frequency_ghz=8.4, min_margin_db=3.0
        )
        self.assertGreater(rate, 0)
        print(f"  [PASS] Max data rate at Mars opposition: {rate:.1e} bps")
    
    def test_dish_gain(self):
        """Larger dish should have higher gain."""
        result_small = self.calc.calculate_link(
            tx_power_w=10.0, tx_dish_diameter_m=1.0, rx_dish_diameter_m=10.0,
            distance_km=1e6, frequency_ghz=8.4, data_rate_bps=1e3
        )
        result_large = self.calc.calculate_link(
            tx_power_w=10.0, tx_dish_diameter_m=3.0, rx_dish_diameter_m=10.0,
            distance_km=1e6, frequency_ghz=8.4, data_rate_bps=1e3
        )
        self.assertGreater(result_large.received_power_dbm, result_small.received_power_dbm)
        print(f"  [PASS] Larger dish: 1m={result_small.received_power_dbm:.1f} dBm, 3m={result_large.received_power_dbm:.1f} dBm")


if __name__ == '__main__':
    unittest.main(verbosity=2)
