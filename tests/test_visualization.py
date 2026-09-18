"""
Unit tests for visualization module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orbital_mechanics import OrbitalBody
from visualization import (
    generate_orbit_path,
    generate_multi_orbit_data,
    orbital_elements_summary,
    create_ascii_orbit_plot
)


class TestVisualization(unittest.TestCase):
    """Test visualization functions."""
    
    def setUp(self):
        self.earth = OrbitalBody(name="Earth", spkid="399", a_au=1.0, e=0.0167, i_deg=0.0)
        self.apophis = OrbitalBody(name="Apophis", spkid="99942", a_au=0.922, e=0.191, i_deg=3.33)
    
    def test_generate_orbit_path(self):
        """Should generate path with correct number of points."""
        xs, ys, zs = generate_orbit_path(self.earth, num_points=100)
        self.assertEqual(len(xs), 100)
        self.assertEqual(len(ys), 100)
        self.assertEqual(len(zs), 100)
        print(f"  [PASS] Orbit path: {len(xs)} points generated")
    
    def test_multi_orbit_data(self):
        """Should generate data for multiple bodies."""
        data = generate_multi_orbit_data([self.earth, self.apophis], num_points=50)
        self.assertIn("Earth", data)
        self.assertIn("Apophis", data)
        self.assertEqual(len(data["Earth"][0]), 50)
        print(f"  [PASS] Multi-orbit: {len(data)} bodies, 50 points each")
    
    def test_orbital_summary(self):
        """Summary should contain all key elements."""
        summary = orbital_elements_summary(self.apophis)
        required_keys = ["semi_major_axis_au", "eccentricity", "inclination_deg",
                        "period_years", "perihelion_au", "aphelion_au"]
        for key in required_keys:
            self.assertIn(key, summary)
        print(f"  [PASS] Summary keys: {list(summary.keys())}")
    
    def test_ascii_plot(self):
        """ASCII plot should generate non-empty string."""
        plot = create_ascii_orbit_plot(self.earth, width=40, height=15)
        self.assertGreater(len(plot), 100)
        self.assertIn("Earth", plot)
        self.assertIn('*', plot)
        print(f"  [PASS] ASCII plot: {len(plot)} chars")


if __name__ == '__main__':
    unittest.main(verbosity=2)
