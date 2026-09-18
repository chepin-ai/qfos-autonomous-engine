"""
Orbital Visualization Module
Generates plots and visualizations of orbital data.
"""

import math
from typing import List, Tuple, Dict
try:
    from .orbital_mechanics import OrbitalBody
except ImportError:
    from orbital_mechanics import OrbitalBody


def generate_orbit_path(body: OrbitalBody, num_points: int = 360, 
                        time_span_days: float = 365.25) -> Tuple[List[float], List[float], List[float]]:
    """Generate 3D orbit path for plotting. Returns (x, y, z) lists in AU."""
    xs, ys, zs = [], [], []
    for i in range(num_points):
        t = time_span_days * i / num_points
        x, y, z = body.position_at_time(t)
        xs.append(x)
        ys.append(y)
        zs.append(z)
    return xs, ys, zs


def generate_multi_orbit_data(bodies: List[OrbitalBody], 
                               num_points: int = 200,
                               time_span_days: float = 730.0) -> Dict[str, Tuple]:
    """Generate orbit paths for multiple bodies."""
    data = {}
    for body in bodies:
        xs, ys, zs = generate_orbit_path(body, num_points, time_span_days)
        data[body.name] = (xs, ys, zs)
    return data


def orbital_elements_summary(body: OrbitalBody) -> Dict[str, float]:
    """Generate summary of key orbital parameters."""
    return {
        "semi_major_axis_au": round(body.semi_major_axis_au, 4),
        "eccentricity": round(body.e, 4),
        "inclination_deg": round(body.inclination_deg, 2),
        "period_years": round(body.period_years, 3),
        "perihelion_au": round(body.perihelion_m / 1.496e11, 4),
        "aphelion_au": round(body.aphelion_m / 1.496e11, 4),
        "velocity_perihelion_kms": round(body.velocity_at_perihelion() / 1000, 2),
        "velocity_aphelion_kms": round(body.velocity_at_aphelion() / 1000, 2),
    }


def create_ascii_orbit_plot(body: OrbitalBody, width: int = 60, height: int = 20) -> str:
    """Create a simple ASCII art orbit plot."""
    xs, ys, _ = generate_orbit_path(body, num_points=width)
    
    # Normalize to plot coordinates
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    
    # Scale to fit
    scale_x = (width - 2) / (x_max - x_min + 0.001)
    scale_y = (height - 2) / (y_max - y_min + 0.001)
    
    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Plot orbit
    for x, y in zip(xs, ys):
        px = int((x - x_min) * scale_x)
        py = int((y - y_min) * scale_y)
        if 0 <= px < width and 0 <= py < height:
            grid[height - 1 - py][px] = '.'
    
    # Mark sun at center
    sx = int((0 - x_min) * scale_x)
    sy = int((0 - y_min) * scale_y)
    if 0 <= sx < width and 0 <= sy < height:
        grid[height - 1 - sy][sx] = '*'
    
    lines = [''.join(row) for row in grid]
    header = f"Orbit: {body.name[:20]} (a={body.semi_major_axis_au:.2f} AU, e={body.e:.3f})"
    return header + '\n' + '\n'.join(lines)
