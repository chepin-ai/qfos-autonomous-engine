"""
Quantum Circuit Module
Quantum gate simulation, circuit execution, and qubit
state manipulation for quantum computing subsystems.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class QubitState:
    """State vector representation of qubits."""
    amplitudes: List[complex] = field(default_factory=list)
    num_qubits: int = 0
    
    def probability(self, index: int) -> float:
        """Get probability of measuring state |index>."""
        if index < 0 or index >= len(self.amplitudes):
            return 0.0
        amp = self.amplitudes[index]
        return abs(amp) ** 2
    
    def normalize(self):
        """Normalize state vector."""
        norm = math.sqrt(sum(abs(a) ** 2 for a in self.amplitudes))
        if norm > 0:
            self.amplitudes = [a / norm for a in self.amplitudes]


class QuantumGate:
    """Base class for quantum gates."""
    
    def __init__(self, matrix: List[List[complex]], name: str = ""):
        """
        Args:
            matrix: Unitary matrix
            name: Gate name
        """
        self.matrix = matrix
        self.name = name
        self.num_qubits = int(math.log2(len(matrix)))
    
    def apply(self, state: QubitState, target_qubits: List[int]) -> QubitState:
        """
        Apply gate to state.
        
        Args:
            state: Current state
            target_qubits: Target qubit indices
        
        Returns:
            New state
        """
        if self.num_qubits == 1:
            return self._apply_single(state, target_qubits[0])
        elif self.num_qubits == 2:
            return self._apply_two(state, target_qubits[0], target_qubits[1])
        return state
    
    def _apply_single(self, state: QubitState, target: int) -> QubitState:
        """Apply single-qubit gate."""
        n = state.num_qubits
        new_amplitudes = [0j] * len(state.amplitudes)
        
        for i in range(len(state.amplitudes)):
            bit = (i >> target) & 1
            partner = i ^ (1 << target)
            
            if bit == 0:
                new_amplitudes[i] += (self.matrix[0][0] * state.amplitudes[i] +
                                     self.matrix[0][1] * state.amplitudes[partner])
            else:
                new_amplitudes[i] += (self.matrix[1][0] * state.amplitudes[partner] +
                                     self.matrix[1][1] * state.amplitudes[i])
        
        result = QubitState(amplitudes=new_amplitudes, num_qubits=n)
        result.normalize()
        return result
    
    def _apply_two(self, state: QubitState, control: int, target: int) -> QubitState:
        """Apply two-qubit gate."""
        n = state.num_qubits
        new_amplitudes = state.amplitudes[:]
        
        for i in range(len(state.amplitudes)):
            c_bit = (i >> control) & 1
            t_bit = (i >> target) & 1
            
            if c_bit == 1 and self.name == "CNOT":
                partner = i ^ (1 << target)
                if i < partner:
                    new_amplitudes[i], new_amplitudes[partner] = (
                        new_amplitudes[partner], new_amplitudes[i]
                    )
        
        result = QubitState(amplitudes=new_amplitudes, num_qubits=n)
        result.normalize()
        return result


# Standard gates
H_GATE = QuantumGate(
    [[1/math.sqrt(2), 1/math.sqrt(2)],
     [1/math.sqrt(2), -1/math.sqrt(2)]],
    "H"
)

X_GATE = QuantumGate(
    [[0, 1],
     [1, 0]],
    "X"
)

Y_GATE = QuantumGate(
    [[0, -1j],
     [1j, 0]],
    "Y"
)

Z_GATE = QuantumGate(
    [[1, 0],
     [0, -1]],
    "Z"
)

CNOT_GATE = QuantumGate(
    [[1, 0, 0, 0],
     [0, 1, 0, 0],
     [0, 0, 0, 1],
     [0, 0, 1, 0]],
    "CNOT"
)


@dataclass
class GateOperation:
    """A gate operation in a circuit."""
    gate: QuantumGate
    targets: List[int]


class QuantumCircuit:
    """
    Quantum circuit builder and executor.
    """
    
    def __init__(self, num_qubits: int):
        """
        Args:
            num_qubits: Number of qubits
        """
        self.num_qubits = num_qubits
        self.operations: List[GateOperation] = []
        self.state = self._initial_state()
    
    def _initial_state(self) -> QubitState:
        """Create initial |0...0> state."""
        amplitudes = [0j] * (2 ** self.num_qubits)
        amplitudes[0] = 1.0
        return QubitState(amplitudes=amplitudes, num_qubits=self.num_qubits)
    
    def h(self, target: int):
        """Add Hadamard gate."""
        self.operations.append(GateOperation(H_GATE, [target]))
    
    def x(self, target: int):
        """Add Pauli-X gate."""
        self.operations.append(GateOperation(X_GATE, [target]))
    
    def y(self, target: int):
        """Add Pauli-Y gate."""
        self.operations.append(GateOperation(Y_GATE, [target]))
    
    def z(self, target: int):
        """Add Pauli-Z gate."""
        self.operations.append(GateOperation(Z_GATE, [target]))
    
    def cnot(self, control: int, target: int):
        """Add CNOT gate."""
        self.operations.append(GateOperation(CNOT_GATE, [control, target]))
    
    def execute(self) -> QubitState:
        """
        Execute circuit.
        
        Returns:
            Final state
        """
        self.state = self._initial_state()
        
        for op in self.operations:
            self.state = op.gate.apply(self.state, op.targets)
        
        return self.state
    
    def measure(self, shots: int = 1024) -> Dict[int, int]:
        """
        Measure state multiple times.
        
        Args:
            shots: Number of measurements
        
        Returns:
            Measurement counts
        """
        import random
        rng = random.Random(42)
        
        if not self.state.amplitudes:
            self.execute()
        
        counts = {}
        for _ in range(shots):
            r = rng.random()
            cumulative = 0.0
            for i, amp in enumerate(self.state.amplitudes):
                prob = abs(amp) ** 2
                cumulative += prob
                if r <= cumulative:
                    counts[i] = counts.get(i, 0) + 1
                    break
        
        return counts
    
    def get_statevector(self) -> List[complex]:
        """Get current state vector."""
        return self.state.amplitudes[:]
    
    def circuit_depth(self) -> int:
        """Get circuit depth (number of operations)."""
        return len(self.operations)
    
    def circuit_summary(self) -> Dict:
        """Get circuit summary."""
        gate_counts = {}
        for op in self.operations:
            gate_counts[op.gate.name] = gate_counts.get(op.gate.name, 0) + 1
        
        return {
            "num_qubits": self.num_qubits,
            "num_operations": len(self.operations),
            "gate_counts": gate_counts,
            "depth": len(self.operations)
        }


class QuantumSimulator:
    """
    Unified quantum simulation controller.
    """
    
    def __init__(self):
        self.circuits: Dict[str, QuantumCircuit] = {}
    
    def create_circuit(self, name: str, num_qubits: int) -> QuantumCircuit:
        """
        Create a named circuit.
        
        Args:
            name: Circuit name
            num_qubits: Number of qubits
        
        Returns:
            QuantumCircuit
        """
        circuit = QuantumCircuit(num_qubits)
        self.circuits[name] = circuit
        return circuit
    
    def run_circuit(self, name: str) -> QubitState:
        """
        Execute named circuit.
        
        Args:
            name: Circuit name
        
        Returns:
            Final state
        """
        circuit = self.circuits.get(name)
        if circuit is None:
            raise ValueError(f"Circuit {name} not found")
        return circuit.execute()
    
    def bell_state(self) -> QuantumCircuit:
        """
        Create Bell state circuit.
        
        Returns:
            Bell state circuit
        """
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cnot(0, 1)
        return circuit
    
    def simulator_summary(self) -> Dict:
        """Get simulator summary."""
        return {
            "circuits": len(self.circuits),
            "circuit_names": list(self.circuits.keys())
        }
