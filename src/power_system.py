"""
Power System Module
Spacecraft power generation, storage, and management.
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass


# Solar constant at 1 AU
SOLAR_CONSTANT_1AU = 1361.0  # W/m^2


@dataclass
class PowerLoad:
    """A power-consuming component."""
    name: str
    power_w: float
    duty_cycle: float = 1.0  # 0.0 to 1.0
    critical: bool = False   # True if cannot be shed


class SolarArray:
    """
    Solar array power generation model.
    
    Accounts for solar distance, incidence angle, degradation, and temperature.
    """
    
    def __init__(self, area_m2: float, efficiency: float = 0.28,
                 degradation_per_year: float = 0.02,
                 temperature_coefficient: float = -0.004):
        """
        Args:
            area_m2: Total solar array area
            efficiency: Cell efficiency at reference temperature
            degradation_per_year: Annual power degradation factor
            temperature_coefficient: Power temp coefficient (%/C, negative)
        """
        self.area_m2 = area_m2
        self.efficiency = efficiency
        self.degradation = degradation_per_year
        self.temp_coeff = temperature_coefficient
        self.age_years = 0.0
    
    def power_output(self, solar_distance_au: float,
                     incidence_angle_deg: float = 0.0,
                     cell_temp_c: float = 25.0) -> float:
        """
        Calculate solar array power output.
        
        Args:
            solar_distance_au: Distance from Sun (AU)
            incidence_angle_deg: Sun incidence angle (0 = normal)
            cell_temp_c: Cell temperature (C)
        
        Returns:
            Power output in Watts
        """
        # Solar flux at given distance
        solar_flux = SOLAR_CONSTANT_1AU / (solar_distance_au ** 2)
        
        # Incidence angle correction
        incidence_rad = math.radians(incidence_angle_deg)
        cosine_factor = max(0.0, math.cos(incidence_rad))
        
        # Temperature correction
        temp_delta = cell_temp_c - 25.0
        temp_factor = 1.0 + self.temp_coeff * temp_delta
        
        # Degradation
        degradation_factor = (1.0 - self.degradation) ** self.age_years
        
        # Total power
        power = (solar_flux * self.area_m2 * self.efficiency *
                 cosine_factor * temp_factor * degradation_factor)
        
        return max(0.0, power)
    
    def set_age(self, years: float):
        """Set solar array age for degradation calculation."""
        self.age_years = years


class Battery:
    """
    Battery energy storage model.
    
    Supports lithium-ion chemistry with depth-of-discharge limits.
    """
    
    def __init__(self, capacity_wh: float, initial_soc: float = 1.0,
                 max_dod: float = 0.8, charge_efficiency: float = 0.95,
                 discharge_efficiency: float = 0.95,
                 self_discharge_per_day: float = 0.001):
        """
        Args:
            capacity_wh: Total energy capacity (Wh)
            initial_soc: Initial state of charge (0-1)
            max_dod: Maximum depth of discharge (0-1)
            charge_efficiency: Charging efficiency
            discharge_efficiency: Discharging efficiency
            self_discharge_per_day: Daily self-discharge fraction
        """
        self.capacity_wh = capacity_wh
        self.soc = initial_soc
        self.max_dod = max_dod
        self.charge_eff = charge_efficiency
        self.discharge_eff = discharge_efficiency
        self.self_discharge = self_discharge_per_day
        self.cycle_count = 0
    
    def charge(self, energy_wh: float, dt_hours: float = 1.0) -> float:
        """
        Charge battery with given energy.
        
        Returns:
            Actual energy accepted (Wh)
        """
        # Self-discharge
        self.soc *= (1.0 - self.self_discharge * dt_hours / 24.0)
        
        # Charge
        available = 1.0 - self.soc
        requested = energy_wh * self.charge_eff / self.capacity_wh
        accepted = min(available, requested)
        self.soc += accepted
        
        actual_energy = accepted * self.capacity_wh / self.charge_eff
        return actual_energy
    
    def discharge(self, energy_wh: float, dt_hours: float = 1.0) -> float:
        """
        Discharge battery to provide given energy.
        
        Returns:
            Actual energy delivered (Wh)
        """
        # Self-discharge
        self.soc *= (1.0 - self.self_discharge * dt_hours / 24.0)
        
        # Discharge
        min_soc = 1.0 - self.max_dod
        available = self.soc - min_soc
        requested = energy_wh / (self.capacity_wh * self.discharge_eff)
        delivered_frac = min(available, requested)
        self.soc -= delivered_frac
        
        actual_energy = delivered_frac * self.capacity_wh * self.discharge_eff
        
        # Count cycle (approximate: full DOD equivalent)
        if delivered_frac > 0.01:
            self.cycle_count += delivered_frac / self.max_dod
        
        return actual_energy
    
    def get_state(self) -> Dict:
        """Get current battery state."""
        return {
            "soc": round(self.soc, 4),
            "energy_wh": round(self.soc * self.capacity_wh, 2),
            "available_wh": round((self.soc - (1.0 - self.max_dod)) * self.capacity_wh, 2),
            "cycle_count": round(self.cycle_count, 2),
            "health": round(max(0.0, 1.0 - self.cycle_count / 2000.0), 4)  # Degrade after 2000 cycles
        }


class PowerManagementSystem:
    """
    Spacecraft power management system.
    
    Coordinates solar arrays, batteries, and loads.
    """
    
    def __init__(self, solar_array: SolarArray, battery: Battery,
                 loads: List[PowerLoad] = None):
        self.solar = solar_array
        self.battery = battery
        self.loads = loads or []
    
    def add_load(self, load: PowerLoad):
        """Add a power load."""
        self.loads.append(load)
    
    def total_load_power(self) -> float:
        """Calculate total power required by all loads."""
        return sum(load.power_w * load.duty_cycle for load in self.loads)
    
    def simulate_timestep(self, solar_distance_au: float,
                          sun_incidence_deg: float,
                          cell_temp_c: float,
                          dt_hours: float = 1.0) -> Dict:
        """
        Simulate one time step of power system operation.
        
        Returns:
            Dict with power balance and system status
        """
        # Solar generation
        solar_power = self.solar.power_output(solar_distance_au, sun_incidence_deg, cell_temp_c)
        
        # Load demand
        load_power = self.total_load_power()
        
        # Power balance
        net_power = solar_power - load_power
        
        if net_power >= 0:
            # Excess solar: charge battery
            battery_energy = net_power * dt_hours
            charged = self.battery.charge(battery_energy, dt_hours)
            battery_power = charged / dt_hours
            status = "CHARGING"
        else:
            # Deficit: discharge battery
            needed_energy = -net_power * dt_hours
            delivered = self.battery.discharge(needed_energy, dt_hours)
            battery_power = -delivered / dt_hours
            
            if delivered < needed_energy * 0.99:
                status = "POWER_SHORTAGE"
            else:
                status = "DISCHARGING"
        
        battery_state = self.battery.get_state()
        
        return {
            "solar_power_w": round(solar_power, 2),
            "load_power_w": round(load_power, 2),
            "net_power_w": round(net_power, 2),
            "battery_power_w": round(battery_power, 2),
            "battery_soc": battery_state["soc"],
            "status": status,
            "loads": {load.name: round(load.power_w * load.duty_cycle, 2) for load in self.loads}
        }
    
    def eclipse_analysis(self, eclipse_duration_hours: float,
                         solar_distance_au: float = 1.0) -> Dict:
        """
        Analyze power system during eclipse (no solar generation).
        
        Returns:
            Dict with eclipse survivability analysis
        """
        load_power = self.total_load_power()
        total_energy_needed = load_power * eclipse_duration_hours
        
        battery_state = self.battery.get_state()
        available_energy = battery_state["available_wh"]
        
        can_survive = available_energy >= total_energy_needed
        
        # Critical vs non-critical loads
        critical_load = sum(load.power_w * load.duty_cycle 
                           for load in self.loads if load.critical)
        non_critical_load = load_power - critical_load
        
        return {
            "eclipse_duration_h": eclipse_duration_hours,
            "total_load_w": round(load_power, 2),
            "critical_load_w": round(critical_load, 2),
            "non_critical_load_w": round(non_critical_load, 2),
            "energy_needed_wh": round(total_energy_needed, 2),
            "battery_available_wh": round(available_energy, 2),
            "can_survive": can_survive,
            "margin_wh": round(available_energy - total_energy_needed, 2),
            "recommendation": "SHED_NON_CRITICAL" if not can_survive else "NOMINAL"
        }
