"""
ISRU Plant Module
In-situ resource utilization plant simulation for autonomous
oxygen generation, fuel production, and material processing.
"""

import math
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ProcessStream:
    """A material stream in the ISRU plant."""
    name: str
    mass_flow_kg_s: float
    composition: Dict[str, float]  # compound -> mass fraction
    temperature_k: float = 300.0
    pressure_pa: float = 101325.0


@dataclass
class PowerRequirement:
    """Power requirement for a process."""
    process_name: str
    power_kw: float
    duty_cycle: float = 1.0  # fraction of time active


class WaterElectrolyzer:
    """
    Water electrolysis: 2 H2O -> 2 H2 + O2
    """
    
    # Reaction enthalpy at 298K: 285.8 kJ/mol
    ENERGY_PER_MOL_H2O = 285.8e3  # J/mol
    MOLAR_MASS_H2O = 18.015  # g/mol
    
    def __init__(self, efficiency: float = 0.7,
                 max_power_kw: float = 10.0):
        """
        Args:
            efficiency: Electrolysis efficiency
            max_power_kw: Maximum power
        """
        self.efficiency = efficiency
        self.max_power = max_power_kw
    
    def process(self, water_mass_kg: float) -> Dict:
        """
        Electrolyze water.
        
        Args:
            water_mass_kg: Water mass to process
        
        Returns:
            Products and energy used
        """
        moles = water_mass_kg * 1000.0 / self.MOLAR_MASS_H2O
        energy_j = moles * self.ENERGY_PER_MOL_H2O / self.efficiency
        energy_kwh = energy_j / 3.6e6
        
        # Stoichiometry: 2 H2O -> 2 H2 + O2
        h2_mass = water_mass_kg * 2.016 / 18.015
        o2_mass = water_mass_kg * 16.0 / 18.015
        
        return {
            "water_consumed_kg": round(water_mass_kg, 4),
            "h2_produced_kg": round(h2_mass, 4),
            "o2_produced_kg": round(o2_mass, 4),
            "energy_required_kwh": round(energy_kwh, 4),
            "power_kw": self.max_power,
            "process_time_hours": round(energy_kwh / self.max_power, 2)
        }
    
    def o2_production_rate(self, water_flow_kg_s: float) -> float:
        """
        Compute O2 production rate.
        
        Args:
            water_flow_kg_s: Water input rate
        
        Returns:
            O2 rate kg/s
        """
        return water_flow_kg_s * 32.0 / 18.015


class SabatierReactor:
    """
    Sabatier reaction: CO2 + 4 H2 -> CH4 + 2 H2O
    For methane/LOX fuel production.
    """
    
    # Reaction enthalpy
    ENERGY_PER_MOL = -165.0e3  # J/mol (exothermic)
    MOLAR_MASS_CO2 = 44.01
    MOLAR_MASS_H2 = 2.016
    MOLAR_MASS_CH4 = 16.04
    
    def __init__(self, efficiency: float = 0.8):
        self.efficiency = efficiency
    
    def process(self, co2_mass_kg: float, h2_mass_kg: float) -> Dict:
        """
        Run Sabatier reaction.
        
        Args:
            co2_mass_kg: CO2 available
            h2_mass_kg: H2 available
        
        Returns:
            Products
        """
        moles_co2 = co2_mass_kg * 1000.0 / self.MOLAR_MASS_CO2
        moles_h2 = h2_mass_kg * 1000.0 / self.MOLAR_MASS_H2
        
        # CO2 is limiting if moles_co2 < moles_h2/4
        limiting = "CO2" if moles_co2 < moles_h2 / 4.0 else "H2"
        
        if limiting == "CO2":
            moles_reacted = moles_co2 * self.efficiency
        else:
            moles_reacted = (moles_h2 / 4.0) * self.efficiency
        
        ch4_mass = moles_reacted * self.MOLAR_MASS_CH4 / 1000.0
        h2o_mass = moles_reacted * 2.0 * 18.015 / 1000.0
        co2_consumed = moles_reacted * self.MOLAR_MASS_CO2 / 1000.0
        h2_consumed = moles_reacted * 4.0 * self.MOLAR_MASS_H2 / 1000.0
        
        return {
            "limiting_reagent": limiting,
            "ch4_produced_kg": round(ch4_mass, 4),
            "h2o_produced_kg": round(h2o_mass, 4),
            "co2_consumed_kg": round(co2_consumed, 4),
            "h2_consumed_kg": round(h2_consumed, 4),
            "energy_released_kj": round(-moles_reacted * self.ENERGY_PER_MOL / 1000.0, 2)
        }


