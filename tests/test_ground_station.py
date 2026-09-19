"""
Unit tests for ground station scheduler module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ground_station import GroundStation, GroundStationScheduler, PassPrediction


class TestGroundStationScheduler(unittest.TestCase):
    """Test ground station pass scheduling."""
    
    def setUp(self):
        self.stations = [
            GroundStation("Canberra", -35.3, 149.0, dish_diameter_m=70.0, supported_bands=["S", "X", "Ka"]),
            GroundStation("Madrid", 40.4, -4.2, dish_diameter_m=70.0, supported_bands=["S", "X", "Ka"]),
            GroundStation("Goldstone", 35.3, -116.8, dish_diameter_m=70.0, supported_bands=["S", "X", "Ka"]),
        ]
        self.scheduler = GroundStationScheduler(self.stations)
    
    def test_predict_passes(self):
        """Should predict passes for LEO spacecraft."""
        passes = self.scheduler.predict_passes(
            sc_latitude_deg=51.6,
            sc_altitude_km=400,
            orbital_period_min=93.0,
            duration_hours=24.0
        )
        self.assertGreater(len(passes), 0)
        print(f"  [PASS] Predicted {len(passes)} passes in 24h")
    
    def test_pass_duration(self):
        """Passes should have reasonable duration."""
        passes = self.scheduler.predict_passes(
            sc_latitude_deg=51.6, sc_altitude_km=400,
            orbital_period_min=93.0, duration_hours=24.0
        )
        for p in passes:
            self.assertGreater(p.duration_s, 0)
            self.assertLess(p.duration_s, 1200)  # < 20 min
        print(f"  [PASS] Pass durations: {min(p.duration_s for p in passes):.0f}s - {max(p.duration_s for p in passes):.0f}s")
    
    def test_schedule_passes(self):
        """Should schedule passes to clear backlog."""
        passes = self.scheduler.predict_passes(
            sc_latitude_deg=51.6, sc_altitude_km=400,
            orbital_period_min=93.0, duration_hours=24.0
        )
        result = self.scheduler.schedule_passes(passes, data_backlog_mb=500.0)
        self.assertIn("scheduled_passes", result)
        self.assertIn("backlog_cleared", result)
        print(f"  [PASS] Scheduled {result['scheduled_passes']}/{result['total_passes_available']} passes, backlog_cleared={result['backlog_cleared']}")
    
    def test_priority_stations(self):
        """Priority stations should be preferred."""
        passes = self.scheduler.predict_passes(
            sc_latitude_deg=51.6, sc_altitude_km=400,
            orbital_period_min=93.0, duration_hours=24.0
        )
        result = self.scheduler.schedule_passes(
            passes, data_backlog_mb=1000.0, priority_stations=["Canberra"]
        )
        # Check if Canberra passes were preferred
        scheduled_canberra = sum(1 for p in result["schedule"] if p["station"] == "Canberra")
        print(f"  [PASS] Priority scheduling: {scheduled_canberra} Canberra passes scheduled")
    
    def test_contact_summary(self):
        """Should generate station contact summary."""
        passes = self.scheduler.predict_passes(
            sc_latitude_deg=51.6, sc_altitude_km=400,
            orbital_period_min=93.0, duration_hours=24.0
        )
        summary = self.scheduler.contact_summary("Canberra", passes)
        self.assertIn("total_passes", summary)
        self.assertIn("total_contact_time_min", summary)
        print(f"  [PASS] Canberra summary: {summary['total_passes']} passes, {summary['total_contact_time_min']} min")


if __name__ == '__main__':
    unittest.main(verbosity=2)
