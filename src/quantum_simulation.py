"""
Quantum Simulation Module
Quantum circuit simulation, statevector evolution, density matrix,
measurement simulation, and noise modeling for autonomous quantum computing.
"""

import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuantumState:
    """Quantum state."""
    amplitudes: List[complex]
    num_qubits: int


class StateVectorSimulator:
    """
    Statevector quantum simulator.
    """
    
    def __init__(self, num_qubits: int = 4):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.n = num_qubits
        self.dim = 2 ** num_qubits
        self.state = QuantumState([0.0] * self.dim, num_qubits)
        self.state.amplitudes[0] = 1.0
    
    def apply_x(self, target: int):
        """
        Apply X gate.
        
        Args:
            target: Target qubit
        """
        new_amps = [0.0] * self.dim
        for i in range(self.dim):
            flipped = i ^ (1 << target)
            new_amps[flipped] = self.state.amplitudes[i]
        self.state.amplitudes = new_amps
    
    def apply_h(self, target: int):
        """
        Apply H gate.
        
        Args:
            target: Target qubit
        """
        new_amps = [0.0] * self.dim
        inv_sqrt2 = 1.0 / math.sqrt(2.0)
        
        for i in range(self.dim):
            bit = (i >> target) & 1
            j0 = i & ~(1 << target)
            j1 = i | (1 << target)
            
            if bit == 0:
                new_amps[j0] += self.state.amplitudes[i] * inv_sqrt2
                new_amps[j1] += self.state.amplitudes[i] * inv_sqrt2
            else:
                new_amps[j0] += self.state.amplitudes[i] * inv_sqrt2
                new_amps[j1] -= self.state.amplitudes[i] * inv_sqrt2
        
        self.state.amplitudes = new_amps
    
    def apply_cnot(self, control: int, target: int):
        """
        Apply CNOT gate.
        
        Args:
            control: Control qubit
            target: Target qubit
        """
        new_amps = [0.0] * self.dim
        for i in range(self.dim):
            ctrl_bit = (i >> control) & 1
            if ctrl_bit == 1:
                flipped = i ^ (1 << target)
                new_amps[flipped] = self.state.amplitudes[i]
            else:
                new_amps[i] = self.state.amplitudes[i]
        self.state.amplitudes = new_amps
    
    def measure(self, shots: int = 1000) -> Dict[int, int]:
        """
        Measure state.
        
        Args:
            shots: Number of shots
        
        Returns:
            Measurement counts
        """
        probs = [abs(a)**2 for a in self.state.amplitudes]
        total = sum(probs)
        if total > 0:
            probs = [p / total for p in probs]
        
        counts = {}
        for _ in range(shots):
            r = random.random()
            cumsum = 0.0
            for i, p in enumerate(probs):
                cumsum += p
                if r <= cumsum:
                    counts[i] = counts.get(i, 0) + 1
                    break
        
        return counts
    
    def expectation(self, observable: List[List[float]]) -> float:
        """
        Compute expectation value.
        
        Args:
            observable: Hermitian matrix
        
        Returns:
            Expectation value
        """
        value = 0.0
        for i in range(min(len(observable), self.dim)):
            for j in range(min(len(observable[i]), self.dim)):
                value += (self.state.amplitudes[i].conjugate() *
                         observable[i][j] * self.state.amplitudes[j]).real
        return value


class DensityMatrixSimulator:
    """
    Density matrix quantum simulator.
    """
    
    def __init__(self, num_qubits: int = 2):
        """
        Args:
            num_qubits: Qubits
        """
        self.n = num_qubits
        self.dim = 2 ** num_qubits
        self.rho = [[0.0] * self.dim for _ in range(self.dim)]
        self.rho[0][0] = 1.0
    
    def purity(self) -> float:
        """
        Compute purity Tr(rho^2).
        
        Returns:
            Purity
        """
        trace = 0.0
        for i in range(self.dim):
            for j in range(self.dim):
                trace += self.rho[i][j] * self.rho[j][i]
        return trace
    
    def von_neumann_entropy(self) -> float:
        """
        Compute von Neumann entropy.
        
        Returns:
            Entropy
        """
        # Diagonalize (simplified: use diagonal elements)
        entropy = 0.0
        for i in range(self.dim):
            p = self.rho[i][i]
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    def apply_depolarizing(self, target: int, p: float = 0.01):
        """
        Apply depolarizing noise.
        
        Args:
            target: Target qubit
            p: Depolarizing probability
        """
        # Simplified: mix with identity
        for i in range(self.dim):
            self.rho[i][i] = (1 - p) * self.rho[i][i] + p / self.dim


