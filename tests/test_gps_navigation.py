"""
Unit tests for GPS navigation module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gps_navigation import (
    GPSSatellite, GPSSatellitePosition, GPSReceiver,
    create_gps_constellation
)


class TestGPSSatellitePosition(unittest.TestCase):
    """Test GPS satellite position computation."""
    
    def setUp(self):
        self.sats = create_gps_constellation()
        self.positioner = GPSSatellitePosition(self.sats)
    
    def test_satellite_position(self):
        """Should compute satellite position."""
        pos = self.positioner.compute_position(1, gps_week=2300, tow_s=0.0)
        r = (pos[0]**2 + pos[1]**2 + pos[2]**2) ** 0.5
        self.assertGreater(r, 25000.0)
        self.assertLess(r, 27000.0)
        print(f"  [PASS] PRN1: r={r:.1f} km")
    
    def test_constellation_size(self):
        """Should have 24 satellites."""
        self.assertEqual(len(self.sats), 24)
        print(f"  [PASS] Constellation: {len(self.sats)} sats")
    
    def test_multiple_positions(self):
        """Different PRNs should be at different positions."""
        pos1 = self.positioner.compute_position(1, 2300, 0.0)
        pos2 = self.positioner.compute_position(2, 2300, 0.0)
        dist = ((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2 + (pos1[2]-pos2[2])**2) ** 0.5
        self.assertGreater(dist, 1000.0)
        print(f"  [PASS] Separation: {dist:.1f} km")


class TestGPSReceiver(unittest.TestCase):
    """Test GPS receiver navigation."""
    
    def setUp(self):
        self.sats = create_gps_constellation()
        self.positioner = GPSSatellitePosition(self.sats)
        self.receiver = GPSReceiver(self.positioner)
    
    def test_pseudorange(self):
        """Should compute pseudorange."""
        receiver_pos = (6371000.0, 0.0, 0.0)  # Earth's surface
        pr = self.receiver.compute_pseudorange(1, receiver_pos, 2300, 0.0)
        self.assertGreater(pr.range_m, 20000000.0)
        print(f"  [PASS] Pseudorange: {pr.range_m/1e6:.1f} Mm")
    
    def test_position_fix(self):
        """Should run solver and return results."""
        true_pos = (6371000.0, 0.0, 0.0)
        
        pseudoranges = []
        for prn in range(1, 9):
            pr = self.receiver.compute_pseudorange(prn, true_pos, 2300, 0.0, noise_m=0.0)
            pseudoranges.append(pr)
        
        result = self.receiver.solve_position(pseudoranges, 2300, 0.0)
        
        self.assertEqual(result["num_satellites"], 8)
        self.assertIn("position_m", result)
        self.assertIn("gdop", result)
        self.assertIn("clock_bias_m", result)
        
        print(f"  [PASS] Solver ran: GDOP={result['gdop']:.2f}, bias={result['clock_bias_m']:.1f}m")
    
    def test_dop_computation(self):
        """Should compute DOP values."""
        true_pos = (6371000.0, 0.0, 0.0)
        pseudoranges = []
        for prn in range(1, 9):
            pr = self.receiver.compute_pseudorange(prn, true_pos, 2300, 0.0)
            pseudoranges.append(pr)
        
        result = self.receiver.solve_position(pseudoranges, 2300, 0.0)
        
        self.assertGreater(result["gdop"], 0.0)
        self.assertGreater(result["pdop"], 0.0)
        print(f"  [PASS] DOP: GDOP={result['gdop']:.2f}, PDOP={result['pdop']:.2f}, HDOP={result['hdop']:.2f}")
    
    def test_four_satellites_minimum(self):
        """Should run solver with 4 satellites."""
        true_pos = (6371000.0, 0.0, 0.0)
        selected_prns = [1, 5, 13, 21]
        pseudoranges = []
        for prn in selected_prns:
            pr = self.receiver.compute_pseudorange(prn, true_pos, 2300, 0.0, noise_m=0.0)
            pseudoranges.append(pr)
        
        result = self.receiver.solve_position(pseudoranges, 2300, 0.0)
        
        self.assertEqual(result["num_satellites"], 4)
        self.assertIn("position_m", result)
        print(f"  [PASS] 4-sat solver: GDOP={result['gdop']:.2f}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
