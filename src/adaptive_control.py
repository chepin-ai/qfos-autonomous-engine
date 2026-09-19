"""
Adaptive Control Module
Model-reference adaptive control (MRAC) and self-tuning
regulators for spacecraft attitude and trajectory control.
"""

import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass


@dataclass
class ReferenceModel:
    """Reference model for MRAC."""
    natural_frequency: float  # rad/s
    damping_ratio: float
    
    def response(self, input_cmd: float, state: Dict) -> Tuple[float, Dict]:
        """
        Compute reference model response.
        
        Second-order system: y'' + 2*zeta*wn*y' + wn^2*y = wn^2*u
        
        Args:
            input_cmd: Input command
            state: Current state {'y': position, 'yd': velocity}
        
        Returns:
            (output, new_state)
        """
        y = state.get("y", 0.0)
        yd = state.get("yd", 0.0)
        dt = state.get("dt", 0.01)
        
        wn = self.natural_frequency
        zeta = self.damping_ratio
        
        # Acceleration from reference model
        ydd = wn**2 * input_cmd - 2.0 * zeta * wn * yd - wn**2 * y
        
        # Integrate
        yd_new = yd + ydd * dt
        y_new = y + yd_new * dt
        
        return y_new, {"y": y_new, "yd": yd_new, "dt": dt}


@dataclass
class AdaptiveGains:
    """Adaptive controller gains."""
    Kp: float = 1.0
    Ki: float = 0.1
    Kd: float = 0.5
    gamma_p: float = 0.1  # Adaptation rate for Kp
    gamma_i: float = 0.05
    gamma_d: float = 0.05


class MRACController:
    """
    Model-Reference Adaptive Controller.
    
    Adapts controller gains to make plant output
    track reference model output.
    """
    
    def __init__(self, reference: ReferenceModel,
                 initial_gains: Optional[AdaptiveGains] = None):
        """
        Args:
            reference: Reference model
            initial_gains: Initial controller gains
        """
        self.reference = reference
        self.gains = initial_gains or AdaptiveGains()
        self.ref_state = {"y": 0.0, "yd": 0.0, "dt": 0.01}
        self.error_integral = 0.0
        self.last_error = 0.0
        self.adaptation_history: List[Dict] = []
    
    def control(self, setpoint: float, measurement: float,
                dt: float = 0.01) -> Tuple[float, Dict]:
        """
        Compute control output with adaptation.
        
        Args:
            setpoint: Desired value
            measurement: Current value
            dt: Time step
        
        Returns:
            (control_output, info)
        """
        # Reference model output
        ref_output, self.ref_state = self.reference.response(setpoint, self.ref_state)
        
        # Tracking error
        error = ref_output - measurement
        
        # PID control
        self.error_integral += error * dt
        error_derivative = (error - self.last_error) / dt
        
        control = (self.gains.Kp * error +
                   self.gains.Ki * self.error_integral +
                   self.gains.Kd * error_derivative)
        
        # Adapt gains using gradient descent on error squared
        error_sq = error ** 2
        
        self.gains.Kp += self.gains.gamma_p * error * error * dt
        self.gains.Ki += self.gains.gamma_i * error * self.error_integral * dt
        self.gains.Kd += self.gains.gamma_d * error * error_derivative * dt
        
        # Keep gains positive
        self.gains.Kp = max(0.01, self.gains.Kp)
        self.gains.Ki = max(0.0, self.gains.Ki)
        self.gains.Kd = max(0.0, self.gains.Kd)
        
        self.last_error = error
        
        info = {
            "reference": round(ref_output, 6),
            "error": round(error, 6),
            "Kp": round(self.gains.Kp, 4),
            "Ki": round(self.gains.Ki, 4),
            "Kd": round(self.gains.Kd, 4),
            "control": round(control, 6)
        }
        
        self.adaptation_history.append(info)
        
        return control, info
    
    def reset(self):
        """Reset controller state."""
        self.ref_state = {"y": 0.0, "yd": 0.0, "dt": 0.01}
        self.error_integral = 0.0
        self.last_error = 0.0


