"""
Delta-V Budget Module
Comprehensive mission delta-V analysis and propellant budgeting.
Aggregates all maneuver costs across mission phases.
"""

import math
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class DeltaVItem:
    """A single delta-V budget item."""
    name: str
    delta_v_ms: float
    margin_percent: float = 10.0
    description: str = ""
    
    def total_with_margin(self) -> float:
        """Get delta-V with margin."""
        return self.delta_v_ms * (1.0 + self.margin_percent / 100.0)


@dataclass
class MissionPhase:
    """A mission phase with delta-V budget."""
    name: str
    items: List[DeltaVItem] = field(default_factory=list)
    
    def phase_total_ms(self) -> float:
        """Total delta-V for phase."""
        return sum(item.total_with_margin() for item in self.items)
    
    def phase_nominal_ms(self) -> float:
        """Nominal delta-V (without margin)."""
        return sum(item.delta_v_ms for item in self.items)


class DeltaVBudget:
    """
    Mission delta-V budget analyzer.
    
    Builds comprehensive delta-V budgets with margins,
    contingency, and propellant mass estimates.
    """
    
    def __init__(self, dry_mass_kg: float = 1000.0,
                 isp_seconds: float = 300.0,
                 contingency_percent: float = 5.0):
        """
        Args:
            dry_mass_kg: Spacecraft dry mass
            isp_seconds: Engine specific impulse
            contingency_percent: Extra contingency margin
        """
        self.dry_mass_kg = dry_mass_kg
        self.isp_seconds = isp_seconds
        self.contingency_percent = contingency_percent
        self.phases: List[MissionPhase] = []
    
    def add_phase(self, phase: MissionPhase):
        """Add a mission phase."""
        self.phases.append(phase)
    
    def add_orbit_transfer(self, from_altitude_km: float, to_altitude_km: float,
                           name: str = "Orbit Transfer"):
        """
        Add Hohmann transfer delta-V.
        
        Args:
            from_altitude_km: Initial altitude
            to_altitude_km: Final altitude
            name: Phase name
        """
        # Compute Hohmann transfer manually (km/s)
        mu = 398600.4418  # km^3/s^2
        re = 6378.0
        r1 = re + from_altitude_km
        r2 = re + to_altitude_km
        
        # Circular orbit velocities
        v1 = math.sqrt(mu / r1)
        v2 = math.sqrt(mu / r2)
        
        # Transfer orbit
        a_transfer = (r1 + r2) / 2.0
        v_transfer_peri = math.sqrt(mu * (2.0/r1 - 1.0/a_transfer))
        v_transfer_apo = math.sqrt(mu * (2.0/r2 - 1.0/a_transfer))
        
        # Delta-Vs in m/s
        dv1_ms = abs(v_transfer_peri - v1) * 1000.0
        dv2_ms = abs(v2 - v_transfer_apo) * 1000.0
        
        phase = MissionPhase(name=name, items=[
            DeltaVItem("departure_burn", dv1_ms, 5.0, "First Hohmann burn"),
            DeltaVItem("arrival_burn", dv2_ms, 5.0, "Second Hohmann burn")
        ])
        self.add_phase(phase)
    
    def add_station_keeping(self, annual_dv_ms: float,
                            mission_years: float,
                            name: str = "Station Keeping"):
        """
        Add station-keeping delta-V.
        
        Args:
            annual_dv_ms: Annual station-keeping budget
            mission_years: Mission duration
            name: Phase name
        """
        total = annual_dv_ms * mission_years
        phase = MissionPhase(name=name, items=[
            DeltaVItem("drag_makeup", total * 0.6, 15.0, "Drag makeup maneuvers"),
            DeltaVItem("inclination_drift", total * 0.2, 15.0, "Inclination maintenance"),
            DeltaVItem("other_sk", total * 0.2, 15.0, "Other station-keeping")
        ])
        self.add_phase(phase)
    
    def add_attitude_control(self, annual_dv_ms: float,
                             mission_years: float,
                             name: str = "Attitude Control"):
        """Add attitude control delta-V."""
        total = annual_dv_ms * mission_years
        phase = MissionPhase(name=name, items=[
            DeltaVItem("momentum_dumping", total * 0.7, 10.0, "Momentum wheel dumping"),
            DeltaVItem("attitude_slew", total * 0.3, 10.0, "Attitude slews")
        ])
        self.add_phase(phase)
    
    def add_end_of_life(self, deorbit_altitude_km: Optional[float] = None,
                        name: str = "End of Life"):
        """
        Add end-of-life delta-V.
        
        Args:
            deorbit_altitude_km: Target deorbit altitude (None = disposal orbit)
            name: Phase name
        """
        if deorbit_altitude_km is not None:
            from orbital_mechanics import hohmann_transfer_delta_v
            r1 = 6378.0 + deorbit_altitude_km + 100.0  # Current orbit
            r2 = 6378.0 + deorbit_altitude_km
            dv_total, _ = hohmann_transfer_delta_v(r1, r2)
            phase = MissionPhase(name=name, items=[
                DeltaVItem("deorbit_burn", dv_total, 10.0, "Deorbit maneuver")
            ])
        else:
            phase = MissionPhase(name=name, items=[
                DeltaVItem("disposal_orbit", 10.0, 20.0, "Disposal orbit insertion")
            ])
        self.add_phase(phase)
    
    def total_delta_v_ms(self) -> float:
        """Total mission delta-V with all margins."""
        total = sum(phase.phase_total_ms() for phase in self.phases)
        # Add contingency
        return total * (1.0 + self.contingency_percent / 100.0)
    
    def total_nominal_ms(self) -> float:
        """Total nominal delta-V."""
        return sum(phase.phase_nominal_ms() for phase in self.phases)
    
    def propellant_mass_kg(self) -> float:
        """
        Compute required propellant mass using Tsiolkovsky.
        
        m_prop = m_dry * (exp(dV / (g0 * Isp)) - 1)
        """
        g0 = 9.80665  # m/s^2
        dv = self.total_delta_v_ms()
        mass_ratio = math.exp(dv / (g0 * self.isp_seconds))
        propellant = self.dry_mass_kg * (mass_ratio - 1.0)
        return round(propellant, 3)
    
    def wet_mass_kg(self) -> float:
        """Total wet mass (dry + propellant)."""
        return self.dry_mass_kg + self.propellant_mass_kg()
    
    def budget_summary(self) -> Dict:
        """Get complete budget summary."""
        phase_summaries = []
        for phase in self.phases:
            phase_summaries.append({
                "name": phase.name,
                "nominal_ms": round(phase.phase_nominal_ms(), 2),
                "with_margin_ms": round(phase.phase_total_ms(), 2),
                "items": [
                    {
                        "name": item.name,
                        "nominal_ms": round(item.delta_v_ms, 2),
                        "margin_percent": item.margin_percent,
                        "total_ms": round(item.total_with_margin(), 2)
                    }
                    for item in phase.items
                ]
            })
        
        return {
            "phases": phase_summaries,
            "total_nominal_ms": round(self.total_nominal_ms(), 2),
            "total_with_margins_ms": round(
                sum(phase.phase_total_ms() for phase in self.phases), 2
            ),
            "total_with_contingency_ms": round(self.total_delta_v_ms(), 2),
            "contingency_percent": self.contingency_percent,
            "dry_mass_kg": self.dry_mass_kg,
            "propellant_mass_kg": round(self.propellant_mass_kg(), 3),
            "wet_mass_kg": round(self.wet_mass_kg(), 3),
            "isp_seconds": self.isp_seconds,
            "propellant_fraction": round(
                self.propellant_mass_kg() / self.wet_mass_kg(), 4
            )
        }
    
    @staticmethod
    def create_leo_mission(dry_mass_kg: float = 1000.0,
                           altitude_km: float = 400.0,
                           mission_years: float = 5.0,
                           station_keeping_annual_ms: float = 5.0) -> 'DeltaVBudget':
        """
        Create a standard LEO mission budget.
        
        Args:
            dry_mass_kg: Dry mass
            altitude_km: Orbit altitude
            mission_years: Mission duration
            station_keeping_annual_ms: Annual SK budget
        
        Returns:
            Pre-configured DeltaVBudget
        """
        budget = DeltaVBudget(dry_mass_kg=dry_mass_kg)
        
        # Station keeping
        budget.add_station_keeping(station_keeping_annual_ms, mission_years)
        
        # Attitude control
        budget.add_attitude_control(2.0, mission_years)
        
        # End of life (deorbit)
        budget.add_end_of_life(deorbit_altitude_km=100.0)
        
        return budget
    
    @staticmethod
    def create_geo_mission(dry_mass_kg: float = 2000.0,
                           mission_years: float = 15.0) -> 'DeltaVBudget':
        """Create a standard GEO mission budget."""
        budget = DeltaVBudget(dry_mass_kg=dry_mass_kg, isp_seconds=450.0)
        
        # LEO to GEO transfer
        budget.add_orbit_transfer(200.0, 35786.0, name="LEO to GEO Transfer")
        
        # Station keeping (GEO needs E-W and N-S)
        budget.add_station_keeping(50.0, mission_years, name="GEO Station Keeping")
        
        # Attitude control
        budget.add_attitude_control(5.0, mission_years)
        
        # End of life (graveyard orbit)
        budget.add_end_of_life(name="Graveyard Orbit Insertion")
        
        return budget
