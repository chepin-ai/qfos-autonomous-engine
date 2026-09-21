"""
Legged Locomotion Module
Gait patterns, foot trajectory planning,
stance/swing phase control, and terrain adaptation for autonomous robotics.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class FootState:
    """Foot position and contact state."""
    x: float
    y: float
    z: float
    in_contact: bool


class GaitPattern:
    """
    Quadruped gait pattern generation.
    """
    
    def __init__(self, num_legs: int = 4):
        """
        Args:
            num_legs: Number of legs
        """
        self.num_legs = num_legs
    
    def trot_gait(self, phase: float) -> List[bool]:
        """
        Generate trot gait contact pattern.
        
        Args:
            phase: Gait phase [0, 1]
        
        Returns:
            Contact states for each leg
        """
        # Diagonal pairs: FL+RR and FR+RL
        return [phase < 0.5, phase >= 0.5, phase >= 0.5, phase < 0.5]
    
    def walk_gait(self, phase: float) -> List[bool]:
        """
        Generate walk gait contact pattern.
        
        Args:
            phase: Gait phase [0, 1]
        
        Returns:
            Contact states
        """
        # Wave gait: each leg has 25% duty cycle offset
        contacts = []
        for i in range(self.num_legs):
            leg_phase = (phase + i * 0.25) % 1.0
            contacts.append(leg_phase > 0.25)
        return contacts
    
    def pace_gait(self, phase: float) -> List[bool]:
        """
        Generate pace gait (lateral pairs).
        
        Args:
            phase: Gait phase [0, 1]
        
        Returns:
            Contact states
        """
        # Left side then right side
        return [phase < 0.5, phase < 0.5, phase >= 0.5, phase >= 0.5]
    
    def duty_factor(self, contact_sequence: List[bool]) -> float:
        """
        Compute duty factor.
        
        Args:
            contact_sequence: Contact states over cycle
        
        Returns:
            Duty factor
        """
        if not contact_sequence:
            return 0.0
        return sum(contact_sequence) / len(contact_sequence)


class FootTrajectory:
    """
    Foot trajectory planning.
    """
    
    def __init__(self, step_height_m: float = 0.05):
        """
        Args:
            step_height_m: Maximum step height
        """
        self.h = step_height_m
    
    def swing_trajectory(self, phase: float,
                        start_x: float, end_x: float) -> Tuple[float, float]:
        """
        Compute swing foot position.
        
        Args:
            phase: Swing phase [0, 1]
            start_x: Start x position
            end_x: End x position
        
        Returns:
            (x, z) position
        """
        # Parabolic trajectory
        x = start_x + (end_x - start_x) * phase
        z = 4.0 * self.h * phase * (1.0 - phase)
        return x, z
    
    def bezier_swing(self, phase: float,
                    p0: Tuple[float, float],
                    p1: Tuple[float, float],
                    p2: Tuple[float, float],
                    p3: Tuple[float, float]) -> Tuple[float, float]:
        """
        Compute cubic Bezier swing trajectory.
        
        Args:
            phase: Swing phase
            p0: Start point
            p1: Control point 1
            p2: Control point 2
            p3: End point
        
        Returns:
            (x, z) position
        """
        t = phase
        t2 = t * t
        t3 = t2 * t
        mt = 1.0 - t
        mt2 = mt * mt
        mt3 = mt2 * mt
        
        x = mt3 * p0[0] + 3.0 * mt2 * t * p1[0] + 3.0 * mt * t2 * p2[0] + t3 * p3[0]
        z = mt3 * p0[1] + 3.0 * mt2 * t * p1[1] + 3.0 * mt * t2 * p2[1] + t3 * p3[1]
        return x, z


class PhaseController:
    """
    Stance/swing phase controller.
    """
    
    def __init__(self, stance_duration_s: float = 0.3,
                 swing_duration_s: float = 0.2):
        """
        Args:
            stance_duration_s: Stance duration
            swing_duration_s: Swing duration
        """
        self.T_stance = stance_duration_s
        self.T_swing = swing_duration_s
    
    def gait_cycle_time(self) -> float:
        """
        Compute total gait cycle time.
        
        Returns:
            Cycle time
        """
        return self.T_stance + self.T_swing
    
    def phase_progression(self, time_s: float) -> float:
        """
        Compute normalized phase.
        
        Args:
            time_s: Current time
        
        Returns:
            Phase [0, 1]
        """
        T = self.gait_cycle_time()
        return (time_s % T) / T
    
    def is_stance(self, phase: float) -> bool:
        """
        Check if in stance phase.
        
        Args:
            phase: Normalized phase
        
        Returns:
            True if stance
        """
        return phase < self.T_stance / self.gait_cycle_time()


class TerrainAdaptation:
    """
    Terrain adaptation for legged robots.
    """
    
    def __init__(self):
        pass
    
    def ground_clearance(self, terrain_height_map: List[float],
                        nominal_clearance_m: float = 0.1) -> float:
        """
        Compute adaptive ground clearance.
        
        Args:
            terrain_height_map: Height samples
            nominal_clearance_m: Nominal clearance
        
        Returns:
            Adjusted clearance
        """
        if not terrain_height_map:
            return nominal_clearance_m
        roughness = max(terrain_height_map) - min(terrain_height_map)
        return nominal_clearance_m + 0.5 * roughness
    
    def step_length_adjustment(self, terrain_slope_deg: float,
                              nominal_step_m: float = 0.3) -> float:
        """
        Adjust step length for slope.
        
        Args:
            terrain_slope_deg: Slope angle
            nominal_step_m: Nominal step length
        
        Returns:
            Adjusted step length
        """
        slope_rad = math.radians(terrain_slope_deg)
        # Reduce step length on steep slopes
        reduction = max(0.0, math.sin(slope_rad))
        return nominal_step_m * (1.0 - 0.3 * reduction)


class LeggedLocomotion:
    """
    Unified legged locomotion controller.
    """
    
    def __init__(self):
        self.gait = GaitPattern()
        self.trajectory = FootTrajectory()
        self.phase = PhaseController()
        self.terrain = TerrainAdaptation()
    
    def locomotion_summary(self) -> Dict:
        """Get summary."""
        return {
            "gaits": ["walk", "trot", "pace"],
            "control": ["trajectory", "phase", "terrain_adaptation"]
        }
