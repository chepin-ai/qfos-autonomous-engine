"""
Unit tests for command sequencer module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from command_sequencer import (CommandStatus, Command, CommandQueue,
                               CommandVerifier, TimeoutManager,
                               CommandSequencer)


class TestCommand(unittest.TestCase):
    """Test command."""
    
    def test_creation(self):
        """Should create command."""
        cmd = Command("cmd1", "THRUST", {"level": 50})
        self.assertEqual(cmd.cmd_id, "cmd1")
        self.assertEqual(cmd.opcode, "THRUST")
        self.assertEqual(cmd.status, CommandStatus.PENDING)
        print("  [PASS] Create: THRUST cmd1")


class TestCommandQueue(unittest.TestCase):
    """Test command queue."""
    
    def setUp(self):
        self.q = CommandQueue()
        self.q.enqueue(Command("c1", "A", priority=3))
        self.q.enqueue(Command("c2", "B", priority=1))
        self.q.enqueue(Command("c3", "C", priority=5))
    
    def test_enqueue(self):
        """Should enqueue by priority."""
        self.assertEqual(self.q.size(), 3)
        print("  [PASS] Enqueue: 3 items")
    
    def test_dequeue(self):
        """Should dequeue by priority."""
        cmd = self.q.dequeue()
        self.assertEqual(cmd.priority, 1)
        print(f"  [PASS] Dequeue: priority={cmd.priority}")
    
    def test_peek(self):
        """Should peek."""
        cmd = self.q.peek()
        self.assertEqual(cmd.priority, 1)
        print("  [PASS] Peek: priority=1")
    
    def test_cancel(self):
        """Should cancel command."""
        result = self.q.cancel("c1")
        self.assertTrue(result)
        self.assertEqual(self.q.size(), 2)
        print("  [PASS] Cancel: removed")
    
    def test_history(self):
        """Should archive history."""
        for _ in range(3):
            cmd = self.q.dequeue()
            self.q._archive(cmd)
        hist = self.q.get_history()
        self.assertEqual(len(hist), 3)
        print(f"  [PASS] History: {len(hist)} items")


class TestCommandVerifier(unittest.TestCase):
    """Test command verifier."""
    
    def setUp(self):
        self.v = CommandVerifier()
        self.v.add_rule("THRUST", lambda r: isinstance(r, (int, float)) and r >= 0)
    
    def test_verify_pass(self):
        """Should pass valid result."""
        cmd = Command("c1", "THRUST")
        cmd.result = 50
        self.assertTrue(self.v.verify(cmd))
        print("  [PASS] Verify: pass")
    
    def test_verify_fail(self):
        """Should fail invalid result."""
        cmd = Command("c1", "THRUST")
        cmd.result = -10
        self.assertFalse(self.v.verify(cmd))
        print("  [PASS] Verify: fail")
    
    def test_verify_no_rule(self):
        """Should pass without rule."""
        cmd = Command("c1", "UNKNOWN")
        cmd.result = "anything"
        self.assertTrue(self.v.verify(cmd))
        print("  [PASS] No rule: pass")


class TestTimeoutManager(unittest.TestCase):
    """Test timeout manager."""
    
    def setUp(self):
        self.tm = TimeoutManager()
    
    def test_start_timer(self):
        """Should start timer."""
        self.tm.start_timer("c1", 5.0)
        self.assertIn("c1", self.tm.active)
        print("  [PASS] Start: active")
    
    def test_check_timeout(self):
        """Should not timeout immediately."""
        self.tm.start_timer("c1", 10.0)
        self.assertFalse(self.tm.check_timeout("c1"))
        print("  [PASS] Timeout: False")
    
    def test_cancel(self):
        """Should cancel timer."""
        self.tm.start_timer("c1", 5.0)
        self.tm.cancel_timer("c1")
        self.assertNotIn("c1", self.tm.active)
        print("  [PASS] Cancel: removed")
    
    def test_remaining(self):
        """Should report remaining time."""
        self.tm.start_timer("c1", 10.0)
        rem = self.tm.remaining_time("c1")
        self.assertGreater(rem, 5.0)
        print(f"  [PASS] Remaining: {rem:.1f}s")


class TestCommandSequencer(unittest.TestCase):
    """Test unified command sequencer."""
    
    def setUp(self):
        self.cs = CommandSequencer()
        self.cs.register_handler("THRUST", lambda c: 50)
        self.cs.register_handler("NOP", lambda c: True)
        self.cs.verifier.add_rule("THRUST", lambda r: isinstance(r, int))
    
    def test_submit(self):
        """Should submit command."""
        self.cs.submit(Command("c1", "THRUST", priority=1))
        self.assertEqual(self.cs.queue.size(), 1)
        print("  [PASS] Submit: 1 queued")
    
    def test_execute(self):
        """Should execute command."""
        self.cs.submit(Command("c1", "THRUST", priority=1))
        cmd = self.cs.execute_next()
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.status, CommandStatus.COMPLETED)
        print(f"  [PASS] Execute: {cmd.status.value}")
    
    def test_execute_batch(self):
        """Should execute batch."""
        self.cs.submit(Command("c1", "NOP", priority=1))
        self.cs.submit(Command("c2", "NOP", priority=2))
        results = self.cs.execute_batch(count=2)
        self.assertEqual(len(results), 2)
        print(f"  [PASS] Batch: {len(results)} executed")
    
    def test_get_status(self):
        """Should get status."""
        self.cs.submit(Command("c1", "NOP", priority=1))
        self.cs.execute_next()
        status = self.cs.get_status("c1")
        self.assertEqual(status, CommandStatus.COMPLETED)
        print(f"  [PASS] Status: {status.value}")
    
    def test_summary(self):
        """Should provide summary."""
        self.cs.submit(Command("c1", "NOP"))
        self.cs.execute_next()
        summary = self.cs.sequencer_summary()
        self.assertEqual(summary["executed"], 1)
        print(f"  [PASS] Summary: {summary['executed']} executed")


if __name__ == '__main__':
    unittest.main(verbosity=2)
