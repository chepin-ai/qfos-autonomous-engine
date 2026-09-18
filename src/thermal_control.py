"""
Thermal Control Module
Spacecraft thermal balance and thermal control system analysis.
"""

import math
from typing import Dict, Tuple, List
from dataclasses import dataclass


# Stefan-Boltzmann constant
SIGMA = 5.670374419e-8  # W/m^2/K^4
# Solar constant at 1 AU
SOLAR_CONSTANT_1AU = 1361.0  # W/m^2


@dataclass
class ThermalZone:
    """A thermal zone on the spacecraft."""
    name: str
    area_m2: float
    absorptivity: float  # Alpha (0-1)
    emissivity: float    # Epsilon (0-1)
    internal_heat_w: float = 0.0
    min_temp_k: float = 233.0  # -40 C
    max_temp_k: float = 333.0  # +60 C


class ThermalControlSystem:
    """
    Analyze spacecraft thermal balance.
    
    Calculates equilibrium temperatures and heater/cooler requirements.
    """
    
    def __init__(self, solar_distance_au: float = 1.0):
        self.solar_distance_au = solar_distance_au
        self.solar_flux = SOLAR_CONSTANT_1AU / (solar_distance_au ** 2)
    
    def equilibrium_temperature(self, zone: ThermalZone, 
                                sun_facing: bool = True,
                                earth_facing: bool = False,
                                earth_ir_w_m2: float = 0.0) -> float:
        """
        Calculate equilibrium temperature of a thermal zone.
        
        Q_in = alpha * S * A_sun + epsilon * Q_IR_earth + Q_internal
        Q_out = epsilon * sigma * A * T^4
        At equilibrium: Q_in = Q_out
        
        Returns:
            Equilibrium temperature in Kelvin
        """
        # Solar heat input
        if sun_facing:
            q_solar = zone.absorptivity * self.solar_flux * zone.area_m2
        else:
            q_solar = 0.0
        
        # Earth IR input
        q_earth_ir = zone.emissivity * earth_ir_w_m2 * zone.area_m2
        
        # Internal heat
        q_internal = zone.internal_heat_w
        
        # Total heat input
        q_in = q_solar + q_earth_ir + q_internal
        
        # Radiative heat output at equilibrium
        # q_out = epsilon * sigma * A * T^4
        # T = (q_in / (epsilon * sigma * A))^(1/4)
        
        if zone.emissivity * zone.area_m2 < 1e-15:
            return 0.0
        
        T_eq = (q_in / (zone.emissivity * SIGMA * zone.area_m2)) ** 0.25
        return T_eq
    
    def thermal_balance(self, zones: List[ThermalZone],
                        sun_facing_areas: Dict[str, bool] = None) -> Dict:
        """
        Calculate thermal balance for all zones.
        
        Returns dict with temperatures and requirements.
        """
        results = {}
        total_heat_in = 0.0
        total_heat_out = 0.0
        
        for zone in zones:
            sun_facing = sun_facing_areas.get(zone.name, True) if sun_facing_areas else True
            T_eq = self.equilibrium_temperature(zone, sun_facing=sun_facing)
            
            # Calculate heat flows
            q_in = zone.absorptivity * self.solar_flux * zone.area_m2 * (1.0 if sun_facing else 0.0)
            q_in += zone.internal_heat_w
            q_out = zone.emissivity * SIGMA * zone.area_m2 * T_eq**4
            
            total_heat_in += q_in
            total_heat_out += q_out
            
            # Determine thermal control needs
            if T_eq < zone.min_temp_k:
                heater_power = zone.emissivity * SIGMA * zone.area_m2 * (zone.min_temp_k**4 - T_eq**4)
                cooler_power = 0.0
                status = "HEATING_REQUIRED"
            elif T_eq > zone.max_temp_k:
                heater_power = 0.0
                cooler_power = zone.emissivity * SIGMA * zone.area_m2 * (T_eq**4 - zone.max_temp_k**4)
                status = "COOLING_REQUIRED"
            else:
                heater_power = 0.0
                cooler_power = 0.0
                status = "NOMINAL"
            
            results[zone.name] = {
                "equilibrium_temp_k": round(T_eq, 2),
                "equilibrium_temp_c": round(T_eq - 273.15, 2),
                "heat_input_w": round(q_in, 2),
                "heat_output_w": round(q_out, 2),
                "heater_power_w": round(heater_power, 2),
                "cooler_power_w": round(cooler_power, 2),
                "status": status
            }
        
        results["_summary"] = {
            "total_heat_in_w": round(total_heat_in, 2),
            "total_heat_out_w": round(total_heat_out, 2),
            "solar_distance_au": self.solar_distance_au,
            "solar_flux_w_m2": round(self.solar_flux, 2)
        }
        
        return results
    
    def radiator_size_required(self, heat_to_dissipate_w: float,
                               emissivity: float = 0.85,
                               max_temp_c: float = 60.0) -> float:
        """
        Calculate required radiator area to dissipate given heat.
        
        Args:
            heat_to_dissipate_w: Heat to remove (W)
            emissivity: Radiator emissivity
            max_temp_c: Maximum radiator temperature (C)
        
        Returns:
            Required radiator area in m^2
        """
        T_k = max_temp_c + 273.15
        if emissivity * SIGMA * T_k**4 < 1e-15:
            return float('inf')
        area = heat_to_dissipate_w / (emissivity * SIGMA * T_k**4)
        return area
    
    def multilayer_insulation_performance(self, n_layers: int,
                                          hot_side_temp_k: float,
                                          cold_side_temp_k: float) -> float:
        """
        Estimate heat leak through multilayer insulation (MLI).
        
        Simplified model: heat leak decreases with layer count.
        
        Returns:
            Heat leak in W/m^2
        """
        # Typical MLI performance: ~1-10 W/m^2 for single layer, decreasing
        base_leak = 5.0  # W/m^2 for single layer
        # Each additional layer reduces leak by ~30%
        leak = base_leak * (0.7 ** (n_layers - 1))
        
        # Temperature gradient correction
        temp_ratio = (hot_side_temp_k - cold_side_temp_k) / 300.0
        leak *= max(0.1, temp_ratio)
        
        return leak
    
    def solar_array_temperature(self, solar_absorptivity: float = 0.85,
                                solar_emissivity: float = 0.85,
                                cell_efficiency: float = 0.28) -> float:
        """
        Calculate equilibrium temperature of solar array.
        
        Solar arrays absorb solar flux and convert some to electricity.
        The rest must be radiated.
        
        Returns:
            Equilibrium temperature in Kelvin
        """
        # Absorbed solar flux minus converted electricity
        absorbed = solar_absorptivity * self.solar_flux
        converted = cell_efficiency * self.solar_flux
        heat_to_radiate = absorbed - converted
        
        # Both sides radiate (front and back)
        T_eq = (heat_to_radiate / (2.0 * solar_emissivity * SIGMA)) ** 0.25
        return T_eq
