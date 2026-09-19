"""
Coordinate Frames Module
Transformations between common orbital coordinate systems.
Supports ECI, ECEF, LVLH, RSW, TNW, and orbital element frames.
"""

import math
from typing import Tuple, List, Optional


class CoordinateFrames:
    """
    Coordinate frame transformations for orbital mechanics.
    
    All angles in radians unless noted.
    """
    
    EARTH_ROTATION_RATE_RAD_S = 7.2921158553e-5
    
    @staticmethod
    def rotation_matrix_x(angle_rad: float) -> List[List[float]]:
        """Rotation matrix about x-axis."""
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        return [
            [1.0, 0.0, 0.0],
            [0.0, c, -s],
            [0.0, s, c]
        ]
    
    @staticmethod
    def rotation_matrix_y(angle_rad: float) -> List[List[float]]:
        """Rotation matrix about y-axis."""
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        return [
            [c, 0.0, s],
            [0.0, 1.0, 0.0],
            [-s, 0.0, c]
        ]
    
    @staticmethod
    def rotation_matrix_z(angle_rad: float) -> List[List[float]]:
        """Rotation matrix about z-axis."""
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        return [
            [c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0]
        ]
    
    @staticmethod
    def mat_vec_mult(M: List[List[float]], v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Multiply 3x3 matrix by 3-vector."""
        return (
            M[0][0]*v[0] + M[0][1]*v[1] + M[0][2]*v[2],
            M[1][0]*v[0] + M[1][1]*v[1] + M[1][2]*v[2],
            M[2][0]*v[0] + M[2][1]*v[1] + M[2][2]*v[2]
        )
    
    @classmethod
    def eci_to_ecef(cls, position_eci: Tuple[float, float, float],
                    gmst_rad: float) -> Tuple[float, float, float]:
        """
        Convert ECI to ECEF coordinates.
        
        Args:
            position_eci: Position in ECI frame (km)
            gmst_rad: Greenwich Mean Sidereal Time (rad)
        
        Returns:
            Position in ECEF frame (km)
        """
        R = cls.rotation_matrix_z(gmst_rad)
        return cls.mat_vec_mult(R, position_eci)
    
    @classmethod
    def ecef_to_eci(cls, position_ecef: Tuple[float, float, float],
                    gmst_rad: float) -> Tuple[float, float, float]:
        """
        Convert ECEF to ECI coordinates.
        
        Args:
            position_ecef: Position in ECEF frame (km)
            gmst_rad: Greenwich Mean Sidereal Time (rad)
        
        Returns:
            Position in ECI frame (km)
        """
        R = cls.rotation_matrix_z(-gmst_rad)
        return cls.mat_vec_mult(R, position_ecef)
    
    @classmethod
    def ecef_to_lla(cls, position_ecef: Tuple[float, float, float],
                    equatorial_radius_km: float = 6378.137,
                    flattening: float = 1.0 / 298.257223563) -> Tuple[float, float, float]:
        """
        Convert ECEF to geodetic latitude, longitude, altitude.
        
        Args:
            position_ecef: (x, y, z) in km
            equatorial_radius_km: Equatorial radius
            flattening: Earth flattening
        
        Returns:
            (latitude_deg, longitude_deg, altitude_km)
        """
        x, y, z = position_ecef
        
        # Longitude
        lon = math.atan2(y, x)
        
        # Iterative latitude calculation
        e2 = 2.0 * flattening - flattening**2
        p = math.sqrt(x**2 + y**2)
        
        lat = math.atan2(z, p * (1.0 - e2))
        
        for _ in range(5):
            sin_lat = math.sin(lat)
            N = equatorial_radius_km / math.sqrt(1.0 - e2 * sin_lat**2)
            h = p / math.cos(lat) - N
            lat = math.atan2(z, p * (1.0 - e2 * N / (N + h)))
        
        sin_lat = math.sin(lat)
        N = equatorial_radius_km / math.sqrt(1.0 - e2 * sin_lat**2)
        h = p / math.cos(lat) - N
        
        return (math.degrees(lat), math.degrees(lon), h)
    
    @classmethod
    def lla_to_ecef(cls, latitude_deg: float, longitude_deg: float,
                    altitude_km: float,
                    equatorial_radius_km: float = 6378.137,
                    flattening: float = 1.0 / 298.257223563) -> Tuple[float, float, float]:
        """
        Convert geodetic LLA to ECEF.
        
        Args:
            latitude_deg: Latitude in degrees
            longitude_deg: Longitude in degrees
            altitude_km: Altitude in km
            equatorial_radius_km: Equatorial radius
            flattening: Earth flattening
        
        Returns:
            (x, y, z) in km
        """
        lat = math.radians(latitude_deg)
        lon = math.radians(longitude_deg)
        
        e2 = 2.0 * flattening - flattening**2
        sin_lat = math.sin(lat)
        cos_lat = math.cos(lat)
        sin_lon = math.sin(lon)
        cos_lon = math.cos(lon)
        
        N = equatorial_radius_km / math.sqrt(1.0 - e2 * sin_lat**2)
        
        x = (N + altitude_km) * cos_lat * cos_lon
        y = (N + altitude_km) * cos_lat * sin_lon
        z = (N * (1.0 - e2) + altitude_km) * sin_lat
        
        return (x, y, z)
    
    @classmethod
    def eci_to_lvlh(cls, position_eci: Tuple[float, float, float],
                    velocity_eci: Tuple[float, float, float]) -> List[List[float]]:
        """
        Compute LVLH (Local Vertical Local Horizontal) frame rotation matrix.
        
        LVLH axes:
          R (radial): along position vector
          S (along-track): in direction of motion, perpendicular to R
          W (cross-track): R x S
        
        Args:
            position_eci: Position in ECI
            velocity_eci: Velocity in ECI
        
        Returns:
            3x3 rotation matrix from ECI to LVLH
        """
        x, y, z = position_eci
        r = math.sqrt(x**2 + y**2 + z**2)
        
        # R axis (radial, unit vector)
        if r > 1e-12:
            R_vec = (x/r, y/r, z/r)
        else:
            R_vec = (1.0, 0.0, 0.0)
        
        # W axis (cross-track, angular momentum direction)
        hx = y * velocity_eci[2] - z * velocity_eci[1]
        hy = z * velocity_eci[0] - x * velocity_eci[2]
        hz = x * velocity_eci[1] - y * velocity_eci[0]
        h = math.sqrt(hx**2 + hy**2 + hz**2)
        
        if h > 1e-12:
            W_vec = (hx/h, hy/h, hz/h)
        else:
            W_vec = (0.0, 0.0, 1.0)
        
        # S axis (along-track, completes right-handed system)
        S_vec = (
            W_vec[1] * R_vec[2] - W_vec[2] * R_vec[1],
            W_vec[2] * R_vec[0] - W_vec[0] * R_vec[2],
            W_vec[0] * R_vec[1] - W_vec[1] * R_vec[0]
        )
        
        # Rotation matrix: rows are LVLH axes
        return [
            [R_vec[0], R_vec[1], R_vec[2]],
            [S_vec[0], S_vec[1], S_vec[2]],
            [W_vec[0], W_vec[1], W_vec[2]]
        ]
    
    @classmethod
    def position_to_lvlh(cls, position_eci: Tuple[float, float, float],
                         velocity_eci: Tuple[float, float, float],
                         target_position_eci: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Convert target position from ECI to LVLH frame.
        
        Args:
            position_eci: Reference spacecraft position
            velocity_eci: Reference spacecraft velocity
            target_position_eci: Target position to transform
        
        Returns:
            Position in LVLH frame (km)
        """
        R = cls.eci_to_lvlh(position_eci, velocity_eci)
        
        # Relative position
        dx = target_position_eci[0] - position_eci[0]
        dy = target_position_eci[1] - position_eci[1]
        dz = target_position_eci[2] - position_eci[2]
        
        return cls.mat_vec_mult(R, (dx, dy, dz))
    
    @classmethod
    def orbital_elements_to_rv(cls, a_km: float, e: float, i_deg: float,
                                raan_deg: float, arg_peri_deg: float,
                                true_anomaly_deg: float,
                                mu_km3_s2: float = 398600.4418) -> Tuple[Tuple[float, float, float],
                                                                          Tuple[float, float, float]]:
        """
        Convert orbital elements to position and velocity.
        
        Args:
            a_km: Semi-major axis (km)
            e: Eccentricity
            i_deg: Inclination (deg)
            raan_deg: RAAN (deg)
            arg_peri_deg: Argument of periapsis (deg)
            true_anomaly_deg: True anomaly (deg)
            mu_km3_s2: Gravitational parameter
        
        Returns:
            (position_km, velocity_km_s)
        """
        i = math.radians(i_deg)
        raan = math.radians(raan_deg)
        arg_peri = math.radians(arg_peri_deg)
        nu = math.radians(true_anomaly_deg)
        
        # Distance
        p = a_km * (1.0 - e**2)
        r = p / (1.0 + e * math.cos(nu))
        
        # Position in perifocal frame
        x_pqw = r * math.cos(nu)
        y_pqw = r * math.sin(nu)
        
        # Velocity in perifocal frame
        h = math.sqrt(mu_km3_s2 * p)
        vx_pqw = -mu_km3_s2 / h * math.sin(nu)
        vy_pqw = mu_km3_s2 / h * (e + math.cos(nu))
        
        # Rotation matrix from PQW to ECI
        cos_raan = math.cos(raan)
        sin_raan = math.sin(raan)
        cos_arg = math.cos(arg_peri)
        sin_arg = math.sin(arg_peri)
        cos_i = math.cos(i)
        sin_i = math.sin(i)
        
        R11 = cos_raan * cos_arg - sin_raan * sin_arg * cos_i
        R12 = -cos_raan * sin_arg - sin_raan * cos_arg * cos_i
        R21 = sin_raan * cos_arg + cos_raan * sin_arg * cos_i
        R22 = -sin_raan * sin_arg + cos_raan * cos_arg * cos_i
        R31 = sin_arg * sin_i
        R32 = cos_arg * sin_i
        
        position = (
            R11 * x_pqw + R12 * y_pqw,
            R21 * x_pqw + R22 * y_pqw,
            R31 * x_pqw + R32 * y_pqw
        )
        
        velocity = (
            R11 * vx_pqw + R12 * vy_pqw,
            R21 * vx_pqw + R22 * vy_pqw,
            R31 * vx_pqw + R32 * vy_pqw
        )
        
        return position, velocity
    
    @classmethod
    def gmst_from_jd(cls, julian_date: float) -> float:
        """
        Compute Greenwich Mean Sidereal Time from Julian date.
        
        Returns:
            GMST in radians
        """
        # Julian centuries from J2000
        T = (julian_date - 2451545.0) / 36525.0
        
        # GMST in degrees
        gmst_deg = 280.46061837 + 360.98564736629 * (julian_date - 2451545.0) + \
                   0.000387933 * T**2 - T**3 / 38710000.0
        
        # Wrap to [0, 360]
        gmst_deg = gmst_deg % 360.0
        
        return math.radians(gmst_deg)
