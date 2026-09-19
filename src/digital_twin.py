"""
Digital Twin Module
Physics-based digital twin with state synchronization
for spacecraft simulation and prediction.
"""

import math
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class TwinState:
    """State vector for digital twin."""
    position_m: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    velocity_ms: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    mass_kg: float = 1000.0
    fuel_kg: float = 500.0
    battery_charge: float = 1.0
    temperature_c: float = 20.0
    timestamp: float = 0.0


class PhysicsModel:
    """
    Simple physics model for spacecraft dynamics.
    
    Integrates position/velocity with gravitational
    and thrust forces.
    """
    
    def __init__(self, mu: float = 3.986e14):  # Earth GM m^3/s^2
        self.mu = mu
    
    def compute_gravity(self, position: Tuple[float, float, float],
                       mass: float) -> Tuple[float, float, float]:
        """
        Compute gravitational acceleration.
        
        Args:
            position: Position vector
            mass: Mass (unused for point mass gravity)
        
        Returns:
            Acceleration (ax, ay, az)
        """
        r = math.sqrt(sum(p**2 for p in position))
        if r == 0:
            return (0.0, 0.0, 0.0)
        
        a = -self.mu / (r ** 2)
        scale = a / r
        return (position[0] * scale, position[1] * scale, position[2] * scale)
    
    def integrate(self, state: TwinState, thrust_n: Tuple[float, float, float],
                 dt_s: float) -> TwinState:
        """
        Integrate state forward by time step.
        
        Args:
            state: Current state
            thrust_n: Thrust vector
            dt_s: Time step
        
        Returns:
            New state
        """
        if state.mass_kg <= 0:
            return state
        
        # Gravity
        g = self.compute_gravity(state.position_m, state.mass_kg)
        
        # Thrust acceleration
        ax_t = thrust_n[0] / state.mass_kg
        ay_t = thrust_n[1] / state.mass_kg
        az_t = thrust_n[2] / state.mass_kg
        
        # Total acceleration
        ax = g[0] + ax_t
        ay = g[1] + ay_t
        az = g[2] + az_t
        
        # Update velocity
        vx = state.velocity_ms[0] + ax * dt_s
        vy = state.velocity_ms[1] + ay * dt_s
        vz = state.velocity_ms[2] + az * dt_s
        
        # Update position
        px = state.position_m[0] + vx * dt_s
        py = state.position_m[1] + vy * dt_s
        pz = state.position_m[2] + vz * dt_s
        
        # Update fuel
        thrust_mag = math.sqrt(sum(t**2 for t in thrust_n))
        isp = 300.0  # s
        g0 = 9.81
        mdot = thrust_mag / (isp * g0) if isp * g0 > 0 else 0.0
        new_fuel = max(0.0, state.fuel_kg - mdot * dt_s)
        new_mass = state.mass_kg - (state.fuel_kg - new_fuel)
        
        return TwinState(
            position_m=(px, py, pz),
            velocity_ms=(vx, vy, vz),
            mass_kg=new_mass,
            fuel_kg=new_fuel,
            battery_charge=state.battery_charge,
            temperature_c=state.temperature_c,
            timestamp=state.timestamp + dt_s
        )


class DigitalTwin:
    """
    Digital twin for spacecraft state synchronization
    and prediction.
    """
    
    def __init__(self, spacecraft_id: str):
        """
        Args:
            spacecraft_id: Spacecraft identifier
        """
        self.spacecraft_id = spacecraft_id
        self.physics = PhysicsModel()
        self.state = TwinState()
        self.history: List[TwinState] = []
        self.sync_offset: float = 0.0
        self.prediction_horizon_s: float = 3600.0
    
    def synchronize(self, measured_state: TwinState):
        """
        Synchronize twin with measured state.
        
        Args:
            measured_state: State from sensors
        """
        # Compute sync offset
        pos_diff = math.sqrt(
            (self.state.position_m[0] - measured_state.position_m[0])**2 +
            (self.state.position_m[1] - measured_state.position_m[1])**2 +
            (self.state.position_m[2] - measured_state.position_m[2])**2
        )
        self.sync_offset = pos_diff
        
        # Update state
        self.state = measured_state
        self.history.append(measured_state)
        
        # Trim history
        if len(self.history) > 1000:
            self.history = self.history[-500:]
    
    def predict(self, duration_s: float,
               thrust_profile: Optional[List[Tuple[float, Tuple[float, float, float]]]] = None) -> List[TwinState]:
        """
        Predict future states.
        
        Args:
            duration_s: Prediction duration
            thrust_profile: List of (time, thrust_vector)
        
        Returns:
            Predicted states
        """
        thrust_profile = thrust_profile or []
        dt_s = 10.0
        steps = int(duration_s / dt_s)
        
        states = []
        current = TwinState(
            position_m=self.state.position_m,
            velocity_ms=self.state.velocity_ms,
            mass_kg=self.state.mass_kg,
            fuel_kg=self.state.fuel_kg,
            battery_charge=self.state.battery_charge,
            temperature_c=self.state.temperature_c,
            timestamp=self.state.timestamp
        )
        
        for i in range(steps):
            t = i * dt_s
            
            # Find thrust at this time
            thrust = (0.0, 0.0, 0.0)
            for tp_time, tp_thrust in thrust_profile:
                if abs(tp_time - t) < dt_s:
                    thrust = tp_thrust
                    break
            
            current = self.physics.integrate(current, thrust, dt_s)
            
            if i % 10 == 0:  # Sample every 10 steps
                states.append(current)
        
        return states
    
    def detect_divergence(self, measured_state: TwinState,
                         threshold_m: float = 1000.0) -> Dict:
        """
        Detect if twin has diverged from reality.
        
        Args:
            measured_state: Current measured state
            threshold_m: Divergence threshold
        
        Returns:
            Divergence info
        """
        pos_diff = math.sqrt(
            (self.state.position_m[0] - measured_state.position_m[0])**2 +
            (self.state.position_m[1] - measured_state.position_m[1])**2 +
            (self.state.position_m[2] - measured_state.position_m[2])**2
        )
        
        vel_diff = math.sqrt(
            (self.state.velocity_ms[0] - measured_state.velocity_ms[0])**2 +
            (self.state.velocity_ms[1] - measured_state.velocity_ms[1])**2 +
            (self.state.velocity_ms[2] - measured_state.velocity_ms[2])**2
        )
        
        return {
            "position_divergence_m": pos_diff,
            "velocity_divergence_ms": vel_diff,
            "is_diverged": pos_diff > threshold_m,
            "threshold_m": threshold_m
        }
    
    def twin_summary(self) -> Dict:
        """Get twin summary."""
        return {
            "spacecraft_id": self.spacecraft_id,
            "sync_offset_m": self.sync_offset,
            "history_length": len(self.history),
            "current_mass_kg": self.state.mass_kg,
            "current_fuel_kg": self.state.fuel_kg,
            "current_battery": self.state.battery_charge,
            "prediction_horizon_s": self.prediction_horizon_s
        }
