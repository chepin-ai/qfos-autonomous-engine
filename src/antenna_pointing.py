"""
Antenna Pointing Module
Tracking algorithms, beam steering, and gimbal control
for communication and sensing antennas.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PointingTarget:
    """Pointing target specification."""
    azimuth_deg: float  # degrees
    elevation_deg: float  # degrees
    range_km: float = 0.0
    target_id: str = ""


class GimbalController:
    """
    Control antenna gimbal pointing.
    """
    
    def __init__(self, max_rate_degs: float = 10.0,
                 max_accel_degs2: float = 5.0):
        """
        Args:
            max_rate_degs: Max gimbal rate (deg/s)
            max_accel_degs2: Max gimbal acceleration (deg/s^2)
        """
        self.max_rate = max_rate_degs
        self.max_accel = max_accel_degs2
        self.azimuth = 0.0
        self.elevation = 0.0
        self.az_rate = 0.0
        self.el_rate = 0.0
    
    def get_pointing(self) -> Tuple[float, float]:
        """Get current pointing (az, el) in degrees."""
        return (self.azimuth, self.elevation)
    
    def slew_to(self, target_az: float, target_el: float,
               dt: float = 1.0) -> bool:
        """
        Slew gimbal toward target.
        
        Args:
            target_az: Target azimuth (deg)
            target_el: Target elevation (deg)
            dt: Time step (seconds)
        
        Returns:
            True if at target
        """
        # Compute errors
        az_err = target_az - self.azimuth
        el_err = target_el - self.elevation
        
        # Normalize azimuth error to [-180, 180]
        while az_err > 180:
            az_err -= 360
        while az_err < -180:
            az_err += 360
        
        # Simple proportional control with rate limiting
        az_cmd = max(-self.max_rate, min(self.max_rate, az_err / dt * 0.5))
        el_cmd = max(-self.max_rate, min(self.max_rate, el_err / dt * 0.5))
        
        # Apply
        self.azimuth += az_cmd * dt
        self.elevation += el_cmd * dt
        
        # Clamp elevation
        self.elevation = max(-90, min(90, self.elevation))
        
        # Check convergence
        return abs(az_err) < 0.1 and abs(el_err) < 0.1
    
    def pointing_error(self, target_az: float, target_el: float) -> float:
        """
        Compute pointing error.
        
        Args:
            target_az: Target azimuth (deg)
            target_el: Target elevation (deg)
        
        Returns:
            Angular error (deg)
        """
        # Convert to unit vectors and compute angle
        az_err = target_az - self.azimuth
        while az_err > 180:
            az_err -= 360
        while az_err < -180:
            az_err += 360
        
        el_err = target_el - self.elevation
        
        # Approximate angular separation
        return math.sqrt(az_err**2 + el_err**2)


class TrackingAlgorithm:
    """
    Target tracking with prediction.
    """
    
    def __init__(self):
        self.target_history: List[Tuple[float, float, float]] = []
        # (timestamp, az, el)
        self.prediction_gain = 0.3
    
    def update(self, timestamp: float, az: float, el: float):
        """Update target measurement."""
        self.target_history.append((timestamp, az, el))
        if len(self.target_history) > 10:
            self.target_history.pop(0)
    
    def predict(self, future_time: float) -> Optional[Tuple[float, float]]:
        """
        Predict target position at future time.
        
        Args:
            future_time: Future timestamp
        
        Returns:
            Predicted (az, el) or None
        """
        if len(self.target_history) < 2:
            if self.target_history:
                return (self.target_history[-1][1], self.target_history[-1][2])
            return None
        
        # Linear extrapolation from last two points
        t1, az1, el1 = self.target_history[-2]
        t2, az2, el2 = self.target_history[-1]
        dt = t2 - t1
        if abs(dt) < 1e-10:
            return (az2, el2)
        
        az_rate = (az2 - az1) / dt
        el_rate = (el2 - el1) / dt
        
        dt_pred = future_time - t2
        az_pred = az2 + az_rate * dt_pred
        el_pred = el2 + el_rate * dt_pred
        
        return (az_pred, el_pred)
    
    def tracking_rate(self) -> Tuple[float, float]:
        """
        Get current tracking rate.
        
        Returns:
            (az_rate, el_rate) in deg/s
        """
        if len(self.target_history) < 2:
            return (0.0, 0.0)
        
        t1, az1, el1 = self.target_history[-2]
        t2, az2, el2 = self.target_history[-1]
        dt = t2 - t1
        if abs(dt) < 1e-10:
            return (0.0, 0.0)
        
        return ((az2 - az1) / dt, (el2 - el1) / dt)


class BeamSteering:
    """
    Electronic beam steering for phased arrays.
    """
    
    def __init__(self, wavelength_m: float = 0.03,  # X-band ~10GHz
                 element_spacing_m: float = 0.015):
        """
        Args:
            wavelength_m: Signal wavelength (m)
            element_spacing_m: Array element spacing (m)
        """
        self.wavelength = wavelength_m
        self.spacing = element_spacing_m
        self.k = 2 * math.pi / wavelength_m
    
    def phase_shift(self, steering_angle_deg: float,
                   element_index: int) -> float:
        """
        Compute phase shift for array element.
        
        Args:
            steering_angle_deg: Steering angle (deg)
            element_index: Element index
        
        Returns:
            Phase shift (rad)
        """
        theta = math.radians(steering_angle_deg)
        return -self.k * element_index * self.spacing * math.sin(theta)
    
    def array_factor(self, steering_angle_deg: float,
                    num_elements: int,
                    observation_angle_deg: float) -> float:
        """
        Compute array factor.
        
        Args:
            steering_angle_deg: Steering angle (deg)
            num_elements: Number of elements
            observation_angle_deg: Observation angle (deg)
        
        Returns:
            Array factor magnitude (0-1)
        """
        theta_s = math.radians(steering_angle_deg)
        theta_o = math.radians(observation_angle_deg)
        
        psi = self.k * self.spacing * (math.sin(theta_o) - math.sin(theta_s))
        
        if abs(psi) < 1e-10:
            return 1.0
        
        af = abs(math.sin(num_elements * psi / 2) / (num_elements * math.sin(psi / 2)))
        return min(1.0, af)
    
    def beamwidth(self, num_elements: int) -> float:
        """
        Estimate beamwidth.
        
        Args:
            num_elements: Number of elements
        
        Returns:
            3dB beamwidth (deg)
        """
        if num_elements <= 1:
            return 180.0
        array_length = (num_elements - 1) * self.spacing
        return math.degrees(0.886 * self.wavelength / array_length)


class AntennaPointing:
    """
    Unified antenna pointing controller.
    """
    
    def __init__(self):
        self.gimbal = GimbalController()
        self.tracker = TrackingAlgorithm()
        self.beam = BeamSteering()
    
    def point_to_target(self, target: PointingTarget, dt: float = 1.0) -> bool:
        """
        Point antenna at target.
        
        Args:
            target: Target specification
            dt: Time step
        
        Returns:
            True if on target
        """
        self.tracker.update(dt, target.azimuth_deg, target.elevation_deg)
        return self.gimbal.slew_to(target.azimuth_deg, target.elevation_deg, dt)
    
    def track_target(self, measurements: List[Tuple[float, float, float]],
                    predict_time: float) -> Optional[Tuple[float, float]]:
        """
        Track and predict target.
        
        Args:
            measurements: List of (timestamp, az, el)
            predict_time: Time to predict
        
        Returns:
            Predicted pointing
        """
        for t, az, el in measurements:
            self.tracker.update(t, az, el)
        return self.tracker.predict(predict_time)
    
    def get_pointing_error(self, target: PointingTarget) -> float:
        """Get pointing error to target."""
        return self.gimbal.pointing_error(target.azimuth_deg, target.elevation_deg)
    
    def compute_beam_phases(self, steering_angle_deg: float,
                           num_elements: int) -> List[float]:
        """
        Compute phase shifts for beam steering.
        
        Args:
            steering_angle_deg: Steering angle
            num_elements: Number of elements
        
        Returns:
            Phase shifts (rad)
        """
        return [self.beam.phase_shift(steering_angle_deg, i)
                for i in range(num_elements)]
    
    def pointing_summary(self) -> Dict:
        """Get pointing summary."""
        az, el = self.gimbal.get_pointing()
        rate = self.tracker.tracking_rate()
        return {
            "azimuth": az,
            "elevation": el,
            "az_rate": rate[0],
            "el_rate": rate[1],
            "beamwidth_8el": self.beam.beamwidth(8)
        }
