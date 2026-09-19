"""
Thermal Management Module
Heat sink modeling, radiator sizing, and temperature
control for spacecraft thermal regulation.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class ThermalNode:
    """A thermal node in the spacecraft."""
    name: str
    mass: float  # kg
    specific_heat: float  # J/(kg·K)
    temperature: float = 300.0  # K
    heat_generation: float = 0.0  # W
    
    def thermal_capacity(self) -> float:
        """Get thermal capacity (J/K)."""
        return self.mass * self.specific_heat


@dataclass
class Radiator:
    """A spacecraft radiator."""
    name: str
    area: float  # m^2
    emissivity: float  # 0-1
    absorptivity: float  # 0-1
    efficiency: float = 0.85
    
    def radiated_power(self, temp: float,
                      ambient_temp: float = 3.0) -> float:
        """
        Compute radiated power using Stefan-Boltzmann.
        
        Args:
            temp: Radiator temperature (K)
            ambient_temp: Ambient temperature (K)
        
        Returns:
            Radiated power (W)
        """
        sigma = 5.67e-8  # Stefan-Boltzmann constant
        return self.efficiency * self.emissivity * self.area * sigma * (
            temp**4 - ambient_temp**4
        )
    
    def required_area(self, power: float, temp: float,
                     ambient_temp: float = 3.0) -> float:
        """
        Compute required radiator area.
        
        Args:
            power: Power to dissipate (W)
            temp: Operating temperature (K)
            ambient_temp: Ambient temperature (K)
        
        Returns:
            Required area (m^2)
        """
        sigma = 5.67e-8
        delta = temp**4 - ambient_temp**4
        if delta <= 0:
            return float('inf')
        return power / (self.efficiency * self.emissivity * sigma * delta)


@dataclass
class HeatPipe:
    """A heat pipe for thermal transfer."""
    name: str
    thermal_conductance: float  # W/K
    max_heat_transfer: float  # W
    
    def transfer_heat(self, temp_hot: float, temp_cold: float) -> float:
        """
        Compute heat transferred.
        
        Args:
            temp_hot: Hot side temperature (K)
            temp_cold: Cold side temperature (K)
        
        Returns:
            Heat transferred (W)
        """
        if temp_hot <= temp_cold:
            return 0.0
        q = self.thermal_conductance * (temp_hot - temp_cold)
        return min(q, self.max_heat_transfer)


class ThermalNetwork:
    """
    Thermal network solver for spacecraft nodes.
    """
    
    def __init__(self):
        self.nodes: Dict[str, ThermalNode] = {}
        self.heat_pipes: List[Tuple[str, str, HeatPipe]] = []
        self.radiators: Dict[str, Radiator] = {}
        self.node_radiator: Dict[str, str] = {}
    
    def add_node(self, node: ThermalNode):
        """Add thermal node."""
        self.nodes[node.name] = node
    
    def add_heat_pipe(self, node1: str, node2: str, pipe: HeatPipe):
        """Add heat pipe between nodes."""
        self.heat_pipes.append((node1, node2, pipe))
    
    def add_radiator(self, node_name: str, radiator: Radiator):
        """Attach radiator to node."""
        self.radiators[radiator.name] = radiator
        self.node_radiator[node_name] = radiator.name
    
    def step(self, dt: float) -> Dict[str, float]:
        """
        Advance thermal simulation by one time step.
        
        Args:
            dt: Time step (seconds)
        
        Returns:
            Updated temperatures
        """
        new_temps = {}
        
        for name, node in self.nodes.items():
            # Internal heat generation
            q_in = node.heat_generation
            
            # Heat from connected nodes via heat pipes
            for n1, n2, pipe in self.heat_pipes:
                if n1 == name:
                    q_in += pipe.transfer_heat(self.nodes[n1].temperature,
                                               self.nodes[n2].temperature)
                elif n2 == name:
                    q_in += pipe.transfer_heat(self.nodes[n2].temperature,
                                               self.nodes[n1].temperature)
            
            # Heat lost via radiator
            if name in self.node_radiator:
                rad_name = self.node_radiator[name]
                radiator = self.radiators[rad_name]
                q_out = radiator.radiated_power(node.temperature)
                q_in -= q_out
            
            # Temperature change: dT = Q * dt / C
            capacity = node.thermal_capacity()
            if capacity > 0:
                dT = q_in * dt / capacity
                new_temps[name] = node.temperature + dT
            else:
                new_temps[name] = node.temperature
        
        # Update node temperatures
        for name, temp in new_temps.items():
            self.nodes[name].temperature = temp
        
        return new_temps
    
    def simulate(self, duration: float, dt: float) -> Dict[str, List[float]]:
        """
        Run thermal simulation.
        
        Args:
            duration: Total simulation time (seconds)
            dt: Time step (seconds)
        
        Returns:
            Temperature history
        """
        history = {name: [node.temperature] for name, node in self.nodes.items()}
        steps = int(duration / dt)
        
        for _ in range(steps):
            temps = self.step(dt)
            for name, temp in temps.items():
                history[name].append(temp)
        
        return history
    
    def get_temperatures(self) -> Dict[str, float]:
        """Get current temperatures."""
        return {name: node.temperature for name, node in self.nodes.items()}


class TemperatureController:
    """
    PID temperature controller for thermal regulation.
    """
    
    def __init__(self, kp: float = 1.0, ki: float = 0.1, kd: float = 0.5):
        """
        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_error = 0.0
    
    def compute(self, setpoint: float, measurement: float,
               dt: float) -> float:
        """
        Compute control output.
        
        Args:
            setpoint: Target temperature (K)
            measurement: Current temperature (K)
            dt: Time step (seconds)
        
        Returns:
            Control output (heating/cooling power in W)
        """
        error = setpoint - measurement
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        self.prev_error = error
        
        return self.kp * error + self.ki * self.integral + self.kd * derivative
    
    def reset(self):
        """Reset controller."""
        self.integral = 0.0
        self.prev_error = 0.0


class ThermalManagement:
    """
    Unified thermal management controller.
    """
    
    def __init__(self):
        self.network = ThermalNetwork()
        self.controllers: Dict[str, TemperatureController] = {}
    
    def add_node(self, node: ThermalNode):
        """Add thermal node."""
        self.network.add_node(node)
    
    def add_controller(self, node_name: str, controller: TemperatureController):
        """Add temperature controller for node."""
        self.controllers[node_name] = controller
    
    def regulate(self, dt: float) -> Dict[str, float]:
        """
        Regulate temperatures for one step.
        
        Args:
            dt: Time step (seconds)
        
        Returns:
            Control outputs
        """
        outputs = {}
        
        for name, controller in self.controllers.items():
            if name in self.network.nodes:
                temp = self.network.nodes[name].temperature
                output = controller.compute(300.0, temp, dt)
                # Apply control as negative heat generation (cooling)
                self.network.nodes[name].heat_generation -= output * 0.1
                outputs[name] = output
        
        # Step thermal network
        self.network.step(dt)
        
        return outputs
    
    def thermal_summary(self) -> Dict:
        """Get thermal summary."""
        temps = self.network.get_temperatures()
        return {
            "nodes": len(self.network.nodes),
            "avg_temperature": sum(temps.values()) / max(1, len(temps)),
            "max_temperature": max(temps.values()) if temps else 0,
            "min_temperature": min(temps.values()) if temps else 0
        }
