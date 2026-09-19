"""
Entry, Descent, and Landing (EDL) Trajectory Module
Plan and simulate atmospheric entry trajectories for planetary landers.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# Planet atmosphere models (simplified exponential)
ATMOSPHERE_MODELS = {
    "Earth": {
        "surface_gravity": 9.81,       # m/s^2
        "scale_height_m": 8500.0,      # m
        "surface_density_kg_m3": 1.225,
        "radius_m": 6.371e6,
        "min_altitude_m": 0.0,
    },
    "Mars": {
        "surface_gravity": 3.72,
        "scale_height_m": 11100.0,
        "surface_density_kg_m3": 0.020,
        "radius_m": 3.389e6,
        "min_altitude_m": 0.0,
    },
    "Venus": {
        "surface_gravity": 8.87,
        "scale_height_m": 15900.0,
        "surface_density_kg_m3": 65.0,
        "radius_m": 6.051e6,
        "min_altitude_m": 0.0,
    },
    "Titan": {
        "surface_gravity": 1.35,
        "scale_height_m": 21000.0,
        "surface_density_kg_m3": 5.3,
        "radius_m": 2.575e6,
        "min_altitude_m": 0.0,
    },
}


@dataclass
class EntryState:
    """State vector during atmospheric entry."""
    altitude_m: float
    velocity_ms: float
    flight_path_angle_deg: float
    range_to_go_m: float
    time_s: float
    deceleration_g: float = 0.0
    heating_rate_w_cm2: float = 0.0
    dynamic_pressure_pa: float = 0.0


class EntryTrajectoryPlanner:
    """
    Plan ballistic and lifting atmospheric entry trajectories.
    
    Supports drag-only (ballistic) and bank-angle-controlled (lifting) entries.
    """
    
    def __init__(self, planet: str = "Mars", ballistic_coefficient_kg_m2: float = 150.0,
                 lift_drag_ratio: float = 0.0):
        """
        Args:
            planet: Target planet name
            ballistic_coefficient_kg_m2: m/(Cd*A) in kg/m^2
            lift_drag_ratio: L/D ratio (0 for ballistic entry)
        """
        self.planet = planet
        self.atm = ATMOSPHERE_MODELS.get(planet, ATMOSPHERE_MODELS["Mars"])
        self.beta = ballistic_coefficient_kg_m2
        self.ld_ratio = lift_drag_ratio
    
    def atmospheric_density(self, altitude_m: float) -> float:
        """Exponential atmosphere model."""
        h = max(0.0, altitude_m)
        return self.atm["surface_density_kg_m3"] * math.exp(-h / self.atm["scale_height_m"])
    
    def _derivatives(self, state: EntryState) -> Tuple[float, float, float]:
        """
        Compute state derivatives (altitude rate, velocity rate, fpa rate).
        
        Returns:
            (dh/dt, dv/dt, dgamma/dt)
        """
        h = state.altitude_m
        v = state.velocity_ms
        gamma = math.radians(state.flight_path_angle_deg)
        
        rho = self.atmospheric_density(h)
        g = self.atm["surface_gravity"]
        
        # Drag acceleration
        a_d = rho * v**2 / (2 * self.beta)
        
        # Lift acceleration
        a_l = a_d * self.ld_ratio
        
        # Derivatives
        dh_dt = -v * math.sin(gamma)
        dv_dt = -a_d - g * math.sin(gamma)
        dgamma_dt = (a_l / v - (g / v - v / self.atm["radius_m"]) * math.cos(gamma))
        
        return dh_dt, dv_dt, math.degrees(dgamma_dt)
    
    def simulate_entry(self, entry_altitude_m: float,
                       entry_velocity_ms: float,
                       entry_fpa_deg: float,
                       dt_s: float = 0.1,
                       max_time_s: float = 600.0) -> List[EntryState]:
        """
        Simulate entry trajectory using forward Euler integration.
        
        Args:
            entry_altitude_m: Initial altitude (m)
            entry_velocity_ms: Entry velocity (m/s)
            entry_fpa_deg: Entry flight path angle (deg, negative = downward)
            dt_s: Integration timestep
            max_time_s: Maximum simulation time
        
        Returns:
            List of EntryState at each timestep
        """
        state = EntryState(
            altitude_m=entry_altitude_m,
            velocity_ms=entry_velocity_ms,
            flight_path_angle_deg=entry_fpa_deg,
            range_to_go_m=0.0,
            time_s=0.0
        )
        
        trajectory = [state]
        
        while state.altitude_m > self.atm["min_altitude_m"] and state.time_s < max_time_s:
            dh_dt, dv_dt, dgamma_dt = self._derivatives(state)
            
            # Update state
            new_alt = state.altitude_m + dh_dt * dt_s
            new_vel = max(0.0, state.velocity_ms + dv_dt * dt_s)
            new_gamma = state.flight_path_angle_deg + dgamma_dt * dt_s
            new_range = state.range_to_go_m + state.velocity_ms * math.cos(
                math.radians(state.flight_path_angle_deg)
            ) * dt_s
            
            # Compute derived quantities
            rho = self.atmospheric_density(new_alt)
            q = 0.5 * rho * new_vel**2  # Dynamic pressure
            decel_g = abs(dv_dt) / 9.81
            
            # Heating rate (Sutton-Graves approximation)
            # q_dot = k * sqrt(rho) * v^3, k ~ 1.83e-4 for 1m nose radius
            k_heat = 1.83e-4
            heating = k_heat * math.sqrt(rho) * new_vel**3 / 1e4  # W/cm^2
            
            state = EntryState(
                altitude_m=new_alt,
                velocity_ms=new_vel,
                flight_path_angle_deg=new_gamma,
                range_to_go_m=new_range,
                time_s=state.time_s + dt_s,
                deceleration_g=decel_g,
                heating_rate_w_cm2=heating,
                dynamic_pressure_pa=q
            )
            
            trajectory.append(state)
            
            # Stop if landed or bounced back to space
            if new_alt <= 0:
                break
            if new_alt > entry_altitude_m * 1.5 and new_vel > entry_velocity_ms * 0.9:
                break  # Skip-out
        
        return trajectory
    
    def find_peak_heating(self, trajectory: List[EntryState]) -> EntryState:
        """Find point of maximum heating in trajectory."""
        return max(trajectory, key=lambda s: s.heating_rate_w_cm2)
    
    def find_peak_g_load(self, trajectory: List[EntryState]) -> EntryState:
        """Find point of maximum deceleration in trajectory."""
        return max(trajectory, key=lambda s: s.deceleration_g)
    
    def find_peak_dynamic_pressure(self, trajectory: List[EntryState]) -> EntryState:
        """Find point of maximum dynamic pressure."""
        return max(trajectory, key=lambda s: s.dynamic_pressure_pa)
    
    def entry_summary(self, trajectory: List[EntryState]) -> Dict:
        """Generate summary statistics for entry trajectory."""
        if not trajectory:
            return {}
        
        peak_heat = self.find_peak_heating(trajectory)
        peak_g = self.find_peak_g_load(trajectory)
        peak_q = self.find_peak_dynamic_pressure(trajectory)
        
        final = trajectory[-1]
        
        return {
            "planet": self.planet,
            "entry_duration_s": round(final.time_s, 1),
            "entry_duration_min": round(final.time_s / 60.0, 2),
            "final_altitude_m": round(final.altitude_m, 1),
            "final_velocity_ms": round(final.velocity_ms, 1),
            "total_range_m": round(final.range_to_go_m, 1),
            "total_range_km": round(final.range_to_go_m / 1000.0, 2),
            "peak_heating_w_cm2": round(peak_heat.heating_rate_w_cm2, 4),
            "peak_heating_altitude_m": round(peak_heat.altitude_m, 1),
            "peak_deceleration_g": round(peak_g.deceleration_g, 2),
            "peak_deceleration_altitude_m": round(peak_g.altitude_m, 1),
            "peak_dynamic_pressure_pa": round(peak_q.dynamic_pressure_pa, 1),
            "trajectory_points": len(trajectory),
            "ballistic_coefficient": self.beta,
            "lift_drag_ratio": self.ld_ratio
        }
    
    def design_entry_corridor(self, entry_velocity_ms: float,
                              min_g_limit: float = 2.0,
                              max_g_limit: float = 15.0,
                              max_heat_limit_w_cm2: float = 500.0) -> Dict:
        """
        Design entry corridor: find min/max acceptable entry flight path angles.
        
        Args:
            entry_velocity_ms: Entry velocity
            min_g_limit: Minimum survivable g-load (too shallow = skip-out)
            max_g_limit: Maximum survivable g-load (too steep = crash)
            max_heat_limit_w_cm2: Maximum heating rate
        
        Returns:
            Corridor bounds
        """
        # Binary search for steep (undershoot) boundary
        # Too steep = high g-load or crash
        gamma_steep = -45.0  # Start very steep
        for _ in range(10):
            traj = self.simulate_entry(125000.0, entry_velocity_ms, gamma_steep, dt_s=0.5)
            summary = self.entry_summary(traj)
            peak_g = summary.get("peak_deceleration_g", 0)
            
            if peak_g > max_g_limit or summary.get("final_altitude_m", 0) > 1000:
                gamma_steep += 2.0  # Too steep, shallow out
            else:
                gamma_steep -= 1.0  # Can go steeper
        
        # Binary search for shallow (overshoot) boundary
        gamma_shallow = -2.0  # Start very shallow
        for _ in range(10):
            traj = self.simulate_entry(125000.0, entry_velocity_ms, gamma_shallow, dt_s=0.5)
            summary = self.entry_summary(traj)
            final_alt = summary.get("final_altitude_m", 0)
            
            if final_alt > 1000:  # Skip-out
                gamma_shallow -= 1.0  # Too shallow, steepen
            else:
                gamma_shallow += 0.5  # Can go shallower
        
        return {
            "planet": self.planet,
            "entry_velocity_ms": entry_velocity_ms,
            "min_fpa_deg": round(min(gamma_shallow, gamma_steep), 2),
            "max_fpa_deg": round(max(gamma_shallow, gamma_steep), 2),
            "corridor_width_deg": round(abs(gamma_steep - gamma_shallow), 2),
            "constraints": {
                "max_g": max_g_limit,
                "max_heat_w_cm2": max_heat_limit_w_cm2
            }
        }


class ParachuteDescent:
    """
    Model parachute descent phase after atmospheric entry.
    """
    
    def __init__(self, planet: str = "Mars", drag_area_m2: float = 100.0,
                 mass_kg: float = 1000.0, drag_coefficient: float = 1.5):
        self.planet = planet
        self.atm = ATMOSPHERE_MODELS.get(planet, ATMOSPHERE_MODELS["Mars"])
        self.CdA = drag_coefficient * drag_area_m2
        self.mass = mass_kg
    
    def terminal_velocity(self, altitude_m: float) -> float:
        """Compute terminal velocity at given altitude."""
        rho = self.atmospheric_density(altitude_m)
        if rho < 1e-6:
            return 0.0
        return math.sqrt(2 * self.mass * self.atm["surface_gravity"] / (rho * self.CdA))
    
    def atmospheric_density(self, altitude_m: float) -> float:
        """Exponential atmosphere model."""
        h = max(0.0, altitude_m)
        return self.atm["surface_density_kg_m3"] * math.exp(-h / self.atm["scale_height_m"])
    
    def simulate_descent(self, deploy_altitude_m: float,
                         initial_velocity_ms: float,
                         dt_s: float = 0.5) -> List[Dict]:
        """
        Simulate parachute descent from deployment to surface.
        
        Returns:
            List of state dicts
        """
        h = deploy_altitude_m
        v = initial_velocity_ms
        t = 0.0
        states = []
        
        while h > 0:
            rho = self.atmospheric_density(h)
            drag = 0.5 * rho * v**2 * self.CdA / self.mass
            g = self.atm["surface_gravity"]
            
            # Simple: drag opposes velocity, gravity pulls down
            dv_dt = g - drag if v > 0 else g
            dh_dt = -v
            
            v = max(0.0, v + dv_dt * dt_s)
            h += dh_dt * dt_s
            t += dt_s
            
            states.append({
                "altitude_m": round(h, 1),
                "velocity_ms": round(v, 2),
                "time_s": round(t, 1),
                "terminal_velocity_ms": round(self.terminal_velocity(h), 2)
            })
            
            if len(states) > 10000:
                break
        
        return states
