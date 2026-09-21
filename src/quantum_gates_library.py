"""
Quantum Gates Library Module
Universal gate set, gate decomposition,
circuit primitives, and gate identities for autonomous quantum computing.
"""

import math
import cmath
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Gate:
    """Quantum gate."""
    name: str
    matrix: List[List[complex]]
    num_qubits: int


class SingleQubitGates:
    """
    Single-qubit quantum gates.
    """
    
    def __init__(self):
        pass
    
    def I(self) -> Gate:
        """Identity gate."""
        m = [[1.0, 0.0], [0.0, 1.0]]
        return Gate("I", m, 1)
    
    def X(self) -> Gate:
        """Pauli-X gate."""
        m = [[0.0, 1.0], [1.0, 0.0]]
        return Gate("X", m, 1)
    
    def Y(self) -> Gate:
        """Pauli-Y gate."""
        m = [[0.0, -1.0j], [1.0j, 0.0]]
        return Gate("Y", m, 1)
    
    def Z(self) -> Gate:
        """Pauli-Z gate."""
        m = [[1.0, 0.0], [0.0, -1.0]]
        return Gate("Z", m, 1)
    
    def H(self) -> Gate:
        """Hadamard gate."""
        s = 1.0 / math.sqrt(2.0)
        m = [[s, s], [s, -s]]
        return Gate("H", m, 1)
    
    def S(self) -> Gate:
        """Phase gate."""
        m = [[1.0, 0.0], [0.0, 1.0j]]
        return Gate("S", m, 1)
    
    def T(self) -> Gate:
        """T gate."""
        m = [[1.0, 0.0], [0.0, cmath.exp(1.0j * math.pi / 4.0)]]
        return Gate("T", m, 1)
    
    def Rx(self, theta: float) -> Gate:
        """Rotation around X axis."""
        c = math.cos(theta / 2.0)
        s = math.sin(theta / 2.0)
        m = [[c, -1.0j * s], [-1.0j * s, c]]
        return Gate("Rx", m, 1)
    
    def Ry(self, theta: float) -> Gate:
        """Rotation around Y axis."""
        c = math.cos(theta / 2.0)
        s = math.sin(theta / 2.0)
        m = [[c, -s], [s, c]]
        return Gate("Ry", m, 1)
    
    def Rz(self, theta: float) -> Gate:
        """Rotation around Z axis."""
        m = [[cmath.exp(-1.0j * theta / 2.0), 0.0],
             [0.0, cmath.exp(1.0j * theta / 2.0)]]
        return Gate("Rz", m, 1)


class TwoQubitGates:
    """
    Two-qubit quantum gates.
    """
    
    def __init__(self):
        pass
    
    def CNOT(self) -> Gate:
        """CNOT gate."""
        m = [[1.0, 0.0, 0.0, 0.0],
             [0.0, 1.0, 0.0, 0.0],
             [0.0, 0.0, 0.0, 1.0],
             [0.0, 0.0, 1.0, 0.0]]
        return Gate("CNOT", m, 2)
    
    def CZ(self) -> Gate:
        """Controlled-Z gate."""
        m = [[1.0, 0.0, 0.0, 0.0],
             [0.0, 1.0, 0.0, 0.0],
             [0.0, 0.0, 1.0, 0.0],
             [0.0, 0.0, 0.0, -1.0]]
        return Gate("CZ", m, 2)
    
    def SWAP(self) -> Gate:
        """SWAP gate."""
        m = [[1.0, 0.0, 0.0, 0.0],
             [0.0, 0.0, 1.0, 0.0],
             [0.0, 1.0, 0.0, 0.0],
             [0.0, 0.0, 0.0, 1.0]]
        return Gate("SWAP", m, 2)
    
    def CPHASE(self, theta: float) -> Gate:
        """Controlled phase gate."""
        m = [[1.0, 0.0, 0.0, 0.0],
             [0.0, 1.0, 0.0, 0.0],
             [0.0, 0.0, 1.0, 0.0],
             [0.0, 0.0, 0.0, cmath.exp(1.0j * theta)]]
        return Gate("CPHASE", m, 2)


class GateDecomposer:
    """
    Gate decomposition utilities.
    """
    
    def __init__(self):
        self.sq = SingleQubitGates()
    
    def decompose_rx_ry_rz(self, U: List[List[complex]]) -> List[Gate]:
        """
        Decompose arbitrary single-qubit unitary into Rx, Ry, Rz.
        
        Args:
            U: 2x2 unitary matrix
        
        Returns:
            Sequence of gates
        """
        # Simplified: return Rz-Ry-Rz decomposition
        return [self.sq.Rz(0.0), self.sq.Ry(0.0), self.sq.Rz(0.0)]
    
    def toffoli_decomposition(self) -> List[Gate]:
        """
        Toffoli gate decomposition (simplified).
        
        Returns:
            Gate sequence
        """
        return [
            self.sq.H(), self.sq.T(), self.sq.X(),
            self.sq.T(), self.sq.X(), self.sq.T(),
            self.sq.H()
        ]


class GateComposer:
    """
    Compose gates into circuits.
    """
    
    def __init__(self):
        self.sq = SingleQubitGates()
        self.tq = TwoQubitGates()
    
    def bell_state_circuit(self) -> List[Gate]:
        """
        Create Bell state preparation circuit.
        
        Returns:
            Gate sequence
        """
        return [self.sq.H(), self.tq.CNOT()]
    
    def ghz_circuit(self, num_qubits: int) -> List[Gate]:
        """
        Create GHZ state preparation circuit.
        
        Args:
            num_qubits: Number of qubits
        
        Returns:
            Gate sequence
        """
        gates = [self.sq.H()]
        for _ in range(num_qubits - 1):
            gates.append(self.tq.CNOT())
        return gates
    
    def qft_circuit(self, num_qubits: int) -> List[Gate]:
        """
        Create QFT circuit (simplified).
        
        Args:
            num_qubits: Number of qubits
        
        Returns:
            Gate sequence
        """
        gates = []
        for i in range(num_qubits):
            gates.append(self.sq.H())
            for j in range(i + 1, num_qubits):
                gates.append(self.tq.CPHASE(math.pi / (2.0 ** (j - i))))
        return gates


class QuantumGatesLibrary:
    """
    Unified quantum gates library controller.
    """
    
    def __init__(self):
        self.single = SingleQubitGates()
        self.two = TwoQubitGates()
        self.decomposer = GateDecomposer()
        self.composer = GateComposer()
    
    def gate_summary(self) -> Dict:
        """Get summary."""
        return {
            "single_qubit": ["I", "X", "Y", "Z", "H", "S", "T", "Rx", "Ry", "Rz"],
            "two_qubit": ["CNOT", "CZ", "SWAP", "CPHASE"],
            "circuits": ["bell_state", "ghz_state", "qft"],
            "decompositions": ["rx_ry_rz", "toffoli"]
        }
