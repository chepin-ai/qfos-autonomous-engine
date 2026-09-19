"""
Ground Station Pass Scheduler Module
Schedule and optimize ground station contacts for spacecraft communication.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


EARTH_RADIUS_KM = 6371.0
EARTH_ROTATION_RATE = 7.2921159e-5  # rad/s


@dataclass
class GroundStation:
    """A ground station on Earth."""
    name: str
    latitude_deg: float
    longitude_deg: float
    altitude_m: float = 0.0
    min_elevation_deg: float = 5.0  # Minimum elevation for contact
    max_range_km: float = 3000.0    # Maximum slant range
    dish_diameter_m: float = 10.0
    supported_bands: List[str] = None
    
    def __post_init__(self):
        if self.supported_bands is None:
            self.supported_bands = ["S", "X"]


@dataclass
class PassPrediction:
    """Predicted ground station pass."""
    station_name: str
    aos_time: float  # Acquisition of signal (seconds from epoch)
    los_time: float  # Loss of signal (seconds from epoch)
    max_elevation_deg: float
    duration_s: float
    max_range_km: float
    data_volume_mb: float = 0.0
    scheduled: bool = False


class GroundStationScheduler:
    """
    Predict and schedule ground station passes for a spacecraft.
    
    Uses simplified orbital geometry for pass prediction.
    """
    
    def __init__(self, stations: List[GroundStation] = None):
        self.stations = stations or []
    
    def add_station(self, station: GroundStation):
        """Add a ground station."""
        self.stations.append(station)
    
    def predict_passes(self,
                       sc_latitude_deg: float,
                       sc_altitude_km: float,
                       orbital_period_min: float,
                       start_time: float = 0.0,
                       duration_hours: float = 24.0) -> List[PassPrediction]:
        """
        Predict ground station passes for a spacecraft.
        
        Simplified model assuming near-equatorial orbit.
        
        Args:
            sc_latitude_deg: Spacecraft orbital inclination (approx latitude coverage)
            sc_altitude_km: Orbital altitude
            orbital_period_min: Orbital period in minutes
            start_time: Start time (seconds from epoch)
            duration_hours: Prediction window
        
        Returns:
            List of predicted passes
        """
        passes = []
        
        # Maximum Earth central angle visible from altitude
        earth_angle_max = math.degrees(math.acos(EARTH_RADIUS_KM / (EARTH_RADIUS_KM + sc_altitude_km)))
        
        for station in self.stations:
            # Check if orbit covers this station's latitude
            if abs(station.latitude_deg) > abs(sc_latitude_deg) + 10:
                continue
            
            # Approximate: one pass per orbital period
            num_orbits = int((duration_hours * 60) / orbital_period_min)
            
            for orbit in range(num_orbits):
                # Approximate pass time (simplified)
                orbit_start = start_time + orbit * orbital_period_min * 60
                
                # Pass duration depends on max elevation
                # Higher max elevation = shorter pass
                max_el = min(90.0, abs(sc_latitude_deg - station.latitude_deg) + 45.0)
                pass_duration = 600 * math.sin(math.radians(max_el))  # ~10 min max
                
                if pass_duration < 60:  # Skip very short passes
                    continue
                
                # AOS/LOS times
                aos = orbit_start + 300  # Approximate mid-pass offset
                los = aos + pass_duration
                
                # Max range (at AOS/LOS)
                max_range = math.sqrt(
                    sc_altitude_km**2 + 2 * EARTH_RADIUS_KM * sc_altitude_km
                )
                
                # Data volume (simplified)
                data_rate_mbps = 10.0 if "X" in station.supported_bands else 1.0
                data_volume = data_rate_mbps * pass_duration / 8.0  # MB
                
                passes.append(PassPrediction(
                    station_name=station.name,
                    aos_time=aos,
                    los_time=los,
                    max_elevation_deg=max_el,
                    duration_s=pass_duration,
                    max_range_km=max_range,
                    data_volume_mb=data_volume
                ))
        
        # Sort by AOS time
        passes.sort(key=lambda p: p.aos_time)
        return passes
    
    def schedule_passes(self, passes: List[PassPrediction],
                        data_backlog_mb: float,
                        priority_stations: List[str] = None) -> Dict:
        """
        Schedule passes to maximize data downlink.
        
        Args:
            passes: Available passes
            data_backlog_mb: Data waiting to be downlinked
            priority_stations: Station names with priority
        
        Returns:
            Scheduling results
        """
        priority_stations = priority_stations or []
        
        # Score each pass
        scored_passes = []
        for p in passes:
            score = p.data_volume_mb * (p.duration_s / 600.0)  # Volume * duration factor
            
            # Boost priority stations
            if p.station_name in priority_stations:
                score *= 1.5
            
            # Penalize short passes
            if p.duration_s < 300:
                score *= 0.5
            
            scored_passes.append((score, p))
        
        # Sort by score descending
        scored_passes.sort(key=lambda x: x[0], reverse=True)
        
        # Greedily schedule non-overlapping passes
        scheduled = []
        total_data = 0.0
        
        for score, p in scored_passes:
            # Check for overlap with already scheduled passes
            overlap = False
            for sp in scheduled:
                if not (p.los_time < sp.aos_time or p.aos_time > sp.los_time):
                    overlap = True
                    break
            
            if not overlap:
                p.scheduled = True
                scheduled.append(p)
                total_data += p.data_volume_mb
                
                if total_data >= data_backlog_mb:
                    break
        
        return {
            "scheduled_passes": len(scheduled),
            "total_passes_available": len(passes),
            "data_capacity_mb": round(total_data, 2),
            "data_backlog_mb": round(data_backlog_mb, 2),
            "backlog_cleared": total_data >= data_backlog_mb,
            "schedule": [
                {
                    "station": p.station_name,
                    "aos": p.aos_time,
                    "los": p.los_time,
                    "duration_min": round(p.duration_s / 60.0, 1),
                    "data_mb": round(p.data_volume_mb, 2)
                }
                for p in sorted(scheduled, key=lambda x: x.aos_time)
            ]
        }
    
    def contact_summary(self, station_name: str, passes: List[PassPrediction]) -> Dict:
        """Get summary statistics for a specific ground station."""
        station_passes = [p for p in passes if p.station_name == station_name]
        
        if not station_passes:
            return {"station": station_name, "total_passes": 0}
        
        total_duration = sum(p.duration_s for p in station_passes)
        total_data = sum(p.data_volume_mb for p in station_passes)
        avg_elevation = sum(p.max_elevation_deg for p in station_passes) / len(station_passes)
        
        return {
            "station": station_name,
            "total_passes": len(station_passes),
            "total_contact_time_min": round(total_duration / 60.0, 1),
            "total_data_capacity_mb": round(total_data, 2),
            "avg_max_elevation_deg": round(avg_elevation, 1),
            "longest_pass_min": round(max(p.duration_s for p in station_passes) / 60.0, 1)
        }
