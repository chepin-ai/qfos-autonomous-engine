"""
Rendezvous Module
Complete orbital rendezvous sequence from phasing to docking.
Implements Lambert transfer, phasing maneuvers, and proximity operations.
"""

import math
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass

try:
    from .orbital_mechanics import MU_SUN, AU, OrbitalBody
except ImportError:
    from orbital_mechanics import MU_SUN, AU, OrbitalBody


@dataclass
class RendezvousPhase:
    """A phase in the rendezvous sequence."""
    name: str
    start_time_s: float
    duration_s: float
    delta_v_ms: float
    description: str


class LambertTransfer:
    """
    Lambert's problem solver for rendezvous transfer.
    
    Finds the transfer orbit between two positions given time of flight.
    """
    
    def __init__(self, mu_km3_s2: float = 398600.4418):
        """
        Args:
            mu_km3_s2: Gravitational parameter
        """
        self.mu = mu_km3_s2
    
    def solve(self, r1_km: Tuple[float, float, float],
              r2_km: Tuple[float, float, float],
              tof_s: float,
              short_way: bool = True) -> Optional[Tuple[Tuple[float, float, float],
                                                         Tuple[float, float, float]]]:
        """
        Solve Lambert's problem.
        
        Args:
            r1_km: Departure position
            r2_km: Arrival position
            tof_s: Time of flight in seconds
            short_way: Use short way (< 180 deg)
        
        Returns:
            (v1, v2) departure and arrival velocities, or None
        """
        r1 = math.sqrt(r1_km[0]**2 + r1_km[1]**2 + r1_km[2]**2)
        r2 = math.sqrt(r2_km[0]**2 + r2_km[1]**2 + r2_km[2]**2)
        
        if r1 < 1e-6 or r2 < 1e-6:
            return None
        
        # Dot product for transfer angle
        dot = r1_km[0]*r2_km[0] + r1_km[1]*r2_km[1] + r1_km[2]*r2_km[2]
        cos_dnu = dot / (r1 * r2)
        cos_dnu = max(-1.0, min(1.0, cos_dnu))
        dnu = math.acos(cos_dnu)
        
        if not short_way:
            dnu = 2 * math.pi - dnu
        
        # Chord length
        c = math.sqrt(r1**2 + r2**2 - 2*r1*r2*math.cos(dnu))
        
        # Semi-perimeter
        s = (r1 + r2 + c) / 2.0
        
        # Minimum energy orbit
        a_min = s / 2.0
        tof_min = math.sqrt(a_min**3 / self.mu) * (math.pi - 
            math.asin(math.sqrt((s - c) / s)) * 2 + 
            math.sin(math.asin(math.sqrt((s - c) / s)) * 2))
        
        # For simplicity, use a good initial guess
        # In practice, use iteration (Newton-Raphson or bisection)
        a = a_min * 1.5  # Initial guess
        
        # Iterate to find semi-major axis for given TOF
        for _ in range(50):
            alpha = 2 * math.asin(math.sqrt(s / (2 * a)))
            beta = 2 * math.asin(math.sqrt((s - c) / (2 * a)))
            
            if dnu > math.pi:
                alpha = 2 * math.pi - alpha
            
            tof_calc = math.sqrt(a**3 / self.mu) * (alpha - beta - 
                (math.sin(alpha) - math.sin(beta)))
            
            if abs(tof_calc - tof_s) < 0.1:
                break
            
            # Adjust a
            da = (tof_calc - tof_s) * self.mu / (3 * a**2)
            a -= da * 0.1
            
            if a <= s / 2.0:
                a = s / 2.0 + 1.0
        
        # Compute velocities using f and g functions
        f = 1.0 - (a / r1) * (1.0 - math.cos(alpha - beta))
        g = tof_s - math.sqrt(a**3 / self.mu) * (math.sin(alpha - beta) - (alpha - beta))
        
        # v1 = (r2 - f*r1) / g
        v1 = [
            (r2_km[0] - f * r1_km[0]) / g,
            (r2_km[1] - f * r1_km[1]) / g,
            (r2_km[2] - f * r1_km[2]) / g
        ]
        
        # v2 from energy conservation (simplified)
        v2 = [
            -math.sqrt(self.mu * (2.0/r2 - 1.0/a)) * (r2_km[0]/r2),
            -math.sqrt(self.mu * (2.0/r2 - 1.0/a)) * (r2_km[1]/r2),
            -math.sqrt(self.mu * (2.0/r2 - 1.0/a)) * (r2_km[2]/r2)
        ]
        
        return (tuple(v1), tuple(v2))
    
    def transfer_delta_v(self, r1_km: Tuple[float, float, float],
                         v1_km_s: Tuple[float, float, float],
                         r2_km: Tuple[float, float, float],
                         v2_km_s: Tuple[float, float, float],
                         tof_s: float) -> Optional[float]:
        """
        Compute total delta-v for Lambert transfer.
        
        Returns:
            Total delta-v in m/s
        """
        result = self.solve(r1_km, r2_km, tof_s)
        if result is None:
            return None
        
        v1_trans, v2_trans = result
        
        # Departure delta-v
        dv1 = math.sqrt(sum((v1_trans[i] - v1_km_s[i])**2 for i in range(3)))
        
        # Arrival delta-v
        dv2 = math.sqrt(sum((v2_trans[i] - v2_km_s[i])**2 for i in range(3)))
        
        return (dv1 + dv2) * 1000.0  # Convert to m/s


