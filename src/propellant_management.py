"""
Propellant Management Module
Tank modeling, consumption tracking, and ullage management
for propulsion systems.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class TankState(Enum):
    """Tank operational state."""
    NOMINAL = "nominal"
    LOW = "low"
    CRITICAL = "critical"
    EMPTY = "empty"
    PRESSURIZING = "pressurizing"


@dataclass
class Tank:
    """Propellant tank."""
    tank_id: str
    propellant_type: str  # e.g., "LOX", "LH2", "MON", "MMH"
    capacity: float  # kg
    current_mass: float  # kg
    temperature: float = 293.15  # K
    pressure: float = 1.0  # bar
    ullage_fraction: float = 0.05  # gas fraction
    
    def fill_level(self) -> float:
        """Fill level (0-1)."""
        if self.capacity <= 0:
            return 0.0
        return self.current_mass / self.capacity
    
    def ullage_volume(self) -> float:
        """Ullage volume fraction."""
        return 1.0 - self.fill_level() * (1.0 - self.ullage_fraction)
    
    def state(self) -> TankState:
        """Get tank state."""
        level = self.fill_level()
        if level <= 0.01:
            return TankState.EMPTY
        elif level < 0.1:
            return TankState.CRITICAL
        elif level < 0.25:
            return TankState.LOW
        return TankState.NOMINAL


class ConsumptionTracker:
    """
    Track propellant consumption over time.
    """
    
    def __init__(self):
        self.history: List[Tuple[float, float, float]] = []
        # (timestamp, mass_kg, flow_rate_kg_s)
        self.total_consumed = 0.0
    
    def record(self, timestamp: float, mass: float,
              flow_rate: float = 0.0):
        """
        Record consumption point.
        
        Args:
            timestamp: Time (seconds)
            mass: Current mass (kg)
            flow_rate: Flow rate (kg/s)
        """
        self.history.append((timestamp, mass, flow_rate))
        
        if len(self.history) >= 2:
            prev = self.history[-2]
            dt = timestamp - prev[0]
            if dt > 0:
                consumed = prev[1] - mass
                if consumed > 0:
                    self.total_consumed += consumed
    
    def average_flow_rate(self) -> float:
        """Average flow rate (kg/s)."""
        if len(self.history) < 2:
            return 0.0
        total_time = self.history[-1][0] - self.history[0][0]
        if total_time <= 0:
            return 0.0
        return self.total_consumed / total_time
    
    def time_to_empty(self, current_mass: float) -> float:
        """
        Estimate time to empty.
        
        Args:
            current_mass: Current mass (kg)
        
        Returns:
            Estimated time (seconds)
        """
        rate = self.average_flow_rate()
        if rate <= 0:
            return float('inf')
        return current_mass / rate
    
    def remaining_burn_time(self, current_mass: float,
                           thrust: float, isp: float) -> float:
        """
        Estimate remaining burn time.
        
        Args:
            current_mass: Current mass (kg)
            thrust: Thrust (N)
            isp: Specific impulse (s)
        
        Returns:
            Burn time (seconds)
        """
        if thrust <= 0 or isp <= 0:
            return float('inf')
        ve = isp * 9.80665
        mdot = thrust / ve
        if mdot <= 0:
            return float('inf')
        return current_mass / mdot


class UllageManager:
    """
    Manage tank ullage and propellant settling.
    """
    
    def __init__(self, settling_accel: float = 0.1):  # m/s^2
        """
        Args:
            settling_accel: Minimum settling acceleration (m/s^2)
        """
        self.settling_accel = settling_accel
        self.settling_active = False
    
    def required_settling_burn(self, tank: Tank,
                              vehicle_mass: float) -> float:
        """
        Compute required settling thrust.
        
        Args:
            tank: Tank
            vehicle_mass: Vehicle mass (kg)
        
        Returns:
            Required thrust (N)
        """
        return vehicle_mass * self.settling_accel
    
    def assess_ullage(self, tank: Tank) -> bool:
        """
        Assess if ullage is acceptable.
        
        Args:
            tank: Tank
        
        Returns:
            True if ullage is acceptable
        """
        ullage = tank.ullage_volume()
        # Need some ullage but not too much
        return 0.02 <= ullage <= 0.5
    
    def settle_propellant(self, tank: Tank):
        """Mark settling as active."""
        self.settling_active = True
        tank.ullage_fraction = 0.02  # Reduce ullage after settling


class PressurizationSystem:
    """
    Tank pressurization system.
    """
    
    def __init__(self, max_pressure: float = 30.0):  # bar
        """
        Args:
            max_pressure: Maximum tank pressure (bar)
        """
        self.max_pressure = max_pressure
        self.pressurant_mass = 0.0  # kg
    
    def required_pressure(self, tank: Tank,
                         engine_chamber_pressure: float) -> float:
        """
        Compute required tank pressure.
        
        Args:
            tank: Tank
            engine_chamber_pressure: Engine chamber pressure (bar)
        
        Returns:
            Required pressure (bar)
        """
        # Simple: need some margin above chamber pressure
        return engine_chamber_pressure * 1.2
    
    def pressurize(self, tank: Tank, target_pressure: float):
        """
        Pressurize tank.
        
        Args:
            tank: Tank
            target_pressure: Target pressure (bar)
        """
        tank.pressure = min(target_pressure, self.max_pressure)
    
    def depressurize(self, tank: Tank):
        """Depressurize tank."""
        tank.pressure = 1.0


class PropellantManagement:
    """
    Unified propellant management controller.
    """
    
    def __init__(self):
        self.tanks: Dict[str, Tank] = {}
        self.trackers: Dict[str, ConsumptionTracker] = {}
        self.ullage = UllageManager()
        self.pressurization = PressurizationSystem()
    
    def add_tank(self, tank: Tank):
        """Add propellant tank."""
        self.tanks[tank.tank_id] = tank
        self.trackers[tank.tank_id] = ConsumptionTracker()
    
    def consume(self, tank_id: str, amount: float, timestamp: float = 0.0):
        """
        Record propellant consumption.
        
        Args:
            tank_id: Tank ID
            amount: Amount consumed (kg)
            timestamp: Time (seconds)
        """
        tank = self.tanks.get(tank_id)
        if not tank:
            return
        tank.current_mass = max(0.0, tank.current_mass - amount)
        
        tracker = self.trackers.get(tank_id)
        if tracker:
            tracker.record(timestamp, tank.current_mass)
    
    def transfer(self, from_id: str, to_id: str, amount: float):
        """
        Transfer propellant between tanks.
        
        Args:
            from_id: Source tank
            to_id: Destination tank
            amount: Amount (kg)
        """
        src = self.tanks.get(from_id)
        dst = self.tanks.get(to_id)
        if not src or not dst:
            return
        
        actual = min(amount, src.current_mass,
                    dst.capacity - dst.current_mass)
        src.current_mass -= actual
        dst.current_mass += actual
    
    def total_propellant(self) -> float:
        """Get total propellant mass."""
        return sum(t.current_mass for t in self.tanks.values())
    
    def total_capacity(self) -> float:
        """Get total capacity."""
        return sum(t.capacity for t in self.tanks.values())
    
    def overall_fill_level(self) -> float:
        """Get overall fill level."""
        cap = self.total_capacity()
        if cap <= 0:
            return 0.0
        return self.total_propellant() / cap
    
    def get_critical_tanks(self) -> List[Tank]:
        """Get tanks in critical state."""
        return [t for t in self.tanks.values()
                if t.state() in (TankState.CRITICAL, TankState.EMPTY)]
    
    def burn_time_remaining(self, tank_id: str, thrust: float,
                           isp: float) -> float:
        """Get burn time for tank."""
        tank = self.tanks.get(tank_id)
        tracker = self.trackers.get(tank_id)
        if not tank or not tracker:
            return 0.0
        return tracker.remaining_burn_time(tank.current_mass, thrust, isp)
    
    def propellant_summary(self) -> Dict:
        """Get propellant summary."""
        return {
            "tanks": len(self.tanks),
            "total_mass": self.total_propellant(),
            "total_capacity": self.total_capacity(),
            "fill_level": self.overall_fill_level(),
            "critical_tanks": len(self.get_critical_tanks()),
            "settling_active": self.ullage.settling_active
        }
