"""
Command Sequencer Module
Command queue, verification, and timeout management
for spacecraft command execution.
"""

import time
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class CommandStatus(Enum):
    """Command execution status."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class Command:
    """A spacecraft command."""
    cmd_id: str
    opcode: str
    args: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    timeout: float = 30.0
    retries: int = 2
    status: CommandStatus = CommandStatus.PENDING
    result: Any = None
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: str = ""
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()


class CommandQueue:
    """
    Priority command queue with reordering.
    """
    
    def __init__(self):
        self._queue: List[Command] = []
        self._history: List[Command] = []
        self.max_history = 1000
    
    def enqueue(self, command: Command):
        """Add command to queue."""
        self._queue.append(command)
        self._queue.sort(key=lambda c: c.priority)
    
    def dequeue(self) -> Optional[Command]:
        """Get next command."""
        if not self._queue:
            return None
        return self._queue.pop(0)
    
    def peek(self) -> Optional[Command]:
        """Peek at next command without removing."""
        return self._queue[0] if self._queue else None
    
    def remove(self, cmd_id: str) -> bool:
        """Remove command by ID."""
        for i, cmd in enumerate(self._queue):
            if cmd.cmd_id == cmd_id:
                self._queue.pop(i)
                return True
        return False
    
    def cancel(self, cmd_id: str) -> bool:
        """Cancel pending command."""
        for cmd in self._queue:
            if cmd.cmd_id == cmd_id:
                cmd.status = CommandStatus.CANCELLED
                self._archive(cmd)
                self.remove(cmd_id)
                return True
        return False
    
    def _archive(self, command: Command):
        """Archive completed command."""
        self._history.append(command)
        if len(self._history) > self.max_history:
            self._history = self._history[-self.max_history:]
    
    def size(self) -> int:
        """Get queue size."""
        return len(self._queue)
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0
    
    def get_history(self, limit: int = 100) -> List[Command]:
        """Get command history."""
        return self._history[-limit:]


class CommandVerifier:
    """
    Verify command execution results.
    """
    
    def __init__(self):
        self.verification_rules: Dict[str, Callable[[Any], bool]] = {}
    
    def add_rule(self, opcode: str,
                validator: Callable[[Any], bool]):
        """Add verification rule for opcode."""
        self.verification_rules[opcode] = validator
    
    def verify(self, command: Command) -> bool:
        """
        Verify command result.
        
        Args:
            command: Command to verify
        
        Returns:
            True if verified
        """
        if command.opcode not in self.verification_rules:
            # No rule = auto-pass
            return True
        
        try:
            return self.verification_rules[command.opcode](command.result)
        except Exception:
            return False
    
    def verify_all(self, commands: List[Command]) -> Dict[str, bool]:
        """Verify multiple commands."""
        return {cmd.cmd_id: self.verify(cmd) for cmd in commands}


class TimeoutManager:
    """
    Manage command execution timeouts.
    """
    
    def __init__(self):
        self.active: Dict[str, Dict] = {}
        self.default_timeout = 30.0
    
    def start_timer(self, cmd_id: str, timeout: float):
        """Start timeout timer."""
        self.active[cmd_id] = {
            "start": time.time(),
            "timeout": timeout
        }
    
    def check_timeout(self, cmd_id: str) -> bool:
        """
        Check if command has timed out.
        
        Args:
            cmd_id: Command ID
        
        Returns:
            True if timed out
        """
        if cmd_id not in self.active:
            return False
        
        info = self.active[cmd_id]
        elapsed = time.time() - info["start"]
        return elapsed > info["timeout"]
    
    def cancel_timer(self, cmd_id: str):
        """Cancel timeout timer."""
        if cmd_id in self.active:
            del self.active[cmd_id]
    
    def check_all(self) -> List[str]:
        """Check all active timers."""
        timed_out = []
        for cmd_id in list(self.active.keys()):
            if self.check_timeout(cmd_id):
                timed_out.append(cmd_id)
                del self.active[cmd_id]
        return timed_out
    
    def remaining_time(self, cmd_id: str) -> float:
        """Get remaining time for command."""
        if cmd_id not in self.active:
            return 0.0
        info = self.active[cmd_id]
        elapsed = time.time() - info["start"]
        return max(0.0, info["timeout"] - elapsed)


class CommandSequencer:
    """
    Unified command sequencer controller.
    """
    
    def __init__(self):
        self.queue = CommandQueue()
        self.verifier = CommandVerifier()
        self.timeout_mgr = TimeoutManager()
        self.handlers: Dict[str, Callable[[Command], Any]] = {}
        self.stats = {"executed": 0, "failed": 0, "timed_out": 0}
    
    def register_handler(self, opcode: str,
                        handler: Callable[[Command], Any]):
        """Register command handler."""
        self.handlers[opcode] = handler
    
    def submit(self, command: Command):
        """Submit command to queue."""
        self.queue.enqueue(command)
    
    def execute_next(self) -> Optional[Command]:
        """
        Execute next command in queue.
        
        Returns:
            Executed command or None
        """
        command = self.queue.dequeue()
        if not command:
            return None
        
        command.status = CommandStatus.EXECUTING
        command.started_at = time.time()
        
        # Start timeout timer
        self.timeout_mgr.start_timer(command.cmd_id, command.timeout)
        
        try:
            if command.opcode in self.handlers:
                command.result = self.handlers[command.opcode](command)
            else:
                command.result = None
            
            # Check timeout
            if self.timeout_mgr.check_timeout(command.cmd_id):
                command.status = CommandStatus.TIMEOUT
                command.error_message = "Execution timed out"
                self.stats["timed_out"] += 1
            else:
                # Verify result
                if self.verifier.verify(command):
                    command.status = CommandStatus.COMPLETED
                    self.stats["executed"] += 1
                else:
                    command.status = CommandStatus.FAILED
                    command.error_message = "Verification failed"
                    self.stats["failed"] += 1
        
        except Exception as e:
            command.status = CommandStatus.FAILED
            command.error_message = str(e)
            self.stats["failed"] += 1
        
        finally:
            self.timeout_mgr.cancel_timer(command.cmd_id)
            command.completed_at = time.time()
            self.queue._archive(command)
        
        return command
    
    def execute_batch(self, count: int = 10) -> List[Command]:
        """
        Execute batch of commands.
        
        Args:
            count: Maximum commands to execute
        
        Returns:
            Executed commands
        """
        results = []
        for _ in range(count):
            if self.queue.is_empty():
                break
            cmd = self.execute_next()
            if cmd:
                results.append(cmd)
        return results
    
    def get_status(self, cmd_id: str) -> Optional[CommandStatus]:
        """Get command status."""
        for cmd in self.queue._queue:
            if cmd.cmd_id == cmd_id:
                return cmd.status
        for cmd in self.queue._history:
            if cmd.cmd_id == cmd_id:
                return cmd.status
        return None
    
    def sequencer_summary(self) -> Dict:
        """Get sequencer summary."""
        return {
            "queue_size": self.queue.size(),
            "executed": self.stats["executed"],
            "failed": self.stats["failed"],
            "timed_out": self.stats["timed_out"],
            "handlers": list(self.handlers.keys()),
            "pending_timeouts": len(self.timeout_mgr.active)
        }
