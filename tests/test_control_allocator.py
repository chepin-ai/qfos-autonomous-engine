"""
Unit tests for control allocator module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from control_allocator import (Thruster, ControlDemand, AllocationResult,
                               PseudoInverseAllocator, RedundancyManager,
                               ControlAllocator)


class TestThruster(unittest.TestCase):
    """Test thruster."""
    
    def test_torque(self):
        """Should compute torque."""
        t = Thruster("T1", (1, 0, 0), (0, 0, 1), 10.0)
        tx, ty, tz = t.torque()
        self.assertEqual(tx, 0)
        self.assertEqual(ty, -1)
        self.assertEqual(tz, 0)
        print(f"  [PASS] Torque: ({tx}, {ty}, {tz})")
    
    def test_normalize(self):
        """Should normalize direction."""
        t = Thruster("T1", (0, 0, 0), (2, 0, 0), 10.0)
        t.normalize_direction()
        self.assertEqual(t.direction, (1, 0, 0))
        print("  [PASS] Normalize: (1, 0, 0)")


class TestPseudoInverseAllocator(unittest.TestCase):
    """Test pseudo-inverse allocator."""
    
    def setUp(self):
        self.alloc = PseudoInverseAllocator()
        # Add 4 thrusters for 3DOF
        self.alloc.add_thruster(Thruster("T1", (1, 0, 0), (0, 0, 1), 10.0))
        self.alloc.add_thruster(Thruster("T2", (-1, 0, 0), (0, 0, 1), 10.0))
        self.alloc.add_thruster(Thruster("T3", (0, 1, 0), (0, 0, 1), 10.0))
        self.alloc.add_thruster(Thruster("T4", (0, -1, 0), (0, 0, 1), 10.0))
    
    def test_add_thruster(self):
        """Should add thruster."""
        self.assertEqual(len(self.alloc.thrusters), 4)
        print("  [PASS] Add: 4 thrusters")
    
    def test_allocate_force(self):
        """Should allocate force."""
        demand = ControlDemand(force=(0, 0, 10), torque=(0, 0, 0))
        result = self.alloc.allocate(demand)
        self.assertIn("T1", result.thruster_forces)
        total = sum(result.thruster_forces.values())
        self.assertAlmostEqual(total, 10.0, places=1)
        print(f"  [PASS] Force: total={total:.1f}N")
    
    def test_allocate_torque(self):
        """Should allocate torque."""
        demand = ControlDemand(force=(0, 0, 0), torque=(0, 10, 0))
        result = self.alloc.allocate(demand)
        self.assertIn("T1", result.thruster_forces)
        print(f"  [PASS] Torque: {len(result.thruster_forces)} thrusters")
    
    def test_feasibility(self):
        """Should check feasibility."""
        demand = ControlDemand(force=(0, 0, 5), torque=(0, 0, 0))
        result = self.alloc.allocate(demand)
        self.assertTrue(result.is_feasible)
        print("  [PASS] Feasible: True")
    
    def test_residual(self):
        """Should compute residual."""
        demand = ControlDemand(force=(0, 0, 5), torque=(0, 0, 0))
        result = self.alloc.allocate(demand)
        self.assertLess(abs(result.residual_force[2]), 0.5)
        print(f"  [PASS] Residual: {result.residual_force[2]:.3f}")


class TestRedundancyManager(unittest.TestCase):
    """Test redundancy manager."""
    
    def setUp(self):
        self.rm = RedundancyManager()
        self.rm.add_redundancy_group("group1", ["T1", "T2", "T3"])
    
    def test_add_group(self):
        """Should add group."""
        self.assertIn("group1", self.rm.thruster_groups)
        print("  [PASS] Group: added")
    
    def test_mark_failed(self):
        """Should mark failed."""
        self.rm.mark_failed("T1")
        self.assertIn("T1", self.rm.failed_thrusters)
        print("  [PASS] Failed: T1")
    
    def test_check_health(self):
        """Should check health."""
        self.rm.mark_failed("T1")
        health = self.rm.check_group_health("group1")
        self.assertEqual(health["failed"], 1)
        self.assertEqual(health["healthy"], 2)
        print(f"  [PASS] Health: {health['healthy']}/{health['total']}")
    
    def test_reconfiguration(self):
        """Should recommend reconfiguration."""
        alloc = PseudoInverseAllocator()
        alloc.add_thruster(Thruster("T1", (0, 0, 0), (0, 0, 1), 10.0))
        alloc.add_thruster(Thruster("T2", (0, 0, 0), (0, 0, 1), 10.0))
        self.rm.mark_failed("T1")
        rec = self.rm.get_reconfiguration(alloc)
        self.assertIn("T2", rec)
        self.assertNotIn("T1", rec)
        print(f"  [PASS] Reconfig: {rec}")


class TestControlAllocator(unittest.TestCase):
    """Test unified control allocator."""
    
    def setUp(self):
        self.ca = ControlAllocator()
        self.ca.add_thruster(Thruster("T1", (1, 0, 0), (0, 0, 1), 10.0))
        self.ca.add_thruster(Thruster("T2", (-1, 0, 0), (0, 0, 1), 10.0))
    
    def test_allocate(self):
        """Should allocate control."""
        result = self.ca.allocate((0, 0, 5), (0, 0, 0))
        self.assertIsNotNone(result)
        self.assertTrue(result.is_feasible)
        print("  [PASS] Allocate: ok")
    
    def test_handle_failure(self):
        """Should handle failure."""
        self.ca.handle_failure("T1")
        self.assertFalse(self.ca.allocator.thrusters["T1"].is_functional)
        print("  [PASS] Failure: handled")
    
    def test_summary(self):
        """Should provide summary."""
        summary = self.ca.allocator_summary()
        self.assertEqual(summary["total_thrusters"], 2)
        print(f"  [PASS] Summary: {summary['total_thrusters']} thrusters")


if __name__ == '__main__':
    unittest.main(verbosity=2)
