"""
Propulsion System Module
Comprehensive propulsion modeling: chemical (biprop, monoprop, solid),
electric (ion, Hall effect), and propellant management.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class EngineType(Enum):
    """Types of rocket engines."""
    BIPROPELLANT = "bipropellant"
    MONOPROPELLANT = "monopropellant"
    COLD_GAS = "cold_gas"
    SOLID = "solid"
    ION = "ion"
    HALL_EFFECT = "hall_effect"


@dataclass
class Engine:
    """Rocket engine specification."""
    name: str
    engine_type: EngineType
    thrust_n: float
    isp_seconds: float
    mass_kg: float
    min_throttle_percent: float = 0.0  # 0 for on/off
    max_throttle_percent: float = 100.0
    duty_cycle: float = 1.0
    
    def exhaust_velocity_ms(self) -> float:
        """Compute exhaust velocity."""
        g0 = 9.80665
        return self.isp_seconds * g0
    
    def mass_flow_rate_kg_s(self) -> float:
        """Propellant mass flow rate."""
        if self.exhaust_velocity_ms() > 0:
            return self.thrust_n / self.exhaust_velocity_ms()
        return 0.0
    
    def thrust_at_throttle(self, throttle_percent: float) -> float:
        """Thrust at given throttle."""
        t = max(self.min_throttle_percent, min(throttle_percent, self.max_throttle_percent))
        return self.thrust_n * (t / 100.0)


class PropulsionSystem:
    """
    Spacecraft propulsion system manager.
    
    Supports multiple engine types, propellant budgeting,
    and burn planning.
    """
    
    def __init__(self, dry_mass_kg: float = 1000.0):
        """
        Args:
            dry_mass_kg: Spacecraft dry mass
        """
        self.dry_mass_kg = dry_mass_kg
        self.engines: List[Engine] = []
        self.propellant_mass_kg = 0.0
        self.pressurant_mass_kg = 0.0
        self.total_burn_time_s = 0.0
    
    def add_engine(self, engine: Engine):
        """Add an engine."""
        self.engines.append(engine)
    
    def add_propellant(self, mass_kg: float):
        """Add propellant mass."""
        self.propellant_mass_kg += mass_kg
    
    def total_mass_kg(self) -> float:
        """Current total mass."""
        return self.dry_mass_kg + self.propellant_mass_kg + self.pressurant_mass_kg
    
    def total_thrust_n(self, throttle_percent: float = 100.0) -> float:
        """Total available thrust."""
        return sum(e.thrust_at_throttle(throttle_percent) for e in self.engines)
    
    def total_mass_flow_kg_s(self, throttle_percent: float = 100.0) -> float:
        """Total propellant consumption."""
        total = 0.0
        for e in self.engines:
            t = max(e.min_throttle_percent, min(throttle_percent, e.max_throttle_percent))
            total += e.mass_flow_rate_kg_s() * (t / 100.0) * e.duty_cycle
        return total
    
    def burn_duration_s(self, delta_v_ms: float,
                        throttle_percent: float = 100.0) -> float:
        """
        Compute burn duration for delta-V.
        
        Args:
            delta_v_ms: Required delta-V
            throttle_percent: Throttle setting
        
        Returns:
            Burn duration in seconds
        """
        thrust = self.total_thrust_n(throttle_percent)
        if thrust <= 0.0:
            return float('inf')
        
        # Approximate: use average mass
        m_avg = self.total_mass_kg()
        acceleration = thrust / m_avg
        
        return delta_v_ms / acceleration
    
    def propellant_for_burn_kg(self, delta_v_ms: float) -> float:
        """
        Compute propellant needed for delta-V.
        
        Uses Tsiolkovsky: m_prop = m0 * (1 - exp(-dV / (g0*Isp)))
        Uses average Isp weighted by thrust.
        """
        if not self.engines:
            return 0.0
        
        # Weighted average Isp
        total_thrust = sum(e.thrust_n for e in self.engines)
        if total_thrust <= 0.0:
            return 0.0
        
        avg_isp = sum(e.thrust_n * e.isp_seconds for e in self.engines) / total_thrust
        
        g0 = 9.80665
        m0 = self.total_mass_kg()
        mass_ratio = math.exp(-delta_v_ms / (g0 * avg_isp))
        m_final = m0 * mass_ratio
        
        return m0 - m_final
    
    def can_perform_burn(self, delta_v_ms: float) -> bool:
        """Check if enough propellant for burn."""
        return self.propellant_for_burn_kg(delta_v_ms) <= self.propellant_mass_kg * 0.99
    
    def execute_burn(self, delta_v_ms: float,
                     throttle_percent: float = 100.0) -> Dict:
        """
        Simulate a burn.
        
        Args:
            delta_v_ms: Delta-V to achieve
            throttle_percent: Throttle setting
        
        Returns:
            Burn result
        """
        prop_used = self.propellant_for_burn_kg(delta_v_ms)
        duration = self.burn_duration_s(delta_v_ms, throttle_percent)
        
        if prop_used > self.propellant_mass_kg:
            return {
                "success": False,
                "reason": "Insufficient propellant",
                "required_kg": round(prop_used, 3),
                "available_kg": round(self.propellant_mass_kg, 3)
            }
        
        self.propellant_mass_kg -= prop_used
        self.total_burn_time_s += duration
        
        return {
            "success": True,
            "delta_v_ms": round(delta_v_ms, 3),
            "propellant_used_kg": round(prop_used, 3),
            "burn_duration_s": round(duration, 3),
            "final_mass_kg": round(self.total_mass_kg(), 3),
            "remaining_propellant_kg": round(self.propellant_mass_kg, 3)
        }
    
    def system_summary(self) -> Dict:
        """Get propulsion system summary."""
        return {
            "num_engines": len(self.engines),
            "engines": [
                {
                    "name": e.name,
                    "type": e.engine_type.value,
                    "thrust_n": e.thrust_n,
                    "isp_s": e.isp_seconds,
                    "mass_kg": e.mass_kg
                }
                for e in self.engines
            ],
            "total_thrust_n": round(self.total_thrust_n(), 3),
            "dry_mass_kg": self.dry_mass_kg,
            "propellant_mass_kg": round(self.propellant_mass_kg, 3),
            "total_mass_kg": round(self.total_mass_kg(), 3),
            "total_burn_time_s": round(self.total_burn_time_s, 3),
            "propellant_fraction": round(
                self.propellant_mass_kg / self.total_mass_kg(), 4
            ) if self.total_mass_kg() > 0 else 0.0
        }
    
    @staticmethod
    def create_chemical_system(dry_mass_kg: float = 1000.0,
                                propellant_kg: float = 500.0) -> 'PropulsionSystem':
        """Create a chemical propulsion system."""
        sys = PropulsionSystem(dry_mass_kg=dry_mass_kg)
        sys.add_engine(Engine(
            name="Main Engine",
            engine_type=EngineType.BIPROPELLANT,
            thrust_n=490.0,
            isp_seconds=320.0,
            mass_kg=15.0
        ))
        sys.add_engine(Engine(
            name="RCS Thruster",
            engine_type=EngineType.MONOPROPELLANT,
            thrust_n=22.0,
            isp_seconds=220.0,
            mass_kg=2.0
        ))
        sys.add_propellant(propellant_kg)
        return sys
    
    @staticmethod
    def create_electric_system(dry_mass_kg: float = 500.0,
                                propellant_kg: float = 50.0) -> 'PropulsionSystem':
        """Create an electric propulsion system."""
        sys = PropulsionSystem(dry_mass_kg=dry_mass_kg)
        sys.add_engine(Engine(
            name="Ion Thruster",
            engine_type=EngineType.ION,
            thrust_n=0.250,
            isp_seconds=3500.0,
            mass_kg=8.0
        ))
        sys.add_propellant(propellant_kg)
        return sys
    
    @staticmethod
    def create_hybrid_system(dry_mass_kg: float = 1500.0,
                              chemical_prop_kg: float = 800.0,
                              electric_prop_kg: float = 100.0) -> 'PropulsionSystem':
        """Create a hybrid chemical + electric system."""
        sys = PropulsionSystem(dry_mass_kg=dry_mass_kg)
        sys.add_engine(Engine(
            name="Main Engine",
            engine_type=EngineType.BIPROPELLANT,
            thrust_n=490.0,
            isp_seconds=320.0,
            mass_kg=15.0
        ))
        sys.add_engine(Engine(
            name="Ion Thruster",
            engine_type=EngineType.ION,
            thrust_n=0.250,
            isp_seconds=3500.0,
            mass_kg=8.0
        ))
        sys.add_propellant(chemical_prop_kg + electric_prop_kg)
        return sys
