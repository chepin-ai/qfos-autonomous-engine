"""
Unit tests for redundancy manager module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redundancy_manager import (ComponentState, Component, RedundancyGroup,
                                HealthMonitor, SwitchoverController,
                                RedundancyManager)


class TestComponent(unittest.TestCase):
    """Test component."""
    
    def test_healthy(self):
        """Should be healthy."""
        c = Component("c1", "sensor", ComponentState.ACTIVE, 0.9)
        self.assertTrue(c.is_healthy())
        print("  [PASS] Healthy: True")
    
    def test_unhealthy(self):
        """Should not be healthy when failed."""
        c = Component("c1", "sensor", ComponentState.FAILED, 0.0)
        self.assertFalse(c.is_healthy())
        print("  [PASS] Unhealthy: False")
    
    def test_activate(self):
        """Should activate."""
        c = Component("c1", "sensor", ComponentState.STANDBY)
        c.activate()
        self.assertEqual(c.state, ComponentState.ACTIVE)
        self.assertEqual(c.activation_count, 1)
        print("  [PASS] Activate: active")


class TestRedundancyGroup(unittest.TestCase):
    """Test redundancy group."""
    
    def setUp(self):
        self.g = RedundancyGroup("g1", "comms")
        self.g.add_component(Component("primary", "comms", ComponentState.ACTIVE))
        self.g.add_component(Component("backup", "comms", ComponentState.STANDBY))
    
    def test_add(self):
        """Should add components."""
        self.assertEqual(len(self.g.components), 2)
        print("  [PASS] Add: 2 components")
    
    def test_get_active(self):
        """Should get active."""
        active = self.g.get_active()
        self.assertIsNotNone(active)
        self.assertEqual(active.component_id, "primary")
        print(f"  [PASS] Active: {active.component_id}")
    
    def test_get_standby(self):
        """Should get standby."""
        standby = self.g.get_standby()
        self.assertEqual(len(standby), 1)
        print(f"  [PASS] Standby: {len(standby)}")
    
    def test_failover(self):
        """Should failover."""
        new_id = self.g.failover()
        self.assertIsNotNone(new_id)
        self.assertEqual(new_id, "backup")
        print(f"  [PASS] Failover: {new_id}")
    
    def test_redundancy_level(self):
        """Should compute redundancy."""
        level = self.g.redundancy_level()
        self.assertEqual(level, 2)
        print(f"  [PASS] Level: {level}")


class TestHealthMonitor(unittest.TestCase):
    """Test health monitor."""
    
    def setUp(self):
        self.hm = HealthMonitor(heartbeat_timeout=5.0)
    
    def test_register(self):
        """Should register check."""
        self.hm.register_check("c1", lambda: 0.8)
        self.assertIn("c1", self.hm.health_checks)
        print("  [PASS] Register: c1")
    
    def test_check_health(self):
        """Should check health."""
        self.hm.register_check("c1", lambda: 0.8)
        c = Component("c1", "sensor", health_score=1.0)
        score = self.hm.check_health(c)
        self.assertGreater(score, 0)
        print(f"  [PASS] Health: {score:.2f}")
    
    def test_heartbeat(self):
        """Should update heartbeat."""
        self.hm.update_heartbeat("c1")
        self.assertIn("c1", self.hm.heartbeats)
        print("  [PASS] Heartbeat: updated")


class TestSwitchoverController(unittest.TestCase):
    """Test switchover controller."""
    
    def setUp(self):
        self.sc = SwitchoverController()
        self.sc.create_group("g1", "comms")
        self.sc.add_to_group("g1", Component("p", "comms", ComponentState.ACTIVE))
        self.sc.add_to_group("g1", Component("b", "comms", ComponentState.STANDBY))
    
    def test_create_group(self):
        """Should create group."""
        self.assertIn("g1", self.sc.groups)
        print("  [PASS] Create: g1")
    
    def test_switchover(self):
        """Should switchover."""
        new_id = self.sc.perform_switchover("g1")
        self.assertIsNotNone(new_id)
        print(f"  [PASS] Switchover: {new_id}")
    
    def test_auto_failover(self):
        """Should auto-failover."""
        # Make primary unhealthy
        self.sc.groups["g1"].components["p"].health_score = 0.1
        self.sc.groups["g1"].components["p"].state = ComponentState.DEGRADED
        new_id = self.sc.auto_failover("g1")
        self.assertIsNotNone(new_id)
        print(f"  [PASS] Auto: {new_id}")
    
    def test_status(self):
        """Should get status."""
        status = self.sc.get_group_status("g1")
        self.assertEqual(status["active"], "p")
        print(f"  [PASS] Status: active={status['active']}")


class TestRedundancyManager(unittest.TestCase):
    """Test unified redundancy manager."""
    
    def setUp(self):
        self.rm = RedundancyManager()
    
    def test_create_pair(self):
        """Should create pair."""
        self.rm.create_redundant_pair("g1", "comms", "p", "b")
        self.assertIn("g1", self.rm.groups)
        print("  [PASS] Pair: g1")
    
    def test_create_n_plus_m(self):
        """Should create N+M group."""
        self.rm.create_n_plus_m("g2", "sensor", ["a1"], ["s1", "s2"])
        self.assertEqual(len(self.rm.groups["g2"].components), 3)
        print(f"  [PASS] N+M: {len(self.rm.groups['g2'].components)} components")
    
    def test_failover(self):
        """Should failover."""
        self.rm.create_redundant_pair("g1", "comms", "p", "b")
        new_id = self.rm.failover("g1")
        self.assertIsNotNone(new_id)
        print(f"  [PASS] Failover: {new_id}")
    
    def test_summary(self):
        """Should provide summary."""
        self.rm.create_redundant_pair("g1", "comms", "p", "b")
        summary = self.rm.rm_summary()
        self.assertEqual(summary["groups"], 1)
        self.assertEqual(summary["total_components"], 2)
        print(f"  [PASS] Summary: {summary['groups']} groups")


if __name__ == '__main__':
    unittest.main(verbosity=2)