class GainScheduler:
    """
    Gain scheduler for parameter-dependent controllers.
    
    Switches or interpolates controller gains based on
    operating conditions.
    """
    
    def __init__(self):
        self.schedule: List[Dict] = []
        self.default_gains = {"Kp": 1.0, "Ki": 0.1, "Kd": 0.5}
    
    def add_schedule_point(self, condition: str,
                          param_range: Tuple[float, float],
                          gains: Dict[str, float]):
        """
        Add a schedule point.
        
        Args:
            condition: Parameter name
            param_range: (min, max) range
            gains: Controller gains for this range
        """
        self.schedule.append({
            "condition": condition,
            "min": param_range[0],
            "max": param_range[1],
            "gains": gains
        })
    
    def get_gains(self, conditions: Dict[str, float]) -> Dict[str, float]:
        """
        Get gains for current conditions.
        
        Args:
            conditions: Current parameter values
        
        Returns:
            Controller gains
        """
        for entry in self.schedule:
            param = entry["condition"]
            if param in conditions:
                val = conditions[param]
                if entry["min"] <= val <= entry["max"]:
                    return entry["gains"].copy()
        
        return self.default_gains.copy()
    
    def interpolate_gains(self, conditions: Dict[str, float]) -> Dict[str, float]:
        """
        Interpolate gains between schedule points.
        
        Args:
            conditions: Current parameter values
        
        Returns:
            Interpolated gains
        """
        result = self.default_gains.copy()
        
        for param, val in conditions.items():
            # Find bracketing schedule points
            lower = None
            upper = None
            
            for entry in self.schedule:
                if entry["condition"] == param:
                    if val >= entry["min"] and (lower is None or entry["min"] > lower["min"]):
                        lower = entry
                    if val <= entry["max"] and (upper is None or entry["max"] < upper["max"]):
                        upper = entry
            
            if lower and upper and lower != upper:
                # Interpolate
                span = upper["max"] - lower["min"]
                if span > 0:
                    t = (val - lower["min"]) / span
                    for gain_name in result:
                        if gain_name in lower["gains"] and gain_name in upper["gains"]:
                            result[gain_name] = ((1.0 - t) * lower["gains"][gain_name] +
                                                t * upper["gains"][gain_name])
        
        return result


class AdaptiveController:
    """
    Unified adaptive controller.
    
    Combines MRAC and gain scheduling.
    """
    
    def __init__(self, reference: Optional[ReferenceModel] = None):
        self.mrac = MRACController(reference or ReferenceModel(1.0, 0.7))
        self.scheduler = GainScheduler()
        self.active_mode = "mrac"  # "mrac" or "scheduled"
        self.performance_log: List[Dict] = []
    
    def set_mode(self, mode: str):
        """Set control mode."""
        if mode in ["mrac", "scheduled"]:
            self.active_mode = mode
    
    def control(self, setpoint: float, measurement: float,
                conditions: Optional[Dict[str, float]] = None,
                dt: float = 0.01) -> Tuple[float, Dict]:
        """
        Compute control output.
        
        Args:
            setpoint: Desired value
            measurement: Current value
            conditions: Operating conditions for gain scheduling
            dt: Time step
        
        Returns:
            (control_output, info)
        """
        if self.active_mode == "mrac":
            return self.mrac.control(setpoint, measurement, dt)
        else:
            gains = self.scheduler.get_gains(conditions or {})
            error = setpoint - measurement
            control = gains.get("Kp", 1.0) * error
            return control, {"mode": "scheduled", "gains": gains, "error": error}
    
    def get_adaptation_history(self) -> List[Dict]:
        """Get MRAC adaptation history."""
        return self.mrac.adaptation_history
    
    def controller_summary(self) -> Dict:
        """Get controller summary."""
        return {
            "mode": self.active_mode,
            "mrac_gains": {
                "Kp": round(self.mrac.gains.Kp, 4),
                "Ki": round(self.mrac.gains.Ki, 4),
                "Kd": round(self.mrac.gains.Kd, 4)
            },
            "schedule_points": len(self.scheduler.schedule),
            "adaptation_steps": len(self.mrac.adaptation_history)
        }
