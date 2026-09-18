# QF-OS Autonomous Navigation Engine

Real-data-driven autonomous navigation system for orbital operations, using NASA/JPL Small-Body Database (SBDB) API for live asteroid orbital elements.

## Features

- **Real NASA Data**: Fetches live orbital elements from NASA/JPL SBDB API
- **Orbital Mechanics**: Full orbital propagation using Keplerian elements
- **Collision Avoidance**: Automated hazard detection and risk assessment
- **Transfer Planning**: Hohmann transfer delta-v calculations
- **Unit Tested**: Comprehensive test suite with real asteroid data

## Quick Start

```python
from src.navigation_engine import AutonomousNavigationEngine

# Initialize engine
engine = AutonomousNavigationEngine("MySpacecraft")
engine.initialize_spacecraft(a_au=1.0, e=0.0167, i_deg=0.0)

# Load real asteroid data
engine.load_asteroid_database(["Apophis", "Bennu", "2024 YR4"])

# Run hazard scan
hazards = engine.run_hazard_scan()
for h in hazards:
    print(f"{h.target_name}: {h.risk_level} (MOID: {h.moid_au} AU)")
```

## Project Structure

```
qfos-autonomous-engine/
  src/
    orbital_mechanics.py      # Core orbital calculations
    data_connector.py         # NASA SBDB API integration
    collision_avoidance.py    # Hazard detection & avoidance
    navigation_engine.py      # Main autonomous engine
  tests/
    test_orbital_mechanics.py # Orbital mechanics tests
    test_collision_avoidance.py # Collision avoidance tests
```

## Running Tests

```bash
cd qfos-autonomous-engine
python -m pytest tests/ -v
```

## Data Source

- [NASA/JPL Small-Body Database (SBDB)](https://ssd-api.jpl.nasa.gov/doc/sbdb.html)
- Real asteroid orbital elements updated continuously

## License

QF-OS Federation License
