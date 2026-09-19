"""
NASA/JPL SBDB Data Connector
Fetches real asteroid orbital elements from the Small-Body Database API.
"""

import requests
import json
from typing import Dict, Optional, List
try:
    from .orbital_mechanics import OrbitalBody
except ImportError:
    from orbital_mechanics import OrbitalBody

SBDB_API_URL = "https://ssd-api.jpl.nasa.gov/sbdb.api"


class SBDBConnector:
    """Connector to NASA/JPL Small-Body Database API."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
    
    def fetch_by_designation(self, designation: str, full_prec: bool = True) -> Optional[Dict]:
        """Fetch asteroid data by designation (e.g., '2024 YR4', 'Apophis')."""
        params = {"sstr": designation}
        if full_prec:
            params["full-prec"] = "true"
        
        try:
            resp = self.session.get(SBDB_API_URL, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch {designation}: {e}")
            return None
    
    def parse_to_orbital_body(self, raw_data: Dict) -> Optional[OrbitalBody]:
        """Parse SBDB API response into OrbitalBody."""
        try:
            obj = raw_data.get('object', {})
            orbit = raw_data.get('orbit', {})
            elements = orbit.get('elements', [])
            
            def get_elem(name: str) -> float:
                for e in elements:
                    if e.get('name') == name:
                        return float(e['value'])
                return 0.0
            
            return OrbitalBody(
                name=obj.get('fullname', 'Unknown'),
                spkid=str(obj.get('spkid', '')),
                a_au=get_elem('a'),
                e=get_elem('e'),
                i_deg=get_elem('i'),
                omega_deg=get_elem('om'),
                Omega_deg=get_elem('node'),
                epoch=orbit.get('epoch')
            )
        except (KeyError, ValueError, TypeError) as e:
            print(f"[ERROR] Parse failed: {e}")
            return None
    
    def get_body(self, designation: str) -> Optional[OrbitalBody]:
        """High-level fetch: designation -> OrbitalBody."""
        raw = self.fetch_by_designation(designation)
        if raw:
            return self.parse_to_orbital_body(raw)
        return None
    
    def fetch_multiple(self, designations: List[str]) -> Dict[str, OrbitalBody]:
        """Fetch multiple asteroids. Returns dict of {designation: OrbitalBody}."""
        results = {}
        for desig in designations:
            body = self.get_body(desig)
            if body:
                results[desig] = body
        return results
