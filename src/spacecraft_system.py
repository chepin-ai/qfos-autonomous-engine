"""
Spacecraft System Module
System-level spacecraft simulator integrating all subsystems.
Provides unified state management and mission timeline execution.
"""

import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class MissionPhase(Enum):
    """Mission phase enumeration."""
    LAUNCH = "launch"
    TRANSFER = "transfer"
    CRUISE = "cruise"
    APPROACH = "approach"
    ORBIT_INSERTION = "orbit_insertion"
    NOMINAL_OPS = "nominal_operations"
    SCIENCE = "science"
    COMMUNICATION = "communication"
    SAFE_MODE = "safe_mode"
    END_OF_LIFE = "end_of_life"


@dataclass
class SpacecraftState:
    """Complete spacecraft state vector."""
    # Position and velocity (km, km/s)
    position_km: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    velocity_km_s: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # Attitude (quaternion)
    attitude_q: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)
    angular_rate_rad_s: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # Power
    battery_soc: float = 1.0  # State of charge
    solar_power_w: float = 0.0
    power_consumption_w: float = 0.0
    
    # Thermal
    temperature_c: float = 20.0
    
    # Propulsion
    propellant_mass_kg: float = 100.0
    total_mass_kg: float = 500.0
    
    # Communication
    data_storage_mb: float = 0.0
    comm_link_active: bool = False
    
    # Mission
    phase: MissionPhase = MissionPhase.LAUNCH
    elapsed_time_s: float = 0.0
    mission_day: int = 0
    
    # Health
    subsystem_health: Dict[str, float] = field(default_factory=lambda: {
        "gnc": 1.0, "propulsion": 1.0, "power": 1.0,
        "thermal": 1.0, "comm": 1.0, "payload": 1.0
    })
    fault_flags: List[str] = field(default_factory=list)


