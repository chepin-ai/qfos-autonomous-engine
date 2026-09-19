"""
Unit tests for data relay module.
"""

import unittest
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_relay import BundleRouter, Bundle, Priority, BundleStatus, Contact


class TestBundleRouter(unittest.TestCase):
    """Test bundle router."""
    
    def setUp(self):
        self.router = BundleRouter()
    
    def test_create_bundle(self):
        """Should create bundle."""
        bundle = self.router.create_bundle("A", "B", 1024, Priority.STANDARD)
        self.assertEqual(bundle.source, "A")
        self.assertEqual(bundle.destination, "B")
        self.assertEqual(bundle.status, BundleStatus.PENDING)
        print(f"  [PASS] Bundle: {bundle.bundle_id}, {bundle.payload_bytes} bytes")
    
    def test_queue_order(self):
        """Should order by priority."""
        self.router.create_bundle("A", "B", 100, Priority.BULK)
        self.router.create_bundle("A", "B", 100, Priority.CRITICAL)
        self.router.create_bundle("A", "B", 100, Priority.STANDARD)
        
        queue = self.router.get_queue("A")
        self.assertEqual(queue[0].priority, Priority.CRITICAL)
        self.assertEqual(queue[1].priority, Priority.STANDARD)
        self.assertEqual(queue[2].priority, Priority.BULK)
        print("  [PASS] Queue: CRITICAL > STANDARD > BULK")
    
    def test_forward_bundle(self):
        """Should forward bundle."""
        bundle = self.router.create_bundle("A", "C", 512)
        result = self.router.forward_bundle(bundle.bundle_id, "A", "B", ["A", "B", "C"])
        self.assertTrue(result)
        self.assertEqual(self.router.bundles[bundle.bundle_id].current_hop, 1)
        print("  [PASS] Forwarded: hop=1")
    
    def test_deliver_bundle(self):
        """Should deliver bundle."""
        bundle = self.router.create_bundle("A", "B", 256)
        result = self.router.deliver_bundle(bundle.bundle_id)
        self.assertTrue(result)
        self.assertEqual(self.router.bundles[bundle.bundle_id].status, BundleStatus.DELIVERED)
        print("  [PASS] Delivered")
    
    def test_process_expired(self):
        """Should process expired."""
        bundle = self.router.create_bundle("A", "B", 100, ttl_hours=0.00001)
        time.sleep(0.1)
        expired = self.router.process_expired()
        self.assertIn(bundle.bundle_id, expired)
        print(f"  [PASS] Expired: {len(expired)} bundles")
    
    def test_simulate_contact(self):
        """Should simulate contact."""
        self.router.create_bundle("A", "B", 100)
        contact = Contact("A", "B", time.time(), time.time() + 60.0, 1e6)
        self.router.add_contact(contact)
        
        result = self.router.simulate_contact(contact)
        self.assertGreaterEqual(result["bundles_sent"], 0)
        print(f"  [PASS] Contact: {result['bundles_sent']} bundles, {result['transferred_bits']} bits")
    
    def test_network_stats(self):
        """Should provide stats."""
        self.router.create_bundle("A", "B", 100)
        stats = self.router.network_stats()
        self.assertEqual(stats["total_bundles"], 1)
        print(f"  [PASS] Stats: {stats['total_bundles']} bundles")
    
    def test_latency_estimate(self):
        """Should estimate latency."""
        bundle = self.router.create_bundle("A", "C", 100)
        self.router.forward_bundle(bundle.bundle_id, "A", "B", ["A", "B", "C"])
        
        contact = Contact("A", "B", time.time(), time.time() + 60.0, 1e6)
        self.router.add_contact(contact)
        
        latency = self.router.latency_estimate(bundle.bundle_id)
        self.assertGreaterEqual(latency, 0.0)
        print(f"  [PASS] Latency: {latency:.1f}s")


if __name__ == '__main__':
    unittest.main(verbosity=2)
