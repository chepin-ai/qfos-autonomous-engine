"""
Landing Site Selection Module
Evaluate and rank potential landing sites based on safety,
science value, accessibility, and illumination.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class LandingSite:
    """A candidate landing site."""
    name: str
    lat_deg: float
    lon_deg: float
    elevation_m: float
    slope_deg: float
    roughness_m: float
    illumination_hours: float = 12.0
    science_value: float = 0.5
    accessibility_score: float = 0.5


class LandingSiteSelector:
    """
    Landing site selection engine.
    
    Evaluates candidate sites using multi-criteria scoring
    for safety, science, and operational constraints.
    """
    
    def __init__(self, max_slope_deg: float = 15.0,
                 max_roughness_m: float = 0.5,
                 min_illumination_hours: float = 8.0):
        """
        Args:
            max_slope_deg: Maximum safe slope
            max_roughness_m: Maximum surface roughness
            min_illumination_hours: Minimum daily illumination
        """
        self.max_slope = max_slope_deg
        self.max_roughness = max_roughness_m
        self.min_illumination = min_illumination_hours
        self.sites: List[LandingSite] = []
    
    def add_candidate(self, site: LandingSite):
        """Add a candidate site."""
        self.sites.append(site)
    
    def safety_score(self, site: LandingSite) -> float:
        """
        Compute safety score (0.0-1.0).
        
        Based on slope and roughness.
        """
        slope_score = max(0.0, 1.0 - site.slope_deg / self.max_slope)
        roughness_score = max(0.0, 1.0 - site.roughness_m / self.max_roughness)
        
        # Combined: geometric mean
        return math.sqrt(slope_score * roughness_score)
    
    def illumination_score(self, site: LandingSite) -> float:
        """
        Compute illumination score (0.0-1.0).
        """
        if site.illumination_hours < self.min_illumination:
            return 0.0
        
        # Score improves up to 14 hours, then plateaus
        return min(1.0, site.illumination_hours / 14.0)
    
    def overall_score(self, site: LandingSite,
                      weights: Optional[Dict[str, float]] = None) -> float:
        """
        Compute weighted overall score.
        
        Args:
            site: Landing site
            weights: Dict of criterion weights (safety, science, illumination, accessibility)
        
        Returns:
            Score 0.0-1.0
        """
        w = weights or {"safety": 0.4, "science": 0.2, "illumination": 0.2, "accessibility": 0.2}
        
        safety = self.safety_score(site)
        illum = self.illumination_score(site)
        
        score = (w.get("safety", 0.25) * safety +
                 w.get("science", 0.25) * site.science_value +
                 w.get("illumination", 0.25) * illum +
                 w.get("accessibility", 0.25) * site.accessibility_score)
        
        return round(score, 4)
    
    def evaluate_all(self, weights: Optional[Dict[str, float]] = None) -> List[Dict]:
        """
        Evaluate all candidate sites.
        
        Args:
            weights: Scoring weights
        
        Returns:
            Sorted list of results
        """
        results = []
        for site in self.sites:
            results.append({
                "name": site.name,
                "lat_deg": site.lat_deg,
                "lon_deg": site.lon_deg,
                "safety_score": round(self.safety_score(site), 4),
                "illumination_score": round(self.illumination_score(site), 4),
                "science_value": site.science_value,
                "accessibility": site.accessibility_score,
                "overall_score": self.overall_score(site, weights),
                "slope_deg": site.slope_deg,
                "roughness_m": site.roughness_m,
                "elevation_m": site.elevation_m
            })
        
        results.sort(key=lambda x: x["overall_score"], reverse=True)
        return results
    
    def filter_safe(self, min_score: float = 0.5) -> List[LandingSite]:
        """
        Filter to safe sites only.
        
        Args:
            min_score: Minimum safety score
        
        Returns:
            Safe sites
        """
        return [s for s in self.sites if self.safety_score(s) >= min_score]
    
    def site_separation_km(self, site1: LandingSite, site2: LandingSite) -> float:
        """
        Compute separation between sites.
        
        Args:
            site1, site2: Two sites
        
        Returns:
            Separation in km
        """
        dlat = math.radians(site2.lat_deg - site1.lat_deg)
        dlon = math.radians(site2.lon_deg - site1.lon_deg)
        
        lat1 = math.radians(site1.lat_deg)
        lat2 = math.radians(site2.lat_deg)
        
        a = (math.sin(dlat/2)**2 +
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
        c = 2.0 * math.asin(min(1.0, math.sqrt(a)))
        
        # Assume Mars radius if not specified
        r = 3396.2  # km
        return r * c
    
    def diversity_selection(self, num_sites: int = 3,
                            min_separation_km: float = 10.0) -> List[Dict]:
        """
        Select diverse top sites.
        
        Ensures minimum separation between selected sites.
        
        Args:
            num_sites: Number of sites to select
            min_separation_km: Minimum separation
        
        Returns:
            Selected sites
        """
        evaluated = self.evaluate_all()
        selected = []
        
        for candidate in evaluated:
            if len(selected) >= num_sites:
                break
            
            # Check separation from already selected
            candidate_site = next((s for s in self.sites
                                   if s.name == candidate["name"]), None)
            
            too_close = False
            for sel in selected:
                sel_site = next((s for s in self.sites
                                if s.name == sel["name"]), None)
                if candidate_site and sel_site:
                    sep = self.site_separation_km(candidate_site, sel_site)
                    if sep < min_separation_km:
                        too_close = True
                        break
            
            if not too_close:
                selected.append(candidate)
        
        return selected
    
    def landing_ellipse_feasibility(self, site: LandingSite,
                                    ellipse_major_km: float = 10.0,
                                    ellipse_minor_km: float = 5.0) -> Dict:
        """
        Assess landing ellipse feasibility.
        
        Args:
            site: Target site
            ellipse_major_km: Ellipse semi-major axis
            ellipse_minor_km: Ellipse semi-minor axis
        
        Returns:
            Feasibility assessment
        """
        area_km2 = math.pi * ellipse_major_km * ellipse_minor_km
        
        # Check if ellipse contains hazards
        # Simplified: assume ellipse centered on site
        hazard_fraction = 0.0
        if site.slope_deg > self.max_slope * 0.5:
            hazard_fraction += 0.3
        if site.roughness_m > self.max_roughness * 0.5:
            hazard_fraction += 0.3
        
        safe_fraction = max(0.0, 1.0 - hazard_fraction)
        
        return {
            "ellipse_area_km2": round(area_km2, 2),
            "safe_fraction": round(safe_fraction, 3),
            "feasible": safe_fraction > 0.5,
            "major_axis_km": ellipse_major_km,
            "minor_axis_km": ellipse_minor_km
        }
    
    @staticmethod
    def create_mars_candidates() -> List[LandingSite]:
        """Create sample Mars landing site candidates."""
        return [
            LandingSite("Jezero Crater", 18.4, 77.5, -2.5, 5.0, 0.2,
                       illumination_hours=12.0, science_value=0.95, accessibility_score=0.7),
            LandingSite("Gale Crater", -5.4, 137.8, -4.5, 3.0, 0.15,
                       illumination_hours=11.0, science_value=0.9, accessibility_score=0.8),
            LandingSite("Meridiani Planum", -2.0, 5.5, -1.5, 2.0, 0.1,
                       illumination_hours=10.0, science_value=0.75, accessibility_score=0.9),
            LandingSite("Valles Marineris", -14.0, -59.0, -5.0, 25.0, 1.5,
                       illumination_hours=9.0, science_value=0.85, accessibility_score=0.4),
            LandingSite("Acidalia Planitia", 45.0, -25.0, -4.0, 1.5, 0.3,
                       illumination_hours=8.0, science_value=0.6, accessibility_score=0.8),
            LandingSite("Hellas Planitia", -42.0, 70.0, -7.0, 2.0, 0.2,
                       illumination_hours=10.0, science_value=0.7, accessibility_score=0.6)
        ]