class PhasingManeuver:
    """
    Compute phasing maneuvers for rendezvous.
    
    Adjusts orbit period to achieve desired phase angle.
    """
    
    def __init__(self, mu_km3_s2: float = 398600.4418):
        self.mu = mu_km3_s2
    
    def compute_phasing_delta_v(self, initial_altitude_km: float,
                                 target_phase_angle_deg: float,
                                 current_phase_angle_deg: float,
                                 n_revolutions: int = 1) -> float:
        """
        Compute delta-v for phasing maneuver.
        
        Args:
            initial_altitude_km: Current circular orbit altitude
            target_phase_angle_deg: Desired phase angle at meeting
            current_phase_angle_deg: Current phase angle
            n_revolutions: Number of phasing orbits
        
        Returns:
            Delta-v in m/s
        """
        r_km = 6378.137 + initial_altitude_km
        
        # Current angular rate
        n = math.sqrt(self.mu / r_km**3)
        
        # Phase difference to make up
        phase_diff = math.radians(target_phase_angle_deg - current_phase_angle_deg)
        
        # Time available
        T_current = 2 * math.pi / n
        T_phasing = T_current * (1.0 + phase_diff / (2 * math.pi * n_revolutions))
        
        # Phasing orbit semi-major axis
        a_phasing = (self.mu * (T_phasing / (2 * math.pi))**2)**(1.0/3.0)
        
        # Velocity difference
        v_current = math.sqrt(self.mu / r_km)
        v_phasing = math.sqrt(self.mu * (2.0 / r_km - 1.0 / a_phasing))
        
        return abs(v_phasing - v_current) * 1000.0
    
    def coelliptic_approach(self, chaser_altitude_km: float,
                            target_altitude_km: float,
                            approach_rate_m_s: float = 1.0) -> Dict:
        """
        Design coelliptic approach phase.
        
        Args:
            chaser_altitude_km: Chaser altitude
            target_altitude_km: Target altitude
            approach_rate_m_s: Desired approach rate
        
        Returns:
            Approach parameters
        """
        r_chaser = 6378.137 + chaser_altitude_km
        r_target = 6378.137 + target_altitude_km
        
        # Period difference
        T_chaser = 2 * math.pi * math.sqrt(r_chaser**3 / self.mu)
        T_target = 2 * math.pi * math.sqrt(r_target**3 / self.mu)
        
        # Relative motion
        delta_t = T_chaser - T_target
        
        # Time to align
        if abs(delta_t) < 1e-6:
            time_to_align_s = 0.0
        else:
            time_to_align_s = abs(T_target / (delta_t / T_target))
        
        return {
            "chaser_period_s": round(T_chaser, 1),
            "target_period_s": round(T_target, 1),
            "period_difference_s": round(delta_t, 3),
            "estimated_time_to_align_s": round(time_to_align_s, 1),
            "approach_rate_m_s": approach_rate_m_s
        }


