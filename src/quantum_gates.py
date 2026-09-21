"""
Quantum Gates Module
Single-qubit, multi-qubit, parameterized, and composite
quantum gates with matrix representation for autonomous quantum computing.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Gate:
    """Quantum gate."""
    name: str
    matrix: List[List[complex]]
    num_qubits: int = 1


class SingleQubitGates:
    """
    Single-qubit gates.
    """
    
    def __init__(self):
        self._gates = {
            "I": [[1.0, 0.0], [0.0, 1.0]],
            "X": [[0.0, 1.0], [1.0, 0.0]],
            "Y": [[0.0, -1.0j], [1.0j, 0.0]],
            "Z": [[1.0, 0.0], [0.0, -1.0]],
            "H": [[1.0/math.sqrt(2), 1.0/math.sqrt(2)],
                  [1.0/math.sqrt(2), -1.0/math.sqrt(2)]],
            "S": [[1.0, 0.0], [0.0, 1.0j]],
            "T": [[1.0, 0.0], [0.0, complex(math.cos(math.pi / 4.0), math.sin(math.pi / 4.0))]]
        }
    
    def get(self, name: str) -> Gate:
        """
        Get gate.
        
        Args:
            name: Gate name
        
        Returns:
            Gate
        """
        m = self._gates.get(name, self._gates["I"])
        return Gate(name, m, 1)
    
    def rx(self, theta: float) -> Gate:
        """
        RX rotation.
        
        Args:
            theta: Rotation angle
        
        Returns:
            RX gate
        """
        c = math.cos(theta / 2.0)
        s = math.sin(theta / 2.0)
        m = [[c, -1.0j * s], [-1.0j * s, c]]
        return Gate("RX", m, 1)
    
    def ry(self, theta: float) -> Gate:
        """
        RY rotation.
        
        Args:
            theta: Rotation angle
        
        Returns:
            RY gate
        """
        c = math.cos(theta / 2.0)
        s = math.sin(theta / 2.0)
        m = [[c, -s], [s, c]]
        return Gate("RY", m, 1)
    
    def rz(self, theta: float) -> Gate:
        """
        RZ rotation.
        
        Args:
            theta: Rotation angle
        
        Returns:
            RZ gate
        """
        m = [[complex(math.cos(-theta / 2.0), math.sin(-theta / 2.0)), 0.0],
             [0.0, complex(math.cos(theta / 2.0), math.sin(theta / 2.0))]]
        return Gate("RZ", m, 1)
    
    def phase(self, phi: float) -> Gate:
        """
        Phase gate.
        
        Args:
            phi: Phase angle
        
        Returns:
            Phase gate
        """
        m = [[1.0, 0.0], [0.0, complex(math.cos(phi), math.sin(phi))]]
        return Gate("P", m, 1)


class MultiQubitGates:
    """
    Multi-qubit gates.
    """
    
    def __init__(self):
        pass
    
    def cnot(self) -> Gate:
        """
        CNOT gate.
        
        Returns:
            CNOT
        """
        m = [[1.0, 0.0, 0.0, 0.0],
             [0.0, 1.0, 0.0, 0.0],
             [0.0, 0.0, 0.0, 1.0],
             [0.0, 0.0, 1.0, 0.0]]
        return Gate("CNOT", m, 2)
    
    def cz(self) -> Gate:
        """
        CZ gate.
        
        Returns:
            CZ
        """
        m = [[1.0, 0.0, 0.0, 0.0],
             [0.0, 1.0, 0.0, 0.0],
             [0.0, 0.0, 1.0, 0.0],
             [0.0, 0.0, 0.0, -1.0]]
        return Gate("CZ", m, 2)
    
    def swap(self) -> Gate:
        """
        SWAP gate.
        
        Returns:
            SWAP
        """
        m = [[1.0, 0.0, 0.0, 0.0],
             [0.0, 0.0, 1.0, 0.0],
             [0.0, 1.0, 0.0, 0.0],
             [0.0, 0.0, 0.0, 1.0]]
        return Gate("SWAP", m, 2)
    
    def toffoli(self) -> Gate:
        """
        Toffoli gate.
        
        Returns:
            Toffoli
        """
        m = [[1.0 if i == j else 0.0 for j in range(8)] for i in range(8)]
        m[6][6] = 0.0
        m[6][7] = 1.0
        m[7][7] = 0.0
        m[7][6] = 1.0
        return Gate("Toffoli", m, 3)


class GateComposer:
    """
    Compose quantum gates.
    """
    
    def __init__(self):
        self.single = SingleQubitGates()
        self.multi = MultiQubitGates()
    
    def apply(self, gate: Gate,
             state: List[complex]) -> List[complex]:
        """
        Apply gate to state.
        
        Args:
            gate: Gate
            state: State vector
        
        Returns:
            New state
        """
        dim = 2 ** gate.num_qubits
        if len(state) != dim:
            return state
        
        new_state = [0.0] * dim
        for i in range(dim):
            for j in range(dim):
                new_state[i] += gate.matrix[i][j] * state[j]
        
        return new_state
    
    def tensor_product(self, gate_a: Gate,
                      gate_b: Gate) -> Gate:
        """
        Compute tensor product of gates.
        
        Args:
            gate_a: Gate A
            gate_b: Gate B
        
        Returns:
            Tensor product
        """
        dim_a = 2 ** gate_a.num_qubits
        dim_b = 2 ** gate_b.num_qubits
        dim = dim_a * dim_b
        
        m = [[0.0] * dim for _ in range(dim)]
        for i in range(dim_a):
            for j in range(dim_a):
                for k in range(dim_b):
                    for l in range(dim_b):
                        row = i * dim_b + k
                        col = j * dim_b + l
                        m[row][col] = gate_a.matrix[i][j] * gate_b.matrix[k][l]
        
        return Gate(f"{gate_a.name}⊗{gate_b.name}", m,
                   gate_a.num_qubits + gate_b.num_qubits)
    
    def controlled(self, gate: Gate) -> Gate:
        """
        Create controlled version of gate.
        
        Args:
            gate: Gate
        
        Returns:
            Controlled gate
        """
        dim = 2 ** (gate.num_qubits + 1)
        m = [[0.0] * dim for _ in range(dim)]
        
        # Identity on |0><0|
        half = dim // 2
        for i in range(half):
            m[i][i] = 1.0
        
        # Gate on |1><1|
        for i in range(half):
            for j in range(half):
                m[half + i][half + j] = gate.matrix[i][j]
        
        return Gate(f"C-{gate.name}", m, gate.num_qubits + 1)


class QuantumGates:
    """
    Unified quantum gates controller.
    """
    
    def __init__(self):
        self.single = SingleQubitGates()
        self.multi = MultiQubitGates()
        self.composer = GateComposer()
        self.circuit: List[Gate] = []
    
    def add_gate(self, gate: Gate):
        """
        Add gate to circuit.
        
        Args:
            gate: Gate
        """
        self.circuit.append(gate)
    
    def apply_circuit(self, state: List[complex]) -> List[complex]:
        """
        Apply circuit to state.
        
        Args:
            state: Initial state
        
        Returns:
            Final state
        """
        current = state[:]
        for gate in self.circuit:
            current = self.composer.apply(gate, current)
        return current
    
    def qg_summary(self) -> Dict:
        """Get summary."""
        return {
            "gates": len(self.circuit),
            "single_qubit": ["I", "X", "Y", "Z", "H", "S", "T", "RX", "RY", "RZ", "P"],
            "multi_qubit": ["CNOT", "CZ", "SWAP", "Toffoli"]
        }