class ISRUPlant:
    """
    Integrated ISRU plant for autonomous resource processing.
    """
    
    def __init__(self,
                 electrolyzer: Optional[WaterElectrolyzer] = None,
                 sabatier: Optional[SabatierReactor] = None,
                 solar_power_kw: float = 50.0,
                 battery_capacity_kwh: float = 100.0):
        """
        Args:
            electrolyzer: Water electrolyzer
            sabatier: Sabatier reactor
            solar_power_kw: Available solar power
            battery_capacity_kwh: Battery capacity
        """
        self.electrolyzer = electrolyzer or WaterElectrolyzer()
        self.sabatier = sabatier or SabatierReactor()
        self.solar_power = solar_power_kw
        self.battery_capacity = battery_capacity_kwh
        self.battery_soc = 1.0  # State of charge
        
        self.total_o2_produced_kg = 0.0
        self.total_h2_produced_kg = 0.0
        self.total_ch4_produced_kg = 0.0
        self.total_water_consumed_kg = 0.0
    
    def daily_production(self, available_water_kg: float,
                         available_co2_kg: float,
                         daylight_hours: float = 12.0) -> Dict:
        """
        Simulate daily production cycle.
        
        Args:
            available_water_kg: Water available for processing
            available_co2_kg: CO2 available from atmosphere
            daylight_hours: Hours of daylight
        
        Returns:
            Daily production summary
        """
        # Power budget: solar during day, battery at night
        day_energy = self.solar_power * daylight_hours  # kWh
        night_energy = self.battery_capacity * self.battery_soc  # kWh
        total_energy = day_energy + night_energy
        
        # Electrolyze water
        elec_result = self.electrolyzer.process(available_water_kg)
        elec_energy = elec_result["energy_required_kwh"]
        
        if elec_energy > total_energy:
            # Limited by power
            fraction = total_energy / elec_energy
            water_used = available_water_kg * fraction
            elec_result = self.electrolyzer.process(water_used)
        
        self.total_water_consumed_kg += elec_result["water_consumed_kg"]
        self.total_o2_produced_kg += elec_result["o2_produced_kg"]
        self.total_h2_produced_kg += elec_result["h2_produced_kg"]
        
        # Sabatier: use H2 and atmospheric CO2
        sab_result = self.sabatier.process(
            available_co2_kg, elec_result["h2_produced_kg"]
        )
        
        self.total_ch4_produced_kg += sab_result["ch4_produced_kg"]
        
        # Update battery
        energy_used = elec_result["energy_required_kwh"]
        if energy_used < day_energy:
            # Charge battery with excess
            self.battery_soc = min(1.0, self.battery_soc + (day_energy - energy_used) / self.battery_capacity)
        else:
            # Discharge battery
            self.battery_soc = max(0.0, self.battery_soc - (energy_used - day_energy) / self.battery_capacity)
        
        return {
            "water_consumed_kg": elec_result["water_consumed_kg"],
            "o2_produced_kg": elec_result["o2_produced_kg"],
            "h2_produced_kg": elec_result["h2_produced_kg"],
            "ch4_produced_kg": sab_result["ch4_produced_kg"],
            "co2_consumed_kg": sab_result["co2_consumed_kg"],
            "energy_used_kwh": round(energy_used, 2),
            "energy_available_kwh": round(total_energy, 2),
            "battery_soc": round(self.battery_soc, 3)
        }
    
    def life_support_o2(self, crew_size: int = 4,
                        o2_rate_per_person_kg_day: float = 0.84) -> Dict:
        """
        Assess life support O2 sufficiency.
        
        Args:
            crew_size: Number of crew
            o2_rate_per_person_kg_day: O2 consumption per person
        
        Returns:
            Life support assessment
        """
        daily_need = crew_size * o2_rate_per_person_kg_day
        daily_production = self.electrolyzer.o2_production_rate(0.001) * 86400.0
        
        # Estimate from total production if no daily data
        if self.total_o2_produced_kg > 0:
            # Assume accumulated over some days
            days = max(1, int(self.total_water_consumed_kg / 10.0))
            daily_production = self.total_o2_produced_kg / days
        
        surplus = daily_production - daily_need
        
        return {
            "crew_size": crew_size,
            "daily_o2_need_kg": round(daily_need, 2),
            "daily_o2_production_kg": round(daily_production, 2),
            "daily_surplus_kg": round(surplus, 2),
            "self_sufficient": daily_production >= daily_need
        }
    
    def propellant_summary(self) -> Dict:
        """
        Get propellant production summary.
        
        CH4 + 2 O2 -> combustion for ascent/descent
        """
        # Stoichiometric O2 for CH4: 2 * 32 / 16.04 = 3.99 ~ 4.0
        o2_for_ch4 = self.total_ch4_produced_kg * 4.0
        excess_o2 = self.total_o2_produced_kg - o2_for_ch4
        
        return {
            "total_ch4_kg": round(self.total_ch4_produced_kg, 2),
            "total_o2_kg": round(self.total_o2_produced_kg, 2),
            "o2_for_ch4_combustion_kg": round(o2_for_ch4, 2),
            "excess_o2_kg": round(excess_o2, 2),
            "propellant_mix_ratio": round(o2_for_ch4 / self.total_ch4_produced_kg, 2) if self.total_ch4_produced_kg > 0 else 0.0
        }
    
    def plant_status(self) -> Dict:
        """Get overall plant status."""
        return {
            "total_water_consumed_kg": round(self.total_water_consumed_kg, 2),
            "total_o2_produced_kg": round(self.total_o2_produced_kg, 2),
            "total_h2_produced_kg": round(self.total_h2_produced_kg, 2),
            "total_ch4_produced_kg": round(self.total_ch4_produced_kg, 2),
            "battery_soc": round(self.battery_soc, 3),
            "solar_power_kw": self.solar_power,
            "battery_capacity_kwh": self.battery_capacity
        }
