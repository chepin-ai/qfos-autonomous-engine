"""
Fault Injection Module
Systematic fault injection and failure mode simulation
for resilience testing of spacecraft systems.
"""

import random
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class FaultType(Enum):
    """Types of faults that can be injected."""
    SENSOR_NOISE = "sensor_noise"
    SENSOR_DROPOUT = "sensor_dropout"
    SENSOR_BIAS = "sensor_bias"
    ACTUATOR_STUCK = "actuator_stuck"
    ACTUATOR_DELAY = "actuator_delay"
    COMM_DEGRADATION = "comm_degradation"
    COMM_LOSS = "comm_loss"
    POWER_DEGRADATION = "power_degradation"
    MEMORY_CORRUPTION = "memory_corruption"
    COMPUTATION_ERROR = "computation_error"
    BYZANTINE_FAULT = "byzantine_fault"


@dataclass
class FaultConfig:
    """Configuration for a fault injection."""
    fault_type: FaultType
    target: str  # subsystem or component ID
    probability: float = 0.1  # 0.0-1.0
    magnitude: float = 1.0  # severity multiplier
    duration_s: float = 10.0
    trigger_condition: Optional[str] = None


@dataclass
class FaultEvent:
    """Recorded fault event."""
    timestamp: float
    fault_type: FaultType
    target: str
    description: str
    recovered: bool = False


class SensorFaultInjector:
    """
    Inject faults into sensor readings.
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.active_faults: Dict[str, FaultConfig] = {}
        self.event_log: List[FaultEvent] = []
    
    def add_fault(self, config: FaultConfig):
        """Add a fault configuration."""
        self.active_faults[f"{config.target}:{config.fault_type.value}"] = config
    
    def inject(self, sensor_id: str, value: float,
               timestamp: float = 0.0) -> Tuple[float, Optional[str]]:
        """
        Potentially inject fault into sensor reading.
        
        Args:
            sensor_id: Sensor identifier
            value: Original reading
            timestamp: Current time
        
        Returns:
            (modified_value, fault_description or None)
        """
        key_noise = f"{sensor_id}:{FaultType.SENSOR_NOISE.value}"
        key_dropout = f"{sensor_id}:{FaultType.SENSOR_DROPOUT.value}"
        key_bias = f"{sensor_id}:{FaultType.SENSOR_BIAS.value}"
        
        modified = value
        description = None
        
        # Noise injection
        if key_noise in self.active_faults:
            config = self.active_faults[key_noise]
            if self.rng.random() < config.probability:
                noise = self.rng.gauss(0, config.magnitude)
                modified += noise
                description = f"noise({noise:.3f})"
                self.event_log.append(FaultEvent(timestamp, FaultType.SENSOR_NOISE,
                                                sensor_id, description))
        
        # Dropout
        if key_dropout in self.active_faults:
            config = self.active_faults[key_dropout]
            if self.rng.random() < config.probability:
                modified = float('nan')
                description = "dropout"
                self.event_log.append(FaultEvent(timestamp, FaultType.SENSOR_DROPOUT,
                                                sensor_id, description))
        
        # Bias
        if key_bias in self.active_faults:
            config = self.active_faults[key_bias]
            if self.rng.random() < config.probability:
                modified += config.magnitude
                description = f"bias(+{config.magnitude})"
                self.event_log.append(FaultEvent(timestamp, FaultType.SENSOR_BIAS,
                                                sensor_id, description))
        
        return modified, description
    
    def clear_faults(self):
        """Clear all active faults."""
        self.active_faults.clear()
    
    def get_event_summary(self) -> Dict:
        """Get summary of fault events."""
        by_type = {}
        for event in self.event_log:
            ft = event.fault_type.value
            by_type[ft] = by_type.get(ft, 0) + 1
        
        return {
            "total_events": len(self.event_log),
            "by_type": by_type,
            "active_faults": len(self.active_faults)
        }


class ActuatorFaultInjector:
    """
    Inject faults into actuator commands.
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.stuck_actuators: Dict[str, float] = {}  # actuator_id -> stuck_value
        self.delayed_commands: List[Dict] = []
        self.delays: Dict[str, float] = {}
    
    def set_stuck(self, actuator_id: str, stuck_value: float):
        """Set actuator to stuck at value."""
        self.stuck_actuators[actuator_id] = stuck_value
    
    def set_delay(self, actuator_id: str, delay_s: float):
        """Set actuator delay."""
        self.delays[actuator_id] = delay_s
    
    def inject(self, actuator_id: str, command: float) -> float:
        """
        Potentially modify actuator command.
        
        Args:
            actuator_id: Actuator identifier
            command: Original command
        
        Returns:
            Modified command
        """
        if actuator_id in self.stuck_actuators:
            return self.stuck_actuators[actuator_id]
        
        return command
    
    def is_stuck(self, actuator_id: str) -> bool:
        """Check if actuator is stuck."""
        return actuator_id in self.stuck_actuators
    
    def release(self, actuator_id: str):
        """Release stuck actuator."""
        if actuator_id in self.stuck_actuators:
            del self.stuck_actuators[actuator_id]
    
    def get_faulty_actuators(self) -> List[str]:
        """Get list of faulty actuators."""
        return list(self.stuck_actuators.keys())


