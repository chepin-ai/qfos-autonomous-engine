"""
Unit tests for mission scheduler module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mission_scheduler import (
    MissionScheduler, MissionActivity, ActivityPriority, ActivityStatus
)


class TestMissionScheduler(unittest.TestCase):
    """Test mission scheduling."""
    
    def setUp(self):
        self.scheduler = MissionScheduler(available_power_w=200.0)
    
    def test_simple_schedule(self):
        """Should schedule activities in priority order."""
        self.scheduler.add_activity(MissionActivity(
            activity_id="A1", name=" Imaging", priority=ActivityPriority.HIGH,
            duration_seconds=3600, power_requirement_w=50.0
        ))
        self.scheduler.add_activity(MissionActivity(
            activity_id="A2", name=" Communication", priority=ActivityPriority.MEDIUM,
            duration_seconds=1800, power_requirement_w=100.0
        ))
        
        result = self.scheduler.schedule_activities(start_time=0.0, end_time=86400.0)
        self.assertEqual(result["scheduled"], 2)
        self.assertEqual(result["failed"], 0)
        print(f"  [PASS] Simple schedule: {result['scheduled']} scheduled, {result['failed']} failed")
    
    def test_prerequisite_ordering(self):
        """Should respect activity prerequisites."""
        self.scheduler.add_activity(MissionActivity(
            activity_id="A1", name=" Point", priority=ActivityPriority.HIGH,
            duration_seconds=300, power_requirement_w=20.0
        ))
        self.scheduler.add_activity(MissionActivity(
            activity_id="A2", name=" Image", priority=ActivityPriority.HIGH,
            duration_seconds=600, power_requirement_w=50.0,
            prerequisites=["A1"]
        ))
        
        # A2 should not be scheduled if A1 is not completed
        result = self.scheduler.schedule_activities()
        # A1 is pending, not completed, so A2 should not schedule
        a2 = self.scheduler.activities["A2"]
        self.assertNotEqual(a2.status, ActivityStatus.SCHEDULED)
        print(f"  [PASS] Prerequisite respected: A2 status={a2.status.value}")
    
    def test_power_constraint(self):
        """Should not exceed available power."""
        self.scheduler.add_activity(MissionActivity(
            activity_id="A1", name=" High Power", priority=ActivityPriority.HIGH,
            duration_seconds=3600, power_requirement_w=300.0  # Exceeds 200W
        ))
        
        result = self.scheduler.schedule_activities()
        self.assertEqual(result["scheduled"], 0)  # Cannot schedule due to power
        print(f"  [PASS] Power constraint: {result['scheduled']} scheduled (exceeds limit)")
    
    def test_time_window(self):
        """Should respect time windows."""
        self.scheduler.add_activity(MissionActivity(
            activity_id="A1", name=" Windowed", priority=ActivityPriority.HIGH,
            duration_seconds=7200, power_requirement_w=30.0,
            earliest_start=0.0, latest_start=1800.0
        ))
        
        # If we start scheduling after the window
        result = self.scheduler.schedule_activities(start_time=2000.0, end_time=86400.0)
        self.assertEqual(result["failed"], 1)
        print(f"  [PASS] Time window: {result['failed']} failed due to window violation")
    
    def test_schedule_execution(self):
        """Should execute scheduled activities."""
        self.scheduler.add_activity(MissionActivity(
            activity_id="A1", name=" Task", priority=ActivityPriority.HIGH,
            duration_seconds=3600, power_requirement_w=30.0
        ))
        self.scheduler.schedule_activities()
        
        # Execute at time 0
        activity = self.scheduler.execute_next(current_time=0.0)
        self.assertIsNotNone(activity)
        self.assertEqual(activity.status, ActivityStatus.EXECUTING)
        
        # Complete
        self.scheduler.complete_activity("A1", success=True)
        self.assertEqual(self.scheduler.activities["A1"].status, ActivityStatus.COMPLETED)
        print("  [PASS] Execute and complete activity")
    
    def test_schedule_summary(self):
        """Should provide schedule summary."""
        for i in range(3):
            self.scheduler.add_activity(MissionActivity(
                activity_id=f"A{i}", name=f"Task {i}",
                priority=ActivityPriority.MEDIUM,
                duration_seconds=600, power_requirement_w=10.0
            ))
        
        self.scheduler.schedule_activities()
        summary = self.scheduler.get_schedule_summary()
        self.assertIn("total_activities", summary)
        self.assertIn("timeline", summary)
        self.assertIn("by_status", summary)
        print(f"  [PASS] Summary: {summary['total_activities']} activities, {summary['by_status']}")
    
    def test_solar_power_optimization(self):
        """Should optimize for solar power peaks."""
        self.scheduler.add_activity(MissionActivity(
            activity_id="A1", name=" Power Hungry", priority=ActivityPriority.HIGH,
            duration_seconds=1800, power_requirement_w=150.0
        ))
        
        # Solar profile: peak at noon (43200s)
        solar_profile = [(0, 0), (21600, 50), (43200, 200), (64800, 50), (86400, 0)]
        result = self.scheduler.optimize_for_power(solar_profile, battery_capacity_wh=1000.0)
        
        self.assertIn("reassigned_to_peak_solar", result)
        print(f"  [PASS] Solar optimization: {result['reassigned_to_peak_solar']} activities reassigned")


if __name__ == '__main__':
    unittest.main(verbosity=2)
