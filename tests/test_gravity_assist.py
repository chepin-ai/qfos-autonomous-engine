"""
Unit tests for gravity assist module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gravity_assist import (
    gravity_assist_turn_angle, 
    gravity_assist_delta_v,
    PLANET_MASSES,
    PLANET_RADII
)


class TestGravityAssist(unittest.TestCase):
    """Test gravity assist calculations."""
    
    def test_earth_gravity_assist(self):
        """Test Earth gravity assist with typical v_inf."""
        v_inf = 5000  # m/s
        delta, max_dv = gravity_assist_delta_v(v_inf, "Earth", 500.0)
        
        self.assertGreater(delta, 0)
        self.assertLess(delta, 180)
        self.assertGreater(max_dv, 0)
        print(f"  [PASS] Earth GA: turn={delta:.2f} deg, max_dv={max_dv:.1f} m/s")
    
    def test_jupiter_gravity_assist(self):
        """Jupiter should provide much larger turn angle than Earth."""
        v_inf = 5000
        
        delta_jup, dv_jup = gravity_assist_delta_v(v_inf, "Jupiter", 500.0)
        delta_earth, dv_earth = gravity_assist_delta_v(v_inf, "Earth", 500.0)
        
        self.assertGreater(delta_jup, delta_earth)
        self.assertGreater(dv_jup, dv_earth)
        print(f"  [PASS] Jupiter GA: turn={delta_jup:.2f} deg, max_dv={dv_jup:.1f} m/s")
        print(f"  [PASS] Earth GA:   turn={delta_earth:.2f} deg, max_dv={dv_earth:.1f} m/s")
    
    def test_turn_angle_formula(self):
        """Verify turn angle formula produces valid results."""
        # Very large flyby -> small turn
        delta_far = gravity_assist_turn_angle(5000, 5.972e24, 1e9)
        # Close flyby -> larger turn
        delta_close = gravity_assist_turn_angle(5000, 5.972e24, 7e6)
        
        self.assertGreater(delta_close, delta_far)
        self.assertGreater(delta_far, 0)
        print(f"  [PASS] Turn angle close={math.degrees(delta_close):.2f} deg, far={math.degrees(delta_far):.2f} deg")
    
    def test_unknown_planet(self):
        """Should raise error for unknown planet."""
        with self.assertRaises(ValueError):
            gravity_assist_delta_v(5000, "Pluto", 500.0)
        print("  [PASS] Unknown planet correctly rejected")
    
    def test_planet_data_loaded(self):
        """Verify planet data is available."""
        self.assertIn("Earth", PLANET_MASSES)
        self.assertIn("Jupiter", PLANET_MASSES)
        self.assertIn("Earth", PLANET_RADII)
        print(f"  [PASS] Planet data: {len(PLANET_MASSES)} planets loaded")


if __name__ == '__main__':
    unittest.main(verbosity=2)