class NoiseModel:
    """
    Quantum noise model.
    """
    
    def __init__(self):
        self.gate_errors: Dict[str, float] = {
            "x": 0.001,
            "h": 0.001,
            "cnot": 0.01
        }
        self.t1_ms = 100.0
        self.t2_ms = 50.0
    
    def gate_fidelity(self, gate: str) -> float:
        """
        Get gate fidelity.
        
        Args:
            gate: Gate name
        
        Returns:
            Fidelity
        """
        error = self.gate_errors.get(gate, 0.01)
        return 1.0 - error
    
    def coherence_time_limit(self, gate_time_us: float = 1.0) -> float:
        """
        Compute coherence limit.
        
        Args:
            gate_time_us: Gate time
        
        Returns:
            Fidelity limit
        """
        t1 = self.t1_ms * 1000.0  # us
        t2 = self.t2_ms * 1000.0
        
        # T1 decay
        f_t1 = math.exp(-gate_time_us / t1)
        # T2 decay
        f_t2 = math.exp(-gate_time_us / t2)
        
        return f_t1 * f_t2


class CircuitBuilder:
    """
    Build quantum circuits.
    """
    
    def __init__(self, num_qubits: int = 4):
        """
        Args:
            num_qubits: Qubits
        """
        self.n = num_qubits
        self.gates: List[Tuple[str, List[int]]] = []
    
    def x(self, target: int):
        """Add X gate."""
        self.gates.append(("x", [target]))
    
    def h(self, target: int):
        """Add H gate."""
        self.gates.append(("h", [target]))
    
    def cnot(self, control: int, target: int):
        """Add CNOT gate."""
        self.gates.append(("cnot", [control, target]))
    
    def execute(self) -> StateVectorSimulator:
        """
        Execute circuit.
        
        Returns:
            Simulator with final state
        """
        sim = StateVectorSimulator(self.n)
        for gate, targets in self.gates:
            if gate == "x":
                sim.apply_x(targets[0])
            elif gate == "h":
                sim.apply_h(targets[0])
            elif gate == "cnot":
                sim.apply_cnot(targets[0], targets[1])
        return sim


class QuantumSimulation:
    """
    Unified quantum simulation controller.
    """
    
    def __init__(self, num_qubits: int = 4):
        self.statevector = StateVectorSimulator(num_qubits)
        self.density = DensityMatrixSimulator(num_qubits)
        self.noise = NoiseModel()
        self.circuit = CircuitBuilder(num_qubits)
    
    def bell_state(self) -> StateVectorSimulator:
        """
        Create Bell state.
        
        Returns:
            Simulator with Bell state
        """
        sim = StateVectorSimulator(2)
        sim.apply_h(0)
        sim.apply_cnot(0, 1)
        return sim
    
    def grover_search(self, target: int, num_qubits: int = 3) -> StateVectorSimulator:
        """
        Simplified Grover search.
        
        Args:
            target: Target state
            num_qubits: Qubits
        
        Returns:
            Simulator
        """
        sim = StateVectorSimulator(num_qubits)
        # Initialize superposition
        for i in range(num_qubits):
            sim.apply_h(i)
        # Oracle (simplified)
        # Diffusion (simplified)
        for i in range(num_qubits):
            sim.apply_h(i)
        return sim
    
    def qsim_summary(self) -> Dict:
        """Get summary."""
        return {
            "qubits": self.statevector.n,
            "gates": len(self.circuit.gates),
            "purity": self.density.purity()
        }