class SpacecraftSimulator:
    """
    System-level spacecraft simulator.
    
    Integrates orbital dynamics, power, thermal, and communication
    subsystems into unified mission simulation.
    """
    
    MU_EARTH = 398600.4418  # km^3/s^2
    
    def __init__(self, initial_state: Optional[SpacecraftState] = None):
        self.state = initial_state or SpacecraftState()
        self.history: List[SpacecraftState] = [self.state]
        self.events: List[Dict] = []
    
    def propagate_orbit(self, dt_s: float) -> None:
        """Propagate spacecraft orbit using two-body dynamics."""
        x, y, z = self.state.position_km
        vx, vy, vz = self.state.velocity_km_s
        
        r = math.sqrt(x**2 + y**2 + z**2)
        if r < 1e-6:
            r = 1e-6
        
        # Acceleration
        a = -self.MU_EARTH / r**3
        ax = a * x
        ay = a * y
        az = a * z
        
        # Simple Euler integration
        dt = dt_s
        self.state.position_km = (
            x + vx * dt + 0.5 * ax * dt**2,
            y + vy * dt + 0.5 * ay * dt**2,
            z + vz * dt + 0.5 * az * dt**2
        )
        self.state.velocity_km_s = (
            vx + ax * dt,
            vy + ay * dt,
            vz + az * dt
        )
    
    def update_power(self, dt_s: float, solar_distance_au: float = 1.0,
                     solar_incidence_deg: float = 0.0,
                     eclipse: bool = False) -> None:
        """Update power subsystem state."""
        if eclipse:
            self.state.solar_power_w = 0.0
        else:
            # Solar power ~ 1/r^2 * cos(incidence)
            base_power = 1000.0  # W at 1 AU
            self.state.solar_power_w = base_power / (solar_distance_au**2) * \
                                       math.cos(math.radians(solar_incidence_deg))
        
        # Battery dynamics
        net_power = self.state.solar_power_w - self.state.power_consumption_w
        battery_capacity_wh = 1000.0  # 1 kWh
        
        if net_power > 0:
            # Charging
            self.state.battery_soc = min(1.0, self.state.battery_soc +
                                          net_power * dt_s / 3600.0 / battery_capacity_wh)
        else:
            # Discharging
            self.state.battery_soc = max(0.0, self.state.battery_soc +
                                          net_power * dt_s / 3600.0 / battery_capacity_wh)
    
    def update_thermal(self, dt_s: float,
                       solar_flux_w_m2: float = 1361.0,
                       albedo: float = 0.3,
                       emissivity: float = 0.85,
                       absorptivity: float = 0.25,
                       area_m2: float = 2.0) -> None:
        """Update thermal subsystem state."""
        # Simplified thermal balance
        # Q_in = absorptivity * solar_flux * area
        # Q_out = emissivity * sigma * T^4 * area
        # dT/dt = (Q_in - Q_out) / (mass * cp)
        
        sigma = 5.67e-8  # Stefan-Boltzmann W/m^2/K^4
        cp = 800.0  # J/kg/K (aluminum-ish)
        
        Q_in = absorptivity * solar_flux_w_m2 * area_m2
        T_k = self.state.temperature_c + 273.15
        Q_out = emissivity * sigma * T_k**4 * area_m2
        
        dT_dt = (Q_in - Q_out) / (self.state.total_mass_kg * cp)
        self.state.temperature_c += dT_dt * dt_s
    
    def execute_maneuver(self, delta_v_ms: Tuple[float, float, float],
                         isp_s: float = 300.0) -> None:
        """
        Execute propulsive maneuver.
        
        Args:
            delta_v_ms: Delta-v vector in m/s
            isp_s: Specific impulse in seconds
        """
        dv = math.sqrt(sum(v**2 for v in delta_v_ms))
        
        # Tsiolkovsky: m_final = m_initial * exp(-dv / (g0 * isp))
        g0 = 9.80665
        m_initial = self.state.total_mass_kg
        m_final = m_initial * math.exp(-dv / (g0 * isp_s))
        
        prop_used = m_initial - m_final
        
        if prop_used > self.state.propellant_mass_kg:
            raise ValueError("Insufficient propellant for maneuver")
        
        self.state.propellant_mass_kg -= prop_used
        self.state.total_mass_kg = m_final
        
        # Update velocity (simplified: instant burn)
        self.state.velocity_km_s = (
            self.state.velocity_km_s[0] + delta_v_ms[0] / 1000.0,
            self.state.velocity_km_s[1] + delta_v_ms[1] / 1000.0,
            self.state.velocity_km_s[2] + delta_v_ms[2] / 1000.0
        )
        
        self.events.append({
            "time_s": self.state.elapsed_time_s,
            "type": "maneuver",
            "delta_v_ms": round(dv, 3),
            "propellant_used_kg": round(prop_used, 4)
        })
    
    def collect_science_data(self, data_mb: float) -> None:
        """Collect science data."""
        self.state.data_storage_mb += data_mb
        self.events.append({
            "time_s": self.state.elapsed_time_s,
            "type": "science",
            "data_mb": round(data_mb, 2)
        })
    
    def downlink_data(self, rate_mbps: float, duration_s: float) -> float:
        """
        Downlink stored data.
        
        Returns:
            Amount of data downlinked in MB
        """
        data_downlinked = rate_mbps * duration_s / 8.0
        actual = min(data_downlinked, self.state.data_storage_mb)
        self.state.data_storage_mb -= actual
        
        self.state.comm_link_active = True
        self.events.append({
            "time_s": self.state.elapsed_time_s,
            "type": "downlink",
            "data_mb": round(actual, 2)
        })
        
        return actual
    
    def check_health(self) -> Dict[str, Any]:
        """Check spacecraft health status."""
        health = {
            "overall": "nominal",
            "subsystems": {},
            "warnings": []
        }
        
        # Battery check
        if self.state.battery_soc < 0.2:
            health["warnings"].append("Low battery")
            health["overall"] = "warning"
        
        # Thermal check
        if self.state.temperature_c > 60.0 or self.state.temperature_c < -40.0:
            health["warnings"].append("Thermal out of limits")
            health["overall"] = "critical"
        
        # Propellant check
        if self.state.propellant_mass_kg < 10.0:
            health["warnings"].append("Low propellant")
        
        # Data storage check
        if self.state.data_storage_mb > 10000.0:
            health["warnings"].append("Data storage nearly full")
        
        health["subsystems"] = {
            "power": {"soc": round(self.state.battery_soc, 3),
                     "solar_w": round(self.state.solar_power_w, 1)},
            "thermal": {"temp_c": round(self.state.temperature_c, 2)},
            "propulsion": {"prop_kg": round(self.state.propellant_mass_kg, 2),
                          "mass_kg": round(self.state.total_mass_kg, 2)},
            "comm": {"storage_mb": round(self.state.data_storage_mb, 2),
                    "link_active": self.state.comm_link_active}
        }
        
        return health
    
    def simulate_timestep(self, dt_s: float = 60.0,
                          solar_distance_au: float = 1.0,
                          eclipse: bool = False) -> None:
        """
        Execute one simulation timestep.
        
        Integrates orbit, power, and thermal subsystems.
        """
        # Propagate orbit
        self.propagate_orbit(dt_s)
        
        # Update power
        self.update_power(dt_s, solar_distance_au=solar_distance_au, eclipse=eclipse)
        
        # Update thermal
        solar_flux = 1361.0 / (solar_distance_au**2)
        self.update_thermal(dt_s, solar_flux_w_m2=solar_flux)
        
        # Update mission time
        self.state.elapsed_time_s += dt_s
        if int(self.state.elapsed_time_s / 86400.0) > self.state.mission_day:
            self.state.mission_day = int(self.state.elapsed_time_s / 86400.0)
        
        # Store history (only every 10 steps to save memory)
        if len(self.history) % 10 == 0:
            self.history.append(SpacecraftState(
                position_km=self.state.position_km,
                velocity_km_s=self.state.velocity_km_s,
                battery_soc=self.state.battery_soc,
                solar_power_w=self.state.solar_power_w,
                temperature_c=self.state.temperature_c,
                propellant_mass_kg=self.state.propellant_mass_kg,
                total_mass_kg=self.state.total_mass_kg,
                data_storage_mb=self.state.data_storage_mb,
                elapsed_time_s=self.state.elapsed_time_s,
                mission_day=self.state.mission_day
            ))
    
    def get_summary(self) -> Dict:
        """Get mission summary."""
        return {
            "mission_day": self.state.mission_day,
            "elapsed_time_s": round(self.state.elapsed_time_s, 1),
            "current_phase": self.state.phase.value,
            "position_km": tuple(round(v, 2) for v in self.state.position_km),
            "velocity_km_s": tuple(round(v, 4) for v in self.state.velocity_km_s),
            "mass_kg": round(self.state.total_mass_kg, 2),
            "propellant_kg": round(self.state.propellant_mass_kg, 2),
            "battery_soc": round(self.state.battery_soc, 3),
            "temperature_c": round(self.state.temperature_c, 2),
            "data_storage_mb": round(self.state.data_storage_mb, 2),
            "event_count": len(self.events),
            "health": self.check_health()["overall"]
        }
