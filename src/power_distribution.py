"""
Power Distribution Module
Bus regulation, load balancing, battery charge control,
and solar array tracking for autonomous system power management.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class PowerSource(Enum):
    """Power source type."""
    SOLAR = "solar"
    BATTERY = "battery"
    FUEL_CELL = "fuel_cell"
    RTG = "rtg"
    EXTERNAL = "external"


class BatteryState(Enum):
    """Battery charge state."""
    IDLE = "idle"
    CHARGING = "charging"
    DISCHARGING = "discharging"
    FULL = "full"
    EMPTY = "empty"
    FAULT = "fault"


@dataclass
class PowerLoad:
    """Electrical power load."""
    load_id: str
    power_W: float
    voltage_V: float
    priority: int = 1  # Lower = higher priority
    enabled: bool = True


class BusRegulator:
    """
    Power bus voltage regulator.
    """
    
    def __init__(self, nominal_voltage_V: float = 28.0,
                 tolerance_percent: float = 5.0,
                 max_current_A: float = 100.0):
        """
        Args:
            nominal_voltage_V: Nominal bus voltage
            tolerance_percent: Voltage tolerance
            max_current_A: Maximum current capacity
        """
        self.nominal_voltage = nominal_voltage_V
        self.tolerance = tolerance_percent / 100.0
        self.max_current = max_current_A
        self.output_voltage = nominal_voltage_V
        self.current_load_A = 0.0
    
    def set_voltage(self, voltage_V: float) -> bool:
        """
        Set output voltage.
        
        Args:
            voltage_V: Target voltage
        
        Returns:
            True if within tolerance
        """
        min_v = self.nominal_voltage * (1 - self.tolerance)
        max_v = self.nominal_voltage * (1 + self.tolerance)
        
        if min_v <= voltage_V <= max_v:
            self.output_voltage = voltage_V
            return True
        return False
    
    def current_draw(self, power_W: float) -> float:
        """
        Compute current for power at current voltage.
        
        Args:
            power_W: Power draw
        
        Returns:
            Current (A)
        """
        if self.output_voltage <= 0:
            return 0.0
        return power_W / self.output_voltage
    
    def available_power(self) -> float:
        """
        Compute available power.
        
        Returns:
            Available power (W)
        """
        available_current = self.max_current - self.current_load_A
        return available_current * self.output_voltage
    
    def is_overloaded(self) -> bool:
        """Check if bus is overloaded."""
        return self.current_load_A > self.max_current
    
    def add_load(self, current_A: float):
        """Add current load."""
        self.current_load_A += current_A
    
    def remove_load(self, current_A: float):
        """Remove current load."""
        self.current_load_A = max(0.0, self.current_load_A - current_A)


class LoadBalancer:
    """
    Distribute power across multiple sources.
    """
    
    def __init__(self):
        self.sources: Dict[PowerSource, float] = {}
        # source -> available power (W)
        self.loads: List[PowerLoad] = []
    
    def register_source(self, source: PowerSource, capacity_W: float):
        """Register power source."""
        self.sources[source] = capacity_W
    
    def add_load(self, load: PowerLoad):
        """Add power load."""
        self.loads.append(load)
    
    def total_demand(self) -> float:
        """Get total power demand."""
        return sum(l.power_W for l in self.loads if l.enabled)
    
    def total_capacity(self) -> float:
        """Get total source capacity."""
        return sum(self.sources.values())
    
    def power_margin(self) -> float:
        """Get power margin (positive = surplus)."""
        return self.total_capacity() - self.total_demand()
    
    def is_sustainable(self) -> bool:
        """Check if demand can be met."""
        return self.power_margin() >= 0
    
    def shed_low_priority(self, target_reduction_W: float) -> List[str]:
        """
        Shed low priority loads.
        
        Args:
            target_reduction_W: Target power reduction
        
        Returns:
            List of shed load IDs
        """
        # Sort by priority (higher number = lower priority)
        sorted_loads = sorted(self.loads, key=lambda l: -l.priority)
        
        shed = []
        reduction = 0.0
        
        for load in sorted_loads:
            if not load.enabled:
                continue
            if reduction >= target_reduction_W:
                break
            
            load.enabled = False
            reduction += load.power_W
            shed.append(load.load_id)
        
        return shed
    
    def allocation(self) -> Dict[PowerSource, float]:
        """
        Allocate power from sources.
        
        Returns:
            Source allocation (W)
        """
        if not self.is_sustainable():
            # Return proportional allocation
            total = self.total_capacity()
            if total <= 0:
                return {s: 0.0 for s in self.sources}
            ratio = total / self.total_demand()
            return {s: cap * ratio for s, cap in self.sources.items()}
        
        # Full allocation
        return dict(self.sources)


class BatteryController:
    """
    Battery charge and discharge control.
    """
    
    def __init__(self, capacity_Ah: float = 100.0,
                 nominal_voltage_V: float = 28.0,
                 max_charge_rate_C: float = 0.5,
                 max_discharge_rate_C: float = 1.0,
                 efficiency: float = 0.95):
        """
        Args:
            capacity_Ah: Battery capacity
            nominal_voltage_V: Nominal voltage
            max_charge_rate_C: Max charge rate (C-rate)
            max_discharge_rate_C: Max discharge rate
            efficiency: Round-trip efficiency
        """
        self.capacity_Ah = capacity_Ah
        self.nominal_voltage = nominal_voltage_V
        self.max_charge_rate = max_charge_rate_C
        self.max_discharge_rate = max_discharge_rate_C
        self.efficiency = efficiency
        self.state_of_charge = 0.5  # Start at 50%
        self.state = BatteryState.IDLE
        self.cycle_count = 0
    
    def charge(self, power_W: float, duration_h: float) -> float:
        """
        Charge battery.
        
        Args:
            power_W: Charge power
            duration_h: Duration
        
        Returns:
            Energy added (Wh)
        """
        max_charge_A = self.capacity_Ah * self.max_charge_rate
        charge_power_max = max_charge_A * self.nominal_voltage
        
        actual_power = min(power_W, charge_power_max)
        energy_Wh = actual_power * duration_h * self.efficiency
        
        # Update SOC
        capacity_Wh = self.capacity_Ah * self.nominal_voltage
        soc_increase = energy_Wh / capacity_Wh
        self.state_of_charge = min(1.0, self.state_of_charge + soc_increase)
        
        if self.state_of_charge >= 0.99:
            self.state = BatteryState.FULL
        else:
            self.state = BatteryState.CHARGING
        
        return energy_Wh
    
    def discharge(self, power_W: float, duration_h: float) -> float:
        """
        Discharge battery.
        
        Args:
            power_W: Discharge power
            duration_h: Duration
        
        Returns:
            Energy delivered (Wh)
        """
        max_discharge_A = self.capacity_Ah * self.max_discharge_rate
        discharge_power_max = max_discharge_A * self.nominal_voltage
        
        actual_power = min(power_W, discharge_power_max)
        energy_Wh = actual_power * duration_h
        
        # Update SOC
        capacity_Wh = self.capacity_Ah * self.nominal_voltage
        soc_decrease = energy_Wh / (capacity_Wh * self.efficiency)
        self.state_of_charge = max(0.0, self.state_of_charge - soc_decrease)
        
        if self.state_of_charge <= 0.01:
            self.state = BatteryState.EMPTY
        else:
            self.state = BatteryState.DISCHARGING
        
        return energy_Wh
    
    def remaining_energy_Wh(self) -> float:
        """Get remaining energy."""
        return self.state_of_charge * self.capacity_Ah * self.nominal_voltage
    
    def remaining_time_h(self, discharge_power_W: float) -> float:
        """
        Estimate remaining time at discharge rate.
        
        Args:
            discharge_power_W: Discharge power
        
        Returns:
            Remaining time (hours)
        """
        if discharge_power_W <= 0:
            return float('inf')
        
        remaining_Wh = self.remaining_energy_Wh()
        return remaining_Wh / discharge_power_W
    
    def health_percent(self) -> float:
        """Get battery health estimate."""
        # Degrade with cycles
        degradation = min(0.3, self.cycle_count * 0.001)
        return (1.0 - degradation) * 100.0


class SolarArrayTracker:
    """
    Solar array sun tracking and power generation.
    """
    
    def __init__(self, area_m2: float = 20.0,
                 efficiency: float = 0.28,
                 max_power_W_m2: float = 1361.0):
        """
        Args:
            area_m2: Total array area
            efficiency: Cell efficiency
            max_power_W_m2: Solar constant
        """
        self.area = area_m2
        self.efficiency = efficiency
        self.solar_constant = max_power_W_m2
        self.azimuth_deg = 0.0
        self.elevation_deg = 90.0
        self.tracking_active = False
    
    def set_orientation(self, azimuth_deg: float, elevation_deg: float):
        """
        Set array orientation.
        
        Args:
            azimuth_deg: Azimuth angle
            elevation_deg: Elevation angle
        """
        self.azimuth_deg = azimuth_deg
        self.elevation_deg = max(0.0, min(90.0, elevation_deg))
    
    def cosine_loss(self, sun_azimuth_deg: float,
                   sun_elevation_deg: float) -> float:
        """
        Compute cosine loss relative to sun.
        
        Args:
            sun_azimuth_deg: Sun azimuth
            sun_elevation_deg: Sun elevation
        
        Returns:
            Cosine factor (0-1)
        """
        # Simplified: based on elevation difference
        d_elev = math.radians(sun_elevation_deg - self.elevation_deg)
        d_azim = math.radians(sun_azimuth_deg - self.azimuth_deg)
        
        # Approximate cosine loss
        cos_elev = math.cos(d_elev)
        cos_azim = math.cos(d_azim)
        
        return max(0.0, cos_elev * cos_azim)
    
    def generated_power(self, sun_azimuth_deg: float = 0.0,
                       sun_elevation_deg: float = 90.0,
                       illumination_factor: float = 1.0) -> float:
        """
        Compute generated power.
        
        Args:
            sun_azimuth_deg: Sun azimuth
            sun_elevation_deg: Sun elevation
            illumination_factor: Illumination (0-1, eclipse=0)
        
        Returns:
            Generated power (W)
        """
        if self.tracking_active:
            # Auto-track: assume perfect alignment
            cosine = 1.0
        else:
            cosine = self.cosine_loss(sun_azimuth_deg, sun_elevation_deg)
        
        return self.area * self.efficiency * self.solar_constant * cosine * illumination_factor
    
    def track_sun(self, sun_azimuth_deg: float, sun_elevation_deg: float):
        """
        Point array at sun.
        
        Args:
            sun_azimuth_deg: Sun azimuth
            sun_elevation_deg: Sun elevation
        """
        self.tracking_active = True
        self.azimuth_deg = sun_azimuth_deg
        self.elevation_deg = sun_elevation_deg


class PowerDistribution:
    """
    Unified power distribution controller.
    """
    
    def __init__(self):
        self.bus = BusRegulator()
        self.balancer = LoadBalancer()
        self.battery = BatteryController()
        self.solar = SolarArrayTracker()
    
    def register_source(self, source: PowerSource, capacity_W: float):
        """Register power source."""
        self.balancer.register_source(source, capacity_W)
    
    def add_load(self, load: PowerLoad):
        """Add electrical load."""
        self.balancer.add_load(load)
        current = self.bus.current_draw(load.power_W)
        self.bus.add_load(current)
    
    def remove_load(self, load_id: str):
        """Remove electrical load."""
        for load in self.balancer.loads:
            if load.load_id == load_id and load.enabled:
                current = self.bus.current_draw(load.power_W)
                self.bus.remove_load(current)
                load.enabled = False
                break
    
    def charge_battery(self, power_W: float, duration_h: float) -> float:
        """Charge battery."""
        return self.battery.charge(power_W, duration_h)
    
    def discharge_battery(self, power_W: float, duration_h: float) -> float:
        """Discharge battery."""
        return self.battery.discharge(power_W, duration_h)
    
    def power_summary(self) -> Dict:
        """Get power distribution summary."""
        return {
            "bus_voltage_V": self.bus.output_voltage,
            "bus_current_A": self.bus.current_load_A,
            "total_demand_W": self.balancer.total_demand(),
            "total_capacity_W": self.balancer.total_capacity(),
            "power_margin_W": self.balancer.power_margin(),
            "battery_soc": self.battery.state_of_charge,
            "battery_state": self.battery.state.value,
            "solar_power_W": self.solar.generated_power(),
            "bus_overloaded": self.bus.is_overloaded()
        }
