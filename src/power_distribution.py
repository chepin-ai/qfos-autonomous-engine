"""
Power Distribution Module
Load balancing, bus regulation, and battery management
for spacecraft electrical power systems.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class PowerLoad:
    """An electrical power load."""
    name: str
    nominal_power: float  # W
    priority: int = 5  # 1=highest, 10=lowest
    is_enabled: bool = True
    duty_cycle: float = 1.0  # 0-1
    
    def current_power(self) -> float:
        """Get current power draw."""
        if not self.is_enabled:
            return 0.0
        return self.nominal_power * self.duty_cycle


@dataclass
class Battery:
    """A spacecraft battery."""
    name: str
    capacity: float  # Wh
    voltage: float  # V
    charge_efficiency: float = 0.95
    discharge_efficiency: float = 0.95
    max_charge_rate: float = 100.0  # W
    max_discharge_rate: float = 200.0  # W
    state_of_charge: float = 1.0  # 0-1
    cycle_count: int = 0
    
    def available_energy(self) -> float:
        """Get available energy (Wh)."""
        return self.capacity * self.state_of_charge * self.discharge_efficiency
    
    def charge(self, power: float, dt: float) -> float:
        """
        Charge battery.
        
        Args:
            power: Charging power (W)
            dt: Time (hours)
        
        Returns:
            Actual energy stored (Wh)
        """
        power = min(power, self.max_charge_rate)
        energy_in = power * dt * self.charge_efficiency
        
        needed = self.capacity * (1.0 - self.state_of_charge)
        stored = min(energy_in, needed)
        
        self.state_of_charge += stored / self.capacity
        self.state_of_charge = min(1.0, self.state_of_charge)
        
        return stored
    
    def discharge(self, power: float, dt: float) -> float:
        """
        Discharge battery.
        
        Args:
            power: Discharging power (W)
            dt: Time (hours)
        
        Returns:
            Actual energy delivered (Wh)
        """
        power = min(power, self.max_discharge_rate)
        energy_out = power * dt / self.discharge_efficiency
        
        available = self.capacity * self.state_of_charge
        delivered = min(energy_out, available)
        
        self.state_of_charge -= delivered / self.capacity
        self.state_of_charge = max(0.0, self.state_of_charge)
        
        if delivered > 0:
            self.cycle_count += 1
        
        return delivered * self.discharge_efficiency
    
    def depth_of_discharge(self) -> float:
        """Get depth of discharge."""
        return 1.0 - self.state_of_charge


@dataclass
class SolarArray:
    """A solar array power source."""
    name: str
    area: float  # m^2
    efficiency: float  # 0-1
    solar_constant: float = 1361.0  # W/m^2 at 1 AU
    
    def output_power(self, sun_angle: float = 0.0,
                    distance_au: float = 1.0) -> float:
        """
        Compute output power.
        
        Args:
            sun_angle: Angle from sun (radians), 0 = direct
            distance_au: Distance from sun (AU)
        
        Returns:
            Output power (W)
        """
        flux = self.solar_constant / (distance_au ** 2)
        return self.area * self.efficiency * flux * math.cos(sun_angle)


class LoadBalancer:
    """
    Balance power loads across available sources.
    """
    
    def __init__(self):
        self.loads: Dict[str, PowerLoad] = {}
        self.available_power: float = 0.0
    
    def add_load(self, load: PowerLoad):
        """Add power load."""
        self.loads[load.name] = load
    
    def set_available_power(self, power: float):
        """Set available power."""
        self.available_power = power
    
    def total_demand(self) -> float:
        """Get total power demand."""
        return sum(load.current_power() for load in self.loads.values())
    
    def balance(self) -> Dict[str, bool]:
        """
        Balance loads based on priority.
        
        Returns:
            Load enable states
        """
        # Sort by priority
        sorted_loads = sorted(self.loads.values(), key=lambda l: l.priority)
        
        remaining = self.available_power
        states = {}
        
        for load in sorted_loads:
            demand = load.nominal_power * load.duty_cycle
            if demand <= remaining:
                load.is_enabled = True
                remaining -= demand
            else:
                load.is_enabled = False
            states[load.name] = load.is_enabled
        
        return states
    
    def get_shed_loads(self) -> List[str]:
        """Get list of shed (disabled) loads."""
        return [name for name, load in self.loads.items() if not load.is_enabled]


class BusRegulator:
    """
    Power bus voltage regulator.
    """
    
    def __init__(self, nominal_voltage: float = 28.0,
                 tolerance: float = 0.05):
        """
        Args:
            nominal_voltage: Nominal bus voltage (V)
            tolerance: Voltage tolerance fraction
        """
        self.nominal_voltage = nominal_voltage
        self.tolerance = tolerance
        self.current_voltage = nominal_voltage
        self.current_load = 0.0
    
    def regulate(self, source_power: float, load_power: float) -> float:
        """
        Regulate bus voltage.
        
        Args:
            source_power: Available source power (W)
            load_power: Total load power (W)
        
        Returns:
            Regulated voltage
        """
        self.current_load = load_power
        
        if source_power >= load_power:
            # Sufficient power
            sag = 0.0
        else:
            # Insufficient power - voltage sags
            sag_ratio = 1.0 - (source_power / load_power) if load_power > 0 else 0
            sag = sag_ratio * self.tolerance * self.nominal_voltage
        
        self.current_voltage = self.nominal_voltage - sag
        return self.current_voltage
    
    def is_within_tolerance(self) -> bool:
        """Check if voltage is within tolerance."""
        lower = self.nominal_voltage * (1 - self.tolerance)
        upper = self.nominal_voltage * (1 + self.tolerance)
        return lower <= self.current_voltage <= upper


class PowerDistribution:
    """
    Unified power distribution controller.
    """
    
    def __init__(self):
        self.batteries: Dict[str, Battery] = {}
        self.solar_arrays: Dict[str, SolarArray] = {}
        self.load_balancer = LoadBalancer()
        self.bus_regulator = BusRegulator()
        self.total_generated: float = 0.0
        self.total_consumed: float = 0.0
    
    def add_battery(self, battery: Battery):
        """Add battery."""
        self.batteries[battery.name] = battery
    
    def add_solar_array(self, array: SolarArray):
        """Add solar array."""
        self.solar_arrays[array.name] = array
    
    def add_load(self, load: PowerLoad):
        """Add power load."""
        self.load_balancer.add_load(load)
    
    def compute_generation(self, sun_angle: float = 0.0,
                          distance_au: float = 1.0) -> float:
        """
        Compute total generation.
        
        Args:
            sun_angle: Sun angle
            distance_au: Distance from sun
        
        Returns:
            Total power generated (W)
        """
        total = 0.0
        for array in self.solar_arrays.values():
            total += array.output_power(sun_angle, distance_au)
        self.total_generated = total
        return total
    
    def distribute(self, dt_hours: float = 1.0) -> Dict:
        """
        Distribute power for one time step.
        
        Args:
            dt_hours: Time step (hours)
        
        Returns:
            Distribution status
        """
        generation = self.total_generated
        demand = self.load_balancer.total_demand()
        
        # Regulate bus
        voltage = self.bus_regulator.regulate(generation, demand)
        
        # Balance loads
        self.load_balancer.set_available_power(generation)
        states = self.load_balancer.balance()
        
        # Use battery if needed
        battery_support = 0.0
        if generation < demand:
            deficit = demand - generation
            for battery in self.batteries.values():
                power = min(deficit, battery.max_discharge_rate)
                delivered = battery.discharge(power, dt_hours)
                battery_support += delivered / dt_hours if dt_hours > 0 else 0
                deficit -= power
                if deficit <= 0:
                    break
        elif generation > demand:
            surplus = generation - demand
            for battery in self.batteries.values():
                power = min(surplus, battery.max_charge_rate)
                stored = battery.charge(power, dt_hours)
                surplus -= power
                if surplus <= 0:
                    break
        
        self.total_consumed = min(generation + battery_support, demand)
        
        return {
            "generation": generation,
            "demand": demand,
            "battery_support": battery_support,
            "voltage": voltage,
            "load_states": states,
            "shed_loads": self.load_balancer.get_shed_loads()
        }
    
    def power_summary(self) -> Dict:
        """Get power summary."""
        return {
            "generation": self.total_generated,
            "consumption": self.total_consumed,
            "battery_soc": {name: b.state_of_charge for name, b in self.batteries.items()},
            "bus_voltage": self.bus_regulator.current_voltage,
            "loads": len(self.load_balancer.loads)
        }