class CommunicationFaultInjector:
    """
    Inject faults into communication channels.
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.packet_loss_rate: Dict[str, float] = {}
        self.latency_ms: Dict[str, float] = {}
        self.corruption_rate: Dict[str, float] = {}
    
    def set_packet_loss(self, channel_id: str, rate: float):
        """Set packet loss rate."""
        self.packet_loss_rate[channel_id] = rate
    
    def set_latency(self, channel_id: str, latency_ms: float):
        """Set channel latency."""
        self.latency_ms[channel_id] = latency_ms
    
    def set_corruption(self, channel_id: str, rate: float):
        """Set corruption rate."""
        self.corruption_rate[channel_id] = rate
    
    def should_drop(self, channel_id: str) -> bool:
        """Check if packet should be dropped."""
        rate = self.packet_loss_rate.get(channel_id, 0.0)
        return self.rng.random() < rate
    
    def get_latency(self, channel_id: str) -> float:
        """Get channel latency."""
        return self.latency_ms.get(channel_id, 0.0)
    
    def is_corrupted(self, channel_id: str) -> bool:
        """Check if packet should be corrupted."""
        rate = self.corruption_rate.get(channel_id, 0.0)
        return self.rng.random() < rate
    
    def get_channel_status(self, channel_id: str) -> Dict:
        """Get channel fault status."""
        return {
            "packet_loss": self.packet_loss_rate.get(channel_id, 0.0),
            "latency_ms": self.latency_ms.get(channel_id, 0.0),
            "corruption": self.corruption_rate.get(channel_id, 0.0)
        }


class FaultInjector:
    """
    Unified fault injection controller.
    
    Combines sensor, actuator, and communication fault injection.
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.sensor = SensorFaultInjector(seed)
        self.actuator = ActuatorFaultInjector(seed)
        self.communication = CommunicationFaultInjector(seed)
        self.scenarios: Dict[str, List[FaultConfig]] = {}
    
    def define_scenario(self, name: str, faults: List[FaultConfig]):
        """Define a fault scenario."""
        self.scenarios[name] = faults
    
    def activate_scenario(self, name: str):
        """Activate a fault scenario."""
        if name not in self.scenarios:
            return False
        
        for fault in self.scenarios[name]:
            if fault.fault_type in [FaultType.SENSOR_NOISE, FaultType.SENSOR_DROPOUT,
                                   FaultType.SENSOR_BIAS]:
                self.sensor.add_fault(fault)
            elif fault.fault_type == FaultType.ACTUATOR_STUCK:
                self.actuator.set_stuck(fault.target, fault.magnitude)
            elif fault.fault_type == FaultType.COMM_LOSS:
                self.communication.set_packet_loss(fault.target, fault.probability)
            elif fault.fault_type == FaultType.COMM_DEGRADATION:
                self.communication.set_latency(fault.target, fault.magnitude)
        
        return True
    
    def clear_all(self):
        """Clear all faults."""
        self.sensor.clear_faults()
        self.actuator.stuck_actuators.clear()
        self.communication.packet_loss_rate.clear()
        self.communication.latency_ms.clear()
        self.communication.corruption_rate.clear()
    
    def injector_summary(self) -> Dict:
        """Get fault injection summary."""
        return {
            "scenarios_defined": len(self.scenarios),
            "sensor_faults": len(self.sensor.active_faults),
            "stuck_actuators": len(self.actuator.stuck_actuators),
            "comm_channels_affected": len(self.communication.packet_loss_rate),
            "total_events": len(self.sensor.event_log)
        }
