"""
Relative Navigation Module
Estimate relative position, velocity, and attitude between
spacecraft using optical, lidar, and RF measurements.
"""

import math
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class RelativeState:
    """Relative navigation state."""
    range_m: float
    range_rate_ms: float
    relative_position_m: Tuple[float, float, float]
    relative_velocity_ms: Tuple[float, float, float]
    relative_attitude_deg: Tuple[float, float, float]  # Euler angles
    timestamp_s: float = 0.0


class RelativeNavigator:
    """
    Relative navigator for proximity operations.
    
    Fuses multiple sensors to estimate relative state
    between chaser and target spacecraft.
    """
    
    def __init__(self, sensor_types: List[str] = None):
        """
        Args:
            sensor_types: List of sensor types ("camera", "lidar", "radar", "gps")
        """
        self.sensor_types = sensor_types or ["camera"]
        self.history: List[RelativeState] = []
        self.filter_state: Optional[RelativeState] = None
    
    def measure_range_optical(self, apparent_diameter_px: float,
                               focal_length_px: float,
                               target_actual_diameter_m: float) -> float:
        """
        Estimate range from optical apparent size.
        
        Args:
            apparent_diameter_px: Apparent diameter in pixels
            focal_length_px: Focal length in pixels
            target_actual_diameter_m: True target diameter
        
        Returns:
            Estimated range in meters
        """
        if apparent_diameter_px <= 0.0:
            return float('inf')
        
        # range = (true_size * focal_length) / apparent_size
        # Convert pixel measurements to angular size
        angular_size_rad = apparent_diameter_px / focal_length_px
        if angular_size_rad <= 0.0:
            return float('inf')
        
        range_m = target_actual_diameter_m / angular_size_rad
        return range_m
    
    def measure_range_lidar(self, time_of_flight_ns: float) -> float:
        """
        Estimate range from LIDAR time of flight.
        
        Args:
            time_of_flight_ns: Round-trip time in nanoseconds
        
        Returns:
            Range in meters
        """
        c = 299792458.0  # m/s
        return (c * time_of_flight_ns * 1.0e-9) / 2.0
    
    def measure_range_rate_doppler(self, doppler_shift_hz: float,
                                    transmit_frequency_hz: float) -> float:
        """
        Estimate range rate from Doppler shift.
        
        Args:
            doppler_shift_hz: Measured Doppler shift
            transmit_frequency_hz: Transmit frequency
        
        Returns:
            Range rate in m/s
        """
        c = 299792458.0
        # v = c * fd / ft
        return c * doppler_shift_hz / transmit_frequency_hz
    
    def triangulate_position(self, bearings: List[Dict]) -> Tuple[float, float, float]:
        """
        Triangulate position from multiple bearing measurements.
        
        Args:
            bearings: List of dicts with sensor_pos, bearing_unit
        
        Returns:
            Estimated position
        """
        if len(bearings) < 2:
            return (0.0, 0.0, 0.0)
        
        # Simple least-squares triangulation
        # For each pair of bearings, find intersection
        # Use first two for simplicity
        s1 = bearings[0]["sensor_pos"]
        d1 = bearings[0]["bearing_unit"]
        s2 = bearings[1]["sensor_pos"]
        d2 = bearings[1]["bearing_unit"]
        
        # Solve: s1 + t1*d1 = s2 + t2*d2
        # (d1, -d2) * (t1, t2)^T = s2 - s1
        # Use cross product method for closest approach
        dx = s2[0] - s1[0]
        dy = s2[1] - s1[1]
        dz = s2[2] - s1[2]
        
        # Cross product d1 x d2
        cx = d1[1]*d2[2] - d1[2]*d2[1]
        cy = d1[2]*d2[0] - d1[0]*d2[2]
        cz = d1[0]*d2[1] - d1[1]*d2[0]
        
        # If parallel, return midpoint
        cross_mag = math.sqrt(cx**2 + cy**2 + cz**2)
        if cross_mag < 1e-10:
            mid = ((s1[0]+s2[0])/2.0, (s1[1]+s2[1])/2.0, (s1[2]+s2[2])/2.0)
            return mid
        
        # Distance between lines
        diff_cross = (dy*cz - dz*cy, dz*cx - dx*cz, dx*cy - dy*cx)
        distance = abs(diff_cross[0]*cx + diff_cross[1]*cy + diff_cross[2]*cz) / cross_mag
        
        # Midpoint of closest approach
        # Simplified: average of points along each line at nearest approach
        # Using projection
        dot = d1[0]*d2[0] + d1[1]*d2[1] + d1[2]*d2[2]
        denom = 1.0 - dot**2
        if abs(denom) < 1e-10:
            return ((s1[0]+s2[0])/2.0, (s1[1]+s2[1])/2.0, (s1[2]+s2[2])/2.0)
        
        t1 = (-dot * (d2[0]*dx + d2[1]*dy + d2[2]*dz) + (d1[0]*dx + d1[1]*dy + d1[2]*dz)) / denom
        
        p1 = (s1[0] + t1*d1[0], s1[1] + t1*d1[1], s1[2] + t1*d1[2])
        return p1
    
    def update_filter(self, measurement: Dict) -> RelativeState:
        """
        Update relative state estimate.
        
        Args:
            measurement: Dict with range, range_rate, angles, etc.
        
        Returns:
            Updated relative state
        """
        range_m = measurement.get("range_m", 1000.0)
        range_rate = measurement.get("range_rate_ms", 0.0)
        
        # Extract angles if available
        az_deg = measurement.get("azimuth_deg", 0.0)
        el_deg = measurement.get("elevation_deg", 0.0)
        
        az = math.radians(az_deg)
        el = math.radians(el_deg)
        
        # Position in line-of-sight coordinates
        x = range_m * math.cos(el) * math.cos(az)
        y = range_m * math.cos(el) * math.sin(az)
        z = range_m * math.sin(el)
        
        # Velocity (simplified: along line of sight)
        vx = range_rate * math.cos(el) * math.cos(az)
        vy = range_rate * math.cos(el) * math.sin(az)
        vz = range_rate * math.sin(el)
        
        state = RelativeState(
            range_m=round(range_m, 3),
            range_rate_ms=round(range_rate, 4),
            relative_position_m=(round(x, 3), round(y, 3), round(z, 3)),
            relative_velocity_ms=(round(vx, 4), round(vy, 4), round(vz, 4)),
            relative_attitude_deg=(0.0, 0.0, 0.0),
            timestamp_s=measurement.get("timestamp_s", 0.0)
        )
        
        self.history.append(state)
        self.filter_state = state
        
        return state
    
    def estimate_approach_time(self, current_state: RelativeState) -> float:
        """
        Estimate time to closest approach.
        
        Args:
            current_state: Current relative state
        
        Returns:
            Time to closest approach in seconds
        """
        r = current_state.range_m
        v = current_state.range_rate_ms
        
        if v >= 0.0:
            return float('inf')
        
        return -r / v
    
    def safety_assessment(self, state: RelativeState,
                          keep_out_sphere_m: float = 200.0,
                          approach_cone_deg: float = 15.0) -> Dict:
        """
        Assess safety of relative trajectory.
        
        Args:
            state: Current relative state
            keep_out_sphere_m: Keep-out sphere radius
            approach_cone_deg: Approach corridor half-angle
        
        Returns:
            Safety assessment
        """
        pos = state.relative_position_m
        range_m = math.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2)
        
        # Check keep-out sphere
        in_keep_out = range_m < keep_out_sphere_m
        
        # Check approach cone (pointing along -x)
        if range_m > 0.0:
            cos_angle = -pos[0] / range_m
            angle_deg = math.degrees(math.acos(max(-1.0, min(1.0, cos_angle))))
            in_cone = angle_deg < approach_cone_deg
        else:
            angle_deg = 0.0
            in_cone = True
        
        # Approach rate check
        closing = state.range_rate_ms < 0.0
        
        status = "SAFE"
        if in_keep_out and not in_cone:
            status = "VIOLATION"
        elif in_keep_out and abs(state.range_rate_ms) > 2.0:
            status = "CAUTION"
        elif range_m < keep_out_sphere_m * 2.0:
            status = "PROXIMATE"
        
        return {
            "range_m": round(range_m, 2),
            "range_rate_ms": round(state.range_rate_ms, 4),
            "in_keep_out_sphere": in_keep_out,
            "in_approach_cone": in_cone,
            "approach_angle_deg": round(angle_deg, 2),
            "closing": closing,
            "status": status,
            "time_to_approach_s": round(self.estimate_approach_time(state), 2)
        }
