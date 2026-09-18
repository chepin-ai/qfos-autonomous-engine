"""
Unit tests for path planner module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orbital_mechanics import OrbitalBody
from path_planner import OrbitalPathPlanner


class TestPathPlanner(unittest.TestCase):
    """Test orbital path planning."""
    
    def setUp(self):
        self.bodies = [
            OrbitalBody(name="Earth", spkid="399", a_au=1.0, e=0.0167, i_deg=0.0),
            OrbitalBody(name="Mars", spkid="499", a_au=1.524, e=0.0934, i_deg=1.85),
            OrbitalBody(name="Venus", spkid="299", a_au=0.723, e=0.0067, i_deg=3.39),
            OrbitalBody(name="Jupiter", spkid="599", a_au=5.204, e=0.0489, i_deg=1.30),
        ]
        self.planner = OrbitalPathPlanner(self.bodies)
    
    def test_direct_transfer(self):
        """Should find direct Earth->Mars transfer."""
        plan = self.planner.plan_transfer("Earth", "Mars", max_legs=1)
        self.assertIsNotNone(plan)
        self.assertEqual(plan["path"], ["Earth", "Mars"])
        self.assertEqual(plan["legs"], 1)
        self.assertGreater(plan["total_delta_v_ms"], 0)
        print(f"  [PASS] Direct Earth->Mars: dv={plan['total_delta_v_ms']:.1f} m/s")
    
    def test_multi_leg_options(self):
        """Should find multiple transfer options."""
        options = self.planner.compare_transfer_options("Earth", "Jupiter")
        self.assertGreater(len(options), 0)
        for opt in options:
            self.assertIn("Earth", opt["path"])
            self.assertIn("Jupiter", opt["path"])
        print(f"  [PASS] Found {len(options)} transfer options to Jupiter")
    
    def test_invalid_target(self):
        """Should return None for unknown body."""
        plan = self.planner.plan_transfer("Earth", "Pluto")
        self.assertIsNone(plan)
        print("  [PASS] Unknown target correctly rejected")
    
    def test_path_comparison(self):
        """Multi-leg should be compared with direct."""
        options = self.planner.compare_transfer_options("Venus", "Mars")
        self.assertGreaterEqual(len(options), 1)
        # Direct should be first or among options
        direct = [o for o in options if o["type"] == "direct"]
        self.assertEqual(len(direct), 1)
        print(f"  [PASS] {len(options)} options Venus->Mars, direct dv={direct[0]['total_delta_v_ms']:.1f} m/s")


if __name__ == '__main__':
    unittest.main(verbosity=2)
