"""
Actuator Control Module
PID, feedforward, saturation, and position/force control
for autonomous system actuation.
"""

import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class ControlMode(Enum):
    """Actuator control mode."""
    POSITION = "position"
    VELOCITY = "velocity"
    FORCE = "force"
    TORQUE = "torque"
    HYBRID = "hybrid"


@dataclass
class ControlState:
    """Actuator control state."""
    position: float = 0.0
    velocity: float = 0.0
    force: float = 0.0
    error: float = 0.0
    integral: float = 0.0
    derivative: float = 0.0


class PIDController:
    """
    Proportional-Integral-Derivative controller.
    """
    
    def __init__(self, kp: float = 1.0,
                 ki: float = 0.0,
                 kd: float = 0.0,
                 integral_limit: float = 100.0,
                 output_limit: float = 100.0):
        """
        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
            integral_limit: Anti-windup limit
            output_limit: Output saturation
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_limit = integral_limit
        self.output_limit = output_limit
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_time = None
    
    def reset(self):
        """Reset controller state."""
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_time = None
    
    def update(self, setpoint: float, measurement: float,
              dt_s: Optional[float] = None) -> float:
        """
        Update PID controller.
        
        Args:
            setpoint: Target value
            measurement: Current value
            dt_s: Time step
        
        Returns:
            Control output
        """
        error = setpoint - measurement
        
        if dt_s is None:
            dt_s = 0.01
        
        # Proportional
        p_term = self.kp * error
        
        # Integral with anti-windup
        self.integral += error * dt_s
        self.integral = max(-self.integral_limit,
                           min(self.integral_limit, self.integral))
        i_term = self.ki * self.integral
        
        # Derivative
        if dt_s > 0:
            d_term = self.kd * (error - self.prev_error) / dt_s
        else:
            d_term = 0.0
        
        self.prev_error = error
        
        # Sum and saturate
        output = p_term + i_term + d_term
        output = max(-self.output_limit, min(self.output_limit, output))
        
        return output
    
    def set_gains(self, kp: float, ki: float, kd: float):
        """Set PID gains."""
        self.kp = kp
        self.ki = ki
        self.kd = kd


class FeedforwardController:
    """
    Feedforward compensation controller.
    """
    
    def __init__(self, mass_kg: float = 1.0,
                 damping_Ns_m: float = 0.1,
                 gravity_m_s2: float = 9.81):
        """
        Args:
            mass_kg: Actuated mass
            damping_Ns_m: Damping coefficient
            gravity_m_s2: Gravity
        """
        self.mass = mass_kg
        self.damping = damping_Ns_m
        self.gravity = gravity_m_s2
    
    def compute(self, desired_accel: float,
               desired_velocity: float = 0.0,
               gravity_compensation: bool = False) -> float:
        """
        Compute feedforward force.
        
        Args:
            desired_accel: Desired acceleration
            desired_velocity: Desired velocity
            gravity_compensation: Include gravity
        
        Returns:
            Feedforward force
        """
        force = self.mass * desired_accel + self.damping * desired_velocity
        
        if gravity_compensation:
            force += self.mass * self.gravity
        
        return force
    
    def compute_trajectory(self, positions: List[float],
                          dt_s: float = 0.01) -> List[float]:
        """
        Compute feedforward for trajectory.
        
        Args:
            positions: Desired positions
            dt_s: Time step
        
        Returns:
            Feedforward forces
        """
        forces = []
        
        for i in range(len(positions)):
            if i == 0:
                accel = 0.0
                vel = 0.0
            elif i == len(positions) - 1:
                accel = 0.0
                vel = (positions[i] - positions[i-1]) / dt_s
            else:
                vel = (positions[i] - positions[i-1]) / dt_s
                next_vel = (positions[i+1] - positions[i]) / dt_s
                accel = (next_vel - vel) / dt_s
            
            forces.append(self.compute(accel, vel))
        
        return forces


class SaturationLimiter:
    """
    Rate and magnitude saturation limiter.
    """
    
    def __init__(self, max_magnitude: float = 100.0,
                 max_rate: float = 1000.0):
        """
        Args:
            max_magnitude: Maximum output magnitude
            max_rate: Maximum rate of change
        """
        self.max_magnitude = max_magnitude
        self.max_rate = max_rate
        self.prev_output = 0.0
        self.prev_time = None
    
    def limit(self, desired_output: float,
             dt_s: Optional[float] = None) -> float:
        """
        Apply saturation limits.
        
        Args:
            desired_output: Desired output
            dt_s: Time step
        
        Returns:
            Limited output
        """
        if dt_s is None:
            dt_s = 0.01
        
        # Rate limit
        if dt_s > 0:
            max_delta = self.max_rate * dt_s
            delta = desired_output - self.prev_output
            delta = max(-max_delta, min(max_delta, delta))
            output = self.prev_output + delta
        else:
            output = desired_output
        
        # Magnitude limit
        output = max(-self.max_magnitude, min(self.max_magnitude, output))
        
        self.prev_output = output
        return output
    
    def reset(self):
        """Reset limiter."""
        self.prev_output = 0.0
        self.prev_time = None


class HybridController:
    """
    Hybrid position/force controller.
    """
    
    def __init__(self):
        self.position_pid = PIDController(kp=100.0, kd=10.0)
        self.force_pid = PIDController(kp=1.0, ki=0.1)
        self.feedforward = FeedforwardController()
        self.saturation = SaturationLimiter()
        self.mode = ControlMode.POSITION
    
    def set_mode(self, mode: ControlMode):
        """Set control mode."""
        self.mode = mode
    
    def update(self, setpoint: float, measurement: float,
              force_feedback: float = 0.0,
              dt_s: float = 0.01) -> float:
        """
        Update controller.
        
        Args:
            setpoint: Target value
            measurement: Current value
            force_feedback: Force measurement
            dt_s: Time step
        
        Returns:
            Control output
        """
        if self.mode == ControlMode.POSITION:
            output = self.position_pid.update(setpoint, measurement, dt_s)
        elif self.mode == ControlMode.VELOCITY:
            output = self.position_pid.update(setpoint, measurement, dt_s)
        elif self.mode == ControlMode.FORCE:
            output = self.force_pid.update(setpoint, force_feedback, dt_s)
        else:
            # Hybrid: position with force limiting
            pos_output = self.position_pid.update(setpoint, measurement, dt_s)
            force_output = self.force_pid.update(0.0, force_feedback, dt_s)
            output = pos_output + force_output
        
        return self.saturation.limit(output, dt_s)
    
    def add_feedforward(self, desired_accel: float,
                       desired_velocity: float = 0.0) -> float:
        """
        Get feedforward term.
        
        Args:
            desired_accel: Desired acceleration
            desired_velocity: Desired velocity
        
        Returns:
            Feedforward force
        """
        return self.feedforward.compute(desired_accel, desired_velocity)


class ActuatorControl:
    """
    Unified actuator control system.
    """
    
    def __init__(self):
        self.controllers: Dict[str, HybridController] = {}
        self.states: Dict[str, ControlState] = {}
    
    def register_actuator(self, name: str,
                         controller: Optional[HybridController] = None):
        """Register actuator."""
        if controller is None:
            controller = HybridController()
        self.controllers[name] = controller
        self.states[name] = ControlState()
    
    def set_target(self, name: str, setpoint: float):
        """Set actuator target."""
        state = self.states.get(name)
        if state:
            state.error = setpoint - state.position
    
    def update(self, name: str, position: float, velocity: float = 0.0,
              force: float = 0.0, dt_s: float = 0.01) -> float:
        """
        Update actuator control.
        
        Args:
            name: Actuator name
            position: Current position
            velocity: Current velocity
            force: Current force
            dt_s: Time step
        
        Returns:
            Control command
        """
        controller = self.controllers.get(name)
        state = self.states.get(name)
        
        if not controller or not state:
            return 0.0
        
        state.position = position
        state.velocity = velocity
        state.force = force
        
        # Get setpoint from stored error
        setpoint = position + state.error
        
        output = controller.update(setpoint, position, force, dt_s)
        state.error = setpoint - position
        
        return output
    
    def control_summary(self) -> Dict:
        """Get control summary."""
        return {
            "actuators": len(self.controllers),
            "modes": {name: c.mode.value for name, c in self.controllers.items()}
        }