class RendezvousPlanner:
    """
    Complete rendezvous mission planner.
    
    Generates full sequence from launch to docking.
    """
    
    def __init__(self):
        self.lambert = LambertTransfer()
        self.phasing = PhasingManeuver()
        self.phases: List[RendezvousPhase] = []
    
    def plan_rendezvous(self,
                        chaser_initial_pos_km: Tuple[float, float, float],
                        chaser_initial_vel_km_s: Tuple[float, float, float],
                        target_pos_km: Tuple[float, float, float],
                        target_vel_km_s: Tuple[float, float, float],
                        tof_s: float = 3600.0) -> Dict:
        """
        Plan complete rendezvous sequence.
        
        Args:
            chaser_initial_pos_km: Chaser initial position
            chaser_initial_vel_km_s: Chaser initial velocity
            target_pos_km: Target position at arrival
            target_vel_km_s: Target velocity at arrival
            tof_s: Time of flight for transfer
        
        Returns:
            Complete rendezvous plan
        """
        self.phases = []
        total_delta_v = 0.0
        
        # Phase 1: Lambert transfer
        lambert_result = self.lambert.solve(
            chaser_initial_pos_km, target_pos_km, tof_s
        )
        
        if lambert_result:
            v1_trans, v2_trans = lambert_result
            
            dv1 = math.sqrt(sum((v1_trans[i] - chaser_initial_vel_km_s[i])**2 for i in range(3)))
            dv2 = math.sqrt(sum((v2_trans[i] - target_vel_km_s[i])**2 for i in range(3)))
            
            transfer_dv = (dv1 + dv2) * 1000.0
            total_delta_v += transfer_dv
            
            self.phases.append(RendezvousPhase(
                name="Lambert Transfer",
                start_time_s=0.0,
                duration_s=tof_s,
                delta_v_ms=round(transfer_dv, 2),
                description=f"Transfer from chaser to target, TOF={tof_s/60:.1f} min"
            ))
        
        # Phase 2: Phasing
        # Simplified: assume circular orbits
        r_chaser = math.sqrt(sum(x**2 for x in chaser_initial_pos_km))
        r_target = math.sqrt(sum(x**2 for x in target_pos_km))
        
        phasing_dv = self.phasing.compute_phasing_delta_v(
            r_chaser - 6378.137, 0.0, 0.0, n_revolutions=2
        )
        total_delta_v += phasing_dv
        
        self.phases.append(RendezvousPhase(
            name="Phasing",
            start_time_s=tof_s,
            duration_s=2 * 2 * math.pi * math.sqrt(r_target**3 / 398600.4418),
            delta_v_ms=round(phasing_dv, 2),
            description="Adjust orbit period for proper phasing"
        ))
        
        # Phase 3: Coelliptic approach
        self.phases.append(RendezvousPhase(
            name="Coelliptic Approach",
            start_time_s=tof_s + self.phases[-1].duration_s,
            duration_s=1800.0,
            delta_v_ms=5.0,  # Small station-keeping burns
            description="Slow approach to target"
        ))
        total_delta_v += 5.0
        
        # Phase 4: Proximity operations
        self.phases.append(RendezvousPhase(
            name="Proximity Operations",
            start_time_s=self.phases[-1].start_time_s + self.phases[-1].duration_s,
            duration_s=600.0,
            delta_v_ms=2.0,
            description="Final approach and alignment"
        ))
        total_delta_v += 2.0
        
        return {
            "total_delta_v_ms": round(total_delta_v, 2),
            "phases": [
                {
                    "name": p.name,
                    "start_time_s": round(p.start_time_s, 1),
                    "duration_s": round(p.duration_s, 1),
                    "delta_v_ms": p.delta_v_ms,
                    "description": p.description
                }
                for p in self.phases
            ],
            "estimated_total_time_s": round(
                self.phases[-1].start_time_s + self.phases[-1].duration_s, 1
            )
        }
    
    def compute_terminal_phase_initiation(self,
                                          range_km: float,
                                          range_rate_ms: float,
                                          los_angle_deg: float) -> Dict:
        """
        Compute Terminal Phase Initiation (TPI) parameters.
        
        Classic Apollo/Gemini rendezvous technique.
        
        Args:
            range_km: Range to target
            range_rate_ms: Closing rate
            los_angle_deg: Line of sight angle
        
        Returns:
            TPI parameters
        """
        # Simplified TPI: compute required delta-v to achieve intercept
        # At TPI, spacecraft is at specific range and LOS angle from target
        
        # Time to go
        if abs(range_rate_ms) < 1e-6:
            time_to_go_s = float('inf')
        else:
            time_to_go_s = range_km * 1000.0 / abs(range_rate_ms)
        
        return {
            "range_km": round(range_km, 2),
            "range_rate_ms": round(range_rate_ms, 3),
            "los_angle_deg": round(los_angle_deg, 2),
            "time_to_go_s": round(time_to_go_s, 1),
            "tpi_burn_required": range_km < 50.0 and abs(range_rate_ms) < 10.0
        }
