"""
Thermal Management Module
Heat pipe, radiator, fluid loop, and cryocooler control
for autonomous system thermal regulation.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ThermalZone(Enum):
    """Thermal management zone."""
    ELECTRONICS = "electronics"
    PROPULSION = "propulsion"
    BATTERY = "battery"
    PAYLOAD = "payload"
    ENVIRONMENT = "environment"


class CoolingMode(Enum):
    """Active cooling mode."""
    PASSIVE = "passive"
    RADIATOR = "radiator"
    FLUID_LOOP = "fluid_loop"
    CRYOCOOLER = "cryocooler"
    EMERGENCY = "emergency"


@dataclass
class TemperatureReading:
    """Temperature sensor reading."""
    zone: ThermalZone
    temperature_K: float
    timestamp: float = 0.0


class HeatPipe:
    """
    Heat pipe thermal transfer device.
    """
    
    def __init__(self, max_power_W: float = 500.0,
                 thermal_resistance_K_W: float = 0.1,
                 working_fluid: str = "ammonia"):
        """
        Args:
            max_power_W: Maximum heat transfer capacity
            thermal_resistance_K_W: Thermal resistance
            working_fluid: Working fluid type
        """
        self.max_power = max_power_W
        self.thermal_resistance = thermal_resistance_K_W
        self.working_fluid = working_fluid
        self.active = False
    
    def transfer_rate(self, delta_T_K: float) -> float:
        """
        Compute heat transfer rate.
        
        Args:
            delta_T_K: Temperature difference
        
        Returns:
            Heat transfer rate (W)
        """
        if not self.active:
            return 0.0
        
        rate = delta_T_K / self.thermal_resistance
        return min(rate, self.max_power)
    
    def efficiency(self, delta_T_K: float) -> float:
        """
        Compute transfer efficiency.
        
        Args:
            delta_T_K: Temperature difference
        
        Returns:
            Efficiency (0-1)
        """
        if delta_T_K <= 0:
            return 0.0
        
        rate = self.transfer_rate(delta_T_K)
        # Efficiency decreases near capacity
        return min(1.0, rate / self.max_power) if self.max_power > 0 else 0.0
    
    def activate(self):
        """Activate heat pipe."""
        self.active = True
    
    def deactivate(self):
        """Deactivate heat pipe."""
        self.active = False


class Radiator:
    """
    Radiator heat rejection system.
    """
    
    def __init__(self, area_m2: float = 10.0,
                 emissivity: float = 0.9,
                 view_factor: float = 1.0):
        """
        Args:
            area_m2: Radiator surface area
            emissivity: Surface emissivity
            view_factor: View factor to deep space
        """
        self.area = area_m2
        self.emissivity = emissivity
        self.view_factor = view_factor
        self.active = False
        # Stefan-Boltzmann constant
        self.sigma = 5.670374419e-8  # W/m^2/K^4
    
    def heat_rejection(self, surface_temp_K: float,
                      ambient_temp_K: float = 3.0) -> float:
        """
        Compute radiated heat.
        
        Args:
            surface_temp_K: Radiator surface temperature
            ambient_temp_K: Ambient temperature (deep space ~3K)
        
        Returns:
            Heat rejection rate (W)
        """
        if not self.active:
            return 0.0
        
        temp_diff_4 = surface_temp_K**4 - ambient_temp_K**4
        if temp_diff_4 <= 0:
            return 0.0
        
        return self.emissivity * self.view_factor * self.area * self.sigma * temp_diff_4
    
    def required_area(self, heat_load_W: float, temp_K: float) -> float:
        """
        Compute required area for heat load.
        
        Args:
            heat_load_W: Heat to reject
            temp_K: Operating temperature
        
        Returns:
            Required area (m^2)
        """
        temp_diff_4 = temp_K**4 - 3.0**4
        if temp_diff_4 <= 0:
            return float('inf')
        
        denominator = self.emissivity * self.view_factor * self.sigma * temp_diff_4
        return heat_load_W / denominator
    
    def activate(self):
        """Activate radiator."""
        self.active = True
    
    def deactivate(self):
        """Deactivate radiator."""
        self.active = False


class FluidLoop:
    """
    Active fluid cooling loop.
    """
    
    def __init__(self, flow_rate_kg_s: float = 0.1,
                 specific_heat_J_kgK: float = 3900.0,
                 pump_efficiency: float = 0.7):
        """
        Args:
            flow_rate_kg_s: Coolant mass flow rate
            specific_heat_J_kgK: Coolant specific heat
            pump_efficiency: Pump efficiency
        """
        self.flow_rate = flow_rate_kg_s
        self.specific_heat = specific_heat_J_kgK
        self.pump_efficiency = pump_efficiency
        self.active = False
        self.inlet_temp_K = 280.0
        self.outlet_temp_K = 300.0
    
    def cooling_capacity(self) -> float:
        """
        Compute cooling capacity.
        
        Returns:
            Cooling power (W)
        """
        if not self.active:
            return 0.0
        
        delta_T = self.outlet_temp_K - self.inlet_temp_K
        return self.flow_rate * self.specific_heat * delta_T
    
    def set_temperatures(self, inlet_K: float, outlet_K: float):
        """
        Set loop temperatures.
        
        Args:
            inlet_K: Inlet temperature
            outlet_K: Outlet temperature
        """
        self.inlet_temp_K = inlet_K
        self.outlet_temp_K = outlet_K
    
    def pump_power(self) -> float:
        """
        Compute pump power consumption.
        
        Returns:
            Power (W)
        """
        if not self.active:
            return 0.0
        
        # Simplified: proportional to flow rate and temperature lift
        base_power = 50.0  # W baseline
        return base_power / self.pump_efficiency
    
    def activate(self):
        """Activate fluid loop."""
        self.active = True
    
    def deactivate(self):
        """Deactivate fluid loop."""
        self.active = False


class Cryocooler:
    """
    Cryogenic cooler for low-temperature components.
    """
    
    def __init__(self, cooling_power_W: float = 1.0,
                 min_temp_K: float = 4.0,
                 carnot_efficiency: float = 0.2):
        """
        Args:
            cooling_power_W: Maximum cooling power
            min_temp_K: Minimum achievable temperature
            carnot_efficiency: Fraction of Carnot efficiency
        """
        self.cooling_power = cooling_power_W
        self.min_temp = min_temp_K
        self.carnot_efficiency = carnot_efficiency
        self.active = False
        self.target_temp_K = 80.0
    
    def required_input_power(self, cold_temp_K: float,
                            hot_temp_K: float = 300.0) -> float:
        """
        Compute required input power.
        
        Args:
            cold_temp_K: Cold side temperature
            hot_temp_K: Hot side temperature
        
        Returns:
            Input power (W)
        """
        if cold_temp_K >= hot_temp_K or cold_temp_K <= 0:
            return float('inf')
        
        # Carnot COP = T_cold / (T_hot - T_cold)
        carnot_cop = cold_temp_K / (hot_temp_K - cold_temp_K)
        actual_cop = carnot_cop * self.carnot_efficiency
        
        if actual_cop <= 0:
            return float('inf')
        
        return self.cooling_power / actual_cop
    
    def achievable_temp(self, heat_load_W: float,
                       hot_temp_K: float = 300.0) -> float:
        """
        Compute achievable temperature.
        
        Args:
            heat_load_W: Heat load
            hot_temp_K: Hot side temperature
        
        Returns:
            Achievable temperature (K)
        """
        if heat_load_W >= self.cooling_power:
            return self.min_temp
        
        # Simplified: temperature rises with load
        load_fraction = heat_load_W / self.cooling_power
        return self.min_temp + (self.target_temp_K - self.min_temp) * load_fraction
    
    def activate(self):
        """Activate cryocooler."""
        self.active = True
    
    def deactivate(self):
        """Deactivate cryocooler."""
        self.active = False


class ThermalManagement:
    """
    Unified thermal management controller.
    """
    
    def __init__(self):
        self.heat_pipe = HeatPipe()
        self.radiator = Radiator()
        self.fluid_loop = FluidLoop()
        self.cryocooler = Cryocooler()
        self.readings: List[TemperatureReading] = []
        self.temperature_limits: Dict[ThermalZone, Tuple[float, float]] = {}
        # (min_K, max_K)
    
    def set_temperature_limits(self, zone: ThermalZone,
                               min_K: float, max_K: float):
        """Set temperature limits for zone."""
        self.temperature_limits[zone] = (min_K, max_K)
    
    def add_reading(self, reading: TemperatureReading):
        """Add temperature reading."""
        self.readings.append(reading)
    
    def get_zone_temperature(self, zone: ThermalZone) -> Optional[float]:
        """Get latest temperature for zone."""
        zone_readings = [r for r in self.readings if r.zone == zone]
        if not zone_readings:
            return None
        return zone_readings[-1].temperature_K
    
    def check_zone_health(self, zone: ThermalZone) -> Tuple[bool, float]:
        """
        Check if zone temperature is within limits.
        
        Args:
            zone: Thermal zone
        
        Returns:
            (healthy, margin_fraction)
        """
        temp = self.get_zone_temperature(zone)
        if temp is None:
            return False, 0.0
        
        limits = self.temperature_limits.get(zone)
        if not limits:
            return True, 1.0
        
        min_K, max_K = limits
        if temp < min_K or temp > max_K:
            return False, 0.0
        
        # Margin as fraction of range
        margin = min(temp - min_K, max_K - temp) / (max_K - min_K)
        return True, margin
    
    def select_cooling_mode(self, zone: ThermalZone,
                           heat_load_W: float) -> CoolingMode:
        """
        Select appropriate cooling mode.
        
        Args:
            zone: Thermal zone
            heat_load_W: Heat load
        
        Returns:
            Recommended cooling mode
        """
        temp = self.get_zone_temperature(zone)
        if temp is None:
            return CoolingMode.PASSIVE
        
        limits = self.temperature_limits.get(zone, (250, 350))
        max_temp = limits[1]
        
        temp_fraction = temp / max_temp
        
        if temp_fraction > 0.95:
            return CoolingMode.EMERGENCY
        elif temp_fraction > 0.85:
            return CoolingMode.CRYOCOOLER if zone == ThermalZone.PAYLOAD else CoolingMode.FLUID_LOOP
        elif temp_fraction > 0.75:
            return CoolingMode.FLUID_LOOP
        elif temp_fraction > 0.6:
            return CoolingMode.RADIATOR
        else:
            return CoolingMode.PASSIVE
    
    def activate_cooling(self, mode: CoolingMode):
        """Activate cooling system for mode."""
        if mode == CoolingMode.RADIATOR:
            self.radiator.activate()
        elif mode == CoolingMode.FLUID_LOOP:
            self.fluid_loop.activate()
        elif mode == CoolingMode.CRYOCOOLER:
            self.cryocooler.activate()
        elif mode == CoolingMode.EMERGENCY:
            self.radiator.activate()
            self.fluid_loop.activate()
    
    def deactivate_all(self):
        """Deactivate all cooling systems."""
        self.heat_pipe.deactivate()
        self.radiator.deactivate()
        self.fluid_loop.deactivate()
        self.cryocooler.deactivate()
    
    def total_heat_rejection(self, surface_temp_K: float) -> float:
        """
        Compute total heat rejection capacity.
        
        Args:
            surface_temp_K: Radiator surface temperature
        
        Returns:
            Total rejection (W)
        """
        return self.radiator.heat_rejection(surface_temp_K)
    
    def thermal_summary(self) -> Dict:
        """Get thermal management summary."""
        return {
            "readings": len(self.readings),
            "zones_monitored": len(self.temperature_limits),
            "cooling_systems": {
                "heat_pipe": self.heat_pipe.active,
                "radiator": self.radiator.active,
                "fluid_loop": self.fluid_loop.active,
                "cryocooler": self.cryocooler.active
            },
            "radiator_rejection_W": self.radiator.heat_rejection(350.0),
            "fluid_loop_capacity_W": self.fluid_loop.cooling_capacity()
        }
